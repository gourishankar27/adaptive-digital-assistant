import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ada_evaluation", ROOT / "scripts/evaluate_retrieval.py"
)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


def test_retrieval_evaluation_measures_relevance_and_isolation(harness):
    report = evaluation.run_benchmark(harness["sessions"])
    metrics = report["metrics"]
    assert metrics["recall_at_5"] >= 0.8
    assert metrics["mrr_at_5"] >= 0.7
    assert metrics["exact_evidence_coverage"] == 1.0
    assert metrics["scope_violations"] == metrics["negative_query_failures"] == 0
    cases = {case["case"]: case for case in report["cases"]}
    assert cases["historical_preference"]["retrieved"][0] == "language_old"
    assert cases["semantic_runtime_miss"]["retrieved"] == []
    assert cases["semantic_beverage_miss"]["retrieved"] == []
