"""Narrow Docker adapter; no application secret or private context enters a container."""

import hashlib
import ipaddress
import json
import os
import re
import socket
import subprocess
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from uuid import uuid4

from ada.web_policy import DEADLINE, MAX_BYTES, WebBlocked, public_ip, user_agent, validate_url

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ("ops/web-broker/Dockerfile", "ops/web-broker/worker.py", "src/ada/web_policy.py")
DNS_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ada-public-dns")
DNS_CAPACITY = threading.BoundedSemaphore(2)


def resolve_public(host):
    # All A/AAAA answers must pass; a public A cannot mask an internal AAAA.
    if not DNS_CAPACITY.acquire(blocking=False):
        raise WebBlocked("public_dns_busy")
    try:
        future = DNS_POOL.submit(socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM)
    except Exception:
        DNS_CAPACITY.release()
        raise WebBlocked("public_dns_unavailable") from None
    future.add_done_callback(lambda _: DNS_CAPACITY.release())
    try:
        answers = future.result(timeout=3)
    except (OSError, TimeoutError):
        raise WebBlocked("public_dns_unavailable") from None
    values = sorted({public_ip(answer[4][0]) for answer in answers})
    candidates = [value for value in values if ipaddress.ip_address(value).version == 4]
    if not candidates:
        raise WebBlocked("ipv6_transport_unavailable")
    return candidates[0]


def docker_environment():
    return {
        key: value
        for key, value in os.environ.items()
        if key.upper()
        in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE", "HOME", "LOCALAPPDATA")
    }


class DockerWebBroker:
    def __init__(self, manifest):
        self.available, self.proof = False, None
        self.image = None
        self.network_capacity = threading.BoundedSemaphore(2)
        self._rate_lock, self._network_starts = threading.Lock(), deque()
        try:
            endpoint = subprocess.run(
                ["docker", "context", "inspect", "--format", "{{json .Endpoints.docker.Host}}"],
                capture_output=True,
                timeout=10,
                env=docker_environment(),
                check=True,
            )
            if not json.loads(endpoint.stdout).startswith(("npipe://", "unix://")):
                return
            metadata = json.loads(Path(manifest).read_text(encoding="utf-8"))
            image = metadata["image_id"]
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", image):
                return
            hashes = {
                source: hashlib.sha256(
                    (ROOT / source).read_bytes().replace(b"\r\n", b"\n")
                ).hexdigest()
                for source in SOURCES
            }
            label = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
            if metadata["files"] != hashes or metadata["source_label"] != label:
                return
            inspected = subprocess.run(
                ["docker", "image", "inspect", image],
                capture_output=True,
                timeout=10,
                env=docker_environment(),
                check=True,
            )
            info = json.loads(inspected.stdout)[0]
            if info["Config"]["Labels"].get("dev.ada.web-source") != label:
                return
            self.image = image
            self.proof = self._execute(
                {
                    "selftest": True,
                    "address": "1.1.1.1",
                    "expires_at": int(time.time() * 1000) + 60000,
                    "receipt_key": str(uuid4()),
                }
            )
            self.available = (
                self.proof.get("state") == "isolated"
                and self.proof.get("all_blocked") is True
                and self.proof.get("blocked_targets") == 9
                and self.proof.get("uid") == 65534
                and all(
                    self.proof.get(k) is True
                    for k in (
                        "read_only",
                        "no_private_env",
                        "host_files_absent",
                        "seccomp",
                        "bounding_set_empty",
                    )
                )
            )
        except (OSError, ValueError, KeyError, subprocess.SubprocessError, WebBlocked):
            self.available = False

    def _execute(self, request):
        name = "ada-web-" + uuid4().hex
        command = [
            "docker",
            "run",
            "--rm",
            "--pull=never",
            "--name",
            name,
            "--log-driver=none",
            "--read-only",
            "--cap-drop=ALL",
            "--cap-add=NET_ADMIN",
            "--cap-add=SETUID",
            "--cap-add=SETGID",
            "--cap-add=SETPCAP",
            "--security-opt=no-new-privileges",
            "--pids-limit=16",
            "--memory=128m",
            "--memory-swap=128m",
            "--cpus=0.5",
            "--network=bridge",
            "--dns=127.0.0.1",
            "--env=HTTP_PROXY=",
            "--env=HTTPS_PROXY=",
            "--env=ALL_PROXY=",
            "--env=NO_PROXY=",
            "--env=http_proxy=",
            "--env=https_proxy=",
            "--env=all_proxy=",
            "--env=no_proxy=",
            "--interactive",
            self.image,
        ]
        environment = docker_environment()

        def remove():
            try:
                subprocess.run(
                    ["docker", "rm", "--force", name],
                    env=environment,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
            except (OSError, subprocess.SubprocessError):
                # A daemon fault must not suppress the unknown receipt or skip CLI cleanup.
                pass

        process = None
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                env=environment,
            )
            # The trusted worker bounds its serialized output; also bound the CLI wait
            # itself so a stalled daemon cannot strand admission on a blocking read.
            data, _ = process.communicate(input=json.dumps(request).encode(), timeout=DEADLINE + 8)
            if len(data) > MAX_BYTES:
                raise WebBlocked("broker_output_bound")
            if process.returncode != 0:
                raise WebBlocked("broker_unavailable")
            return json.loads(data)
        except (OSError, ValueError, subprocess.SubprocessError):
            raise WebBlocked("broker_outcome_unknown") from None
        finally:
            remove()
            if process:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
                process.stdout.close()

    def fetch(self, kind, url, expiry, receipt_key, agent=None):
        if not self.available:
            raise WebBlocked("research_isolation_unavailable")
        parsed = validate_url(kind, url)
        with self._rate_lock:
            instant = time.monotonic()
            while self._network_starts and instant - self._network_starts[0] >= 60:
                self._network_starts.popleft()
            if len(self._network_starts) >= 10:
                raise WebBlocked("research_network_rate_limited")
            self._network_starts.append(instant)
        if not self.network_capacity.acquire(blocking=False):
            raise WebBlocked("research_network_busy")
        try:
            address = resolve_public(parsed.hostname)
            return self._execute(
                {
                    "kind": kind,
                    "url": url,
                    "address": address,
                    "expires_at": expiry,
                    "receipt_key": receipt_key,
                    "user_agent": agent or user_agent(),
                }
            )
        finally:
            self.network_capacity.release()


class UnavailableWebBroker:
    available = False

    def fetch(self, *args):
        raise WebBlocked("research_isolation_unavailable")
