"""Separate emulator APK: owned work preview, brief and exact process-stop recovery."""

import argparse
import os

from verify_password_android import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    args = parser.parse_args()
    os.environ["ADA_WEB_TEST_CURIOSITY_FIXTURE"] = "1"
    os.environ["ADA_WEB_TEST_WORK_FIXTURE"] = "1"
    run(
        args.device,
        package="dev.ada.validation.phase30.debug",
        fixture_bearer=True,
        test_class="dev.ada.assistant.WorkUiHttpTest",
        stages=("workPrepareBeforeProcessStop", "workRestoreAfterProcessStop"),
        instrumentation_arguments={"adaTestOrigin": "http://127.0.0.1:19822"},
    )
