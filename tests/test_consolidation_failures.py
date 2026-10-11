import json
from uuid import uuid4

import pytest
from conftest import make_conversation, send
from sqlalchemy import func, select
from test_consolidation import enqueue, job, prepared
from test_document_api import upload
from test_memory import note, scope
from test_proposals import pin, review, review_body

from ada.admin import set_admin_grant
from ada.consolidation import VERSION
from ada.consolidation_models import Episode
from ada.models import Claim, SourceVersion
from ada.proposal_models import MemoryExtraction, MemoryProposal
from ada.providers import Completion


def test_evidence_byte_bound_rejects_without_reserving_or_inferencing(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    selected = [note(h, s, "😀" * 751), note(h, s, "😀" * 751)]
    response = enqueue(h, s, body | {"sources": [pin(item) for item in selected]})
    assert response.status_code == 413
    assert job(h, body["job_id"]).status_code == 404 and provider.calls == 0
    assert h["client"].get(f"/v1/scopes/{s}/episodes", headers=h["a"]).json() == []


def test_whole_context_bound_fails_without_truncation_or_model_call(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    selected = note(h, s, "😀" * 1500)
    assert enqueue(h, s, body | {"sources": [pin(selected)]}).status_code == 201
    assert service.run_once()
    failed = job(h, body["job_id"]).json()
    assert failed["status"] == "failed" and failed["error_code"] == "consolidation_context_bound"
    assert provider.calls == 0
    assert h["client"].get(f"/v1/scopes/{s}/episodes", headers=h["a"]).json() == []
    assert enqueue(h, s, body | {"sources": [pin(selected)]}).json() == failed


def test_invalid_inferred_interval_leaves_no_partial_proposal_batch(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    good = {
        "subject": "Mira",
        "predicate": "topic",
        "value": "tea",
        "kind": "fact",
        "support": [pin(n)],
    }
    bad = good | {"predicate": "dated", "valid_to": "2000-01-01T00:00:00Z"}
    provider.complete = lambda *_: Completion(
        json.dumps({"candidates": [good, bad]}), provider.model
    )
    assert enqueue(h, s, body | {"kind": "proposals"}).status_code == 201
    assert service.run_once()
    assert job(h, body["job_id"]).json()["status"] == "failed"
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(MemoryExtraction)) == 0
        assert db.scalar(select(func.count()).select_from(MemoryProposal)) == 0


@pytest.mark.parametrize(
    "invalid",
    [
        "foreign_pin",
        "span",
        "duplicate",
        "nonfinite",
        "entity",
        "oversize",
        "wrong_model",
        "unicode_tag",
    ],
)
def test_invalid_generated_mapping_or_model_never_publishes(harness, invalid):
    h = harness
    s, n, body, service, provider = prepared(h)
    original = provider.complete

    def complete(messages, schema):
        result = original(messages, schema)
        raw = json.loads(result.text)
        support = raw["sections"][0]["support"][0]
        if invalid == "foreign_pin":
            support["source_version_id"] = str(uuid4())
        elif invalid == "span":
            support["span_end"] += 1
        elif invalid == "entity":
            raw["owner_id"] = h["a_id"]
        elif invalid == "unicode_tag":
            raw["tags"] = ["\ud800"]
        text = json.dumps(raw)
        if invalid == "duplicate":
            text = text[:-1] + ', "tags": []}'
        elif invalid == "nonfinite":
            text = text.replace('"tags": ["discussion"]', '"tags": [NaN]')
        elif invalid == "oversize":
            text = "x" * 16385
        return Completion(text, "another-model" if invalid == "wrong_model" else provider.model)

    provider.complete = complete
    enqueue(h, s, body)
    assert service.run_once()
    result = job(h, body["job_id"]).json()
    assert result["status"] == "failed" and result["receipt"]["episode_id"] is None
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Episode)) == 0


