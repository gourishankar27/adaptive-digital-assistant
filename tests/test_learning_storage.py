from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from test_consolidation import enqueue, prepared
from test_learning import config, inbox, observation, review, scope_of

from ada.consolidation_models import Episode
from ada.learning import DAY
from ada.learning_models import InteractionProposal, LearningEnrollment, LearningReceipt
from ada.models import Conversation
from ada.providers import ProviderError
from ada.schema import SCHEMA_HEAD


def learned_setup(h):
    cid, _ = make_conversation(h)
    sid = scope_of(h, cid)
    assert config(h, sid).status_code == 201
    for content in (
        "Concise planning is useful.",
        "Short coding explanations help.",
        "Brief reviews work best.",
    ):
        assert observation(h, cid, content)[0].status_code == 201
    return cid, sid, inbox(h, sid)["proposals"][0]


def test_account_reuse_is_enum_only_requires_both_consents_and_reset_propagates(harness):
    h = harness
    cid, sid, p = learned_setup(h)
    assert review(h, sid, p, account_wide=True)[0].status_code == 201
    other = (
        h["client"]
        .post("/v1/scopes", headers=h["a"], json={"name": "Unrelated project"})
        .json()["id"]
    )
    with h["sessions"]() as db:
        pid = db.get(Conversation, cid).personality_id
    fresh = (
        h["client"]
        .post("/v1/conversations", headers=h["a"], json={"personality_id": pid, "scope_id": other})
        .json()["id"]
    )
    response = send(h, fresh)
    assert (
        h["client"]
        .get(f"/v1/requests/{response.json()['request_id']}/learning", headers=h["a"])
        .json()["learning"]
        is None
    )
    config(h, other)
    response = send(h, fresh, "Explain unrelated settings.")
    snap = (
        h["client"]
        .get(f"/v1/requests/{response.json()['request_id']}/learning", headers=h["a"])
        .json()["learning"]
    )
    assert snap["preferences"]["verbosity"] == "concise" and snap["continuity"] == []
    assert "Short coding" not in str(h["provider"].calls[-1])
    config(h, sid, "paused", 1)
    response = send(h, fresh, "New unrelated reply.")
    assert not any(
        h["client"]
        .get(f"/v1/requests/{response.json()['request_id']}/learning", headers=h["a"])
        .json()["learning"]["preferences"]
        .values()
    )
    config(h, sid, "off", 2)
    assert inbox(h, sid)["learned"] == []


def test_reviewed_edit_expiry_and_minimal_reset_audit(harness):
    h = harness
    cid, sid, p = learned_setup(h)
    assert review(h, sid, p, values={"verbosity": "balanced"})[0].status_code == 201
    assert inbox(h, sid)["learned"][0]["values"]["verbosity"] == "balanced"
    assert inbox(h, sid)["proposals"][0]["values"]["verbosity"] == "concise"
    r, _ = observation(h, cid, "This is only a weak tentative guess.", "weak_inference", "detailed")
    assert r.status_code == 201
    weak = next(p for p in inbox(h, sid)["proposals"] if p["values"]["verbosity"] == "detailed")
    assert not weak["eligible"] and review(h, sid, weak)[0].status_code == 409
    h["app"].state.learning.clock = lambda: weak["expires_at"] + DAY
    assert all(p["id"] != weak["id"] for p in inbox(h, sid)["proposals"])
    assert review(h, sid, weak, decision="reject")[0].status_code == 409
    assert (
        h["client"]
        .post(
            f"/v1/scopes/{sid}/learning/reset",
            headers=h["a"],
            json={"operation_id": str(uuid4()), "expected_revision": 1},
        )
        .status_code
        == 201
    )
    with h["sessions"]() as db:
        for audit in db.scalars(select(LearningReceipt)):
            assert set(audit.result) == {
                "operation_id",
                "scope_id",
                "action",
                "revision",
                "epoch",
                "observation_id",
                "proposal_id",
                "decision",
                "created_at",
                "observation_ids",
                "proposal_revision",
            }


