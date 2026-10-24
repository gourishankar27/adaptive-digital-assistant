"""Phase32 real HTTP/Keystore/restart flow in a separate validation APK."""

import argparse
import os

from verify_password_android import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    parser.add_argument(
        "--suite", choices=("long", "shared-session", "password", "wake-session"), default="long"
    )
    args = parser.parse_args()
    os.environ["ADA_WEB_TEST_VOICE_FIXTURE"] = "1"
    if args.suite == "wake-session":
        os.environ["ADA_SESSION_ACCESS_SECONDS"] = "60"
    run(
        args.device,
        package="dev.ada.validation.privatevoice.debug"
        if args.suite == "wake-session"
        else "dev.ada.validation.voicehttp32.debug",
        test_class="dev.ada.assistant."
        + {
            "long": "LongVoiceUiHttpTest",
            "shared-session": "SharedPasswordSessionHttpTest",
            "password": "PasswordLoginUiHttpTest",
            "wake-session": "SharedWakeSessionHttpTest",
        }[args.suite],
        stages={
            "long": (
                "checkpointPersistsExactGeneratedSegmentsWithoutSending",
                "recoveredStoryNeedsContextAndExplicitSendThenPreservesLineage",
            ),
            "shared-session": (
                "sharedRotationThenUnknownOutcomeIsDurable",
                "consumedSecretAfterProcessDeathNeverReturnsToHttp",
            ),
            "password": None,
            "wake-session": ("backgroundWakeRenewsThenRemoteRevocationStopsIt",),
        }[args.suite],
        fixture_bearer=args.suite == "long",
        physical_model="SM-S721U1",
        instrumentation_arguments={"adaTestOrigin": "http://127.0.0.1:19822"},
        stage_timeout=180 if args.suite == "wake-session" else 120,
    )
