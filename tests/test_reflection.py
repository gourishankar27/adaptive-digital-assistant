"""Real authenticated idle consent/review without factual or external writes."""

from uuid import uuid4

from sqlalchemy import func, select
from test_memory import note, scope

from ada.models import Claim, now_ms

SAFE_RESOURCES = {
    "ac_power": True,
    "disk_free_bytes": 10 * 1024**3,
    "memory_available_percent": 50,
    "thermal_c": 45,
}


def enabled(h, text="TODO: Review the public notebook.", kinds=None):
    s = scope(h)
    original = note(h, s, text)
    policy = h["client"].get("/v1/reflection/policy", headers=h["a"])
    assert policy.status_code == 200
    service = h["app"].state.reflection
    clock = [now_ms()]
    service.clock = lambda: clock[0]
    service.resources = lambda: dict(SAFE_RESOURCES)
    service.settings.scheduler_enabled = True
    service.settings.reflection_enabled = True
    service.settings.consolidation_worker_enabled = True
    scheduler = h["app"].state.scheduling.policy(h["a_id"])
    assert (
        h["client"]
        .post(
            "/v1/scheduling/policy",
            headers=h["a"],
            json={
                "operation_id": str(uuid4()),
                "expected_revision": scheduler["revision"],
                "enabled": True,
            },
        )
        .status_code
        == 200
    )
    op = {
        "operation_id": str(uuid4()),
        "expected_revision": policy.json()["revision"],
        "settings": {
            "enabled": True,
            "scope_ids": [s],
            "job_kinds": kinds or ["report"],
            "allowed_start": 0,
            "allowed_end": 1440,
        },
    }
    result = h["client"].post("/v1/reflection/policy", headers=h["a"], json=op)
    assert result.status_code == 200
    clock[0] += 901000
    return service, clock, s, original, op


def test_reflection_defaults_off_and_no_implicit_completed_turn_selection(harness):
    c = harness["client"]
    assert c.get("/v1/reflection/policy").status_code == 401
    value = c.get("/v1/reflection/policy", headers=harness["a"])
    assert value.status_code == 200
    assert not value.json()["settings"]["enabled"]
    assert not value.json()["settings"]["automatic_completed_turns"]
    assert not value.json()["summary_generation"]


def test_owner_report_review_exact_replay_never_writes_a_fact(harness):
    h = harness
    service, clock, s, original, op = enabled(h)
    assert service.queue_once()
    assert service.run_once()
    assert not service.queue_once()
    items = h["client"].get("/v1/reflection/artifacts", headers=h["a"]).json()
    assert len(items) == 1 and items[0]["kind"] == "report"
    assert items[0]["sources"][0]["evidence"]["quote"] == original["content"]
    assert items[0]["content"]["findings"][0]["category"] == "owner_marked_open_item"
    key = items[0]["id"]
    assert h["client"].get(f"/v1/reflection/artifacts/{key}", headers=h["b"]).status_code == 404
    body = {"operation_id": str(uuid4()), "action": "keep"}
    first = h["client"].post(f"/v1/reflection/artifacts/{key}/actions", headers=h["a"], json=body)
    assert first.status_code == 200
    assert (
        h["client"]
        .post(f"/v1/reflection/artifacts/{key}/actions", headers=h["a"], json=body)
        .json()
        == first.json()
    )
    assert (
        h["client"]
        .post(
            f"/v1/reflection/artifacts/{key}/actions",
            headers=h["a"],
            json=body | {"action": "dismiss"},
        )
        .status_code
        == 409
    )
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


def test_unknown_resource_or_foreground_activity_prevents_dispatch(harness):
    service, clock, _, _, _ = enabled(harness)
    service.resources = lambda: SAFE_RESOURCES | {"thermal_c": None}
    assert not service.queue_once()
    service.resources = lambda: dict(SAFE_RESOURCES)
    service.activity(harness["a_id"])
    assert not service.queue_once()
    clock[0] += 901000
    assert service.queue_once()


def test_owner_off_revokes_queued_work_and_exact_policy_replay(harness):
    h = harness
    service, clock, _, _, original = enabled(h)
    assert service.queue_once()
    current = h["client"].get("/v1/reflection/policy", headers=h["a"]).json()
    off = {
        "operation_id": str(uuid4()),
        "expected_revision": current["revision"],
        "settings": current["settings"] | {"enabled": False},
    }
    assert h["client"].post("/v1/reflection/policy", headers=h["a"], json=off).status_code == 200
    assert not service.run_once()
    assert h["client"].get("/v1/reflection/artifacts", headers=h["a"]).json() == []
    rows = h["client"].get("/v1/reflection/runs", headers=h["a"]).json()
    assert rows[0]["state"] == "suppressed"
