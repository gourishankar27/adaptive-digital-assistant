"""Actual one-worker HTTP and CLI boundary on disposable migrated databases."""

import os
import socket
import subprocess
import sys
import tempfile
import time

import httpx


def test_admin_grant_http_monitoring_and_cli_revocation(harness):
    h = harness
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    environment = os.environ.copy()
    environment.update(ADA_DATABASE_URL=h["settings"].database_url, ADA_PROVIDER="fake")
    marker = "SYNTHETIC_HTTP_PRIVATE_BODY"
    with tempfile.TemporaryFile() as logs:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "ada.api:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--workers",
                "1",
                "--no-access-log",
            ],
            env=environment,
            stdout=logs,
            stderr=logs,
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", timeout=5, trust_env=False
            ) as client:
                deadline = time.monotonic() + 15
                while True:
                    assert process.poll() is None, "Disposable HTTP server exited"
                    try:
                        if client.get("/health/ready").status_code == 200:
                            break
                    except httpx.RequestError:
                        pass
                    assert time.monotonic() < deadline, (
                        "Disposable HTTP server did not become ready"
                    )
                    time.sleep(0.05)
                assert client.get("/v1/admin/me", headers=h["a"]).status_code == 403

                def cli(command):
                    result = subprocess.run(
                        [sys.executable, "-m", "ada.cli", command, h["a_id"]],
                        env=environment,
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                    assert result.returncode == 0, "Local admin CLI command failed"
                    assert "token" not in result.stdout and "Alice" not in result.stdout

                cli("grant-admin")
                assert client.get("/v1/admin/me", headers=h["a"]).json()["permissions"] == [
                    "monitoring:read"
                ]
                profile = client.post("/v1/personalities", headers=h["b"], json={}).json()["id"]
                conv = client.post(
                    "/v1/conversations", headers=h["b"], json={"personality_id": profile}
                ).json()["id"]
                from uuid import uuid4

                reply = client.post(
                    f"/v1/conversations/{conv}/messages",
                    headers=h["b"],
                    json={"request_id": str(uuid4()), "content": marker},
                )
                assert reply.status_code == 200
                rid = reply.json()["request_id"]
                response = client.get(f"/v1/admin/requests/{h['b_id']}/{rid}", headers=h["a"])
                assert response.status_code == 200 and marker not in response.text
                assert response.json()["owner_id"] == h["b_id"]
                assert client.get(f"/v1/requests/{rid}", headers=h["a"]).status_code == 404
                cli("revoke-admin")
                assert client.get("/v1/admin/me", headers=h["a"]).status_code == 403
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        logs.seek(0)
        captured = logs.read().decode("utf-8", errors="replace")
        assert marker not in captured and "token_hash" not in captured
        assert h["a"]["Authorization"].removeprefix("Bearer ") not in captured
        assert h["b"]["Authorization"].removeprefix("Bearer ") not in captured
