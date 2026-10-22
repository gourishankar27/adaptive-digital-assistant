"""One owned API child; bounded recovery never manages external Ollama/DB processes."""

import asyncio
import json
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from uuid import uuid4

from ada.host_health import observe
from ada.host_runtime import admission_owner
from ada.host_security import HostError, OwnedJob, Singleton, atomic_json, timestamp


class RetryBudget:
    def __init__(self, limit=5, stable_seconds=300):
        self.limit, self.stable_seconds, self.failures = limit, stable_seconds, 0

    def failed(self, now, uptime=0):
        if uptime >= self.stable_seconds:
            self.failures = 0
        self.failures += 1
        return min(30, 2 ** (self.failures - 1)) if self.failures <= self.limit else None


def health_action(health):
    if health["database"] == "schema_mismatch":
        return "stop_schema"
    if health["database"] != "ready":
        return "wait_database"
    if health["provider"] not in ("ready", "synthetic"):
        return "wait_provider"
    return "ready"


def stop_requested(root, run):
    try:
        return json.loads((root / "stop.json").read_bytes()).get("run") == run
    except (OSError, ValueError):
        return False


def request_stop(root):
    try:
        state = json.loads((root / "supervisor.json").read_bytes())
        atomic_json(root / "stop.json", {"run": state["run"], "requested_at": timestamp()})
    except (OSError, KeyError, ValueError):
        raise HostError("supervisor_not_observed") from None


def parent_alive(pid):
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE; never terminate rights.
        if not handle:
            return False
        try:
            return kernel.WaitForSingleObject(handle, 0) == 258
        finally:
            kernel.CloseHandle(handle)
    return Path(f"/proc/{pid}").exists()


def serve(config, root, settings, run):
    """Graceful shutdown works without a console/CTRL_BREAK signal."""
    import uvicorn

    from ada.api import create_app
    from ada.monitoring import ProviderProbe
    from ada.providers import FakeProvider, OllamaProvider
    from ada.service import recover_stale

    parent = os.getppid()
    with admission_owner(settings, root):
        app = create_app(settings)
        # Safe only under the installation's API singleton, before accepting HTTP.
        # Active streaming is reconciled by its existing instance fences at startup.
        recover_stale(app.state.sessions, timestamp() + 1)
        probe = ProviderProbe(
            OllamaProvider(settings) if settings.provider == "ollama" else FakeProvider()
        )
        latest, foreground = {"value": None}, {"at": time.monotonic()}
        stop = threading.Event()

        def sample():
            while not stop.is_set():
                latest["value"] = observe(config, root, settings, probe)
                stop.wait(config.poll_seconds)

        observer = threading.Thread(target=sample, name="ada-host-health", daemon=True)
        observer.start()

        def allowed():
            snapshot = latest["value"]
            return (
                snapshot is not None
                and timestamp() - snapshot["observed_at"] <= config.poll_seconds * 3000
                and snapshot["discretionary_pause"] is None
                and snapshot["provider"] in ("ready", "synthetic")
                and snapshot["database"] == "ready"
                and time.monotonic() - foreground["at"] >= config.quiet_seconds
            )

        def delivery_allowed():
            snapshot = latest["value"]
            return (
                snapshot is not None
                and timestamp() - snapshot["observed_at"] <= config.poll_seconds * 3000
                and snapshot["discretionary_pause"] is None
                and snapshot["database"] == "ready"
            )

        app.state.consolidation.discretionary_allowed = allowed
        # Inbox publication uses no model or inference admission/quiet period.
        app.state.scheduling.discretionary_allowed = delivery_allowed

        def reflection_resources():
            snapshot = latest["value"]
            if (
                snapshot is None
                or timestamp() - snapshot["observed_at"] > config.poll_seconds * 3000
            ):
                return {}
            return dict(snapshot.get("resources", {}))

        app.state.reflection.resources = reflection_resources

        @app.middleware("http")
        async def foreground_activity(request, call_next):
            # Server activity only. No phone-presence, message or query logging.
            if request.method == "POST" and (
                request.url.path.endswith("/messages") or request.url.path.endswith("/stream")
            ):
                foreground["at"] = time.monotonic()
            return await call_next(request)

        server = uvicorn.Server(
            uvicorn.Config(
                app,
                host="127.0.0.1",
                port=config.port,
                workers=1,
                access_log=False,
                log_config=None,
                proxy_headers=False,
                limit_concurrency=128,
                timeout_keep_alive=5,
                h11_max_incomplete_event_size=16384,
                timeout_graceful_shutdown=config.shutdown_seconds,
            )
        )

        async def monitor():
            while not server.should_exit:
                if stop_requested(root, run) or not parent_alive(parent):
                    server.should_exit = True
                    return
                await asyncio.sleep(0.25)

        async def run_server():
            monitor_task = asyncio.create_task(monitor())
            try:
                await server.serve()
            finally:
                monitor_task.cancel()
                stop.set()

        try:
            asyncio.run(run_server())
        finally:
            stop.set()
            observer.join(timeout=4)


