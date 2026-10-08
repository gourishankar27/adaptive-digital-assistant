import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from conftest import make_conversation, send
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from ada.models import Claim, Conversation, Event, PromptChange, Source, SourceVersion


def scope(h, who="a", name="ADA development"):
    response = h["client"].post("/v1/scopes", headers=h[who], json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def note(h, scope_id, content="I prefer Python.", who="a", source_id=None):
    response = h["client"].post(
        f"/v1/scopes/{scope_id}/notes",
        headers=h[who],
        json={"source_id": source_id or str(uuid4()), "content": content},
    )
    assert response.status_code in (200, 201), response.text
    return response.json()


def proposal(source, **changes):
    body = {
        "claim_id": str(uuid4()),
        "subject": "user",
        "predicate": "preferred_language",
        "value": "Python",
        "kind": "preference",
        "source_version_id": source["id"],
        "span_start": 0,
        "span_end": len(source["content"]),
    }
    return body | changes


def add(h, scope_id, source, **changes):
    return h["client"].post(
        f"/v1/scopes/{scope_id}/claims", headers=h["a"], json=proposal(source, **changes)
    )


def correct(h, old, source, **changes):
    body = {
        "claim_id": str(uuid4()),
        "value": "Java",
        "source_version_id": source["id"],
        "span_start": 0,
        "span_end": len(source["content"]),
    }
    return h["client"].post(
        f"/v1/claims/{old['id']}/supersede", headers=h["a"], json=body | changes
    )


def test_claim_requires_existing_evidence_and_exact_nonblank_span(harness):
    h = harness
    s = scope(h)
    n = note(h, s, "🙂 I prefer Python.   ")
    for change, status in (
        ({"source_version_id": str(uuid4())}, 404),
        ({"span_start": -1}, 422),
        ({"span_end": len(n["content"]) + 1}, 422),
        ({"span_start": 2, "span_end": 2}, 422),
        ({"span_start": len(n["content"]) - 3}, 422),
    ):
        assert add(h, s, n, **change).status_code == status
    result = add(h, s, n, span_start=2, span_end=18)
    assert result.status_code == 201, result.text
    assert result.json()["evidence"]["quote"] == "I prefer Python."
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 1


def test_model_output_is_not_user_memory(harness):
    h = harness
    c, _ = make_conversation(h)
    assert send(h, c, "I prefer Python.").status_code == 200
    events = h["client"].get(f"/v1/conversations/{c}/events", headers=h["a"]).json()
    s = h["client"].get(f"/v1/conversations/{c}", headers=h["a"]).json()["scope_id"]
    for event in events:
        src = (
            h["client"]
            .get(f"/v1/source-versions/{event['source_version_id']}", headers=h["a"])
            .json()
        )
        result = add(h, s, src)
        assert result.status_code == (201 if event["role"] == "user" else 422)
    assert len(h["provider"].calls) == 1


def test_scope_and_user_isolation_for_all_memory_resources(harness):
    h = harness
    s, other = scope(h), scope(h, name="Other project")
    n = note(h, s)
    claim = add(h, s, n).json()
    assert add(h, other, n).status_code == 404
    for path in (
        f"/v1/scopes/{s}",
        f"/v1/scopes/{s}/source-versions",
        f"/v1/scopes/{s}/claims",
        f"/v1/source-versions/{n['id']}",
        f"/v1/claims/{claim['id']}",
    ):
        assert h["client"].get(path, headers=h["b"]).status_code == 404
        assert h["client"].get(path).status_code == 401
    assert h["client"].get("/v1/scopes", headers=h["b"]).json() == []
    assert (
        h["client"]
        .post(
            f"/v1/scopes/{s}/notes",
            headers=h["b"],
            json={"source_id": str(uuid4()), "content": "stolen"},
        )
        .status_code
        == 404
    )
    assert (
        h["client"].post(f"/v1/scopes/{s}/claims", headers=h["b"], json=proposal(n)).status_code
        == 404
    )
    assert (
        h["client"]
        .post(
            f"/v1/claims/{claim['id']}/supersede",
            headers=h["b"],
            json={
                "claim_id": str(uuid4()),
                "value": "Java",
                "source_version_id": n["id"],
                "span_start": 0,
                "span_end": 2,
            },
        )
        .status_code
        == 404
    )


def test_database_rejects_cross_scope_and_missing_evidence(harness):
    h = harness
    a, b = scope(h), scope(h, name="Other")
    n = note(h, a)
    original = add(h, a, n).json()
    with h["sessions"]() as db:
        row = db.get(Claim, original["id"])
        fields = {column.name: getattr(row, column.name) for column in Claim.__table__.columns}
    for changes in (
        {"source_version_id": str(uuid4())},
        {"scope_id": b},
        {"owner_id": h["b_id"]},
        {"source_version_id": None},
        {"valid_to": fields["valid_from"]},
    ):
        with pytest.raises(IntegrityError), h["sessions"].begin() as db:
            db.add(Claim(**(fields | {"id": str(uuid4()), "write_hash": uuid4().hex} | changes)))


def test_notes_and_claims_are_idempotent_and_payload_bound(harness):
    h = harness
    s = scope(h)
    n = note(h, s)
    assert note(h, s, source_id=n["source_id"]) == n
    changed = h["client"].post(
        f"/v1/scopes/{s}/notes",
        headers=h["a"],
        json={"source_id": n["source_id"], "content": "changed"},
    )
    assert changed.status_code == 409
    body = proposal(n)
    url = f"/v1/scopes/{s}/claims"
    first = h["client"].post(url, headers=h["a"], json=body)
    second = h["client"].post(url, headers=h["a"], json=body)
    duplicate = h["client"].post(url, headers=h["a"], json=body | {"claim_id": str(uuid4())})
    assert first.status_code == 201 and second.status_code == 200
    assert duplicate.status_code == 409 and duplicate.json()["detail"] == "claim_duplicate"
    assert first.json() == second.json()
    assert h["client"].post(url, headers=h["a"], json=body | {"value": "Java"}).status_code == 409
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 1
        assert db.scalar(select(func.count()).select_from(SourceVersion)) == 1
    assert h["provider"].calls == []


def test_temporal_correction_is_atomic_and_half_open(harness):
    h = harness
    s = scope(h)
    old_source, new_source = note(h, s), note(h, s, "I now prefer Java.")
    start = datetime(2026, 1, 1, tzinfo=UTC)
    boundary = datetime(2026, 2, 1, tzinfo=UTC)
    old = add(h, s, old_source, valid_from=start.isoformat()).json()
    new = correct(h, old, new_source, effective_at=boundary.isoformat())
    assert new.status_code == 201, new.text
    old_now = h["client"].get(f"/v1/claims/{old['id']}", headers=h["a"]).json()
    assert old_now["status"] == "superseded"
    assert old_now["superseded_by"] == new.json()["id"]
    for at, expected in (
        (start - timedelta(milliseconds=1), []),
        (start, [old["id"]]),
        (boundary - timedelta(milliseconds=1), [old["id"]]),
        (boundary, [new.json()["id"]]),
    ):
        result = h["client"].get(
            f"/v1/scopes/{s}/claims", headers=h["a"], params={"as_of": at.isoformat()}
        )
        assert [row["id"] for row in result.json()] == expected
    history = (
        h["client"].get(f"/v1/scopes/{s}/claims", headers=h["a"], params={"history": True}).json()
    )
    assert len(history) == 2


def test_future_replacement_does_not_hide_current_claim(harness):
    h = harness
    s = scope(h)
    old = add(h, s, note(h, s)).json()
    future = (datetime.now(UTC) + timedelta(days=1)).replace(microsecond=0)
    new = correct(
        h, old, note(h, s, "I will prefer Java tomorrow."), effective_at=future.isoformat()
    )
    assert new.status_code == 201
    current = h["client"].get(f"/v1/scopes/{s}/claims", headers=h["a"]).json()
    assert [c["id"] for c in current] == [old["id"]]
    assert current[0]["status"] == "superseded"
    independent = add(
        h, s, note(h, s, "I plan to learn Rust."), value="Rust", valid_from=future.isoformat()
    )
    assert independent.status_code == 201
    assert len(h["client"].get(f"/v1/scopes/{s}/claims", headers=h["a"]).json()) == 1


def test_failed_or_repeated_correction_leaves_consistent_history(harness):
    h = harness
    s = scope(h)
    n = note(h, s)
    old = add(h, s, n, valid_from="2026-01-01T00:00:00Z").json()
    bad = correct(h, old, n, effective_at="2026-01-01T00:00:00Z")
    assert bad.status_code == 422
    bad = correct(h, old, n, source_version_id=str(uuid4()), effective_at="2026-02-01T00:00:00Z")
    assert bad.status_code == 404
    key = str(uuid4())
    args = {"claim_id": key, "effective_at": "2026-02-01T00:00:00Z"}
    first, repeat = correct(h, old, n, **args), correct(h, old, n, **args)
    assert first.status_code == 201 and repeat.status_code == 200
    assert first.json() == repeat.json()
    assert correct(h, old, n, effective_at="2026-03-01T00:00:00Z").status_code == 409
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 2


def test_source_content_change_is_detected(harness):
    h = harness
    s = scope(h)
    n = note(h, s)
    with h["sessions"].begin() as db:
        db.get(SourceVersion, n["id"]).content = "tampered source"
    assert add(h, s, n).status_code == 409
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


def test_inputs_cannot_forge_authority_or_use_naive_time(harness):
    h = harness
    s = scope(h)
    n = note(h, s)
    for changes in (
        {"owner_id": h["b_id"]},
        {"trust_class": "verified"},
        {"confidence": 1.0},
        {"quote": "invented"},
        {"valid_from": "2026-01-01T00:00:00"},
        {"valid_from": "2026-01-01T00:00:00.000001Z"},
        {"valid_from": "2026-02-01T00:00:00Z", "valid_to": "2026-01-01T00:00:00Z"},
    ):
        assert add(h, s, n, **changes).status_code == 422
    assert (
        h["client"]
        .get(
            f"/v1/scopes/{s}/claims",
            headers=h["a"],
            params={"history": True, "as_of": "2026-01-01T00:00:00Z"},
        )
        .status_code
        == 422
    )


def test_project_conversations_share_scope_but_not_history_or_personality(harness):
    h = harness
    s = scope(h)
    first, p = make_conversation(h)
    body = {"personality_id": p, "scope_id": s}
    created = h["client"].post("/v1/conversations", headers=h["a"], json=body)
    assert created.status_code == 201
    second = created.json()["id"]
    assert send(h, first, "private first conversation").status_code == 200
    assert send(h, second, "project conversation").status_code == 200
    assert "private first conversation" not in str(h["provider"].calls[-1])
    assert h["client"].post("/v1/conversations", headers=h["b"], json=body).status_code == 404
    sources = h["client"].get(f"/v1/scopes/{s}/source-versions", headers=h["a"]).json()
    assert len(sources) == 2
    assert all(src["scope_id"] == s for src in sources)


def test_concurrent_corrections_have_one_winner_on_postgres(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("row-lock concurrency must be checked on PostgreSQL")
    s = scope(h)
    n = note(h, s)
    old = add(h, s, n, valid_from="2026-01-01T00:00:00Z").json()
    barrier = threading.Barrier(2)

    def race(value):
        barrier.wait(timeout=10)
        return correct(h, old, n, value=value, effective_at="2026-02-01T00:00:00Z")

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(race, ["Java", "Rust"]))
    assert sorted(r.status_code for r in responses) == [201, 409]
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 2


def test_prompt_upgrade_is_explicit_audited_and_fences_old_retries(harness):
    h = harness
    c, _ = make_conversation(h, name="Ada", style="direct")
    with h["sessions"].begin() as db:
        conversation = db.get(Conversation, c)
        conversation.system_prompt = "Old baseline"
        conversation.prompt_version = "ada-baseline-v1"
    url = f"/v1/conversations/{c}/prompt-upgrade"
    assert h["client"].post(url, headers=h["b"]).status_code == 404
    from ada.providers import ProviderError

    h["provider"].error = ProviderError("provider_timeout")
    request_id = str(uuid4())
    assert send(h, c, "retry", request_id).status_code == 502
    upgraded = h["client"].post(url, headers=h["a"])
    assert upgraded.status_code == 200
    assert upgraded.json()["prompt_version"] == "ada-baseline-v3"
    assert h["client"].post(url, headers=h["a"]).json() == upgraded.json()
    h["provider"].error = None
    assert send(h, c, "retry", request_id).status_code == 409
    assert send(h, c, "Who are you?").status_code == 200
    assert "Adaptive Digital Assistant" in h["provider"].calls[-1][0]["content"]
    with h["sessions"]() as db:
        changes = db.scalars(select(PromptChange)).all()
        assert len(changes) == 1 and changes[0].previous_prompt == "Old baseline"
        assert db.scalar(select(func.count()).select_from(Event)) == 3
        assert db.scalar(select(func.count()).select_from(Source)) == 3
        for version in db.scalars(select(SourceVersion)):
            assert version.content_hash == hashlib.sha256(version.content.encode()).hexdigest()


def test_correction_rolls_back_if_commit_path_is_interrupted(harness, monkeypatch):
    h = harness
    s = scope(h)
    n = note(h, s)
    old = add(h, s, n, valid_from="2026-01-01T00:00:00Z").json()

    def fail_after_write(_):
        raise RuntimeError("simulate interrupted correction transaction")

    monkeypatch.setattr("ada.memory.public_claim", fail_after_write)
    with pytest.raises(RuntimeError):
        correct(h, old, n, effective_at="2026-02-01T00:00:00Z")
    with h["sessions"]() as db:
        row = db.get(Claim, old["id"])
        assert row.status == "active" and row.valid_to is None and row.superseded_by is None
        assert db.scalar(select(func.count()).select_from(Claim)) == 1


def test_unrelated_greeting_does_not_retrieve_saved_memory(harness):
    h = harness
    s = scope(h)
    n = note(h, s, "The secret project code is blue-heron.")
    assert add(h, s, n, predicate="project_code", value="blue-heron").status_code == 201
    _, p = make_conversation(h)
    created = h["client"].post(
        "/v1/conversations", headers=h["a"], json={"personality_id": p, "scope_id": s}
    )
    assert send(h, created.json()["id"], "Hello").status_code == 200
    assert "blue-heron" not in str(h["provider"].calls[-1])


def test_prompt_upgrade_is_rejected_during_inference(harness):
    h = harness
    c, _ = make_conversation(h)
    with h["sessions"].begin() as db:
        db.get(Conversation, c).prompt_version = "ada-baseline-v1"
    started, release = threading.Event(), threading.Event()
    original = h["provider"].complete

    def blocked(messages):
        started.set()
        assert release.wait(10)
        return original(messages)

    h["provider"].complete = blocked
    with ThreadPoolExecutor() as pool:
        future = pool.submit(send, h, c)
        assert started.wait(5)
        try:
            result = h["client"].post(f"/v1/conversations/{c}/prompt-upgrade", headers=h["a"])
            assert result.status_code == 409
        finally:
            release.set()
        assert future.result().status_code == 200
    with h["sessions"]() as db:
        assert db.get(Conversation, c).prompt_version == "ada-baseline-v1"
        assert db.scalar(select(func.count()).select_from(PromptChange)) == 0


def test_text_incompatible_with_postgresql_is_rejected_at_input_boundary(harness):
    h = harness
    s = scope(h)
    for content in ("nul\x00text", "unpaired\ud800surrogate"):
        raw = json.dumps({"source_id": str(uuid4()), "content": content})
        response = h["client"].post(
            f"/v1/scopes/{s}/notes",
            headers=h["a"] | {"Content-Type": "application/json"},
            content=raw,
        )
        assert response.status_code == 422
    assert (
        h["client"]
        .get(f"/v1/scopes/{s}/claims", headers=h["a"], params={"subject": "nul\x00text"})
        .status_code
        == 422
    )
