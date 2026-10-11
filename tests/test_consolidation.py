"""Synthetic owned sources; no model output can endorse memory."""

import json
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from test_memory import note, scope
from test_proposals import pin

from ada.models import Claim, SourceVersion
from ada.providers import Completion, ProviderError


def prepared(h):
    s = scope(h)
    n = note(h, s, "Synthetic Mira discussed tea. 😀")

    class Summarizer:
        id, model = "fixture", "synthetic-summary-v1"
        calls = 0
        failure = None
        hook = None

        def complete(self, messages, schema):
            assert h["sessions"].kw["bind"].pool.checkedout() == 0
            self.calls += 1
            if self.hook:
                self.hook()
            if self.failure:
                raise self.failure
            return Completion(
                json.dumps(
                    {
                        "sections": [{"text": "Mira discussed tea.", "support": [pin(n)]}],
                        "tags": ["discussion"],
                        "omissions": ["Emoji omitted."],
                    }
                ),
                self.model,
            )

    provider = Summarizer()
    service = h["app"].state.consolidation
    service.provider = provider
    body = {"job_id": str(uuid4()), "kind": "episode", "sources": [pin(n)]}
    return s, n, body, service, provider


def enqueue(h, s, body, who="a"):
    return h["client"].post(f"/v1/scopes/{s}/consolidation-jobs", headers=h[who], json=body)


def job(h, key, who="a"):
    return h["client"].get(f"/v1/consolidation-jobs/{key}", headers=h[who])


def test_queue_replay_key_mismatch_dedup_and_owner_scope(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    first = enqueue(h, s, body)
    assert first.status_code == 201, first.text
    assert first.json()["status"] == "queued" and provider.calls == 0
    assert first.headers["cache-control"] == "no-store"
    assert enqueue(h, s, body).json() == first.json()
    assert enqueue(h, s, body | {"kind": "proposals"}).status_code == 409
    assert enqueue(h, s, body | {"job_id": str(uuid4())}).status_code == 409
    assert enqueue(h, s, body, "b").status_code == 404
    assert job(h, body["job_id"], "b").status_code == 404
    other = scope(h, name="Other")
    assert enqueue(h, other, body | {"job_id": str(uuid4())}).status_code == 404
    assert h["client"].get(f"/v1/consolidation-jobs/{body['job_id']}").status_code == 401


def test_generated_episode_exact_mapping_no_claims_and_frozen_context(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    assert enqueue(h, s, body).status_code == 201
    assert service.run_once()
    done = job(h, body["job_id"]).json()
    assert done["status"] == "completed" and done["checkpoint"] == "published"
    assert done["attempt"] == 1 and done["receipt"]["outcome"] == "completed"
    assert done["elapsed_ms"] >= 0 and done["finished_at"] >= done["started_at"]
    key = done["receipt"]["episode_id"]
    episode = h["client"].get(f"/v1/episodes/{key}", headers=h["a"]).json()
    assert episode["trust_class"] == "model_generated"
    assert episode["sections"][0]["support"][0] == pin(n)
    assert episode["sources"][0]["evidence"]["quote"] == n["content"]
    assert episode["sources"][0]["trust_class"] == "user_explicit"
    assert h["client"].get(f"/v1/episodes/{key}", headers=h["b"]).status_code == 404
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0
    context = {"request_id": str(uuid4()), "episode_ids": [key]}
    path = f"/v1/scopes/{s}/episode-contexts"
    frozen = h["client"].post(path, json=context, headers=h["a"])
    assert frozen.status_code == 201, frozen.text
    with h["sessions"].begin() as db:
        db.get(SourceVersion, n["id"]).content = "Synthetic changed input"
    assert h["client"].post(path, json=context, headers=h["a"]).json() == frozen.json()
    assert (
        h["client"]
        .post(path, json=context | {"request_id": str(uuid4())}, headers=h["a"])
        .status_code
        == 409
    )
    assert enqueue(h, s, body).json() == done and provider.calls == 1


@pytest.mark.parametrize(
    "failure", [ProviderError("provider_timeout"), RuntimeError("private-input")]
)
def test_model_failure_unpublished_and_capacity_released(harness, failure):
    h = harness
    s, n, body, service, provider = prepared(h)
    provider.failure = failure
    assert enqueue(h, s, body).status_code == 201
    assert service.run_once()
    result = job(h, body["job_id"])
    assert result.json()["status"] == "failed" and "private-input" not in result.text
    assert result.json()["receipt"]["episode_id"] is None
    assert h["client"].get(f"/v1/scopes/{s}/episodes", headers=h["a"]).json() == []
    assert service.capacity.acquire(blocking=False)
    service.capacity.release()


def test_capacity_leaves_queued_without_attempt_or_inference(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    assert enqueue(h, s, body).status_code == 201
    assert service.capacity.acquire(blocking=False) and service.capacity.acquire(blocking=False)
    try:
        assert not service.run_once()
        value = job(h, body["job_id"]).json()
        assert value["status"] == "queued" and value["attempt"] == 0 and provider.calls == 0
    finally:
        service.capacity.release()
        service.capacity.release()


def test_source_hash_change_during_model_is_stale_not_published(harness):
    h = harness
    s, n, body, service, provider = prepared(h)

    def change():
        with h["sessions"].begin() as db:
            db.get(SourceVersion, n["id"]).content = "Changed synthetic source"

    provider.hook = change
    assert enqueue(h, s, body).status_code == 201
    assert service.run_once()
    value = job(h, body["job_id"]).json()
    assert value["status"] == "stale" and value["receipt"]["episode_id"] is None
    assert h["client"].get(f"/v1/scopes/{s}/episodes", headers=h["a"]).json() == []
