"""Isolated ADA/TLS routing rehearsal. No VPN, firewall, system trust or live DB changes."""

import argparse
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import httpx
from alembic import command
from alembic.config import Config
from verify_private_proxy import certificates

from ada.admin import set_admin_grant
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.schema import SCHEMA_HEAD

ROOT = Path(__file__).resolve().parents[1]


def seed(directory):
    url = "sqlite:///" + (directory / "fixture.db").as_posix()
    previous = os.environ.get("ADA_DATABASE_URL")
    try:
        os.environ["ADA_DATABASE_URL"] = url
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    finally:
        if previous is None:
            os.environ.pop("ADA_DATABASE_URL", None)
        else:
            os.environ["ADA_DATABASE_URL"] = previous
    engine, sessions = connect(url)
    try:
        owner, token = create_user(sessions, "Synthetic proxy owner")
        other, other_token = create_user(sessions, "Synthetic other owner")
        set_admin_grant(sessions, owner, True)
        return token, other_token
    finally:
        engine.dispose()


def fixture(directory, port):
    import uvicorn

    from ada.api import create_app

    settings = Settings(
        database_url="sqlite:///" + (directory / "fixture.db").as_posix(),
        provider="fake",
        consolidation_worker_enabled=False,
    )
    uvicorn.run(
        create_app(settings),
        host="127.0.0.1",
        port=port,
        workers=1,
        access_log=False,
        log_level="critical",
    )