def test_failed_retry_retains_learning_after_reset(harness):
    h = harness
    cid, sid, p = learned_setup(h)
    review(h, sid, p)
    rid = str(uuid4())
    h["provider"].error = ProviderError("synthetic_failure")
    assert send(h, cid, "Exact retry", rid).status_code == 502
    original = h["provider"].calls[-1]
    config(h, sid, "off", 1)
    h["provider"].error = None
    assert send(h, cid, "Exact retry", rid).status_code == 200
    assert h["provider"].calls[-1] == original and "ada-learning-v1" in original[0]["content"]


def test_continuity_uses_original_sources_not_false_summary_keeps_scope_time_replay(harness):
    h = harness
    sid, note, body, service, _ = prepared(h)
    assert enqueue(h, sid, body).status_code == 201 and service.run_once()
    cid, pid = make_conversation(h)
    conv = (
        h["client"]
        .post("/v1/conversations", headers=h["a"], json={"personality_id": pid, "scope_id": sid})
        .json()["id"]
    )
    assert config(h, sid, continuity=True).status_code == 201
    with h["sessions"].begin() as db:
        episode = db.scalar(select(Episode).where(Episode.scope_id == sid))
        episode.summary = {
            "sections": [{"text": "We travelled together to Mars.", "support": body["sources"]}],
            "tags": ["Mars"],
            "omissions": ["Synthetic conflict omitted."],
        }
    r = send(h, conv, "Mira tea discussion?")
    rid = r.json()["request_id"]
    snapshot = h["client"].get(f"/v1/requests/{rid}/learning", headers=h["a"]).json()["learning"]
    assert len(snapshot["continuity"]) == 1
    assert snapshot["continuity"][0]["evidence"]["quote"] == note["content"]
    assert snapshot["continuity"][0]["summary_trust"] == "model_generated"
    assert "Mars" not in str(h["provider"].calls[-1]) and "C1" in str(h["provider"].calls[-1])
    h["client"].post(
        f"/v1/conversations/{conv}/messages",
        headers=h["a"],
        json={"request_id": str(uuid4()), "content": "Mira tea as of 2000-01-01"},
    )
    assert "C1" not in str(h["provider"].calls[-1])
    send(h, conv, "Mira tea yesterday")
    assert "C1" not in str(h["provider"].calls[-1])
    assert send(h, cid, "Mira tea discussion?").status_code == 200
    assert "C1" not in str(h["provider"].calls[-1])
    config(h, sid, "off", 1)
    assert send(h, conv, "Mira tea discussion?", rid).json() == r.json()


def test_populated_0011_upgrade_old_replay_nullable_snapshot_and_schema(harness):
    h = harness
    cid, _ = make_conversation(h)
    old = send(h, cid)
    with h["sessions"]() as db:
        saved_prompt = db.get(Conversation, cid).system_prompt
    command.downgrade(h["config"], "0011")
    command.upgrade(h["config"], "head")
    assert send(h, cid, request_id=old.json()["request_id"]).json() == old.json()
    with h["sessions"]() as db:
        assert db.get(Conversation, cid).system_prompt == saved_prompt
        assert db.scalar(text("SELECT learning_snapshot FROM requests LIMIT 1")) is None
    command.check(h["config"])
    config(h, scope_of(h, cid))
    with pytest.raises(RuntimeError, match="Learning history"):
        command.downgrade(h["config"], "0011")
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_HEAD


def test_postgres_concurrent_cas_has_one_winner(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Native PostgreSQL row locks required")
    cid, _ = make_conversation(h)
    sid = scope_of(h, cid)
    barrier = Barrier(2)

    def change():
        barrier.wait(timeout=10)
        return config(h, sid).status_code

    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(lambda _: change(), range(2))) == [201, 409]


def test_native_learning_value_and_owner_constraints(harness):
    h = harness
    cid, _ = make_conversation(h)
    sid = scope_of(h, cid)
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(
            LearningEnrollment(
                owner_id=h["b_id"],
                scope_id=sid,
                revision=1,
                epoch=0,
                status="enrolled",
                continuity_enabled=True,
            )
        )


