"""Explicit work commitments are private, revisioned and never inferred facts."""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from conftest import make_conversation, send
from sqlalchemy import func, select

from ada.models import Claim


def setup(h):
    cid, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    return cid, scope


def body(**changes):
    return {
        "operation_id": str(uuid4()),
        "expected_revision": 0,
        "review": "confirm",
        "fields": {
            "kind": "task",
            "description": "Review the public test project",
            "status": "planned",
        },
        **changes,
    }


def save(h, scope, key, value, who="a"):
    p = h["client"].post(f"/v1/scopes/{scope}/work/{key}/preview", headers=h[who], json=value)
    assert p.status_code == 200
    value["preview_hash"] = p.json()["preview_hash"]
    return h["client"].post(f"/v1/scopes/{scope}/work/{key}", headers=h[who], json=value)


def test_explicit_preview_revision_receipt_duplicate_and_old_chat_are_distinct(harness):
    h = harness
    cid, scope = setup(h)
    old_id = str(uuid4())
    old = send(h, cid, "Public work migration snapshot.", old_id).json()
    key, value = str(uuid4()), body()
    r = save(h, scope, key, value)
    assert r.status_code == 200 and r.json()["revision"] == 1
    assert (
        h["client"].post(f"/v1/scopes/{scope}/work/{key}", headers=h["a"], json=value).json()
        == r.json()
    )
    assert (
        h["client"].get(f"/v1/work/receipts/{value['operation_id']}", headers=h["a"]).json()
        == r.json()
    )
    value2 = body(expected_revision=1, fields=value["fields"] | {"status": "done"})
    assert save(h, scope, key, value2).json()["revision"] == 2
    history = h["client"].get(f"/v1/work/{key}/history", headers=h["a"]).json()
    assert [x["fields"]["status"] for x in history] == ["planned", "done"]
    assert send(h, cid, "Public work migration snapshot.", old_id).json() == old
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


def test_private_scope_parent_preview_tampering_and_no_implicit_post(harness):
    h = harness
    _, scope = setup(h)
    key, value = str(uuid4()), body()
    assert (
        h["client"]
        .post(f"/v1/scopes/{scope}/work/{key}/preview", headers=h["b"], json=value)
        .status_code
        == 404
    )
    assert (
        h["client"].post(f"/v1/scopes/{scope}/work/{key}", headers=h["a"], json=value).status_code
        == 409
    )
    assert save(h, scope, key, value).status_code == 200
    assert h["client"].get(f"/v1/work/{key}", headers=h["b"]).status_code == 404
    altered = value | {"fields": value["fields"] | {"status": "done"}}
    assert (
        h["client"].post(f"/v1/scopes/{scope}/work/{key}", headers=h["a"], json=altered).status_code
        == 409
    )
    assert h["client"].get(f"/v1/scopes/{scope}/work").status_code == 401
    bad = body(fields=value["fields"] | {"goal_id": str(uuid4())})
    assert (
        h["client"]
        .post(f"/v1/scopes/{scope}/work/{uuid4()}/preview", headers=h["a"], json=bad)
        .status_code
        == 404
    )


@pytest.mark.parametrize(
    "extra",
    [
        {"due_local": "2026-11-01T01:30", "timezone": "America/New_York"},
        {"due_local": "2027-03-14T02:30", "timezone": "America/New_York"},
        {"due_local": "2027-01-02T09:00"},
        {"due_local": "tomorrow", "timezone": "UTC"},
        {"status": "completed_by_model"},
    ],
)
def test_ambiguous_missing_or_invented_time_status_never_saves(harness, extra):
    h = harness
    _, scope = setup(h)
    value = body(fields=body()["fields"] | extra)
    r = h["client"].post(f"/v1/scopes/{scope}/work/{uuid4()}/preview", headers=h["a"], json=value)
    assert r.status_code == 422


def test_past_due_unknown_and_dated_brief_preserve_status_and_source_trust(harness):
    h = harness
    cid, scope = setup(h)
    reply = send(h, cid, "Public source fixture.").json()
    events = h["client"].get(f"/v1/conversations/{cid}/events", headers=h["a"]).json()
    model = next(x for x in events if x["role"] == "assistant")
    source = (
        h["client"].get(f"/v1/source-versions/{model['source_version_id']}", headers=h["a"]).json()
    )
    pin = {
        "source_version_id": source["id"],
        "version": source["version"],
        "content_hash": source["content_hash"],
        "span_start": 0,
        "span_end": len(source["content"]),
    }
    key = str(uuid4())
    value = body(
        fields=body()["fields"]
        | {
            "due_local": "2026-01-01T09:00",
            "timezone": "UTC",
            "pins": [pin],
            "origin_request_id": reply["request_id"],
        }
    )
    assert save(h, scope, key, value).status_code == 200
    row = h["client"].get(f"/v1/work/{key}", headers=h["a"]).json()
    assert row["fields"]["status"] == "planned" and row["overdue"]
    assert row["origin_conversation_id"] == cid
    assert (
        row["provenance"] == "owner_reviewed_suggestion"
        and row["sources"][0]["trust_class"] == "model_generated"
    )
    brief = {
        "operation_id": str(uuid4()),
        "scope_ids": [scope],
        "item_ids": [key],
        "day": "2026-10-22",
        "timezone": "America/Phoenix",
    }
    r = h["client"].post("/v1/work/briefs", headers=h["a"], json=brief)
    assert r.status_code == 200
    result = r.json()
    assert result["items"][0]["label"] == "T1" and result["items"][0]["overdue"]
    assert (
        result["factual_evidence"] is False
        and result["generated_by"] == "deterministic_task_projection"
    )
    assert reply["status"] == "completed"


def test_concurrent_revision_edits_have_one_winner(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Native row locks")
    _, scope = setup(h)
    key = str(uuid4())
    value = body()
    assert save(h, scope, key, value).status_code == 200
    changes = [
        body(expected_revision=1, fields=value["fields"] | {"status": s})
        for s in ["done", "deferred"]
    ]
    for change in changes:
        change["preview_hash"] = (
            h["client"]
            .post(f"/v1/scopes/{scope}/work/{key}/preview", headers=h["a"], json=change)
            .json()["preview_hash"]
        )

    def post(v):
        return (
            h["client"].post(f"/v1/scopes/{scope}/work/{key}", headers=h["a"], json=v).status_code
        )

    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(post, changes)) == [200, 409]
