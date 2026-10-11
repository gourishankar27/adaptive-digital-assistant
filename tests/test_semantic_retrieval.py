from uuid import uuid4

import pytest
from conftest import make_conversation, send
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from test_memory import add, correct, note

from ada.embedding_models import EmbeddingEntry
from ada.embeddings import EmbeddingError
from ada.models import Claim, SourceVersion
from ada.providers import Completion, ProviderError


class SyntheticEmbeddingProvider:
    """Explicit fixture: hand-built concepts test plumbing, never model quality."""

    def __init__(self, h):
        self.h, self.calls, self.error, self.hook = h, [], None, None

    def embed(self, texts, *, query=False):
        assert self.h["sessions"].kw["bind"].pool.checkedout() == 0
        # Concurrent source writes must be possible: caller holds no DB locks.
        with self.h["sessions"]() as db:
            assert db.scalar(select(Claim.id).limit(1)) is not None
        self.calls.append((texts, query))
        if self.hook:
            hook, self.hook = self.hook, None
            hook()
        if self.error:
            raise EmbeddingError(self.error)
        return [
            [
                float(any(word in t.lower() for word in ("train", "rail"))),
                float(any(word in t.lower() for word in ("bike", "cycle"))),
                1.0,
            ]
            for t in texts
        ]


def setup(h):
    conv, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]
    claim = add(
        h,
        scope,
        note(h, scope, "Synthetic Mira travels by train."),
        subject="Mira",
        predicate="commute",
        value="train",
    ).json()
    service = h["app"].state.chat.semantic
    service.settings.embedding_enabled = True
    service.settings.embedding_digest = "a" * 64
    service.settings.embedding_dimensions = 3
    # Fixture identity is intentionally distinct from the production model.
    service.namespace = "b" * 64
    service.settings.embedding_min_similarity = 0.9
    service.provider = SyntheticEmbeddingProvider(h)
    return conv, scope, claim, service


def rebuild(h, scope):
    return h["client"].post(f"/v1/scopes/{scope}/semantic-index/rebuild", headers=h["a"])


def query(h, scope, **changes):
    return h["client"].post(
        f"/v1/scopes/{scope}/retrieve",
        headers=h["a"],
        json={"query": "rail journey", "budget_bytes": 12000} | changes,
    )


def test_disabled_semantics_preserves_lexical_and_reports_fallback(harness):
    h = harness
    conv, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]
    evidence = note(h, scope, "Synthetic Atlas database is PostgreSQL.")
    claim = add(
        h, scope, evidence, subject="Atlas", predicate="database", value="PostgreSQL"
    ).json()
    result = (
        h["client"]
        .post(f"/v1/scopes/{scope}/retrieve", headers=h["a"], json={"query": "Atlas database"})
        .json()
    )
    assert result["selected"][0]["claim_id"] == claim["id"]
    assert result["plan"]["semantic"]["state"] == "disabled"
    assert not any("semantic" in c["channels"] for c in result["candidates"])
    saved = send(h, conv, "Atlas database", str(uuid4())).json()
    assert (
        send(h, conv, "Atlas database", saved["request_id"]).json()["response"] == saved["response"]
    )
    assert (
        h["client"].post(f"/v1/scopes/{scope}/semantic-index/rebuild", headers=h["b"]).status_code
        == 404
    )
    assert (
        h["client"].post(f"/v1/scopes/{scope}/semantic-index/rebuild", headers=h["a"]).status_code
        == 503
    )
    assert h["client"].post(f"/v1/scopes/{scope}/semantic-index/rebuild").status_code == 401


def test_exact_semantic_index_reuse_paraphrase_and_stale_hash(harness):
    h = harness
    _, scope, claim, service = setup(h)
    assert rebuild(h, scope).json()["indexed"] == 1
    assert rebuild(h, scope).json()["reused"] == 1
    result = query(h, scope).json()
    assert result["selected"][0]["claim_id"] == claim["id"]
    assert result["candidates"][0]["channels"] == ["semantic"]
    assert result["candidates"][0]["semantic_similarity"] == 1.0
    assert result["plan"]["semantic"]["state"] == "available"
    with h["sessions"].begin() as db:
        db.get(SourceVersion, claim["evidence"]["source_version_id"]).content += " changed"
    assert not query(h, scope).json()["selected"]
    assert rebuild(h, scope).json()["indexed"] == 0


