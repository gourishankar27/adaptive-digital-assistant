from scripts.evaluate_episodes import run_benchmark


def test_documented_synthetic_episode_corpus_real_jobs_exact_maps_and_no_claims(harness):
    report = run_benchmark(harness["sessions"])
    assert report["completed"] == 4 and report["exact_support_checks"] == 5
    assert report["marker_coverage"] == 1 and report["endorsed_claims"] == 0
    assert all(c["attempt"] == 1 and not c["omitted_markers"] for c in report["cases"])
