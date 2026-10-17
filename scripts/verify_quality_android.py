"""Phase23 emulator-only real HTTP window/source and explicit prompt UI check."""

import argparse

from verify_password_android import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    args = parser.parse_args()
    run(
        args.device,
        package="dev.ada.validation.phase23.debug",
        stages=("calendarWindowAndQualityUpgrade",),
        test_class="dev.ada.assistant.QualityUiHttpTest",
    )
