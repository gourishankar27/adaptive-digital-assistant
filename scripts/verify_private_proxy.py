"""Validate the real Caddy template and isolated, CA-verified loopback TLS routing.

No system trust installation, live ADA connection, real account or deployment.
The upstream is a synthetic protocol fixture, not a substitute for ADA auth tests.
"""

import argparse
import asyncio
import datetime
import json
import os
import secrets
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parents[1]


def certificates(directory):
    now = datetime.datetime.now(datetime.UTC)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ADA synthetic proxy CA")])
    ca = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")]))
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    (directory / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    (directory / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (directory / "key.pem").write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )


def fixture(port):
    import uvicorn
    from fastapi import FastAPI, Header, HTTPException
    from fastapi.responses import StreamingResponse

    app = FastAPI()

    @app.get("/health/live")
    def live():
        return {"status": "synthetic"}

    @app.get("/v1/probe")
    def probe(authorization: str = Header(default="")):
        if authorization != "Bearer " + os.environ["ADA_PROXY_FIXTURE_TOKEN"]:
            raise HTTPException(401, "fixture_authentication_required")
        return {"fixture": "public_proxy_v1"}

    @app.get("/v1/events")
    def events():
        async def chunks():
            yield "event: probe\ndata: 1\n\n"
            await asyncio.sleep(0.05)
            yield "event: done\ndata: 2\n\n"

        return StreamingResponse(chunks(), media_type="text/event-stream")

    uvicorn.run(app, host="127.0.0.1", port=port, workers=1, access_log=False, log_level="critical")


def run(binary, output, tls_port=19420, upstream_port=18420):
    for port in (tls_port, upstream_port):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", port))  # Refuse an occupied port; never stop its owner.
    child = proxy = None
    with tempfile.TemporaryDirectory(prefix="ada-proxy-validation-") as temporary:
        directory = Path(temporary)
        certificates(directory)
        (directory / "index.html").write_text(
            "<title>ADA synthetic proxy fixture</title>", encoding="utf-8"
        )
        env = os.environ.copy()
        env.update(
            ADA_PRIVATE_HOST=f"localhost:{tls_port}",
            ADA_TLS_CERT=(directory / "cert.pem").as_posix(),
            ADA_TLS_KEY=(directory / "key.pem").as_posix(),
            ADA_ADMIN_DIST=directory.as_posix(),
            ADA_PROXY_FIXTURE_TOKEN=secrets.token_urlsafe(32),
        )
        template = ROOT / "ops/Caddyfile.private.example"
        # Validate the unchanged template with supplied certificates before adapting test ports.
        subprocess.run(
            [str(binary), "validate", "--config", str(template), "--adapter", "caddyfile"],
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        adapted = subprocess.run(
            [str(binary), "adapt", "--config", str(template), "--adapter", "caddyfile"],
            env=env,
            check=True,
            capture_output=True,
        )
        config = json.loads(adapted.stdout)
        for server in config["apps"]["http"]["servers"].values():
            server["listen"] = [f"127.0.0.1:{tls_port}"]

        def replace(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "dial" and item == "127.0.0.1:8000":
                        value[key] = f"127.0.0.1:{upstream_port}"
                    else:
                        replace(item)
            elif isinstance(value, list):
                for item in value:
                    replace(item)

        replace(config)
        configuration = directory / "validation.json"
        configuration.write_text(json.dumps(config), encoding="utf-8")
        try:
            child = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--fixture-port",
                    str(upstream_port),
                ],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            proxy = subprocess.Popen(
                [str(binary), "run", "--config", str(configuration)],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            context = ssl.create_default_context(cafile=str(directory / "ca.pem"))
            origin = f"https://localhost:{tls_port}"
            with httpx.Client(verify=context, trust_env=False, timeout=2) as client:
                deadline = time.monotonic() + 20
                while True:
                    if child.poll() is not None or proxy.poll() is not None:
                        raise RuntimeError("Isolated proxy fixture exited")
                    try:
                        if client.get(origin + "/health/live").status_code == 200:
                            break
                    except httpx.RequestError:
                        pass
                    if time.monotonic() > deadline:
                        raise RuntimeError("Proxy readiness timed out")
                    time.sleep(0.1)
                response = client.get(
                    origin + "/v1/probe",
                    headers={"Authorization": "Bearer " + env["ADA_PROXY_FIXTURE_TOKEN"]},
                )
                assert response.status_code == 200 and response.json() == {
                    "fixture": "public_proxy_v1"
                }
                assert response.headers["Cache-Control"] == "no-store"
                assert client.get(origin + "/v1/probe").status_code == 401
                missing = client.get(origin + "/v1/missing")
                assert missing.status_code == 404 and missing.headers["Content-Type"].startswith(
                    "application/json"
                )
                assert "synthetic proxy fixture" in client.get(origin + "/admin/nested/route").text
                root_redirect = client.get(origin + "/admin")
                assert (
                    root_redirect.status_code == 308
                    and root_redirect.headers["Location"] == "/admin/"
                )
                assert client.get(origin + "/outside").status_code == 404
                with client.stream("GET", origin + "/v1/events") as response:
                    assert response.headers["Content-Type"].startswith("text/event-stream")
                    lines = list(response.iter_lines())
                    assert "data: 1" in lines and "data: 2" in lines
            # Direct sockets avoid HTTP client's address-retry wrappers hiding TLS errors.
            for hostname, trust in (
                ("localhost", ssl.create_default_context()),
                ("127.0.0.1", context),
            ):
                with socket.create_connection(("127.0.0.1", tls_port), timeout=2) as raw:
                    try:
                        with trust.wrap_socket(raw, server_hostname=hostname):
                            pass
                    except ssl.SSLError as error:
                        if hostname == "localhost":
                            assert isinstance(error, ssl.SSLCertVerificationError)
                    else:
                        raise AssertionError("Untrusted root or wrong hostname was accepted")
            result = {
                "template_validated": True,
                "ca_verified_loopback_tls": True,
                "api_auth_forwarding": True,
                "api_json_not_spa": True,
                "spa_nested_route": True,
                "sse_frames": 2,
                "untrusted_ca_and_wrong_hostname_rejected": True,
                "limits": "Synthetic upstream, per-process test CA; no system trust, physical client or live private HTTPS deployment",
            }
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result))
        finally:
            for process in (proxy, child):
                if process and process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caddy", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".pytest_cache/private-proxy.json"))
    parser.add_argument("--fixture-port", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.fixture_port:
        fixture(args.fixture_port)
    elif args.caddy:
        run(args.caddy.resolve(), args.output)
    else:
        parser.error("--caddy is required")
