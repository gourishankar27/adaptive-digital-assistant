"""Disposable PostgreSQL + actual Caddy TLS + built browser password flow.

The ephemeral leaf key is pinned in this Chromium process only. No OS trust,
live accounts, screenshots, traces, access logs or deployment.
"""

import argparse
import base64
import hashlib
import os
import secrets
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from verify_private_connectivity import adapt, start_proxy
from verify_private_proxy import certificates

ROOT = Path(__file__).resolve().parents[1]


def run(binary):
    if not os.environ.get("ADA_TEST_DATABASE_URL"):
        raise SystemExit("A disposable ADA_TEST_DATABASE_URL is required")
    for port in (18422, 19422):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", port))
    children = []
    environment = os.environ.copy()
    environment.update(
        ADA_WEB_TEST_SCHEMA="ada_web_test_" + uuid4().hex,
        ADA_WEB_TEST_PASSWORD=secrets.token_urlsafe(32),
        ADA_WEB_TEST_TOKEN=secrets.token_urlsafe(32),
        ADA_WEB_TEST_SECOND_TOKEN=secrets.token_urlsafe(32),
        ADA_WEB_TEST_ORDINARY_TOKEN=secrets.token_urlsafe(32),
        ADA_BROWSER_ORIGIN="https://localhost:19422",
        ADA_SESSION_ACCESS_SECONDS="60",
        PYTHONUTF8="1",
    )
    try:
        with tempfile.TemporaryDirectory(prefix="ada-password-browser-") as temporary:
            directory = Path(temporary)
            certificates(directory)
            certificate = x509.load_pem_x509_certificate((directory / "cert.pem").read_bytes())
            key = certificate.public_key().public_bytes(
                serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
            )
            environment.update(
                ADA_TLS_SPKI=base64.b64encode(hashlib.sha256(key).digest()).decode(),
                ADA_PRIVATE_HOST="localhost:19422",
                ADA_TLS_CERT=(directory / "cert.pem").as_posix(),
                ADA_TLS_KEY=(directory / "key.pem").as_posix(),
                ADA_ADMIN_DIST=(ROOT / "apps/admin-web/dist").as_posix(),
            )
            config = adapt(
                binary,
                ROOT / "ops/Caddyfile.private.example",
                environment,
                directory,
                "proxy",
                (("127.0.0.1:8000", "127.0.0.1:18422"),),
            )
            children.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        str(ROOT / "scripts/admin_web_test_server.py"),
                        "--port",
                        "18422",
                    ],
                    env=environment,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
            children.append(start_proxy(binary, config, environment))
            context = ssl.create_default_context(cafile=str(directory / "ca.pem"))
            with httpx.Client(verify=context, trust_env=False, timeout=2) as client:
                for _ in range(150):
                    try:
                        if client.get("https://localhost:19422/health/ready").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    if any(child.poll() is not None for child in children):
                        raise RuntimeError("Disposable browser fixture exited")
                    time.sleep(0.2)
                else:
                    raise RuntimeError("Disposable browser fixture readiness timed out")
            subprocess.run(
                ["node", "e2e/password-browser.mjs"],
                cwd=ROOT / "apps/admin-web",
                env=environment,
                check=True,
                timeout=120,
            )
    finally:
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=15)
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/admin_web_test_server.py"), "--action", "cleanup"],
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=15,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caddy", type=Path, required=True)
    run(parser.parse_args().caddy.resolve())