def test_partial_rebuild_timeout_invalid_vectors_and_drift_preserve_lexical(harness):
    h = harness
    _, scope, claim, service = setup(h)
    assert rebuild(h, scope).status_code == 200
    service.provider.error = "embedding_timeout"
    result = query(h, scope, query="Mira commute").json()
    assert result["plan"]["semantic"]["reason"] == "embedding_timeout"
    assert result["selected"][0]["claim_id"] == claim["id"]
    assert rebuild(h, scope).json()["reused"] == 1  # no new calls for unchanged vectors
    for i in range(9):
        add(
            h,
            scope,
            note(h, scope, f"Synthetic bike note {i}."),
            subject=f"Rider{i}",
            predicate="commute",
            value="bike",
        )
    service.provider.error = None
    original = service.provider.embed
    batches = []

    def partial(texts, *, query=False):
        batches.append(len(texts))
        if len(batches) == 2:
            raise EmbeddingError("embedding_timeout")
        return original(texts, query=query)

    service.provider.embed = partial
    assert rebuild(h, scope).status_code == 503
    assert batches == [8, 1]
    service.provider.embed = original
    with h["sessions"]() as db:
        assert len(db.scalars(select(EmbeddingEntry)).all()) == 1
    service.provider.error = None
    result = query(h, scope).json()
    assert result["plan"]["semantic"]["reason"] == "index_incomplete_or_stale"
    assert all("semantic" not in c["channels"] for c in result["candidates"])
    service.settings.embedding_dimensions = 4
    assert query(h, scope).json()["plan"]["semantic"]["reason"] == "embedding_dimension_changed"


def test_failed_retry_and_completed_replay_never_reembed(harness):
    h = harness
    conv, scope, claim, service = setup(h)
    assert rebuild(h, scope).status_code == 200
    h["provider"].error = ProviderError("provider_timeout")
    rid = str(uuid4())
    assert send(h, conv, "rail journey", rid).status_code == 502
    frozen = h["client"].get(f"/v1/requests/{rid}/retrieval", headers=h["a"]).json()
    calls = len(service.provider.calls)
    service.provider.error = "embedding_model_changed"
    h["provider"].error = None
    assert send(h, conv, "rail journey", rid).status_code == 200
    assert send(h, conv, "rail journey", rid).status_code == 200
    assert len(service.provider.calls) == calls
    assert h["client"].get(f"/v1/requests/{rid}/retrieval", headers=h["a"]).json() == frozen


def test_foreign_reference_rejected_and_rebuild_correction_race(harness):
    h = harness
    _, scope, claim, service = setup(h)
    assert rebuild(h, scope).status_code == 200
    foreign = h["client"].post("/v1/scopes", headers=h["a"], json={"name": "Foreign"}).json()["id"]
    with h["sessions"]() as db:
        saved = db.scalars(select(EmbeddingEntry)).first()
        fields = {c.name: getattr(saved, c.name) for c in EmbeddingEntry.__table__.columns}
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(EmbeddingEntry(**(fields | {"scope_id": foreign})))
    # A real write during provider execution changes the snapshot. All vectors
    # computed so far remain unpublished; old complete namespace stays intact.
    add(
        h,
        scope,
        note(h, scope, "Synthetic bike addition."),
        subject="B",
        predicate="commute",
        value="bike",
    )
    service.provider.hook = lambda: correct(
        h, claim, note(h, scope, "Synthetic Mira now travels by bike."), value="bike"
    )
    assert rebuild(h, scope).status_code == 409
    with h["sessions"]() as db:
        assert len(db.scalars(select(EmbeddingEntry)).all()) == 1


def test_shared_generation_capacity_rebuild_and_query_fallback(harness):
    h = harness
    _, scope, claim, service = setup(h)
    semaphore = h["app"].state.chat.capacity
    assert semaphore.acquire(False) and semaphore.acquire(False)
    try:
        assert rebuild(h, scope).status_code == 503
        result = query(h, scope, query="Mira commute").json()
        assert result["plan"]["semantic"]["reason"] == "generation_capacity_busy"
        assert result["selected"][0]["claim_id"] == claim["id"]
    finally:
        semaphore.release()
        semaphore.release()