def test_reset_still_works_when_normal_receipt_quota_is_full(harness, monkeypatch):
    h = harness
    cid, sid, p = learned_setup(h)
    assert review(h, sid, p)[0].status_code == 201
    monkeypatch.setattr("ada.learning.MAX_RECEIPTS", 1)
    response = h["client"].post(
        f"/v1/scopes/{sid}/learning/reset",
        headers=h["a"],
        json={"operation_id": str(uuid4()), "expected_revision": 1},
    )
    assert response.status_code == 201, response.text
    assert inbox(h, sid)["learned"] == []


def test_review_lineage_stays_inspectable_after_new_evidence_and_expiry(harness):
    h = harness
    cid, sid, p = learned_setup(h)
    approved, _ = review(h, sid, p)
    assert approved.status_code == 201
    original_ids = approved.json()["observation_ids"]
    assert len(original_ids) == 3
    observation(h, cid, "Another independent preference exchange.")
    state = inbox(h, sid)
    assert state["learned"][0]["observation_ids"] == original_ids
    h["app"].state.learning.clock = lambda: (
        max(o["expires_at"] for o in state["observations"]) + DAY
    )
    state = inbox(h, sid)
    assert {o["id"] for o in state["observations"]} == set(original_ids)
    assert state["learned"][0]["observation_ids"] == original_ids


def test_continuity_preserves_conflicting_original_sources_and_records_omissions(harness):
    from test_memory import note
    from test_proposals import pin

    h = harness
    sid, _, body, service, _ = prepared(h)
    second = note(h, sid, "Mira discussed tea but chose coffee instead.")
    unrelated = note(h, sid, "A separate topic was omitted from the generated interpretation.")
    body["sources"].extend([pin(second), pin(unrelated)])
    assert enqueue(h, sid, body).status_code == 201 and service.run_once()
    _, profile = make_conversation(h)
    cid = (
        h["client"]
        .post(
            "/v1/conversations", headers=h["a"], json={"personality_id": profile, "scope_id": sid}
        )
        .json()["id"]
    )
    config(h, sid, continuity=True)
    reply = send(h, cid, "Mira tea discussion?")
    cards = (
        h["client"]
        .get(f"/v1/requests/{reply.json()['request_id']}/learning", headers=h["a"])
        .json()["learning"]["continuity"]
    )
    assert len(cards) == 2 and all(c["omitted_source_count"] == 1 for c in cards)
    assert any("coffee" in c["evidence"]["quote"] for c in cards)
    assert all(c["uncertainty"] == "source_reference_not_verified_recollection" for c in cards)
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(
            InteractionProposal(
                owner_id=h["a_id"],
                id=str(uuid4()),
                scope_id=sid,
                epoch=0,
                revision=1,
                field="permissions",
                value="admin",
                status="pending",
                expires_at=1,
            )
        )


def test_cited_continuity_response_card_freezes_after_reset(harness):
    from ada.providers import Completion

    h = harness
    sid, original, body, service, _ = prepared(h)
    enqueue(h, sid, body)
    assert service.run_once()
    _, pid = make_conversation(h)
    cid = (
        h["client"]
        .post("/v1/conversations", headers=h["a"], json={"personality_id": pid, "scope_id": sid})
        .json()["id"]
    )
    config(h, sid, continuity=True)

    def complete(messages):
        assert h["sessions"].kw["bind"].pool.checkedout() == 0
        return Completion("Recorded context [C1].", "test-v1")

    h["provider"].complete = complete
    reply = send(h, cid, "Mira tea discussion?")
    assert reply.status_code == 200, reply.text
    card = reply.json()["continuity_citations"][0]
    assert (
        card["evidence"]["quote"] == original["content"] and card["trust_class"] == "user_explicit"
    )
    config(h, sid, "off", 1)
    assert send(h, cid, "Mira tea discussion?", reply.json()["request_id"]).json() == reply.json()
