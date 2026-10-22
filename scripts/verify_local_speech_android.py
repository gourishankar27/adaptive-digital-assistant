"""Phase29 emulator-only speech contract checks; synthetic audio, real owned HTTP."""

import argparse
import os

from verify_password_android import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    args = parser.parse_args()
    os.environ["ADA_WEB_TEST_VOICE_FIXTURE"] = "1"
    run(
        args.device,
        package="dev.ada.validation.phase29.debug",
        test_class="dev.ada.assistant.VoiceUiHttpTest",
        stages=(
            "publicVoicePreviewAndEngineStatusNeverCaptureOrSubmit",
            "explicitRecordReviewSendLineageAndPlaybackStopAreIndependentOfGeneration",
            "denialBackgroundLateResultsAndEncryptedDraftRecoveryDoNotSend",
        ),
        fixture_bearer=True,
        instrumentation_arguments={"adaTestOrigin": "http://127.0.0.1:19822"},
    )
