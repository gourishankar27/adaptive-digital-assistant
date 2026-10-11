import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ada_hybrid_evaluation", ROOT / "scripts/evaluate_hybrid.py"
)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


def test_hybrid_comparison_is_measured_and_keeps_authorized_exact_evidence(harness):
    report = evaluation.run_benchmark(harness["sessions"])
    lexical, hybrid = report["results"]["lexical"], report["results"]["hybrid"]
    assert hybrid["recall_at_5"] > lexical["recall_at_5"]
    assert hybrid["recall_at_5"] == 1.0
    for result in (lexical, hybrid):
        assert result["isolation_or_integrity_violations"] == result["negative_failures"] == 0
        assert result["fallback_rate"] == 0
    assert report["provider"] == "fixture"
    assert report["entries"] <= 256
    destination = ROOT / ".pytest_cache" / f"hybrid-evaluation-{harness['backend']}.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def test_evaluation_rejects_application_database_before_connecting(monkeypatch, tmp_path):
    monkeypatch.setenv("ADA_TEST_DATABASE_URL", "postgresql+psycopg://unused/ada")
    with pytest.raises(ValueError, match="dedicated ada_phase2_test"):
        evaluation.evaluate(tmp_path / "report.json", postgres=True)
