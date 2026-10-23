"""Profile fixed public synthetic PDF layouts with the actual isolated parser; no DB/model."""

import argparse
import hashlib
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from ada.pdf_sandbox import DockerPdfParser
from ada.pdfs import pdf_chunks, validate_extraction

ROOT = Path(__file__).resolve().parents[1]


def evaluate(manifest):
    sys.path.insert(0, str(ROOT / "tests"))
    from pdf_fixtures import public_pdf_profiles

    parser = DockerPdfParser(manifest)
    if not parser.available:
        raise SystemExit("Verified local PDF isolation is required")
    cases = []
    for profile in public_pdf_profiles():
        started = time.monotonic()
        result = validate_extraction(profile["raw"], parser.parse(profile["raw"]))
        chunks = pdf_chunks(result["text"], result["pages"])
        if len(result["pages"]) != profile["pages"] or not all(
            fragment in result["text"] for fragment in profile["fragments"]
        ):
            raise SystemExit("Public fixture extraction failed its expected fragments/pages")
        cases.append(
            {
                "case": profile["key"],
                "raw_sha256": hashlib.sha256(profile["raw"]).hexdigest(),
                "raw_bytes": len(profile["raw"]),
                "text_bytes": len(result["text"].encode("utf-8")),
                "text_sha256": result["text_hash"],
                "pages": len(result["pages"]),
                "chunks": len(chunks),
                "fits_android_64kib": len(profile["raw"]) <= 65536,
                "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
            }
        )
    dense = next(case for case in cases if case["case"] == "dense-16-pages")
    compressed = next(case for case in cases if case["case"] == "compressed-16-pages")
    if (
        dense["text_sha256"] != compressed["text_sha256"]
        or dense["raw_sha256"] == compressed["raw_sha256"]
    ):
        raise SystemExit("Compression must preserve exact extracted text and distinct originals")
    return {
        "version": "ada-public-text-pdf-profiles-v1",
        "observed_at": datetime.now(UTC).isoformat(),
        "input_kind": "developer_generated_public_synthetic",
        "human_acceptance": False,
        "parser": result["parser"],
        "image_id": parser.image,
        "cases": cases,
    }


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--manifest", type=Path, required=True)
    arguments.add_argument("--output", type=Path)
    options = arguments.parse_args()
    report = json.dumps(evaluate(options.manifest), indent=2) + "\n"
    if options.output:
        options.output.write_text(report, encoding="utf-8")
    print(report, end="")
