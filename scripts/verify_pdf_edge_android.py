"""Explicit S24 FE, separate APK, public model/PDF and real HTTP/Keystore recovery."""

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from verify_password_android import ROOT, run


def verify(device, model, pdf_only=False, sync_fixture=False, manual_review=False):
    if sync_fixture and not pdf_only:
        raise SystemExit(
            "Synthetic signing fixtures require explicit --pdf-only; no inference claim"
        )
    if manual_review and (not pdf_only or sync_fixture):
        raise SystemExit("Manual PDF review requires --pdf-only without signing fixtures")
    if not pdf_only:
        if model is None:
            raise SystemExit("The exact public model is required for native checks")
        with model.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        lock = json.loads((ROOT / "ops/edge-runtime/runtime.lock.json").read_text(encoding="utf-8"))
        if (
            digest != lock["candidate_model"]["sha256"]
            or model.stat().st_size != lock["candidate_model"]["bytes"]
        ):
            raise SystemExit("Only the exact public candidate model may enter the validation APK")
    os.environ["ADA_WEB_TEST_CURIOSITY_FIXTURE"] = "1"
    os.environ["ADA_WEB_TEST_PDF_EDGE_FIXTURE"] = "1"
    package = "dev.ada.validation.phase19.debug"
    prepared = False

    def provision(command):
        nonlocal prepared
        if prepared:
            return
        import sys

        sys.path.insert(0, str(ROOT / "tests"))
        from pdf_fixtures import text_pdf

        adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
        command("shell", "run-as", package, "mkdir", "-p", "files/edge")
        for name, content in (
            (
                "files/public-study.pdf",
                text_pdf(("Public orbit launch is Monday.", "Public table: Mars 3; Venus 5.")),
            ),
            ("files/public-scan.pdf", text_pdf(("",))),
            ("files/edge/qwen3-0.6b-q8.gguf", None),
        ):
            if content is None and pdf_only:
                continue
            arguments = [
                str(adb),
                "-s",
                device,
                "shell",
                "run-as",
                package,
                "sh",
                "-c",
                f'"cat > {name}"',
            ]
            if content is None:
                with model.open("rb") as stream:
                    subprocess.run(
                        arguments, stdin=stream, capture_output=True, check=True, timeout=180
                    )
            else:
                subprocess.run(
                    arguments, input=content, capture_output=True, check=True, timeout=20
                )
        prepared = True

    run(
        device,
        package=package,
        fixture_bearer=True,
        physical_model=None if device.startswith("emulator-") and pdf_only else "SM-S721U1",
        test_class="dev.ada.assistant.PdfEdgeDeviceTest",
        stages=(
            "preparePdfAndPrivateModelDirectory",
            "prepareSignedReceiptFixtureWithoutInference",
            "restoreGetOnlyRetryOriginalAndRevoke",
        )
        if sync_fixture
        else ("preparePdfAndPrivateModelDirectory", "restorePdfOnlyAfterProcessStop")
        + (("reviewPublicPdfOnPhone",) if manual_review else ())
        if pdf_only
        else (
            "preparePdfAndPrivateModelDirectory",
            "nativeIsolatedReplyAndSignedUnknownReceipt",
            "restoreGetOnlyRetryOriginalAndRevoke",
            "isolatedNativeCancellationTerminatesBinder",
        ),
        instrumentation_arguments={
            "adaTestOrigin": "http://127.0.0.1:19822",
            **({"adaPdfManualReview": "1"} if manual_review else {}),
        },
        before_stage=provision,
        stage_timeout=600 if manual_review else 120,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--pdf-only", action="store_true")
    parser.add_argument("--sync-fixture", action="store_true")
    parser.add_argument("--manual-review", action="store_true")
    args = parser.parse_args()
    verify(args.device, args.model, args.pdf_only, args.sync_fixture, args.manual_review)
