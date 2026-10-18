"""Emulator-only real HTTP research approval/source/Keystore force-stop checks."""

import argparse
import os

from verify_password_android import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    args = parser.parse_args()
    os.environ["ADA_WEB_TEST_RESEARCH_FIXTURE"] = "1"
    run(
        args.device,
        package="dev.ada.validation.phase24.debug",
        stages=("researchApprovalBeforeProcessStop", "researchRestoreAfterProcessStop"),
        test_class="dev.ada.assistant.ResearchUiHttpTest",
    )
