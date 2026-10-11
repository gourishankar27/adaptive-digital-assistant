import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from test_memory import add, note, scope

from ada.models import Claim, SourceVersion
from ada.proposal_models import MemoryProposal
from ada.providers import Completion


def pin(source):
    return {
        "source_version_id": source["id"],
        "content_hash": source["content_hash"],
        "span_start": 0,
        "span_end": len(source["content"]),
        "version": source["version"],
    }


def setup(h, text="Synthetic Mira prefers tea. 😀", **fields):
    s = scope(h)
    n = note(h, s, text)
    candidate = {
        "subject": "Mira",
        "predicate": "drink",
        "value": "tea",
        "kind": "preference",
        "valid_from": None,
        "valid_to": None,
        "support": [pin(n)],
        "confidence": 0.9,
    } | fields

    class Extractor:
        model = "synthetic-extractor-v1"
        id = "fixture"
        calls = 0

        def complete(self, messages):
            assert h["sessions"].kw["bind"].pool.checkedout() == 0
            self.calls += 1
            return Completion(json.dumps({"candidates": [candidate]}), self.model)

    extractor = Extractor()
    h["app"].state.proposals.provider = extractor
    body = {"extraction_id": str(uuid4()), "sources": [pin(n)]}
    return s, n, candidate, body, extractor


def extract(h, s, body, who="a"):
    return h["client"].post(f"/v1/scopes/{s}/memory-extractions", headers=h[who], json=body)


def detail(h, p):
    return h["client"].get(f"/v1/memory-proposals/{p}", headers=h["a"])


def review_body(p, **changes):
    return {
        "review_id": str(uuid4()),
        "revision": p["revision"],
        "review_hash": p["review_hash"],
        "decision": "accept",
        "annotation": "I explicitly endorse this synthetic memory.",
        "candidate": p["candidate"],
        "replace_claim_id": None,
    } | changes


def review(h, p, body, who="a"):
    return h["client"].post(f"/v1/memory-proposals/{p}/review", headers=h[who], json=body)


def test_unreviewed_proposal_is_not_memory_and_approval_is_atomic_exact_replay(harness):
    h = harness
    s, n, _, body, provider = setup(h)
    result = extract(h, s, body)
    assert result.status_code == 201, result.text
    p = detail(h, result.json()["proposal_ids"][0]).json()
    assert p["status"] == "pending" and p["support"][0]["evidence"]["quote"] == n["content"]
    assert h["client"].get(f"/v1/scopes/{s}/claims", headers=h["a"]).json() == []
    assert extract(h, s, body).json() == result.json() and provider.calls == 1
    reviewed = review_body(p)
    receipt = review(h, p["id"], reviewed)
    assert receipt.status_code == 201, receipt.text
    assert review(h, p["id"], reviewed).status_code == 200
    assert review(h, p["id"], reviewed).json() == receipt.json()
    claim = h["client"].get(f"/v1/claims/{receipt.json()['claim_id']}", headers=h["a"]).json()
    assert claim["provenance"]["origin"] == "user_reviewed"
    assert claim["evidence"]["source_version_id"] != n["id"]
    assert claim["provenance"]["support"][0]["evidence"]["quote"] == n["content"]
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 1
        assert db.get(SourceVersion, n["id"]).trust_class == "user_explicit"
    assert review(h, p["id"], reviewed | {"annotation": "Changed"}).status_code == 409
    assert review(h, p["id"], reviewed | {"review_id": str(uuid4())}).status_code == 409


