"""Foreground startup must refuse duplicates and report actual listener state."""

import asyncio
import os
import shutil
import socket
import subprocess
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest


@pytest.mark.skipif(os.name != "nt", reason="Native Windows foreground launcher")
@pytest.mark.parametrize("shell", ["powershell.exe", "pwsh.exe"])
@pytest.mark.parametrize(
    "address,family", [("127.0.0.1", socket.AF_INET), ("::1", socket.AF_INET6)]
)
def test_foreground_refuses_occupied_port_before_runtime_writes(tmp_path, shell, address, family):
    if shutil.which(shell) is None:
        pytest.skip("Optional PowerShell edition is unavailable")
    profile = tmp_path / "isolated-profile"
    environment = dict(
        os.environ,
        LOCALAPPDATA=str(profile),
        ADA_DATABASE_URL="postgresql+psycopg://ada_validation@127.0.0.1:1/ada_test_unavailable",
        ADA_PROVIDER="fake",
        ADA_WEB_RESEARCH_ENABLED="false",
    )
    repository = Path(__file__).resolve().parents[1]
    with socket.socket(family) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        listener.bind((address, 0))
        listener.listen()
        result = subprocess.run(
            [
                shell,
                "-NoProfile",
                "-File",
                str(repository / "scripts/start.ps1"),
                "-ListenAddress",
                address,
                "-Port",
                str(listener.getsockname()[1]),
            ],
            cwd=repository,
            env=environment,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=30,
        )
    assert result.returncode != 0
    assert "already in use" in result.stderr.lower()
    assert not (profile / "ADA/operations").exists(), (
        "Occupied-port refusal entered the private runtime"
    )


@pytest.mark.skipif(os.name != "nt", reason="Native Windows foreground launcher")
@pytest.mark.parametrize(
    "shell,address,family",
    [("powershell.exe", "127.0.0.1", socket.AF_INET), ("pwsh.exe", "::1", socket.AF_INET6)],
)
def test_foreground_free_port_reaches_database_gate(tmp_path, shell, address, family):
    if shutil.which(shell) is None:
        pytest.skip("Optional PowerShell edition is unavailable")
    profile = tmp_path / "isolated-profile"
    environment = dict(
        os.environ,
        LOCALAPPDATA=str(profile),
        ADA_DATABASE_URL="postgresql+psycopg://ada_validation@127.0.0.1:1/ada_test_unavailable",
        ADA_PROVIDER="fake",
        ADA_WEB_RESEARCH_ENABLED="false",
    )
    repository = Path(__file__).resolve().parents[1]
    with socket.socket(family) as probe:
        probe.bind((address, 0))
        port = probe.getsockname()[1]
    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-File",
            str(repository / "scripts/start.ps1"),
            "-ListenAddress",
            address,
            "-Port",
            str(port),
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=30,
    )
    assert result.returncode != 0
    assert "database_ownership_gate_unavailable" in result.stdout
    assert "Starting ADA." in result.stdout
    assert "Checking the protected runtime" in result.stdout
    assert "ADA API is running" not in result.stdout
    assert (profile / "ADA/operations").is_dir()


def isolated_foreground(monkeypatch, tmp_path):
    """Use a public ASGI fixture; never read/recover the operator's database."""
    from fastapi import FastAPI

    from ada import api, host_runtime, service

    root = tmp_path / "ADA/operations"
    root.mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(host_runtime, "admission_owner", lambda *_: nullcontext())
    app = FastAPI()
    app.state.sessions = object()

    @app.get("/health/live")
    def live():
        return {"status": "ok"}

    monkeypatch.setattr(api, "create_app", lambda _: app)
    monkeypatch.setattr(service, "recover_stale", lambda *_: None)
    return host_runtime.foreground


