"""Optional owned loopback proxy; reuses the reviewed Phase21 Caddy pin/template."""

import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path

from dotenv import dotenv_values

from ada.host_security import HostError


def launch_proxy(config, root, launch=subprocess.Popen):
    repository = Path(config.repository)
    pin = json.loads((repository / "ops/validation-tools.json").read_bytes())["caddy"]
    binary = Path(config.profile) / f"ADA/tools/caddy-{pin['version']}/caddy.exe"
    if (
        not binary.is_file()
        or hashlib.sha256(binary.read_bytes()).hexdigest() != pin["windows_amd64_exe_sha256"]
    ):
        raise HostError("private_proxy_pin_unavailable")
    value = os.environ.get("ADA_ADMIN_DIST") or dotenv_values(
        repository / ".env", interpolate=False
    ).get("ADA_ADMIN_DIST")
    if not value or not Path(value).is_absolute() or not (Path(value) / "index.html").is_file():
        raise HostError("private_proxy_admin_build_missing")
    with socket.socket() as probe:
        if os.name == "nt":
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            probe.bind(("127.0.0.1", config.proxy_port))
        except OSError:
            raise HostError("private_proxy_owned_elsewhere") from None
    # Only port literals change; auth, headers, admin-off and loopback binding remain.
    template = (repository / "ops/Caddyfile.tailnet.example").read_text(encoding="utf-8")
    template = template.replace("http://:18764", f"http://:{config.proxy_port}").replace(
        "127.0.0.1:8000", f"127.0.0.1:{config.port}"
    )
    path = root / "Caddyfile.generated"
    path.write_text(template, encoding="utf-8", newline="\n")
    environment = os.environ.copy()
    environment["ADA_ADMIN_DIST"] = Path(value).resolve().as_posix()
    validation = subprocess.run(
        [str(binary), "validate", "--config", str(path), "--adapter", "caddyfile"],
        env=environment,
        cwd=repository,
        capture_output=True,
        timeout=15,
    )
    if validation.returncode:
        raise HostError("private_proxy_configuration_invalid")
    return launch(
        [str(binary), "run", "--config", str(path), "--adapter", "caddyfile"],
        cwd=repository,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