def test_review_keys_and_derived_ids_are_isolated_between_owners(harness):
    h = harness
    first_scope, _, candidate, body, _ = setup(h)
    first = detail(h, extract(h, first_scope, body).json()["proposal_ids"][0]).json()
    reviewed = review_body(first)
    first_receipt = review(h, first["id"], reviewed)
    assert first_receipt.status_code == 201
    second_scope = scope(h, "b")
    second_source = note(h, second_scope, "Synthetic second owner prefers tea.", who="b")
    second_candidate = candidate | {"support": [pin(second_source)]}

    class SecondOwnerExtractor:
        model = "synthetic-extractor-v1"

        def complete(self, messages):
            return Completion(json.dumps({"candidates": [second_candidate]}), self.model)

    h["app"].state.proposals.provider = SecondOwnerExtractor()
    second_body = body | {"sources": [pin(second_source)]}
    extracted = extract(h, second_scope, second_body, "b")
    assert extracted.status_code == 201
    second = (
        h["client"]
        .get(f"/v1/memory-proposals/{extracted.json()['proposal_ids'][0]}", headers=h["b"])
        .json()
    )
    second_review = review_body(second, review_id=reviewed["review_id"])
    second_receipt = review(h, second["id"], second_review, "b")
    assert second_receipt.status_code == 201, second_receipt.text
    assert first["id"] != second["id"]
    for field in ("claim_id", "endorsement_source_version_id", "principal_id"):
        assert first_receipt.json()[field] != second_receipt.json()[field]
    assert review(h, second["id"], second_review, "b").json() == second_receipt.json()
    assert review(h, first["id"], reviewed).json() == first_receipt.json()
    assert (
        h["client"]
        .get(f"/v1/claims/{first_receipt.json()['claim_id']}", headers=h["b"])
        .status_code
        == 404
    )


@pytest.mark.parametrize("mutation", ["unknown", "foreign", "hash", "span", "empty", "nonfinite"])
def test_malformed_or_fabricated_model_output_has_no_proposal_or_claim(harness, mutation):
    h = harness
    s, _, candidate, body, _ = setup(h)
    if mutation == "unknown":
        candidate["owner_id"] = h["b_id"]
    elif mutation == "foreign":
        candidate["support"][0]["source_version_id"] = note(h, scope(h, "b"), who="b")["id"]
    elif mutation == "hash":
        candidate["support"][0]["content_hash"] = "0" * 64
    elif mutation == "span":
        candidate["support"][0]["span_end"] += 1
    elif mutation == "empty":
        candidate["support"] = []
    else:
        candidate["confidence"] = float("nan")
    result = extract(h, s, body)
    assert result.status_code == 201, result.text
    assert result.json()["state"] == "failed" and result.json()["proposal_ids"] == []
    assert h["client"].get(f"/v1/scopes/{s}/claims", headers=h["a"]).json() == []
    assert extract(h, s, body).json() == result.json()


def test_review_revision_hash_identity_edit_and_rejection(harness):
    h = harness
    s, _, _, body, _ = setup(h)
    p = detail(h, extract(h, s, body).json()["proposal_ids"][0]).json()
    b = review_body(p)
    assert review(h, p["id"], b, "b").status_code == 404
    assert h["client"].post(f"/v1/memory-proposals/{p['id']}/review", json=b).status_code == 401
    assert review(h, p["id"], b | {"review_hash": "0" * 64}).status_code == 409
    changed = h["client"].post(
        f"/v1/memory-proposals/{p['id']}/edit",
        headers=h["a"],
        json={
            "revision": p["revision"],
            "review_hash": p["review_hash"],
            "candidate": p["candidate"] | {"value": "coffee"},
        },
    )
    assert changed.status_code == 200, changed.text
    assert review(h, p["id"], b).status_code == 409
    new = changed.json()
    rejected = review(h, p["id"], review_body(new, decision="reject", annotation="Not accurate."))
    assert rejected.status_code == 201 and rejected.json()["claim_id"] is None
    assert detail(h, p["id"]).json()["rejection_reason"] == "Not accurate."
    assert h["client"].get(f"/v1/scopes/{s}/claims", headers=h["a"]).json() == []


def test_stale_support_and_foreign_entity_cannot_be_endorsed(harness):
    h = harness
    s, n, _, body, _ = setup(h)
    p = detail(h, extract(h, s, body).json()["proposal_ids"][0]).json()
    b = review_body(p)
    assert (
        review(
            h, p["id"], b | {"candidate": b["candidate"] | {"subject_entity_id": str(uuid4())}}
        ).status_code
        == 404
    )
    with h["sessions"].begin() as db:
        db.get(SourceVersion, n["id"]).content = "Changed by trusted operator"
    assert review(h, p["id"], b).status_code == 409
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


