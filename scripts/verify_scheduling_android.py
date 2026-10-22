"""Emulator-only real HTTP inbox and encrypted exact-ack force-stop recovery."""

import argparse
import os

from verify_password_android import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    args = parser.parse_args()
    os.environ["ADA_WEB_TEST_CURIOSITY_FIXTURE"] = "1"
    os.environ["ADA_WEB_TEST_SCHEDULING_FIXTURE"] = "1"
    run(
        args.device,
        package="dev.ada.validation.phase27.debug",
        stages=("schedulePrepareBeforeProcessStop", "scheduleRestoreAfterProcessStop"),
        test_class="dev.ada.assistant.ScheduleUiHttpTest",
    )
