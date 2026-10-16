"""Cross-feature public regression scorecard; never reads the application database."""

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import tempfile
import time
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from ada.db import connect

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evaluations/quality-baseline-v1.json"
DATASETS = {
    "retrieval": "evaluations/retrieval-v1.json",
    "documents": "evaluations/document-retrieval-v1.json",
    "hybrid": "evaluations/hybrid-retrieval-v1.json",
    "extraction": "evaluations/memory-extraction-v1.json",
    "episodes": "evaluations/episode-summary-v1.json",
    "heldout": "evaluations/quality-heldout-v1.json",
}
ADAPTERS = {
    "retrieval": "evaluate_retrieval",
    "documents": "evaluate_documents",
    "hybrid": "evaluate_hybrid",
    "extraction": "evaluate_extraction",
    "episodes": "evaluate_episodes",
}


def canonical_hash(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_manifest(path=MANIFEST):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if value.get("version") != "ada-quality-baseline-v1" or set(value["datasets"]) != set(DATASETS):
        raise ValueError("Unsupported quality corpus manifest")
    for family, expected in DATASETS.items():
        entry = value["datasets"][family]
        if entry["path"] != expected or entry["sha256"] != canonical_hash(ROOT / expected):
            raise ValueError(
                "Frozen corpus path or digest mismatch; create an explicit new version"
            )
    return value


def adapter(family):
    name = ADAPTERS[family]
    spec = importlib.util.spec_from_file_location(
        "ada_quality_" + name, ROOT / "scripts" / (name + ".py")
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def score_component(family, report):
    def scalars(values):
        result = {}
        for key, value in values.items():
            if type(value) not in (int, float) and value is not None:
                continue
            if (
                key
                in {
                    "scope_violations",
                    "negative_query_failures",
                    "negative_failures",
                    "isolation_or_integrity_violations",
                    "known_excerpt_failures",
                }
                and value
            ):
                raise ValueError("Quality corpus authority/isolation invariant failed")
            if key == "exact_evidence_coverage" and value != 1:
                raise ValueError("Quality corpus exact evidence invariant failed")
            result[key] = value
        return result

    metrics = (
        {name: scalars(value) for name, value in report["results"].items()}
        if family == "hybrid"
        else scalars(report.get("metrics", report))
    )
    return {
        "metrics": metrics,
        "semantic_quality": {
            "answer_usefulness": None,
            "citation_entailment": None,
            "justified_uncertainty": None,
            "followup_helpfulness": None,
            "assessment": "Unassessed: exact spans, fixture gold and markers are not semantic grades",
        },
    }


def holdout(output, postgres):
    prior = os.environ.get("ADA_DATABASE_URL")
    admin = engine = schema = None
    with tempfile.TemporaryDirectory(prefix="ada-quality-heldout-") as directory:
        try:
            url = "sqlite:///" + (Path(directory) / "holdout.db").as_posix()
            if postgres:
                raw = os.environ.get("ADA_TEST_DATABASE_URL")
                if (
                    not raw
                    or make_url(raw).database != "ada_phase2_test"
                    or make_url(raw).get_backend_name() != "postgresql"
                ):
                    raise ValueError("Use the dedicated ada_phase2_test database")
                schema = "ada_quality_" + uuid4().hex
                admin = create_engine(raw)
                with admin.begin() as conn:
                    conn.execute(text(f'CREATE SCHEMA "{schema}"'))
                url = (
                    make_url(raw)
                    .update_query_dict({"options": "-csearch_path=" + schema})
                    .render_as_string(hide_password=False)
                )
            os.environ["ADA_DATABASE_URL"] = url
            command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
            engine, sessions = connect(url)
            result = adapter("retrieval").run_benchmark(sessions, ROOT / DATASETS["heldout"])
            # Raw synthetic queries stay in the committed corpus, not the combined report.
            safe = {
                "metrics": result["metrics"],
                "backend": result["backend"],
                "case_ids": [case["case"] for case in result["cases"]],
            }
            output.write_text(json.dumps(safe, indent=2) + "\n", encoding="utf-8")
            return result
        finally:
            if engine:
                engine.dispose()
            if admin:
                with admin.begin() as conn:
                    conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
                admin.dispose()
            if prior is None:
                os.environ.pop("ADA_DATABASE_URL", None)
            else:
                os.environ["ADA_DATABASE_URL"] = prior


def evaluate(output, postgres=False, generation_provider="fixture"):
    manifest = load_manifest()
    if generation_provider not in ("fixture", "ollama"):
        raise ValueError("Unsupported generation provider")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    components = {}
    for family in DATASETS:
        started = time.perf_counter()
        tracemalloc.start()
        try:
            target = output.parent / (output.stem + "-" + family + ".json")
            with contextlib.redirect_stdout(io.StringIO()):
                if family == "heldout":
                    report = holdout(target, postgres)
                elif family in ("retrieval", "documents"):
                    report = adapter(family).evaluate(target, postgres)
                elif family == "hybrid":
                    report = adapter(family).evaluate(target, "fixture", postgres)
                elif family == "extraction":
                    report = adapter(family).evaluate(target, generation_provider)
                else:
                    report = adapter(family).evaluate(target, generation_provider, postgres)
            peak = tracemalloc.get_traced_memory()[1]
            summary = score_component(family, report)
            components[family] = (
                summary
                | {
                    "backend": report.get(
                        "backend", "sqlite" if family == "extraction" else "unknown"
                    ),
                    "execution": generation_provider
                    if family in ("extraction", "episodes")
                    else "deterministic",
                    "elapsed_seconds": round(time.perf_counter() - started, 3),
                    "python_peak_bytes": peak,
                    "case_ids": [
                        case.get("case", case.get("key")) for case in report.get("cases", [])
                    ],
                    "model": report.get("model"),
                    "model_digest": None,  # Unknown/fixture: never substitute a corpus digest for weights.
                }
            )
            print(json.dumps({"component": family, "status": "completed"}), flush=True)
        finally:
            tracemalloc.stop()
    result = {
        "version": manifest["version"],
        "measured_at_utc": datetime.now(UTC).isoformat(),
        "schema_head": "0015",
        "manifest_sha256": canonical_hash(MANIFEST),
        "components": components,
        "review_rubric": manifest["review_rubric"],
        "limitations": [
            "Public synthetic fixtures, not representative private quality",
            "Frozen regression holdout is not a guarantee of unseen model training data",
            "Python peaks exclude database, native speech, GPU and other process allocations",
            "Extraction standalone adapter uses SQLite even when other components use PostgreSQL",
            "No model download, semantic activation, prompt upgrade or private evaluation",
        ],
    }
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".pytest_cache/quality-scorecard.json"))
    parser.add_argument("--postgres", action="store_true")
    parser.add_argument("--generation-provider", choices=("fixture", "ollama"), default="fixture")
    args = parser.parse_args()
    try:
        evaluate(args.output, args.postgres, args.generation_provider)
    except Exception:
        parser.exit(1, "Quality baseline failed; no application data was used.\n")


if __name__ == "__main__":
    main()
