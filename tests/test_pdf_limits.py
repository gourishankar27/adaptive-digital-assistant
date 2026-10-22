"""Actual Docker resource/egress proof and deliberately isolated failure drivers."""

import subprocess
import time

import pytest
from pdf_fixtures import text_pdf
from test_pdf_flow import pdf_parser  # noqa: F401

from ada.errors import ServiceError


def test_container_proof_has_no_egress_or_application_environment(pdf_parser, monkeypatch):  # noqa: F811
    monkeypatch.setenv("ADA_TEST_SYNTHETIC_SECRET", "public-synthetic-sentinel")
    proof = pdf_parser.parse(b"ADA_PDF_BOUNDARY_PROBE_V1")
    assert proof["network"] is False and proof["app_env"] is False
    assert proof["uid"] == 65534 and proof["memory"] == "268435456" and proof["pids"] == "16"


@pytest.mark.parametrize(
    "driver",
    [
        "import os;os._exit(7)",
        "import time;time.sleep(60)",
        "import sys,time;sys.stdout.buffer.write(b'x'*2097154);sys.stdout.flush();time.sleep(60)",
    ],
    ids=["crash", "hang", "stdout-flood"],
)
def test_real_failure_driver_cannot_escape_time_or_output_limits(pdf_parser, monkeypatch, driver):  # noqa: F811
    original = subprocess.Popen

    def replaced(command, *args, **kwargs):
        if command[:2] == ["docker", "run"]:
            command = command[:-1] + ["--entrypoint", "python", command[-1], "-I", "-c", driver]
        return original(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", replaced)
    started = time.monotonic()
    with pytest.raises(ServiceError) as error:
        pdf_parser.parse(text_pdf())
    assert error.value.status in (422, 503) and time.monotonic() - started < 18


def test_compressed_expansion_is_bounded_in_isolated_worker(pdf_parser):  # noqa: F811
    raw = text_pdf(("Public " + ("A" * 2_000_000),), compressed=True)
    assert len(raw) < 262144
    with pytest.raises(ServiceError):
        pdf_parser.parse(raw)


def test_encrypted_pdf_is_rejected_without_decryption_or_partial_text(pdf_parser):  # noqa: F811
    raw = text_pdf()
    encryption = (
        b" /Encrypt << /Filter /Standard /V 1 /R 2 /Length 40 /P -4 /O <"
        + b"00" * 32
        + b"> /U <"
        + b"00" * 32
        + b"> >> /ID [<00112233445566778899AABBCCDDEEFF><00112233445566778899AABBCCDDEEFF>]"
    )
    raw = raw.replace(b"/Root 1 0 R >>", b"/Root 1 0 R" + encryption + b" >>")
    with pytest.raises(ServiceError) as error:
        pdf_parser.parse(raw)
    assert error.value.code == "pdf_encrypted"


def test_malformed_huge_xref_header_is_bounded(pdf_parser):  # noqa: F811
    raw = text_pdf().replace(b"xref\n0 ", b"xref\n0 999999999")
    started = time.monotonic()
    with pytest.raises(ServiceError):
        pdf_parser.parse(raw)
    assert time.monotonic() - started < 18
