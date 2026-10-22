"""Occupied foreground listeners must be refused before private runtime recovery."""

import os
import shutil
import socket
import subprocess
from pathlib import Path

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
    assert (profile / "ADA/operations").is_dir()
