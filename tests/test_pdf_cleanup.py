"""Cleanup errors must not permanently consume parser capacity."""

import io
import subprocess

import pytest

from ada.errors import ServiceError
from ada.pdf_sandbox import CAPACITY, DockerPdfParser


def test_timeout_and_failed_host_cleanup_still_release_capacity(monkeypatch):
    class Process:
        stdin = io.BytesIO()
        stdout = io.BytesIO(b"{}")
        returncode = None

        def wait(self, timeout):
            raise subprocess.TimeoutExpired("public-failure-driver", timeout)

        def poll(self):
            return None

        def kill(self):
            raise OSError("Public cleanup failure")

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: Process())

    def cleanup(*args, **kwargs):
        raise OSError("Public cleanup failure")

    monkeypatch.setattr(subprocess, "run", cleanup)
    parser = DockerPdfParser.__new__(DockerPdfParser)
    parser.available, parser.image = True, "sha256:" + "0" * 64
    with pytest.raises(ServiceError) as error:
        parser.parse(b"%PDF-public")
    assert error.value.code == "pdf_parser_timeout"
    assert CAPACITY.acquire(blocking=False)
    CAPACITY.release()