def test_proposal_job_never_endorses_until_existing_explicit_review(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    candidate = {
        "subject": "Mira",
        "predicate": "topic",
        "value": "tea",
        "kind": "fact",
        "support": [pin(n)],
    }
    provider.complete = lambda *_: Completion(
        json.dumps({"candidates": [candidate]}), provider.model
    )
    body = body | {"kind": "proposals"}
    assert enqueue(h, s, body).status_code == 201 and service.run_once()
    receipt = job(h, body["job_id"]).json()["receipt"]
    assert receipt["outcome"] == "completed" and len(receipt["proposal_ids"]) == 1
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0
    p = h["client"].get(f"/v1/memory-proposals/{receipt['proposal_ids'][0]}", headers=h["a"]).json()
    assert p["status"] == "pending" and p["support"][0]["trust_class"] == "user_explicit"
    accepted = review(h, p["id"], review_body(p))
    assert accepted.status_code == 201, accepted.text
    assert job(h, body["job_id"]).json()["receipt"] == receipt


def test_cross_conversation_same_scope_input_preserves_event_and_model_trust(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    conv, profile = make_conversation(h)
    s = h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]
    second = (
        h["client"]
        .post("/v1/conversations", headers=h["a"], json={"personality_id": profile, "scope_id": s})
        .json()["id"]
    )
    saved = send(h, conv).json()
    send(h, second)
    inputs = []
    for c in (conv, second):
        events = h["client"].get(f"/v1/conversations/{c}/events", headers=h["a"]).json()
        source = (
            h["client"]
            .get(f"/v1/source-versions/{events[-1]['source_version_id']}", headers=h["a"])
            .json()
        )
        inputs.append(pin(source))
    provider.complete = lambda *_: Completion(
        json.dumps(
            {
                "sections": [{"text": "Generated replies were recorded.", "support": inputs}],
                "tags": [],
                "omissions": [],
            }
        ),
        provider.model,
    )
    body = body | {"sources": inputs}
    assert enqueue(h, s, body).status_code == 201 and service.run_once()
    ep = service.episode(h["a_id"], job(h, body["job_id"]).json()["receipt"]["episode_id"])
    assert {r["conversation_id"] for r in ep["sources"]} == {conv, second}
    assert all(r["event_id"] and r["trust_class"] == "model_generated" for r in ep["sources"])
    assert send(h, conv, request_id=saved["request_id"]).json() == saved
    assert h["provider"].calls[-1][-1]["content"] == "hello"  # Episodes never enter factual chat.


def test_policy_drift_source_change_and_future_document_are_stale_or_rejected(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    provider.model = "changed-policy-model"
    assert service.run_once()
    assert job(h, body["job_id"]).json()["status"] == "stale" and provider.calls == 0
    provider.model = "synthetic-summary-v1"
    doc = upload(h, s, b"Synthetic future document", available_from="2100-01-01T00:00:00Z").json()
    with h["sessions"]() as db:
        version = db.get(SourceVersion, doc["source_version_id"])
        v = {
            "id": version.id,
            "version": version.version,
            "content_hash": version.content_hash,
            "content": version.content,
        }
    assert enqueue(h, s, body | {"job_id": str(uuid4()), "sources": [pin(v)]}).status_code == 409
    other = scope(h, who="b")
    v = note(h, other, who="b")
    assert enqueue(h, s, body | {"job_id": str(uuid4()), "sources": [pin(v)]}).status_code == 404


def test_admin_allowlist_counts_times_no_private_inputs_and_no_episode_access(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    service.run_once()
    set_admin_grant(h["sessions"], h["b_id"], True)
    data = h["client"].get("/v1/admin/overview", headers=h["b"]).json()
    assert data["consolidation_job_counts"] == {
        "queued": 0,
        "running": 0,
        "completed": 1,
        "failed": 0,
        "stale": 0,
    }
    rows = data["consolidation_jobs"]
    assert len(rows) == 1 and rows[0]["elapsed_ms"] >= 0
    assert set(rows[0]) == {
        "id",
        "owner_id",
        "scope_id",
        "kind",
        "status",
        "checkpoint",
        "version",
        "attempt",
        "created_at",
        "started_at",
        "finished_at",
        "elapsed_ms",
    }
    assert n["content"] not in json.dumps(data) and "Mira discussed tea" not in json.dumps(data)
    assert job(h, body["job_id"], "b").status_code == 404
    set_admin_grant(h["sessions"], h["b_id"], False)
    assert h["client"].get("/v1/admin/overview", headers=h["b"]).status_code == 403
    assert VERSION == rows[0]["version"]