def test_concurrent_review_has_one_winner_and_conflict_for_unseen_content(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("PostgreSQL row-lock concurrency")
    s, _, _, body, _ = setup(h)
    p = detail(h, extract(h, s, body).json()["proposal_ids"][0]).json()
    bodies = [review_body(p), review_body(p, annotation="A different explicit decision")]
    with ThreadPoolExecutor(2) as pool:
        responses = list(pool.map(lambda b: review(h, p["id"], b), bodies))
    assert sorted(r.status_code for r in responses) == [201, 409]
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 1


def test_concurrent_edit_and_review_cannot_endorse_an_unseen_revision(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("PostgreSQL row-lock concurrency")
    body_scope, _, _, body, _ = setup(h)
    proposal = detail(h, extract(h, body_scope, body).json()["proposal_ids"][0]).json()
    barrier = Barrier(2)

    def act(edit):
        barrier.wait(timeout=10)
        if edit:
            return h["client"].post(
                f"/v1/memory-proposals/{proposal['id']}/edit",
                headers=h["a"],
                json={
                    "revision": proposal["revision"],
                    "review_hash": proposal["review_hash"],
                    "candidate": proposal["candidate"] | {"value": "coffee"},
                },
            )
        return review(h, proposal["id"], review_body(proposal))

    with ThreadPoolExecutor(2) as pool:
        edited, approved = list(pool.map(act, [True, False]))
    assert [edited.status_code, approved.status_code] in ([200, 409], [409, 201])
    current = detail(h, proposal["id"]).json()
    claims = h["client"].get(f"/v1/scopes/{body_scope}/claims", headers=h["a"]).json()
    if edited.status_code == 200:
        assert current["revision"] == 2 and current["status"] == "pending" and claims == []
    else:
        assert current["revision"] == 1 and current["status"] == "accepted"
        assert len(claims) == 1 and claims[0]["value"] == "tea"


def test_concurrent_extractions_recheck_retained_quota_at_publication(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("PostgreSQL row-lock concurrency")
    s, _, candidate, body, _ = setup(h)
    original_id = extract(h, s, body).json()["proposal_ids"][0]
    with h["sessions"].begin() as db:
        original = db.get(MemoryProposal, (h["a_id"], original_id))
        values = {
            column.name: getattr(original, column.name)
            for column in MemoryProposal.__table__.columns
            if column.name != "id"
        }
        db.add_all(MemoryProposal(id=str(uuid4()), **values) for _ in range(391))
    barrier = Barrier(2)

    class ConcurrentExtractor:
        model = "synthetic-extractor-v1"

        def complete(self, messages):
            barrier.wait(timeout=10)
            return Completion(json.dumps({"candidates": [candidate] * 8}), self.model)

    h["app"].state.proposals.provider = ConcurrentExtractor()
    inputs = [body | {"extraction_id": str(uuid4())} for _ in range(2)]
    with ThreadPoolExecutor(2) as pool:
        receipts = list(pool.map(lambda value: extract(h, s, value), inputs))
    assert all(receipt.status_code == 201 for receipt in receipts)
    assert sorted(receipt.json()["state"] for receipt in receipts) == ["completed", "failed"]
    failed_index = next(
        index for index, receipt in enumerate(receipts) if receipt.json()["state"] == "failed"
    )
    assert receipts[failed_index].json()["error_code"] == "proposal_retained_limit"
    assert receipts[failed_index].json()["proposal_ids"] == []
    assert extract(h, s, inputs[failed_index]).json() == receipts[failed_index].json()
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(MemoryProposal)) == 400
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


def test_conflict_preview_correction_and_interval_are_atomic(harness):
    h = harness
    s, n, _, body, _ = setup(h)
    old = add(
        h, s, n, subject="Mira", predicate="drink", value="water", valid_from="2020-01-01T00:00:00Z"
    ).json()
    p = detail(h, extract(h, s, body).json()["proposal_ids"][0]).json()
    assert p["conflicts"][0]["id"] == old["id"]
    b = review_body(p, replace_claim_id=old["id"])
    result = review(h, p["id"], b)
    assert result.status_code == 201, result.text
    saved = h["client"].get(f"/v1/claims/{old['id']}", headers=h["a"]).json()
    assert saved["status"] == "superseded" and saved["superseded_by"] == result.json()["claim_id"]
    assert review(h, p["id"], b).json() == result.json()


def test_imported_and_model_sources_keep_trust_and_old_retrieval_is_frozen(harness):
    from conftest import make_conversation, send

    from ada.providers import Completion

    h = harness
    s, _, _, body, extractor = setup(h)
    c, personality = make_conversation(h)
    assert send(h, c, "Synthetic original model material").status_code == 200
    events = h["client"].get(f"/v1/conversations/{c}/events", headers=h["a"]).json()
    model = events[-1]["source_version_id"]
    model_scope = h["client"].get(f"/v1/conversations/{c}", headers=h["a"]).json()["scope_id"]
    source = h["client"].get(f"/v1/source-versions/{model}", headers=h["a"]).json()
    h["app"].state.proposals.provider = type(
        "ModelFixture",
        (),
        {
            "model": "synthetic-v1",
            "complete": lambda self, messages: Completion(
                json.dumps(
                    {
                        "candidates": [
                            {
                                "subject": "Mira",
                                "predicate": "drink",
                                "value": "tea",
                                "kind": "preference",
                                "support": [pin(source)],
                            }
                        ]
                    }
                ),
                "synthetic-v1",
            ),
        },
    )()
    for evidence, selected_scope in [(source, model_scope)]:
        job = extract(
            h, selected_scope, {"extraction_id": str(uuid4()), "sources": [pin(evidence)]}
        )
        p = detail(h, job.json()["proposal_ids"][0]).json()
        result = review(h, p["id"], review_body(p))
        assert result.status_code == 201, result.text
        assert detail(h, p["id"]).json()["support"][0]["trust_class"] == "model_generated"
    upload = h["client"].post(
        f"/v1/scopes/{s}/documents/uploads/{uuid4()}",
        headers=h["a"] | {"Content-Type": "text/plain"},
        params={"source_id": str(uuid4()), "filename": "synthetic.txt"},
        content=b"Synthetic Mira prefers tea.",
    )
    assert upload.status_code == 201, upload.text
    doc = h["client"].get(
        f"/v1/document-versions/{upload.json()['source_version_id']}", headers=h["a"]
    )
    assert doc.status_code == 200, doc.text
    evidence = doc.json()
    h["app"].state.proposals.provider = type(
        "ImportFixture",
        (),
        {
            "model": "synthetic-v1",
            "complete": lambda self, messages: Completion(
                json.dumps(
                    {
                        "candidates": [
                            {
                                "subject": "Mira",
                                "predicate": "drink",
                                "value": "tea",
                                "kind": "preference",
                                "support": [pin(evidence)],
                            }
                        ]
                    }
                ),
                "synthetic-v1",
            ),
        },
    )()
    job = extract(h, s, {"extraction_id": str(uuid4()), "sources": [pin(evidence)]})
    p = detail(h, job.json()["proposal_ids"][0]).json()
    result = review(h, p["id"], review_body(p))
    assert result.status_code == 201, result.text
    conv = (
        h["client"]
        .post(
            "/v1/conversations", headers=h["a"], json={"personality_id": personality, "scope_id": s}
        )
        .json()["id"]
    )
    h["provider"].complete = lambda messages: Completion(
        "Synthetic cited answer [M1]", h["provider"].model
    )
    saved = send(h, conv, "Mira drink").json()
    assert saved["citations"][0]["provenance"]["support"][0]["trust_class"] == "imported_untrusted"
    with h["sessions"].begin() as db:
        assert db.get(SourceVersion, evidence["id"]).trust_class == "imported_untrusted"
        db.get(SourceVersion, evidence["id"]).content = "Operator tamper"
    assert send(h, conv, "Mira drink", saved["request_id"]).json() == saved
    current = (
        h["client"]
        .post(f"/v1/scopes/{s}/retrieve", headers=h["a"], json={"query": "Mira drink"})
        .json()
    )
    assert current["selected"] == []


def test_review_write_failure_rolls_back_endorsement_claim_and_receipt(harness, monkeypatch):
    import ada.proposals
    from ada.proposal_models import ClaimSupport, MemoryReview

    h = harness
    s, _, _, body, _ = setup(h)
    p = detail(h, extract(h, s, body).json()["proposal_ids"][0]).json()
    with h["sessions"]() as db:
        count = db.scalar(select(func.count()).select_from(SourceVersion))

    def fail(*args):
        raise RuntimeError("Synthetic storage failure")

    monkeypatch.setattr(ada.proposals, "index_claim", fail)
    with pytest.raises(RuntimeError, match="Synthetic storage failure"):
        review(h, p["id"], review_body(p))
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(SourceVersion)) == count
        for table in (Claim, ClaimSupport, MemoryReview):
            assert db.scalar(select(func.count()).select_from(table)) == 0
    assert detail(h, p["id"]).json()["status"] == "pending"


def test_concurrent_conflict_write_stale_preview_and_busy_capacity(harness):
    h = harness
    s, n, _, body, _ = setup(h)
    capacity = h["app"].state.chat.capacity
    assert capacity.acquire(False) and capacity.acquire(False)
    try:
        assert extract(h, s, body).status_code == 503
    finally:
        capacity.release()
        capacity.release()
    job = extract(h, s, body)
    p = detail(h, job.json()["proposal_ids"][0]).json()
    assert add(h, s, n, subject="Mira", predicate="drink", value="milk").status_code == 201
    assert review(h, p["id"], review_body(p)).status_code == 409


def test_populated_upgrade_downgrade_guard_and_old_completed_replay(harness):
    from alembic import command
    from conftest import make_conversation, send

    h = harness
    c, _ = make_conversation(h)
    saved = send(h, c).json()
    command.downgrade(h["config"], "0007")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, c, request_id=saved["request_id"]).json() == saved
    s, _, _, body, _ = setup(h)
    extract(h, s, body)
    with pytest.raises(RuntimeError, match="review history"):
        command.downgrade(h["config"], "0007")
    command.check(h["config"])


