"""Cleanup errors must not permanently consume parser capacity."""

import io
import subprocess

import pytest

from ada.errors import ServiceError
from ada.pdf_sandbox import CAPACITY, DockerPdfParser


@pytest.mark.parametrize("removal", ["exception", "nonzero", "poll-failure"])
def test_uncertain_worker_cleanup_disables_parser_and_releases_host_capacity(monkeypatch, removal):
    class Process:
        stdin = io.BytesIO()
        stdout = io.BytesIO(b"{}")
        returncode = None

        def wait(self, timeout):
            raise subprocess.TimeoutExpired("public-failure-driver", timeout)

        def poll(self):
            if removal == "poll-failure":
                raise OSError("Public process-status failure")
            return None

        def kill(self):
            raise OSError("Public cleanup failure")

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: Process())

    def cleanup(*args, **kwargs):
        if removal != "nonzero":
            raise OSError("Public cleanup failure")
        return subprocess.CompletedProcess(args[0], 1)

    monkeypatch.setattr(subprocess, "run", cleanup)
    parser = DockerPdfParser.__new__(DockerPdfParser)
    parser.available, parser.image = True, "sha256:" + "0" * 64
    with pytest.raises(ServiceError) as error:
        parser.parse(b"%PDF-public")
    assert error.value.code == "pdf_parser_timeout"
    assert CAPACITY.acquire(blocking=False)
    CAPACITY.release()
    # A failed container removal leaves its execution state unknown. Releasing
    # the host slot must not permit another parser beside that unknown worker.
    assert not parser.available
    with pytest.raises(ServiceError) as unavailable:
        parser.parse(b"%PDF-public-second-attempt")
    assert unavailable.value.code == "pdf_parser_unavailable"
