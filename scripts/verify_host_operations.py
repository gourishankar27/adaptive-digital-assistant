"""Disposable Windows/PG/HTTP rehearsal; four-hour fake-provider soak by default."""

import argparse
import json
import os
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import httpx
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.host_backup import run_backup
from ada.host_config import initialize, load_config
from ada.host_health import model_residency
from ada.host_security import HostError, atomic_json, private_directory, protect, timestamp
from ada.host_supervisor import request_stop, supervise
from ada.monitoring import safe_tag

ROOT = Path(__file__).resolve().parents[1]


def task_rehearsal(work, config_path, profile):
    actor = work / "task_actor.py"
    actor.write_text(
        "import os,sys\nfrom pathlib import Path\nos.environ['LOCALAPPDATA']=sys.argv[2]\n"
        "from ada.host_config import load_config\nfrom ada.host_backup import key\n"
        "from ada.host_security import atomic_json\nc,r=load_config(Path(sys.argv[1]));key(r)\n"
        "atomic_json(Path(sys.argv[3]), {'state':'scheduled_identity_key_access_verified'})\n",
        encoding="utf-8",
    )
    output = work / "scheduled-key-result.json"
    script = work / "task-rehearsal.ps1"
    script.write_text(
        r"""
param($Python,$Actor,$Config,$Profile,$Output,$TaskName)
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSHOME 'Modules/CimCmdlets')
Import-Module (Join-Path $PSHOME 'Modules/ScheduledTasks')
$registered=$false
try {
    $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $arguments='"'+$Actor+'" "'+$Config+'" "'+$Profile+'" "'+$Output+'"'
    $a=New-ScheduledTaskAction -Execute $Python -Argument $arguments
    $p=New-ScheduledTaskPrincipal -UserId $sid -LogonType Interactive -RunLevel Limited
    $s=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 1)
    $t=New-ScheduledTask -Action $a -Principal $p -Settings $s
    Register-ScheduledTask -TaskName $TaskName -InputObject $t | Out-Null
    $registered=$true
    Start-ScheduledTask -TaskName $TaskName
    $deadline=[DateTime]::UtcNow.AddSeconds(30)
    while(-not(Test-Path -LiteralPath $Output) -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Milliseconds 250 }
    if(-not(Test-Path -LiteralPath $Output)) { exit 2 }
} catch { exit 3 }
finally { if($registered) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false } }
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(script),
            "-Python",
            str(ROOT / ".venv/Scripts/pythonw.exe"),
            "-Actor",
            str(actor),
            "-Config",
            str(config_path),
            "-Profile",
            str(profile),
            "-Output",
            str(output),
            "-TaskName",
            "ADA26-Validation-" + uuid4().hex,
        ],
        cwd=ROOT,
        capture_output=True,
        timeout=45,
    )
    return "passed" if result.returncode == 0 and output.exists() else "unavailable_or_failed"


def run(seconds, scheduled, native=False, proxy=False, reader_contention=False):
    if (
        os.name != "nt"
        or not os.environ.get("ADA_TEST_DATABASE_URL")
        or not os.environ.get("ADA_TEST_PG_BIN")
    ):
        raise RuntimeError("Explicit Windows/native test PostgreSQL required")
    if native:
        # Never run a competing native inference owner alongside the usual private API/proxy.
        for port in (8000, 18764):
            with socket.socket() as probe:
                if probe.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError(
                        "Private API must be independently stopped for native rehearsal"
                    )
        resident = model_residency(Settings())
        if resident["loaded_models"] and not resident["configured_model_loaded"]:
            raise RuntimeError("Other model is resident; do not load a second model")
    parsed = make_url(os.environ["ADA_TEST_DATABASE_URL"]).set(query={})
    name = "ada_host_fixture_" + uuid4().hex[:16]
    admin = create_engine(parsed.set(database="postgres"), isolation_level="AUTOCOMMIT")
    work = ROOT / ".pytest_cache/phase26" / ("run-" + uuid4().hex[:10])
    profile = work / "validation profile"
    profile.mkdir(parents=True)
    previous = os.environ.copy()
    url = parsed.set(database=name).render_as_string(hide_password=False)
    os.environ.update(
        ADA_DATABASE_URL=url,
        LOCALAPPDATA=str(profile),
        ADA_PROVIDER="ollama" if native else "fake",
        ADA_MAX_PARALLEL="1",
        ADA_WEB_RESEARCH_ENABLED="false",
    )
    config_path = profile / "ADA/operations/host.json"
    children, failures, supervisor_thread = [], [], None
    owned = [name]
    result = {
        "provider": "configured_ollama" if native else "explicit_fake",
        "requested_soak_seconds": seconds,
        "started_at": timestamp(),
        "task_scheduler": "not_requested",
    }
    stage, started, ticks, unavailable, durations = "bootstrap", None, 0, 0, []
    try:
        with admin.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{name}" TEMPLATE template0'))
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        initialize(config_path, ROOT, os.environ["ADA_TEST_PG_BIN"], port)
        data = json.loads(config_path.read_bytes())
        if proxy:
            import shutil

            pin = json.loads((ROOT / "ops/validation-tools.json").read_bytes())["caddy"]
            relative = f"ADA/tools/caddy-{pin['version']}/caddy.exe"
            source = Path(previous["LOCALAPPDATA"]) / relative
            destination_binary = profile / relative
            destination_binary.parent.mkdir(parents=True)
            shutil.copyfile(source, destination_binary)
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                data["proxy_port"] = listener.getsockname()[1]
            data["tailnet_proxy"] = True
        atomic_json(
            config_path, data | {"poll_seconds": 2, "stable_seconds": 30, "quiet_seconds": 5}
        )
        config, root = load_config(config_path)
        destination = private_directory(config.backup_directory)
        (root / "backup-key.dpapi").write_bytes(
            protect(b"Public synthetic Windows operations backup phrase")
        )
        settings = Settings()
        result["model"] = safe_tag(settings.ollama_model) if native else "explicit_fake"
        result["context_tokens"] = settings.context_tokens
        result["output_tokens"] = settings.output_tokens
        result["model_residency_before"] = model_residency(settings)
        engine, sessions = connect(url)
        _, token = create_user(sessions, "Public operations fixture owner")
        engine.dispose()
        if scheduled:
            stage = "scheduled_key_access"
            result["task_scheduler"] = task_rehearsal(work, config_path, profile)

        def launch(*args, **kwargs):
            child = subprocess.Popen(*args, **kwargs)
            if "ada.host_ops" in args[0]:
                children.append(child)
            return child

        def start():
            try:
                supervise(config, root, settings, config_path, launch=launch)
            except Exception as exc:
                failures.append(type(exc).__name__)

        supervisor_thread = threading.Thread(target=start, daemon=True)
        stage = "supervisor_start"
        supervisor_thread.start()
        origin = f"http://127.0.0.1:{port}"
        with httpx.Client(
            base_url=origin,
            timeout=settings.timeout_seconds + 15,
            trust_env=False,
            headers={"Authorization": "Bearer " + token},
        ) as client:

            def ready():
                try:
                    return client.get("/health/ready").status_code == 200
                except httpx.HTTPError:
                    return False

            deadline = time.monotonic() + 45
            while not ready() and time.monotonic() < deadline and supervisor_thread.is_alive():
                time.sleep(0.2)
            assert ready(), "API startup did not become ready"
            if proxy:
                deadline = time.monotonic() + 20
                with httpx.Client(timeout=3, trust_env=False) as proxy_client:
                    proxy_ready = False
                    while not proxy_ready and time.monotonic() < deadline:
                        try:
                            answer = proxy_client.get(
                                f"http://127.0.0.1:{config.proxy_port}/health/ready"
                            )
                            proxy_ready = (
                                answer.status_code == 200
                                and answer.headers.get("cache-control") == "no-store"
                            )
                        except httpx.HTTPError:
                            time.sleep(0.2)
                    assert proxy_ready
                result["owned_pinned_proxy_ready"] = True
            duplicate = subprocess.run(
                [sys.executable, "-m", "ada.host_ops", "supervise", "--config", str(config_path)],
                capture_output=True,
                timeout=15,
            )
            assert duplicate.returncode != 0
            result["duplicate_start_rejected"] = True
            personality = client.post("/v1/personalities", json={}).json()["id"]
            conversation = client.post(
                "/v1/conversations", json={"personality_id": personality}
            ).json()["id"]
            route = f"/v1/conversations/{conversation}/messages"
            body = {
                "request_id": str(uuid4()),
                "content": "Public synthetic restart replay sample",
                "use_memory": False,
            }
            cold_started = time.monotonic()
            saved = client.post(route, json=body)
            assert saved.status_code == 200
            result["first_public_reply_seconds"] = round(time.monotonic() - cold_started, 3)
            result["model_residency_after"] = model_residency(settings)
            children[-1].terminate()  # Exact Popen object created by this fixture's supervisor.
            children[-1].wait(timeout=10)
            deadline = time.monotonic() + 45
            while (len(children) < 2 or not ready()) and time.monotonic() < deadline:
                time.sleep(0.2)
            assert len(children) >= 2 and ready()
            replay = client.post(route, json=body)
            assert replay.status_code == 200 and replay.json() == saved.json()
            result["owned_api_crash_recovered_with_completed_replay"] = True

            # Concurrent public requests exercise actual process admission, not model speed.
            conversations = [
                client.post("/v1/conversations", json={"personality_id": personality}).json()["id"]
                for _ in range(8)
            ]
            barrier = threading.Barrier(len(conversations))

            def concurrent(conversation_id):
                barrier.wait(timeout=10)
                return client.post(
                    f"/v1/conversations/{conversation_id}/messages",
                    json={
                        "request_id": str(uuid4()),
                        "content": "Public capacity sample",
                        "use_memory": False,
                    },
                ).status_code

            with ThreadPoolExecutor(max_workers=8) as pool:
                statuses = list(pool.map(concurrent, conversations))
            assert all(code in (200, 429, 503) for code in statuses)
            result["capacity_status_counts"] = {
                str(code): statuses.count(code) for code in set(statuses)
            }
            stage = "soak_health"
            started = time.monotonic()
            if reader_contention:
                # Public metadata reader, never a private data read. Exercise Windows
                # sharing while the real supervisor publishes its next receipt.
                def hold_receipt():
                    with (root / "supervisor.json").open("rb"):
                        time.sleep(2.75)

                reader = threading.Thread(target=hold_receipt)
                reader.start()
                result["receipt_reader_contention"] = True
            while time.monotonic() - started < seconds:
                stage = "soak_health"
                if not ready():
                    unavailable += 1
                if ticks % 10 == 0:
                    stage = "soak_chat"
                    began = time.monotonic()
                    response = client.post(
                        route,
                        json={
                            "request_id": str(uuid4()),
                            "content": "Public host soak sample",
                            "use_memory": False,
                        },
                    )
                    assert response.status_code == 200
                    durations.append(time.monotonic() - began)
                ticks += 1
                time.sleep(1)
            result.update(
                actual_soak_seconds=round(time.monotonic() - started, 2),
                health_samples=ticks,
                unavailable_samples=unavailable,
                public_chat_samples=len(durations),
                public_chat_max_seconds=round(max(durations), 4),
                public_chat_mean_seconds=round(sum(durations) / len(durations), 4),
                real_model_latency="measured_public_only" if native else "not_measured",
                cold_warm_model_readiness="residency_and_public_request_timings"
                if native
                else "not_measured",
            )
        stage = "backup"
        result["backup_busy_retries"] = 0
        for backup_attempt in range(10):
            try:
                backup_receipt = run_backup(config, root, settings)
                break
            except HostError as error:
                if str(error) != "already_running" or backup_attempt == 9:
                    raise
                result["backup_busy_retries"] += 1
                time.sleep(0.25)
        assert backup_receipt["state"] == "verified", "Backup deferred by actual host pressure"
        restore_target = "ada_restore_" + uuid4().hex[:16]
        owned.append(restore_target)
        began = time.monotonic()
        stage = "isolated_restore"
        restore_process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ada.host_ops",
                "restore",
                "--config",
                str(config_path),
                "--database",
                restore_target,
                "--artifact",
                str(destination / backup_receipt["artifact"]),
                "--deletion-ledger",
                str(destination / backup_receipt["ledger"]),
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert restore_process.returncode == 0
        restored = json.loads(restore_process.stdout)
        assert restored["quarantined"]
        result.update(
            backup_seconds=backup_receipt["seconds"],
            encrypted_backup_bytes=backup_receipt["bytes"],
            isolated_restore_seconds=round(time.monotonic() - began, 3),
            recovery_credentials_quarantined=True,
        )
        result["last_host_metrics"] = json.loads((root / "supervisor.json").read_bytes())["health"][
            "resources"
        ]
        stage = "graceful_stop"
        request_stop(root)
        supervisor_thread.join(timeout=config.shutdown_seconds + 15)
        assert not supervisor_thread.is_alive() and not failures
        stopped = json.loads((root / "supervisor.json").read_bytes())
        assert (
            stopped["state"] == "stopped"
            and stopped["child_pid"] is None
            and stopped["proxy_pid"] is None
        )
        result["graceful_supervisor_stop"] = True
        result["state"] = "passed"
    except Exception as exc:
        result.update(
            state="failed",
            code=type(exc).__name__,
            stage=stage,
            actual_soak_seconds=result.get(
                "actual_soak_seconds", round(time.monotonic() - started, 2) if started else None
            ),
            health_samples=ticks,
            unavailable_samples=unavailable,
            public_chat_samples=len(durations),
        )
        raise
    finally:
        try:
            if (config_path.parent / "supervisor.json").exists():
                request_stop(config_path.parent)
            if supervisor_thread:
                supervisor_thread.join(timeout=40)
            for child in children:
                if child.poll() is None:
                    child.terminate()
                    child.wait(timeout=10)
            with admin.connect() as conn:
                for database in reversed(owned):
                    assert database.startswith(("ada_host_fixture_", "ada_restore_"))
                    conn.execute(text(f'DROP DATABASE IF EXISTS "{database}" WITH (FORCE)'))
        finally:
            admin.dispose()
            os.environ.clear()
            os.environ.update(previous)
            result["finished_at"] = timestamp()
            result["supervisor_errors"] = list(failures)
            result["api_child_exit_codes"] = [child.poll() for child in children]
            atomic_json(work / "result.json", result)
            print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=4 * 3600)
    parser.add_argument("--task-scheduler", action="store_true")
    parser.add_argument("--native-model", action="store_true")
    parser.add_argument("--with-proxy", action="store_true")
    parser.add_argument("--reader-contention", action="store_true")
    args = parser.parse_args()
    if not 15 <= args.seconds <= 24 * 3600:
        parser.error("Duration must be15seconds through24hours; report actual duration")
    try:
        run(
            args.seconds,
            args.task_scheduler,
            args.native_model,
            args.with_proxy,
            args.reader_contention,
        )
    except Exception:
        raise SystemExit(
            "Isolated host rehearsal failed; inspect its fixed-metadata result"
        ) from None