@pytest.mark.parametrize(
    "address,family,browser_origin",
    [
        ("127.0.0.1", socket.AF_INET, None),
        ("::1", socket.AF_INET6, "https://ada-validation.example"),
    ],
)
def test_running_banner_follows_real_listener_and_explains_connections(
    monkeypatch, tmp_path, capsys, address, family, browser_origin
):
    import uvicorn

    foreground = isolated_foreground(monkeypatch, tmp_path)
    with socket.socket(family) as probe:
        probe.bind((address, 0))
        port = probe.getsockname()[1]
    host = f"[{address}]" if family == socket.AF_INET6 else address
    origin = f"http://{host}:{port}"

    def exercise(server):
        assert server.config.workers == 1
        assert server.config.access_log is False
        assert server.config.proxy_headers is False

        async def run():
            task = asyncio.create_task(server.serve())
            try:
                for _ in range(100):
                    if server.started or task.done():
                        break
                    await asyncio.sleep(0.01)
                assert server.started
                async with httpx.AsyncClient(trust_env=False) as client:
                    result = await client.get(origin + "/health/live", timeout=5)
                assert result.status_code == 200
                assert result.json() == {"status": "ok"}
            finally:
                server.should_exit = True
                await asyncio.wait_for(task, timeout=5)

        asyncio.run(run())

    monkeypatch.setattr(uvicorn.Server, "run", exercise)
    foreground(SimpleNamespace(browser_origin=browser_origin), address, port)
    output = capsys.readouterr().out
    assert f"ADA API is running at {origin}" in output
    assert f"Readiness: {origin}/health/ready (expect status: ready)" in output
    assert output.index("Starting the HTTP listener") < output.index("ADA API is running")
    assert "Press Ctrl+C to stop ADA" in output
    assert "API stopped" in output
    if browser_origin:
        assert f"Admin: {browser_origin}/admin/" in output
        assert f"Android server: {browser_origin}" in output
        assert "With the private proxy and HTTPS route running" in output
    else:
        assert "docs/PRIVATE-SETUP-WINDOWS-TAILSCALE.md" in output


def test_late_bind_failure_never_prints_running_or_connection_instructions(
    monkeypatch, tmp_path, capsys
):
    foreground = isolated_foreground(monkeypatch, tmp_path)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        with pytest.raises(SystemExit):
            foreground(
                SimpleNamespace(browser_origin="https://ada-validation.example"),
                "127.0.0.1",
                listener.getsockname()[1],
            )
    output = capsys.readouterr().out
    assert "ADA API is running" not in output
    assert "Admin:" not in output
    assert "API stopped" in output


def test_lifespan_failure_never_announces_running(monkeypatch, tmp_path, capsys):
    from contextlib import asynccontextmanager

    from fastapi import FastAPI

    from ada import api

    foreground = isolated_foreground(monkeypatch, tmp_path)

    @asynccontextmanager
    async def broken_lifespan(_):
        raise RuntimeError("Public synthetic startup failure")
        yield  # pragma: no cover

    app = FastAPI(lifespan=broken_lifespan)
    app.state.sessions = object()
    monkeypatch.setattr(api, "create_app", lambda _: app)
    with pytest.raises(SystemExit):
        foreground(SimpleNamespace(browser_origin=None), "127.0.0.1", 0)
    output = capsys.readouterr().out
    assert "ADA API is running" not in output
    assert "API stopped" in output


@pytest.mark.parametrize("started", [False, True])
def test_ctrl_c_is_quiet_and_startup_interruption_is_not_success(
    monkeypatch, tmp_path, capsys, started
):
    import uvicorn

    foreground = isolated_foreground(monkeypatch, tmp_path)

    def interrupt(server):
        server.started = started
        raise KeyboardInterrupt

    monkeypatch.setattr(uvicorn.Server, "run", interrupt)
    settings = SimpleNamespace(browser_origin=None)
    if started:
        foreground(settings, "127.0.0.1", 0)
    else:
        with pytest.raises(SystemExit) as result:
            foreground(settings, "127.0.0.1", 0)
        assert result.value.code == 1
    output = capsys.readouterr().out
    assert "Traceback" not in output
    assert "API stopped" in output
