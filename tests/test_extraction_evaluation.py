import importlib.util
from pathlib import Path


def test_synthetic_extraction_evidence_and_explicit_endorsement_corpus(harness):
    path = Path(__file__).resolve().parents[1] / "scripts/evaluate_extraction.py"
    spec = importlib.util.spec_from_file_location("extraction_eval", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.run_benchmark(harness["sessions"])
    assert report["precision"] == report["recall"] == 1
    assert (
        report["proposals"]
        == report["exact_evidence_checks"]
        == report["explicitly_reviewed_claims"]
        == 5
    )
    assert report["extraction_failures"] == 0
    output = path.parents[1] / ".pytest_cache" / f"extraction-{harness['backend']}.json"
    output.write_text(__import__("json").dumps(report, indent=2), encoding="utf-8")
