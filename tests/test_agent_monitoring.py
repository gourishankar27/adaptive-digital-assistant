from test_admin import grant
from test_agents import prepared


def test_agent_monitoring_contains_only_aggregate_states_and_no_cross_owner_authority(harness):
    h = harness
    run, approval, path, _ = prepared(h)
    assert h["client"].get("/v1/admin/overview", headers=h["b"]).status_code == 403
    grant(h, "b")
    response = h["client"].get("/v1/admin/overview", headers=h["b"])
    assert response.status_code == 200
    counts = response.json()["agent_run_counts"]
    assert counts == {
        "running": 0,
        "pending_approval": 1,
        "completed": 0,
        "failed": 0,
        "unknown": 0,
    }
    assert set(counts) == {"running", "pending_approval", "completed", "failed", "unknown"}
    assert all(
        key not in response.text
        for key in ("expression", "arguments", "tool_result", "preview_hash", run["id"])
    )
    assert h["client"].post(path + "/approve", headers=h["b"], json=approval).status_code == 404