def supervise(config, root, settings, config_path, *, launch=subprocess.Popen):
    from ada.host_backup import refresh_ledger

    with Singleton(root / "supervisor.lock"), OwnedJob() as owned_job:
        if (root / "crash-stop.json").exists():
            raise HostError("crash_stop_requires_operator_reset")
        run = uuid4().hex
        state = dict(
            format="ada-supervisor-v1",
            run=run,
            state="starting",
            pid=os.getpid(),
            child_pid=None,
            observed_at=timestamp(),
            attempts=0,
            code=None,
            health=None,
        )
        child = None
        proxy = None
        budget = RetryBudget(config.crash_limit, config.stable_seconds)
        proxy_budget = RetryBudget(config.crash_limit, config.stable_seconds)
        proxy_started = 0.0
        last_tick, last_ledger, launched = time.monotonic(), 0.0, 0.0

        def publish(status, code=None, health=None):
            state.update(
                state=status,
                code=code,
                health=health if health is not None else state["health"],
                observed_at=timestamp(),
                child_pid=child.pid if child and child.poll() is None else None,
                proxy_pid=proxy.pid if proxy and proxy.poll() is None else None,
            )
            atomic_json(root / "supervisor.json", state)

        def wait(seconds):
            until = time.monotonic() + seconds
            while time.monotonic() < until and not stop_requested(root, run):
                time.sleep(0.25)

        try:
            publish("starting")
            # An externally owned listener is never adopted or terminated.
            with socket.socket() as sock:
                if os.name == "nt":
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
                try:
                    sock.bind(("127.0.0.1", config.port))
                except OSError:
                    raise HostError("api_port_owned_elsewhere") from None
            startup = 0
            while not stop_requested(root, run):
                health = observe(config, root, settings)
                action = health_action(health)
                if action == "stop_schema":
                    raise HostError("schema_upgrade_required")
                if child is None and action == "wait_database":
                    startup += 1
                    publish("waiting_database", health=health)
                    if startup >= config.startup_attempts:
                        raise HostError("database_startup_budget_exhausted")
                    wait(min(30, 2 ** (startup - 1)))
                    continue
                if child is None:
                    child = launch(
                        [
                            sys.executable,
                            "-m",
                            "ada.host_ops",
                            "serve",
                            "--config",
                            str(config_path),
                            "--run",
                            run,
                        ],
                        cwd=config.repository,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                    owned_job.assign(child)
                    launched = time.monotonic()
                    state["attempts"] += 1
                if child.poll() is not None:
                    delay = budget.failed(time.monotonic(), time.monotonic() - launched)
                    child = None
                    publish("backoff", code="api_child_exited", health=health)
                    if delay is None:
                        raise HostError("api_crash_loop_stopped")
                    wait(delay)
                    continue
                if config.tailnet_proxy and health["api_ready"]:
                    if proxy is not None and proxy.poll() is not None:
                        delay = proxy_budget.failed(
                            time.monotonic(), time.monotonic() - proxy_started
                        )
                        proxy = None
                        if delay is None:
                            raise HostError("private_proxy_crash_loop_stopped")
                        wait(delay)
                    if proxy is None:
                        from ada.host_proxy import launch_proxy

                        proxy = launch_proxy(config, root, launch)
                        owned_job.assign(proxy)
                        proxy_started = time.monotonic()
                gap = time.monotonic() - last_tick
                last_tick = time.monotonic()
                health["resume_gap_detected"] = gap > max(60, config.poll_seconds * 3)
                publish(
                    "ready"
                    if health["api_ready"] and action == "ready"
                    else "degraded"
                    if health["api_live"]
                    else "api_unresponsive"
                    if time.monotonic() - launched > 30
                    else "starting",
                    health=health,
                )
                if (root / "backup-key.dpapi").is_file() and time.monotonic() - last_ledger >= 60:
                    try:
                        refresh_ledger(config, root, settings)
                    except Exception:
                        atomic_json(
                            root / "ledger-latest.json", {"state": "failed", "verified_at": None}
                        )
                    last_ledger = time.monotonic()
                wait(config.poll_seconds)
        except HostError as error:
            if str(error) == "api_crash_loop_stopped":
                atomic_json(
                    root / "crash-stop.json", {"stopped_at": timestamp(), "code": str(error)}
                )
            publish("stopped", code=str(error))
            raise
        finally:
            atomic_json(root / "stop.json", {"run": run, "requested_at": timestamp()})
            if child and child.poll() is None:
                try:
                    child.wait(timeout=config.shutdown_seconds + 8)
                except subprocess.TimeoutExpired:
                    # Only this exact Popen child. Never pkill/taskkill or kill external tools.
                    child.terminate()
                    child.wait(timeout=10)
                    publish("stopped", code="owned_child_forced_after_grace")
            if proxy and proxy.poll() is None:
                # Admin-off proxy has no control API. API drains first; stop only our proxy.
                proxy.terminate()
                proxy.wait(timeout=10)
            publish("stopped", code=state["code"])
