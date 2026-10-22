"""Fail-closed, secret-free, non-networked and resource-bounded PDF subprocess."""

import hashlib
import json
import re
import subprocess
import threading
from pathlib import Path
from uuid import uuid4

from ada.errors import ServiceError
from ada.web_broker import docker_environment

ROOT = Path(__file__).resolve().parents[2]
FILES = ("ops/pdf-parser/Dockerfile", "ops/pdf-parser/worker.py", "ops/pdf-parser/requirements.txt")
CAPACITY = threading.BoundedSemaphore(1)
MAX_OUTPUT = 2 * 1024 * 1024


class DockerPdfParser:
    def __init__(self, manifest=None):
        self.available = False
        self.image = None
        if not manifest:
            return
        try:
            env = docker_environment()
            endpoint = subprocess.run(
                ["docker", "context", "inspect", "--format", "{{json .Endpoints.docker.Host}}"],
                env=env,
                capture_output=True,
                timeout=10,
                check=True,
            )
            if not json.loads(endpoint.stdout).startswith(("npipe://", "unix://")):
                return
            data = json.loads(Path(manifest).read_text(encoding="utf-8"))
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", data["image_id"]):
                return
            hashes = {
                p: hashlib.sha256((ROOT / p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
                for p in FILES
            }
            label = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
            if data["files"] != hashes or data["source_label"] != label:
                return
            info = json.loads(
                subprocess.run(
                    ["docker", "image", "inspect", data["image_id"]],
                    env=env,
                    capture_output=True,
                    timeout=10,
                    check=True,
                ).stdout
            )[0]
            if info["Config"]["Labels"].get("dev.ada.pdf-source") != label:
                return
            if info["Config"]["User"] != "65534:65534" or info["Config"].get("Volumes"):
                return
            self.image = data["image_id"]
            self.available = True
            proof = self.parse(b"ADA_PDF_BOUNDARY_PROBE_V1")
            if (
                proof.get("probe") != "ada-pdf-boundary-v1"
                or proof.get("network") is not False
                or proof.get("app_env") is not False
                or proof.get("uid") != 65534
                or proof.get("memory") != "268435456"
                or proof.get("pids") != "16"
                or proof.get("cpu") != "100000 100000"
                or proof.get("address_space") != 268435456
            ):
                self.available = False
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, ServiceError):
            self.available = False

    def parse(self, raw):
        if not self.available:
            raise ServiceError(503, "pdf_parser_unavailable")
        if not CAPACITY.acquire(blocking=False):
            raise ServiceError(429, "pdf_parser_busy")
        name = "ada-pdf-" + uuid4().hex
        process = reader = writer = None
        try:
            command = [
                "docker",
                "run",
                "--rm",
                "--name",
                name,
                "--network",
                "none",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--memory",
                "256m",
                "--memory-swap",
                "256m",
                "--cpus",
                "1",
                "--pids-limit",
                "16",
                "--ulimit",
                "nofile=32:32",
                "--log-driver",
                "none",
                "-i",
                self.image,
            ]
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                env=docker_environment(),
            )
            output = []

            def read_output():
                try:
                    output.append(process.stdout.read(MAX_OUTPUT + 1))
                except (OSError, ValueError):
                    output.append(b"")

            reader = threading.Thread(target=read_output, daemon=True)
            reader.start()

            def write_input():
                try:
                    process.stdin.write(raw)
                except (OSError, ValueError):
                    pass
                finally:
                    try:
                        process.stdin.close()
                    except (OSError, ValueError):
                        pass

            writer = threading.Thread(target=write_input, daemon=True)
            writer.start()
            process.wait(timeout=10)
            reader.join(timeout=2)
            writer.join(timeout=2)
            if (
                reader.is_alive()
                or writer.is_alive()
                or process.returncode != 0
                or len(output) != 1
                or len(output[0]) > MAX_OUTPUT
            ):
                raise ServiceError(422, "pdf_parser_failed")
            result = json.loads(output[0])
            if "error" in result:
                allowed = {
                    "pdf_invalid",
                    "pdf_encrypted",
                    "pdf_object_limit",
                    "pdf_active_content",
                    "pdf_page_limit",
                    "pdf_ocr_required",
                    "pdf_text_limit",
                    "pdf_malformed",
                }
                raise ServiceError(
                    422, result["error"] if result["error"] in allowed else "pdf_parser_failed"
                )
            return result | {"image_id": self.image}
        except subprocess.TimeoutExpired:
            raise ServiceError(422, "pdf_parser_timeout") from None
        except (OSError, ValueError, TypeError, KeyError):
            raise ServiceError(422, "pdf_parser_failed") from None
        finally:
            # Only the unpredictable name reserved by this call is removed.
            try:
                subprocess.run(
                    ["docker", "rm", "-f", name],
                    env=docker_environment(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
            except (OSError, subprocess.SubprocessError):
                pass
            try:
                if process:
                    try:
                        if process.poll() is None:
                            process.kill()
                        process.wait(timeout=3)
                    except (OSError, subprocess.SubprocessError):
                        pass
                    for thread in (reader, writer):
                        if thread:
                            thread.join(timeout=1)
                    # Never block closing a pipe still owned by a live I/O thread.
                    for stream, thread in ((process.stdout, reader), (process.stdin, writer)):
                        if thread is None or not thread.is_alive():
                            try:
                                stream.close()
                            except (OSError, ValueError):
                                pass
            finally:
                CAPACITY.release()
