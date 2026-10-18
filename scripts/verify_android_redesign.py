"""Separate emulator-only UI validation; public fixture images, no production window capture."""

import argparse
import base64
import os
import struct
import subprocess
from pathlib import Path

from verify_password_android import run

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "dev.ada.validation.redesign.debug"


def collect_public_images(command, variant, capture_root):
    output = capture_root / variant
    output.mkdir(parents=True, exist_ok=True)
    wrong_orientation = False
    for name in (
        "connect",
        "home",
        "chat",
        "typing",
        "typing-window",
        "sources",
        "settings",
        "light",
        "presence",
    ):
        relative = "files/ada-public-" + name + ".png"
        try:
            command("shell", "run-as", PACKAGE, "test", "-f", relative)
            encoded = command("exec-out", "run-as", PACKAGE, "base64", relative).stdout
        except subprocess.CalledProcessError:
            continue
        target = output / (name + ".png")
        assert target.resolve().is_relative_to(output.resolve())
        data = base64.b64decode("".join(encoded.split()), validate=True)
        target.write_bytes(data)
        if name in ("chat", "typing") and variant == "landscape":
            width, height = struct.unpack(">II", data[16:24])
            if width <= height:
                wrong_orientation = True
    if wrong_orientation:
        raise RuntimeError("Landscape validation captured a portrait surface; rerun rotation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    parser.add_argument("--stage", action="append")
    parser.add_argument(
        "--capture-root", type=Path, default=ROOT / ".pytest_cache/ui-redesign/screens"
    )
    parser.add_argument(
        "--variant", choices=("portrait", "landscape", "expanded"), default="portrait"
    )
    parser.add_argument(
        "--suite", choices=("visual", "curiosity", "password", "foundation"), default="visual"
    )
    args = parser.parse_args()
    os.environ["ADA_WEB_TEST_CURIOSITY_FIXTURE"] = "1"
    suites = {
        "visual": ("AmbientUiHttpTest", ("publicChatAndKeyboard", "presenceSemanticsAndLightMode")),
        "curiosity": (
            "CuriosityUiHttpTest",
            ("curiosityPrepareBeforeProcessStop", "curiosityRestoreAfterProcessStop"),
        ),
        "password": (
            "PasswordLoginUiHttpTest",
            (
                "passwordLoginAndRenewBeforeProcessStop",
                "passwordRestoreAfterActualProcessStopThenRevoke",
            ),
        ),
        "foundation": ("FoundationSmokeTest", ("launchesLabelsInputsAndThemePreview",)),
    }
    test_class, stages = suites[args.suite]
    run(
        args.device,
        package=PACKAGE,
        stages=args.stage or stages,
        test_class="dev.ada.assistant." + test_class,
        after_stage=(
            lambda command: collect_public_images(command, args.variant, args.capture_root)
        )
        if args.suite == "visual"
        else None,
    )
