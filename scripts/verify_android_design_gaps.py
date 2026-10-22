"""Explicit separate-APK Android design validation; disposable PG and public fixtures only."""

import argparse
import base64
import os
import subprocess
from pathlib import Path

from verify_password_android import run

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "dev.ada.validation.designgaps.debug"


def collect_public_images(command, output):
    output.mkdir(parents=True, exist_ok=True)
    try:
        names = command("shell", "run-as", PACKAGE, "ls", "files").stdout.splitlines()
    except subprocess.CalledProcessError:
        return  # A failure before the first public capture must keep its original error.
    for name in names:
        if (
            not name.startswith("ada-design-")
            or not name.endswith(".png")
            or Path(name).name != name
        ):
            continue
        encoded = command("exec-out", "run-as", PACKAGE, "base64", "files/" + name).stdout
        (output / name).write_bytes(base64.b64decode("".join(encoded.split()), validate=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    parser.add_argument(
        "--physical-model", help="Explicitly permit only the matching connected model"
    )
    parser.add_argument("--stage", action="append")
    parser.add_argument(
        "--variant", choices=("phone", "landscape", "large-font", "expanded"), default="phone"
    )
    parser.add_argument(
        "--suite",
        choices=(
            "design",
            "foundation",
            "entities",
            "documents",
            "proposals",
            "voice",
            "streaming",
            "security",
            "expression",
            "tools",
            "learning",
            "curiosity",
            "research",
        ),
        default="design",
    )
    args = parser.parse_args()
    os.environ["ADA_WEB_TEST_DESIGN_FIXTURE"] = "1"
    output = (
        ROOT
        / ".pytest_cache/android-design-gaps/screens"
        / ("physical" if args.physical_model else "emulator")
        / args.variant
    )
    suites = {
        "design": (
            "DesignGapsUiTest",
            (
                "feedbackSelectionNativeTargetsAndModalKeyboardFocus",
                "darkPrimaryScreensAndSafeConfirmations",
                "lightPrimaryScreensAndSafeConfirmations",
                "shortWindowContextAndOptionsStayInsideWindow",
            ),
        ),
        "foundation": ("FoundationSmokeTest", ("launchesLabelsInputsAndThemePreview",)),
        "entities": (
            "EntityUiHttpTest",
            ("reviewedCreationAliasesAmbiguityLinksMergeAndUndoPreserveEvidence",),
        ),
        "documents": (
            "DocumentUiHttpTest",
            ("reviewedExactPastedTextUploadsOnlyAfterExplicitButton",),
        ),
        "proposals": (
            "ProposalUiHttpTest",
            ("selectedSourceEditAcceptAndRejectUseRealHttpAndHonestEvidence",),
        ),
        "voice": (
            "VoiceUiHttpTest",
            (
                "explicitRecordReviewSendLineageAndPlaybackStopAreIndependentOfGeneration",
                "denialBackgroundLateResultsAndEncryptedDraftRecoveryDoNotSend",
            ),
        ),
        "streaming": (
            "StreamingUiHttpTest",
            ("provisionalObserverDetachStopAndExactCancelledRetryOverHttp",),
        ),
        "security": (
            "SecurityUiHttpTest",
            ("deviceInstallRotationRevocationAndExplicitErasureClearPrivateRecovery",),
        ),
        "expression": (
            "ExpressionUiHttpTest",
            ("explicitScopedPreferencesToneDisableAndResetOverRealHttp",),
        ),
        "tools": ("AgentUiHttpTest", ("exactCalculatorApprovalAndDenialUseRealHttpReceipts",)),
        "learning": (
            "LearningUiHttpTest",
            ("enrollSelectEvidenceReviewEditRejectPauseAndResetOverRealHttp",),
        ),
        "curiosity": (
            "CuriosityUiHttpTest",
            ("curiosityPrepareBeforeProcessStop", "curiosityRestoreAfterProcessStop"),
        ),
        "research": (
            "ResearchUiHttpTest",
            ("researchApprovalBeforeProcessStop", "researchRestoreAfterProcessStop"),
        ),
    }
    test_class, stages = suites[args.suite]
    run(
        args.device,
        package=PACKAGE,
        physical_model=args.physical_model,
        fixture_bearer=args.suite not in ("design", "foundation"),
        instrumentation_arguments={
            "designVariant": args.variant,
            "adaTestOrigin": "http://127.0.0.1:19822",
        },
        stages=args.stage or stages,
        test_class="dev.ada.assistant." + test_class,
        after_stage=(lambda command: collect_public_images(command, output))
        if args.suite == "design"
        else None,
    )
