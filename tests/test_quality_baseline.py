import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location(
        "quality_baseline", ROOT / "scripts/evaluate_quality.py"
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_frozen_corpus_changes_and_unsafe_paths_are_rejected(tmp_path):
    evaluation = module()
    manifest = evaluation.load_manifest()
    path = tmp_path / "manifest.json"
    changed = json.loads(json.dumps(manifest))
    changed["datasets"]["retrieval"]["sha256"] = "0" * 64
    path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError):
        evaluation.load_manifest(path)
    changed["datasets"]["retrieval"]["path"] = "../private.json"
    path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError):
        evaluation.load_manifest(path)


def test_fixture_scores_never_claim_usefulness_or_entailment():
    evaluation = module()
    report = evaluation.score_component(
        "retrieval",
        {
            "metrics": {
                "recall_at_5": 1,
                "scope_violations": 0,
                "negative_query_failures": 0,
                "exact_evidence_coverage": 1,
            }
        },
    )
    assert report["semantic_quality"]["citation_entailment"] is None
    assert report["semantic_quality"]["answer_usefulness"] is None
    with pytest.raises(ValueError):
        evaluation.score_component(
            "retrieval",
            {
                "metrics": {
                    "recall_at_5": 1,
                    "scope_violations": 1,
                    "negative_query_failures": 0,
                    "exact_evidence_coverage": 1,
                }
            },
        )


def test_canonical_corpus_hash_handles_windows_newlines_and_rejects_native_paths(tmp_path):
    evaluation = module()
    path = tmp_path / "corpus.json"
    path.write_bytes(b'{\n  "synthetic": true\n}\n')
    original = evaluation.canonical_hash(path)
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert evaluation.canonical_hash(path) == original
    manifest = evaluation.load_manifest()
    manifest["datasets"]["retrieval"]["path"] = "evaluations\\retrieval-v1.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError):
        evaluation.load_manifest(path)


def test_frozen_holdout_checks_corrections_uncertainty_and_isolation(harness):
    evaluation = module()
    retrieval = evaluation.adapter("retrieval")
    report = retrieval.run_benchmark(
        harness["sessions"], ROOT / "evaluations/quality-heldout-v1.json"
    )
    metrics = report["metrics"]
    assert metrics["recall_at_5"] == metrics["exact_evidence_coverage"] == 1
    assert metrics["scope_violations"] == metrics["negative_query_failures"] == 0
    assert report["positive_queries"] == 3 and report["negative_queries"] == 5