def adapt(binary, source, environment, directory, name, replacements=()):
    result = subprocess.run(
        [str(binary), "adapt", "--config", str(source), "--adapter", "caddyfile"],
        env=environment,
        check=True,
        capture_output=True,
    )
    configuration = json.loads(result.stdout)

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "listen":
                    value[key] = ["127.0.0.1:" + address.rsplit(":", 1)[1] for address in item]
                elif key == "dial":
                    for old, new in replacements:
                        value[key] = value[key].replace(old, new)
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(configuration)
    target = directory / (name + ".json")
    target.write_text(json.dumps(configuration))
    subprocess.run(
        [str(binary), "validate", "--config", str(target)],
        env=environment,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return target


def start_proxy(binary, config, environment):
    return subprocess.Popen(
        [str(binary), "run", "--config", str(config)],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def tls_rejected(port, context, hostname):
    with socket.create_connection(("127.0.0.1", port), timeout=3) as raw:
        try:
            with context.wrap_socket(raw, server_hostname=hostname):
                pass
        except ssl.SSLError as error:
            # Caddy may reject an unknown SNI before presenting a certificate.
            return isinstance(error, ssl.SSLCertVerificationError) or hostname != "localhost"
    return False


def exercise(origin, context, token, other_token):
    headers = {"Authorization": "Bearer " + token}
    with httpx.Client(
        base_url=origin, verify=context, trust_env=False, timeout=10, follow_redirects=False
    ) as c:
        assert c.get("/health/ready").json() == {"status": "ready", "schema": SCHEMA_HEAD}
        assert c.get("/v1/me").status_code == 401
        assert (
            c.get(
                "/v1/admin/me", headers={"Tailscale-User-Login": "admin@example.invalid"}
            ).status_code
            == 401
        )
        assert (
            c.get("/v1/admin/me", headers={"Authorization": "Bearer " + other_token}).status_code
            == 403
        )
        assert c.get("/v1/admin/me", headers=headers).status_code == 200
        assert c.get("/admin").status_code == 308
        assert c.get("/admin").headers["location"] == "/admin/"
        assert 'id="root"' in c.get("/admin/settings").text
        assert (
            c.get("/v1/missing", headers=headers)
            .headers["content-type"]
            .startswith("application/json")
        )
        personality = c.post("/v1/personalities", headers=headers, json={})
        assert personality.status_code == 201
        conversation = c.post(
            "/v1/conversations",
            headers=headers,
            json={
                "personality_id": personality.json()["id"],
                "title": "Public synthetic TLS rehearsal",
            },
        )
        assert conversation.status_code == 201
        cid, rid = conversation.json()["id"], str(uuid4())
        payload = {
            "request_id": rid,
            "content": "Public synthetic transport check",
            "use_memory": False,
        }
        submitted = c.post(
            f"/v1/conversations/{cid}/stream-requests", headers=headers, json=payload
        )
        assert submitted.status_code == 202
        deadline = time.monotonic() + 10
        while True:
            status = c.get(f"/v1/requests/{rid}/stream-status", headers=headers).json()
            if status["stream_state"] == "completed":
                break
            assert time.monotonic() < deadline
            time.sleep(0.05)
        with c.stream(
            "GET", f"/v1/requests/{rid}/stream?attempt=1&after=0", headers=headers
        ) as response:
            assert response.status_code == 200
            assert "no-store" in {
                part.strip() for part in response.headers["cache-control"].split(",")
            }
            events = [
                json.loads(line[6:]) for line in response.iter_lines() if line.startswith("data: ")
            ]
        assert events[0]["type"] == "started" and events[-1]["type"] == "completed"
        cursor = events[-2]["sequence"]
        replay = c.get(f"/v1/requests/{rid}/stream?attempt=1&after={cursor}", headers=headers)
        assert replay.text.count("data: ") == 1
        assert (
            c.post(f"/v1/conversations/{cid}/messages", headers=headers, json=payload).json()
            == status["result"]
        )
        denied = c.get(
            f"/v1/requests/{rid}/stream?attempt=1&after=0",
            headers={"Authorization": "Bearer " + other_token},
        )
        assert denied.status_code == 404
        return {
            "api_authentication_and_admin_role": True,
            "network_header_not_authority": True,
            "same_origin_built_ui": True,
            "stream_events": len(events),
            "cursor_and_completed_replay": True,
            "other_owner_denied": True,
        }


def run(binary, output, route, android_device=None):
    base = 19621 if route == "lan" else 19631
    tls_port, upstream, inner, expired_port = base, base + 1, base + 2, base + 3
    for port in (tls_port, upstream, inner, expired_port):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", port))
    processes = []
    with tempfile.TemporaryDirectory(prefix="ada-private-network-") as temporary:
        directory = Path(temporary)
        certificates(directory)
        token, other_token = seed(directory)
        environment = os.environ.copy()
        environment.update(
            ADA_PRIVATE_HOST=f"localhost:{tls_port}",
            ADA_TLS_CERT=(directory / "cert.pem").as_posix(),
            ADA_TLS_KEY=(directory / "key.pem").as_posix(),
            ADA_ADMIN_DIST=(ROOT / "apps/admin-web/dist").as_posix(),
        )
        assert (ROOT / "apps/admin-web/dist/index.html").is_file(), "Build the admin UI first"
        try:
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        str(Path(__file__).resolve()),
                        "--fixture",
                        str(directory),
                        "--port",
                        str(upstream),
                    ],
                    env=environment,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
            if route == "lan":
                config = adapt(
                    binary,
                    ROOT / "ops/Caddyfile.private.example",
                    environment,
                    directory,
                    "lan",
                    (("127.0.0.1:8000", f"127.0.0.1:{upstream}"),),
                )
            else:
                backend = adapt(
                    binary,
                    ROOT / "ops/Caddyfile.tailnet.example",
                    environment,
                    directory,
                    "tailnet-backend",
                    (("127.0.0.1:8000", f"127.0.0.1:{upstream}"),),
                )
                backend_value = json.loads(backend.read_text())
                for server in backend_value["apps"]["http"]["servers"].values():
                    server["listen"] = [f"127.0.0.1:{inner}"]
                backend.write_text(json.dumps(backend_value))
                processes.append(start_proxy(binary, backend, environment))
                # A local TLS edge rehearses the Serve protocol boundary, not Tailscale itself.
                front = directory / "edge.Caddyfile"
                front.write_text(
                    "{\n admin off\n auto_https disable_redirects\n}\nhttps://localhost:"
                    + str(tls_port)
                    + " {\n tls {$ADA_TLS_CERT} {$ADA_TLS_KEY}\n reverse_proxy 127.0.0.1:"
                    + str(inner)
                    + " {\n flush_interval -1\n }\n}\n"
                )
                config = adapt(binary, front, environment, directory, "edge")
            processes.append(start_proxy(binary, config, environment))
            context = ssl.create_default_context(cafile=str(directory / "ca.pem"))
            origin = f"https://localhost:{tls_port}"
            deadline = time.monotonic() + 25
            with httpx.Client(verify=context, trust_env=False, timeout=1) as client:
                while True:
                    assert all(p.poll() is None for p in processes), "Isolated fixture exited"
                    try:
                        if client.get(origin + "/health/ready").status_code == 200:
                            break
                    except httpx.RequestError:
                        pass
                    assert time.monotonic() < deadline, "Isolated readiness timed out"
                    time.sleep(0.1)
            result = exercise(origin, context, token, other_token)
            if android_device:
                if not re.fullmatch(r"emulator-[0-9]+", android_device):
                    raise ValueError("Select an owned emulator, not a physical device")
                sdk = Path(
                    os.environ.get("ANDROID_HOME", Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk")
                )
                instrument = subprocess.run(
                    [
                        str(sdk / "platform-tools/adb.exe"),
                        "-s",
                        android_device,
                        "shell",
                        "am",
                        "instrument",
                        "-w",
                        "-e",
                        "class",
                        "dev.ada.assistant.ServerAddressUiTest#platformTlsRejectsTheLaboratoryCaWithoutSendingTheSyntheticCredential",
                        "-e",
                        "tlsProbeOrigin",
                        f"https://10.0.2.2:{tls_port}",
                        "dev.ada.validation.phase21.debug.test/androidx.test.runner.AndroidJUnitRunner",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                assert instrument.returncode == 0 and "OK (1 test)" in instrument.stdout, (
                    "Emulator TLS rejection check failed"
                )
                result["android_platform_tls_rejection"] = True
            assert tls_rejected(tls_port, ssl.create_default_context(), "localhost")
            assert tls_rejected(tls_port, context, "127.0.0.1")
            expired = directory / "expired"
            expired.mkdir()
            certificates(expired, expired=True)
            expired_env = dict(
                environment,
                ADA_PRIVATE_HOST=f"localhost:{expired_port}",
                ADA_TLS_CERT=(expired / "cert.pem").as_posix(),
                ADA_TLS_KEY=(expired / "key.pem").as_posix(),
            )
            expired_config = adapt(
                binary, ROOT / "ops/Caddyfile.private.example", expired_env, directory, "expired"
            )
            processes.append(start_proxy(binary, expired_config, expired_env))
            deadline = time.monotonic() + 10
            while True:
                try:
                    with socket.create_connection(("127.0.0.1", expired_port), timeout=1):
                        break
                except OSError:
                    assert time.monotonic() < deadline
                    time.sleep(0.1)
            assert tls_rejected(
                expired_port,
                ssl.create_default_context(cafile=str(expired / "ca.pem")),
                "localhost",
            )
            processes[0].terminate()
            processes[0].wait(timeout=5)
            with httpx.Client(verify=context, trust_env=False, timeout=3) as client:
                assert client.get(origin + "/health/ready").status_code in (502, 503, 504)
            result["stopped_upstream_reported_unavailable"] = True
            result.update(
                route=route,
                untrusted_wrong_host_expired_rejected=True,
                limits="Isolated loopback Caddy/SQLite/fake-provider/per-process CA; no actual tailnet, LAN firewall, system trust, physical device or live deployment",
            )
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result))
            return result
        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caddy", type=Path)
    parser.add_argument("--route", choices=("lan", "tailnet"), default="lan")
    parser.add_argument(
        "--android-device", help="Owned emulator with separate Phase21 validation APKs"
    )
    parser.add_argument(
        "--output", type=Path, default=Path(".pytest_cache/private-connectivity.json")
    )
    parser.add_argument("--fixture", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.fixture:
        fixture(args.fixture, args.port)
    elif args.caddy:
        run(args.caddy.resolve(), args.output, args.route, args.android_device)
    else:
        parser.error("--caddy is required")
