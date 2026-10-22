"""Separate-APK password/Keystore flow with disposable PostgreSQL and device opt-in."""

import argparse
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "dev.ada.validation.phase22.debug"


def run(
    device,
    *,
    package=PACKAGE,
    stages=None,
    test_class="dev.ada.assistant.PasswordLoginUiHttpTest",
    after_stage=None,
    physical_model=None,
    instrumentation_arguments=None,
    fixture_bearer=False,
):
    if not os.environ.get("ADA_TEST_DATABASE_URL"):
        raise SystemExit("Select a dedicated ADA_TEST_DATABASE_URL")
    if not re.fullmatch(r"emulator-\d+", device) and not physical_model:
        raise SystemExit("Physical validation requires an explicit expected device model")
    if not re.fullmatch(r"dev\.ada\.validation\.[a-z][a-z0-9_]{0,30}\.debug", package):
        raise SystemExit("Only a separate validation application ID may be installed")
    adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
    if physical_model:
        observed = subprocess.run(
            [str(adb), "-s", device, "shell", "getprop", "ro.product.model"],
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        ).stdout.strip()
        if observed != physical_model:
            raise SystemExit("Selected device does not match the explicitly expected model")
    for relative, expected in (("debug", package), ("androidTest/debug", package + ".test")):
        metadata = ROOT / "apps/android/app/build/outputs/apk" / relative / "output-metadata.json"
        if json.loads(metadata.read_text(encoding="utf-8")).get("applicationId") != expected:
            raise SystemExit(
                "Build the separate validation application ID first; nothing installed"
            )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 18423))
    environment = os.environ.copy()
    environment.update(
        ADA_WEB_TEST_SCHEMA="ada_web_test_" + uuid4().hex,
        ADA_WEB_TEST_PASSWORD="Public synthetic Android passphrase 123",
        ADA_WEB_TEST_TOKEN=secrets.token_urlsafe(32),
        ADA_WEB_TEST_SECOND_TOKEN=secrets.token_urlsafe(32),
        ADA_WEB_TEST_ORDINARY_TOKEN=secrets.token_urlsafe(32),
        PYTHONUTF8="1",
    )
    child = None
    (ROOT / ".pytest_cache").mkdir(exist_ok=True)
    snapshot = tempfile.TemporaryDirectory(
        prefix="ada-validation-apks-", dir=ROOT / ".pytest_cache"
    )

    def command(*arguments, timeout=90):
        return subprocess.run(
            [str(adb), "-s", device, *arguments],
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True,
        )

    try:
        # Stable copies prevent a concurrent normal build replacing a validated APK.
        aapt = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/build-tools/35.0.0/aapt2.exe"
        for folder, name, expected in (
            ("debug", "app-debug.apk", package),
            ("androidTest/debug", "app-debug-androidTest.apk", package + ".test"),
        ):
            copied = Path(snapshot.name) / name
            shutil.copyfile(ROOT / "apps/android/app/build/outputs/apk" / folder / name, copied)
            badging = subprocess.run(
                [str(aapt), "dump", "badging", str(copied)],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            ).stdout
            identity = re.search(r"^package: name='([^']+)'", badging)
            if identity is None or identity.group(1) != expected:
                raise RuntimeError("APK contents do not match the separate validation package")
        child = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts/admin_web_test_server.py"), "--port", "18423"],
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with httpx.Client(trust_env=False, timeout=2) as client:
            for _ in range(150):
                try:
                    if client.get("http://127.0.0.1:18423/health/ready").status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                if child.poll() is not None:
                    raise RuntimeError("Disposable Android fixture exited")
                time.sleep(0.2)
            else:
                raise RuntimeError("Disposable Android fixture readiness timed out")
        command("wait-for-device")
        command("install", "--user", "0", "-r", str(Path(snapshot.name) / "app-debug.apk"))
        command(
            "install",
            "--user",
            "0",
            "-r",
            str(Path(snapshot.name) / "app-debug-androidTest.apk"),
        )
        command("reverse", "tcp:19822", "tcp:18423")
        if fixture_bearer:
            command("shell", "run-as", package, "mkdir", "-p", "files")
            subprocess.run(
                [
                    str(adb),
                    "-s",
                    device,
                    "shell",
                    "run-as",
                    package,
                    "sh",
                    "-c",
                    '"cat > files/foundation-test-token"',
                ],
                input=environment["ADA_WEB_TEST_ORDINARY_TOKEN"],
                text=True,
                capture_output=True,
                check=True,
                timeout=20,
            )
        for stage in stages or (
            "passwordLoginAndRenewBeforeProcessStop",
            "passwordRestoreAfterActualProcessStopThenRevoke",
        ):
            result = command(
                "shell",
                "am",
                "instrument",
                "-w",
                "-e",
                "class",
                test_class + "#" + stage,
                "-e",
                "passwordOrigin",
                "http://127.0.0.1:19822",
                *[
                    part
                    for key, value in (instrumentation_arguments or {}).items()
                    for part in ("-e", key, value)
                ],
                package + ".test/androidx.test.runner.AndroidJUnitRunner",
                timeout=120,
            )
            safe_output = result.stdout
            for key in (
                "ADA_WEB_TEST_TOKEN",
                "ADA_WEB_TEST_SECOND_TOKEN",
                "ADA_WEB_TEST_ORDINARY_TOKEN",
                "ADA_WEB_TEST_PASSWORD",
            ):
                safe_output = safe_output.replace(environment[key], "[redacted test credential]")
            print(safe_output)
            if after_stage is not None:
                after_stage(command)
            if "OK (1 test)" not in result.stdout or "FAILURES" in result.stdout:
                raise RuntimeError("Android password validation failed")
            command("shell", "am", "force-stop", package)
    finally:
        removals = (
            (
                ("shell", "pm", "uninstall", "--user", "0", package + ".test"),
                ("shell", "pm", "uninstall", "--user", "0", package),
            )
            if physical_model
            else (("uninstall", package + ".test"), ("uninstall", package))
        )
        for arguments in (
            ("reverse", "--remove", "tcp:19822"),
            *removals,
        ):
            try:
                command(*arguments)
            except (subprocess.SubprocessError, OSError):
                print("Validation device cleanup needs inspection")
        if child and child.poll() is None:
            child.terminate()
            child.wait(timeout=15)
        snapshot.cleanup()
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
    parser.add_argument("--device", required=True)
    run(parser.parse_args().device)
