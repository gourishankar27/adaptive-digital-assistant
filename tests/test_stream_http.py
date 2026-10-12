"""Real loopback TCP/SSE, including in-flight credential rotation and detach."""

import os
import socket
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

import httpx

from ada.api import create_app
from ada.auth import token_hash
from ada.config import Settings
from ada.models import User
from ada.providers import Completion, FakeProvider


class HttpStreamFixture(FakeProvider):
    def stream(self, messages, cancel):
        text = ""
        for _ in range(40):
            if cancel.wait(0.05):
                return
            text += "synthetic "
            yield "synthetic "
        yield Completion(text.strip(), self.model)


def fixture_app():
    return create_app(
        Settings(provider="fake", consolidation_worker_enabled=False), HttpStreamFixture()
    )


def test_actual_tcp_detach_reconnect_cancel_and_inflight_revocation(harness):
    h = harness
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    env["ADA_DATABASE_URL"] = h["settings"].database_url
    with tempfile.TemporaryFile() as logs:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "test_stream_http:fixture_app",
                "--app-dir",
                "tests",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--workers",
                "1",
                "--no-access-log",
            ],
            env=env,
            stdout=logs,
            stderr=logs,
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", timeout=10, trust_env=False
            ) as client:
                until = time.monotonic() + 15
                while time.monotonic() < until:
                    try:
                        if client.get("/health/ready").status_code == 200:
                            break
                    except httpx.RequestError:
                        pass
                    time.sleep(0.05)
                else:
                    raise AssertionError("owned stream server did not become ready")
                p = client.post("/v1/personalities", headers=h["a"], json={}).json()["id"]
                cid = client.post(
                    "/v1/conversations", headers=h["a"], json={"personality_id": p}
                ).json()["id"]
                rid = str(uuid4())
                assert (
                    client.post(
                        f"/v1/conversations/{cid}/stream-requests",
                        headers=h["a"],
                        json={"request_id": rid, "content": "Synthetic TCP stream"},
                    ).status_code
                    == 202
                )
                with client.stream(
                    "GET", f"/v1/requests/{rid}/stream?attempt=1&after=0", headers=h["a"]
                ) as stream:
                    assert stream.status_code == 200
                    for line in stream.iter_lines():
                        if line.startswith("data: "):
                            break
                checkpoint = client.get(f"/v1/requests/{rid}/stream-status", headers=h["a"]).json()
                assert checkpoint["stream_state"] == "running"
                assert (
                    client.post(
                        f"/v1/requests/{rid}/cancel", headers=h["b"], json={"attempt": 1}
                    ).status_code
                    == 404
                )
                with client.stream(
                    "GET",
                    f"/v1/requests/{rid}/stream?attempt=1&after={checkpoint['sequence']}",
                    headers=h["a"],
                ) as stream:
                    assert stream.status_code == 200
                    with h["sessions"].begin() as db:
                        db.get(User, h["a_id"]).token_hash = token_hash(
                            "synthetic-rotated-stream-credential"
                        )
                    lines = list(stream.iter_lines())
                    assert "event: access_lost" in lines
                assert (
                    client.get(f"/v1/requests/{rid}/stream-status", headers=h["a"]).status_code
                    == 401
                )
                rotated = {"Authorization": "Bearer synthetic-rotated-stream-credential"}
                receipt = client.post(
                    f"/v1/requests/{rid}/cancel", headers=rotated, json={"attempt": 1}
                )
                assert receipt.status_code == 200 and receipt.json()["outcome"] == "requested"
                until = time.monotonic() + 5
                while time.monotonic() < until:
                    result = client.get(f"/v1/requests/{rid}/stream-status", headers=rotated).json()
                    if result["stream_state"] == "cancelled":
                        break
                    time.sleep(0.02)
                assert (
                    result["result"]["status"] == "failed"
                    and result["result"]["error_code"] == "request_cancelled"
                )
                assert (
                    client.post(
                        f"/v1/requests/{rid}/cancel", headers=rotated, json={"attempt": 1}
                    ).json()
                    == receipt.json()
                )
                slow_id = str(uuid4())
                assert (
                    client.post(
                        f"/v1/conversations/{cid}/stream-requests",
                        headers=rotated,
                        json={"request_id": slow_id, "content": "Synthetic slow observer"},
                    ).status_code
                    == 202
                )
                with client.stream(
                    "GET", f"/v1/requests/{slow_id}/stream?attempt=1&after=0", headers=rotated
                ) as slow_observer:
                    assert slow_observer.status_code == 200
                    # Do not consume this connection's body: durable generation remains independent.
                    until = time.monotonic() + 8
                    while time.monotonic() < until:
                        completed = client.get(
                            f"/v1/requests/{slow_id}/stream-status", headers=rotated
                        ).json()
                        if completed["stream_state"] == "completed":
                            break
                        time.sleep(0.05)
                    assert completed["stream_state"] == "completed"
                # Detach at/after final commit, then recover the same terminal response by GET.
                assert (
                    client.get(f"/v1/requests/{slow_id}", headers=rotated).json()
                    == completed["result"]
                )
                manager = create_app(h["settings"], sessions=h["sessions"]).state.streaming
                batch, terminal = manager.events(h["a_id"], slow_id, 1, 0)
                assert len(batch) == 16 and terminal
                replay = client.get(
                    f"/v1/requests/{slow_id}/stream?attempt=1&after={completed['sequence'] - 1}",
                    headers=rotated,
                )
                assert replay.status_code == 200 and replay.text.count("data: ") == 1
        finally:
            process.terminate()
            process.wait(timeout=10)