def test_oversized_scope_and_invalid_stored_vector_fail_closed(harness):
    from unittest.mock import patch

    h = harness
    _, scope, claim, service = setup(h)
    assert rebuild(h, scope).status_code == 200
    with h["sessions"].begin() as db:
        db.scalars(select(EmbeddingEntry)).first().vector = [0, 0, 0]
    assert query(h, scope).json()["plan"]["semantic"]["reason"] == "embedding_invalid_vector"
    assert rebuild(h, scope).json()["reused"] == 0
    add(
        h,
        scope,
        note(h, scope, "Synthetic extra bike."),
        subject="Extra",
        predicate="commute",
        value="bike",
    )
    with patch("ada.semantic.CORPUS_LIMIT", 1):
        result = query(h, scope, query="Mira commute").json()
        assert result["plan"]["semantic"]["reason"] == "scope_work_bound"
        assert result["selected"][0]["claim_id"] == claim["id"]
        assert rebuild(h, scope).status_code == 503


def test_no_embedding_for_foreign_scope_disabled_memory_or_unresolved_time(harness):
    h = harness
    conv, scope, _, service = setup(h)
    assert rebuild(h, scope).status_code == 200
    count = len(service.provider.calls)
    assert (
        h["client"]
        .post(f"/v1/scopes/{scope}/retrieve", headers=h["b"], json={"query": "rail"})
        .status_code
        == 404
    )
    assert (
        h["client"]
        .post(
            f"/v1/conversations/{conv}/messages",
            headers=h["a"],
            json={"request_id": str(uuid4()), "content": "rail", "use_memory": False},
        )
        .status_code
        == 200
    )
    assert (
        query(h, scope, query="What was my commute last year?").json()["plan"]["time_mode"]
        == "needs_date"
    )
    assert len(service.provider.calls) == count


def test_namespace_change_requires_rebuild_and_never_compares_old_vectors(harness):
    from ada.semantic import SemanticService

    h = harness
    _, scope, _, service = setup(h)
    assert rebuild(h, scope).status_code == 200
    changed = SemanticService(
        h["sessions"],
        service.settings.model_copy(update={"embedding_digest": "c" * 64}),
        service.capacity,
        service.provider,
    )
    assert changed.namespace != service.namespace
    from ada.retrieval import _base_query, plan_query

    plan = plan_query("rail journey")
    prepared = changed.prepare("rail journey")
    with h["sessions"].begin() as db:
        result = changed.rank(
            db, h["a_id"], scope, prepared, _base_query(h["a_id"], scope, plan["as_of"])
        )
        assert result["diagnostic"]["reason"] == "index_incomplete_or_stale"
        assert result["claim"] == []
    assert changed.rebuild(h["a_id"], scope)["reused"] == 0
    with h["sessions"]() as db:
        assert {e.namespace for e in db.scalars(select(EmbeddingEntry))} == {changed.namespace}


def test_semantic_claim_and_imported_citations_preserve_original_version_on_replay(harness):
    from test_document_retrieval import document

    h = harness
    conv, scope, claim, service = setup(h)
    imported = document(h, scope, "Synthetic train operations excerpt.")
    assert rebuild(h, scope).status_code == 200
    h["provider"].complete = lambda messages: Completion(
        "Synthetic reply [M1] [D1]", "test-v1", 10, 5
    )
    rid = str(uuid4())
    body = {"request_id": rid, "content": "rail journey", "use_documents": True}
    path = f"/v1/conversations/{conv}/messages"
    response = h["client"].post(path, headers=h["a"], json=body)
    assert response.status_code == 200
    original = response.json()
    assert original["citations"][0]["claim_id"] == claim["id"]
    card = original["document_citations"][0]
    assert card["source_version_id"] == imported["source_version_id"]
    assert card["trust_class"] == "imported_untrusted"
    assert card["evidence"]["quote"] == imported["text"]
    document(
        h,
        scope,
        "Synthetic bike replacement excerpt.",
        source_id=imported["source_id"],
        version=2,
        available=2,
    )
    assert rebuild(h, scope).status_code == 200
    service.provider.error = "embedding_timeout"
    replay = h["client"].post(path, headers=h["a"], json=body).json()
    assert replay | {"replayed": False} == original | {"replayed": False}
