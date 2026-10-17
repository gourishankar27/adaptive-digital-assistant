"""Emulator-only password/Keystore/Activity flow with disposable PostgreSQL ADA."""

import argparse
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "dev.ada.validation.phase22.debug"


def run(
    device, *, package=PACKAGE, stages=None, test_class="dev.ada.assistant.PasswordLoginUiHttpTest"
):
    if not re.fullmatch(r"emulator-\d+", device) or not os.environ.get("ADA_TEST_DATABASE_URL"):
        raise SystemExit("Select an emulator and dedicated ADA_TEST_DATABASE_URL")
    if not re.fullmatch(r"dev\.ada\.validation\.[a-z][a-z0-9_]{0,30}\.debug", package):
        raise SystemExit("Only a separate validation application ID may be installed")
    adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
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

    def command(*arguments, timeout=90):
        return subprocess.run(
            [str(adb), "-s", device, *arguments],
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True,
        )

    try:
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
        command(
            "install", "-r", str(ROOT / "apps/android/app/build/outputs/apk/debug/app-debug.apk")
        )
        command(
            "install",
            "-r",
            str(
                ROOT
                / "apps/android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk"
            ),
        )
        command("reverse", "tcp:19822", "tcp:18423")
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
                package + ".test/androidx.test.runner.AndroidJUnitRunner",
                timeout=120,
            )
            print(result.stdout)
            if "OK (1 test)" not in result.stdout or "FAILURES" in result.stdout:
                raise RuntimeError("Android password validation failed")
            command("shell", "am", "force-stop", package)
    finally:
        for arguments in (
            ("reverse", "--remove", "tcp:19822"),
            ("uninstall", package + ".test"),
            ("uninstall", package),
        ):
            try:
                command(*arguments)
            except (subprocess.SubprocessError, OSError):
                print("Validation emulator cleanup needs inspection")
        if child and child.poll() is None:
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
    parser.add_argument("--device", required=True)
    run(parser.parse_args().device)
