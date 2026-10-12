"""Consent/review boundaries before expanding the interaction write path."""

from uuid import uuid4

from conftest import make_conversation, send
from sqlalchemy import select

from ada.models import Conversation, Event, Source, SourceVersion


def scope_of(h, cid):
    with h["sessions"]() as db:
        return db.get(Conversation, cid).scope_id


def config(h, scope, status="enrolled", revision=0, continuity=False):
    return h["client"].post(
        f"/v1/scopes/{scope}/learning/config",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_revision": revision,
            "status": status,
            "continuity_enabled": continuity,
        },
    )


def observation(h, cid, text, confidence="repeated_observation", value="concise"):
    reply = send(h, cid, text)
    assert reply.status_code == 200, reply.text
    with h["sessions"]() as db:
        row = db.scalar(
            select(SourceVersion)
            .join(Source, Source.id == SourceVersion.source_id)
            .join(Event, Event.id == Source.event_id)
            .where(Event.request_id == reply.json()["request_id"], Event.role == "user")
        )
        pin = {
            "source_version_id": row.id,
            "version": row.version,
            "content_hash": row.content_hash,
            "span_start": 0,
            "span_end": len(row.content),
        }
    body = {
        "operation_id": str(uuid4()),
        "source": pin,
        "values": {"verbosity": value},
        "confidence_class": confidence,
    }
    response = h["client"].post(
        f"/v1/scopes/{scope_of(h, cid)}/learning/observations", headers=h["a"], json=body
    )
    return response, body


def inbox(h, scope):
    r = h["client"].get(f"/v1/scopes/{scope}/learning", headers=h["a"])
    assert r.status_code == 200, r.text
    return r.json()


def review(h, scope, proposal, **extra):
    body = {
        "operation_id": str(uuid4()),
        "proposal_id": proposal["id"],
        "expected_revision": proposal["revision"],
        "decision": "approve",
        "account_wide": False,
        "reviewed": True,
        **extra,
    }
    return h["client"].post(f"/v1/scopes/{scope}/learning/reviews", headers=h["a"], json=body), body


def test_consent_off_has_no_learning_and_owner_boundary(harness):
    h = harness
    cid, _ = make_conversation(h)
    sid = scope_of(h, cid)
    r, _ = observation(h, cid, "Please keep this explanation concise.")
    assert r.status_code == 409
    assert inbox(h, sid)["observations"] == []
    assert h["client"].get(f"/v1/scopes/{sid}/learning", headers=h["b"]).status_code == 404
    assert h["client"].get(f"/v1/scopes/{sid}/learning").status_code == 401
    reply = send(h, cid)
    snapshot = h["client"].get(
        f"/v1/requests/{reply.json()['request_id']}/learning", headers=h["a"]
    )
    assert snapshot.json()["learning"] is None


def test_three_independent_interactions_review_override_pause_reset_replay(harness):
    h = harness
    cid, pid = make_conversation(h)
    sid = scope_of(h, cid)
    assert config(h, sid).status_code == 201
    for text in (
        "Short replies help with planning.",
        "I prefer concise explanations while coding.",
        "Keep this review brief and concise please.",
    ):
        r, _ = observation(h, cid, text)
        assert r.status_code == 201, r.text
    state = inbox(h, sid)
    p = state["proposals"][0]
    assert p["independent_count"] == 3 and p["eligible"]
    assert state["learned"] == []
    accepted, body = review(h, sid, p)
    assert accepted.status_code == 201, accepted.text
    assert (
        h["client"]
        .post(f"/v1/scopes/{sid}/learning/reviews", headers=h["a"], json=body)
        .status_code
        == 200
    )
    reply = send(h, cid, "Explain a fresh topic.")
    rid = reply.json()["request_id"]
    snapshot = h["client"].get(f"/v1/requests/{rid}/learning", headers=h["a"]).json()["learning"]
    assert {k: v for k, v in snapshot["preferences"].items() if v is not None} == {
        "verbosity": "concise"
    }
    setting = {
        "operation_id": str(uuid4()),
        "expected_revision": 0,
        "values": {"verbosity": "detailed"},
    }
    assert (
        h["client"]
        .post(f"/v1/preferences/conversation/{cid}", headers=h["a"], json=setting)
        .status_code
        == 201
    )
    newer = send(h, cid, "Explain another topic.")
    snap = (
        h["client"]
        .get(f"/v1/requests/{newer.json()['request_id']}/learning", headers=h["a"])
        .json()["learning"]
    )
    assert not any(snap["preferences"].values())
    assert config(h, sid, "paused", 1).status_code == 201
    assert send(h, cid, "Explain a fresh topic.", rid).json() == reply.json()
    assert config(h, sid, "off", 2).status_code == 201
    state = inbox(h, sid)
    assert state["learned"] == state["proposals"] == state["observations"] == []
    assert send(h, cid, "Explain a fresh topic.", rid).json() == reply.json()
    assert (
        h["client"]
        .post(f"/v1/scopes/{sid}/learning/reviews", headers=h["a"], json=body)
        .status_code
        == 200
    )
    assert inbox(h, sid)["learned"] == []


def test_duplicates_single_event_weak_and_stale_never_promote(harness):
    h = harness
    cid, _ = make_conversation(h)
    sid = scope_of(h, cid)
    config(h, sid)
    r, body = observation(h, cid, "Please keep it concise.")
    assert r.status_code == 201
    assert (
        h["client"]
        .post(f"/v1/scopes/{sid}/learning/observations", headers=h["a"], json=body)
        .status_code
        == 200
    )
    body["operation_id"] = str(uuid4())
    assert (
        h["client"]
        .post(f"/v1/scopes/{sid}/learning/observations", headers=h["a"], json=body)
        .status_code
        == 409
    )
    observation(h, cid, "Please keep it concise.")
    p = inbox(h, sid)["proposals"][0]
    assert p["independent_count"] == 1
    assert review(h, sid, p)[0].status_code == 409
    observation(h, cid, "Different weak inference.", "weak_inference")
    assert review(h, sid, p)[0].status_code == 409
    assert inbox(h, sid)["learned"] == []


def test_forged_values_review_and_cross_scope_sources_rejected(harness):
    h = harness
    cid, _ = make_conversation(h)
    sid = scope_of(h, cid)
    config(h, sid)
    r, body = observation(h, cid, "Use shorter replies.")
    body["operation_id"] = str(uuid4())
    body["values"] = {"permissions": "admin"}
    assert (
        h["client"]
        .post(f"/v1/scopes/{sid}/learning/observations", headers=h["a"], json=body)
        .status_code
        == 422
    )
    body["values"] = {"verbosity": "concise"}
    other = h["client"].post("/v1/scopes", headers=h["a"], json={"name": "Other"}).json()["id"]
    config(h, other)
    assert (
        h["client"]
        .post(f"/v1/scopes/{other}/learning/observations", headers=h["a"], json=body)
        .status_code
        == 404
    )
    p = inbox(h, sid)["proposals"][0]
    assert review(h, sid, p, reviewed=1)[0].status_code == 422
