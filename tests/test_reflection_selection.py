"""Positive completed-turn opt-in and completion-state/source trust fences."""

from uuid import uuid4

from conftest import make_conversation, send
from sqlalchemy import func, select
from test_reflection import enabled

from ada.models import Claim, Request
from ada.providers import Completion


def selected_turns(h):
    cid, _ = make_conversation(h)
    h["provider"].complete = lambda messages: Completion(
        "TODO: Invent an unsupported personal fact.", h["provider"].model
    )
    request_id = str(uuid4())
    assert send(h, cid, "TODO: Review the public release notes.", request_id).status_code == 200
    conversation = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()
    service, clock, _, _, _ = enabled(h)
    p = service.policy(h["a_id"])
    r = h["client"].post(
        "/v1/reflection/policy",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_revision": p["revision"],
            "settings": p["settings"]
            | {
                "scope_ids": [conversation["scope_id"]],
                "automatic_completed_turns": True,
                "source_types": ["completed_user_turns", "completed_model_turns"],
            },
        },
    )
    assert r.status_code == 200
    clock[0] += 901000
    return service, request_id


def test_completed_turn_auto_selection_preserves_original_trust_and_never_accepts_model_todo(
    harness,
):
    h = harness
    service, _ = selected_turns(h)
    assert service.queue_once()
    run, _ = service.claim()
    assert len(run.snapshot) == 2
    assert {s["trust_class"] for s in run.snapshot} == {"user_explicit", "model_generated"}
    content = service._report(run)
    assert len(content["findings"]) == 1
    assert "release notes" in content["findings"][0]["text"]
    assert "personal fact" not in content["findings"][0]["text"]
    assert service._finish(run, content, None, 1, None)
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


def test_completion_state_change_rejects_late_turn_derived_output(harness):
    h = harness
    service, request_id = selected_turns(h)
    assert service.queue_once()
    run, _ = service.claim()
    result = service._report(run)
    with h["sessions"].begin() as db:
        db.get(Request, (h["a_id"], request_id)).status = "failed"
    assert not service._finish(run, result, None, 1, None)
    assert not service.artifacts(h["a_id"])
