import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ada_document_evaluation", ROOT / "scripts/evaluate_documents.py"
)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


def test_document_corpus_records_real_repository_artifact_and_synthetic_inputs():
    corpus = json.loads(
        (ROOT / "evaluations/document-retrieval-v1.json").read_text(encoding="utf-8")
    )
    real = next(item for item in corpus["documents"] if item["key"] == "repository_introduction")
    # Exact source artifact was corroborated against Git during capture.
    # The committed digest keeps ZIP/shallow installs independent of history.
    expected = "e9940183c4a569858ee6b7ebda0b64051304b41892864c43c7a8df01419cf8c4"
    assert hashlib.sha256(real["text"].encode("utf-8")).hexdigest() == expected
    assert real["source_sha256"] == expected
    assert real["source_ref"] == "README.md@1ca228a:2"
    assert real["input_kind"] == "real_repository_excerpt"
    assert all("\\" not in item["source_ref"] for item in corpus["documents"])
    assert any(item["input_kind"] == "synthetic" for item in corpus["documents"])


def test_document_evaluation_checks_exact_excerpts_and_isolation(harness):
    report = evaluation.run_benchmark(harness["sessions"])
    metrics = report["metrics"]
    assert metrics["recall_at_5"] == metrics["mrr_at_5"] == 1.0
    assert metrics["exact_evidence_coverage"] == 1.0
    assert metrics["scope_violations"] == metrics["negative_query_failures"] == 0
    assert metrics["known_excerpt_failures"] == 0
    cases = {case["case"]: case for case in report["cases"]}
    assert cases["historical_old"]["retrieved"] == ["reactor_old"]
    assert cases["historical_new"]["retrieved"] == ["reactor_new"]
    assert cases["expired_latest_no_fallback"]["retrieved"] == []
    assert cases["real_repository_excerpt"]["input_kinds"] == ["real_repository_excerpt"]