def test_admin_receives_counts_without_review_or_source_text(harness):
    from ada.admin import set_admin_grant

    h = harness
    s, _, _, body, _ = setup(h, text="SYNTHETIC_PRIVATE_SOURCE_SENTINEL prefers tea")
    p = detail(h, extract(h, s, body).json()["proposal_ids"][0]).json()
    assert (
        review(
            h, p["id"], review_body(p, annotation="SYNTHETIC_PRIVATE_REVIEW_SENTINEL")
        ).status_code
        == 201
    )
    assert h["client"].get("/v1/admin/overview", headers=h["a"]).status_code == 403
    set_admin_grant(h["sessions"], h["a_id"], True)
    response = h["client"].get("/v1/admin/overview", headers=h["a"])
    assert response.status_code == 200
    assert response.json()["memory_proposal_counts"] == {"pending": 0, "accepted": 1, "rejected": 0}
    assert "SYNTHETIC_PRIVATE" not in response.text
    assert "quote" not in response.text and "annotation" not in response.text


def test_publication_rechecks_source_and_invalid_second_span_never_publishes_partial_batch(harness):
    h = harness
    s, n, candidate, body, provider = setup(h, text="Tea.      ")
    bad = candidate | {"support": [pin(n) | {"span_start": 4, "span_end": 8}]}
    provider.complete = lambda messages: Completion(
        json.dumps({"candidates": [candidate, bad]}), provider.model
    )
    result = extract(h, s, body).json()
    assert result["state"] == "failed" and result["proposal_ids"] == []
    assert h["client"].get(f"/v1/scopes/{s}/memory-proposals", headers=h["a"]).json() == []

    def raced(messages):
        assert h["sessions"].kw["bind"].pool.checkedout() == 0
        with h["sessions"].begin() as db:
            db.get(SourceVersion, n["id"]).content = "Operator tamper during extraction"
        return Completion(json.dumps({"candidates": [candidate]}), provider.model)

    provider.complete = raced
    result = extract(h, s, body | {"extraction_id": str(uuid4())}).json()
    assert (
        result["state"] == "failed"
        and result["error_code"] == "proposal_source_changed"
        and result["proposal_ids"] == []
    )


def test_native_support_foreign_key_rejects_foreign_owner_source(harness):
    from sqlalchemy.exc import IntegrityError

    from ada.proposal_models import ClaimSupport

    h = harness
    s, _, _, body, _ = setup(h)
    p = detail(h, extract(h, s, body).json()["proposal_ids"][0]).json()
    receipt = review(h, p["id"], review_body(p)).json()
    foreign = note(h, scope(h, "b"), who="b")
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(
            ClaimSupport(
                owner_id=h["a_id"],
                scope_id=s,
                claim_id=receipt["claim_id"],
                ordinal=99,
                review_id=receipt["id"],
                source_version_id=foreign["id"],
                evidence_hash=foreign["content_hash"],
                span_start=0,
                span_end=len(foreign["content"]),
                quote=foreign["content"],
            )
        )
