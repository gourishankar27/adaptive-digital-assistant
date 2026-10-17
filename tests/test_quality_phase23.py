"""Public synthetic boundaries for explicit temporal windows and opt-in context."""

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from conftest import make_conversation, send
from sqlalchemy import select
from test_memory import add, correct, note, scope

from ada.models import Conversation, PromptChange, SourceVersion


def window(h, scope_id, **changes):
    return h["client"].post(
        f"/v1/scopes/{scope_id}/retrieve-window",
        headers=h["a"],
        json={
            "query": "preferred language",
            "selection": {
                "version": "ada-time-window-v1",
                "expression": "yesterday",
                "timezone": "America/Phoenix",
                "reference": "2025-06-02T12:00:00-07:00",
            },
            **changes,
        },
    )


def test_relative_windows_need_explicit_context_and_handle_dst(harness):
    client, auth = harness["client"], harness["a"]
    path = "/v1/temporal/resolve"
    for timezone, reference, hours in (
        ("America/Phoenix", "2026-03-09T12:00:00-07:00", 24),
        ("America/New_York", "2026-03-09T12:00:00-04:00", 23),
        ("America/New_York", "2026-11-02T12:00:00-05:00", 25),
    ):
        r = client.post(
            path,
            headers=auth,
            json={"expression": "yesterday", "timezone": timezone, "reference": reference},
        )
        assert r.status_code == 200
        value = r.json()
        assert value["state"] == "resolved"
        assert value["end"] - value["start"] == hours * 3600000
    for body in (
        {"expression": "yesterday"},
        {"expression": "last month"},
        {
            "expression": "yesterday",
            "timezone": "Mars/Unknown",
            "reference": "2026-01-01T00:00:00Z",
        },
    ):
        r = client.post(path, headers=auth, json=body)
        assert r.json()["state"] == "needs_clarification"
        assert r.json()["start"] is None
    assert client.post(path, json={"expression": "yesterday"}).status_code == 401
    assert (
        client.post(
            path, headers=auth, json={"expression": "yesterday", "reference": "2026-01-01"}
        ).status_code
        == 422
    )


def test_interval_preserves_both_sides_of_correction_and_owner_fences(harness):
    h = harness
    s = scope(h)
    old = add(h, s, note(h, s), valid_from="2025-01-01T00:00:00Z").json()
    new = correct(
        h, old, note(h, s, "😀 I prefer Java."), effective_at="2025-06-01T12:00:00Z"
    ).json()
    out = window(h, s)
    assert out.status_code == 200
    value = out.json()
    assert {c["claim_id"] for c in value["selected"]} == {old["id"], new["id"]}
    assert all(c["conflict"] for c in value["selected"])
    assert value["resolution"]["semantics"] == "valid_time_overlap_current_recorded_state"
    assert window(h, s, limit=1).json()["selected"] == []
    assert window(h, s, budget_bytes=1).json()["selected"] == []
    assert window(h, str(uuid4())).status_code == 404
    assert (
        h["client"]
        .post(
            f"/v1/scopes/{s}/retrieve-window",
            headers=h["b"],
            json={"query": "language", "selection": {"expression": "yesterday"}},
        )
        .status_code
        == 404
    )
    with h["sessions"].begin() as db:
        db.get(SourceVersion, new["evidence"]["source_version_id"]).content = "tampered"
    assert window(h, s).json()["selected"] == []


def test_quality_upgrade_is_explicit_audited_and_replay_frozen(harness):
    h = harness
    cid, _ = make_conversation(h)
    first = send(h, cid, "What do you remember?").json()
    with h["sessions"]() as db:
        original = db.get(Conversation, cid).system_prompt
    path = f"/v1/conversations/{cid}/quality-upgrade"
    assert h["client"].post(path, headers=h["b"]).status_code == 404
    result = h["client"].post(path, headers=h["a"])
    assert result.status_code == 200
    assert result.json()["prompt_version"] == "ada-baseline-v5"
    assert h["client"].post(path, headers=h["a"]).json() == result.json()
    replay = h["client"].post(
        f"/v1/conversations/{cid}/messages",
        headers=h["a"],
        json={"request_id": first["request_id"], "content": "What do you remember?"},
    )
    assert replay.json() == first
    with h["sessions"]() as db:
        changes = list(db.scalars(select(PromptChange).where(PromptChange.conversation_id == cid)))
        assert len(changes) == 1 and changes[0].previous_prompt == original
    assert send(h, cid, "What evidence was supplied?").status_code == 200
    assert (
        h["client"]
        .get(f"/v1/requests/{first['request_id']}/quality-context", headers=h["b"])
        .status_code
        == 404
    )
    assert (
        h["client"].post(f"/v1/conversations/{cid}/prompt-upgrade", headers=h["a"]).status_code
        == 409
    )


def test_old_point_time_and_default_prompt_are_unchanged(harness):
    h = harness
    cid, _ = make_conversation(h)
    assert (
        h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["prompt_version"]
        == "ada-baseline-v4"
    )
    from ada.retrieval import plan_query

    assert plan_query("as of 2025-01-01")["as_of"] == int(
        datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000
    )
    assert plan_query("yesterday")["time_mode"] == "needs_date"


@pytest.mark.parametrize(
    "zone,reference,expression,expected",
    [
        ("America/Phoenix", "2026-01-01T00:30:00-07:00", "yesterday", "2025-12-31T00:00:00-07:00"),
        ("America/Phoenix", "2026-03-02T20:00:00-07:00", "last week", "2026-02-23T00:00:00-07:00"),
        ("Pacific/Apia", "2011-12-31T12:00:00+14:00", "yesterday", None),
        ("America/Havana", "2026-11-02T12:00:00-05:00", "yesterday", None),
    ],
)
def test_calendar_boundaries_never_guess_missing_or_folded_midnight(
    zone, reference, expression, expected
):
    from ada.temporal import TimeSelection, resolve_time

    value = resolve_time(TimeSelection(timezone=zone, reference=reference, expression=expression))
    assert value.local_start == expected
    assert value.state == ("resolved" if expected else "needs_clarification")


def test_rankers_use_original_words_and_keep_bounded_recent_context():
    from ada.quality_context import rank_history, rank_original_sources

    rows = [
        SimpleNamespace(base_revision=i, messages=[{"content": text}], response="Mira tea")
        for i, text in reversed(
            list(enumerate(["Mira tea project", "unrelated", "newest", "last"]))
        )
    ]
    ranked = rank_history(rows, "Mira tea project")
    assert ranked[:1] == rows[:1]
    assert ranked[1].base_revision == 0

    def source(text, trust="user_explicit"):
        return {
            "trust_class": trust,
            "evidence": {
                "source_version_id": text,
                "span_start": 0,
                "span_end": len(text),
                "quote": text,
            },
        }

    older = SimpleNamespace(id="older", created_at=1)
    newer = SimpleNamespace(id="newer", created_at=2)
    good = source("Mira tea project blue")
    found = rank_original_sources(
        [
            (newer, [source("Mira tea"), source("Mira tea project blue", "model_generated")]),
            (older, [good, good]),
        ],
        "Mira tea project blue",
    )
    assert found[0] == (older, good)
    assert len(found) == 2


def test_v5_continuity_keeps_original_source_and_consent_not_generated_summary(harness):
    from test_consolidation import enqueue, prepared
    from test_learning import config

    from ada.consolidation_models import Episode

    h = harness
    sid, n, body, service, _ = prepared(h)
    assert enqueue(h, sid, body).status_code == 201 and service.run_once()
    _, pid = make_conversation(h)
    cid = (
        h["client"]
        .post("/v1/conversations", headers=h["a"], json={"personality_id": pid, "scope_id": sid})
        .json()["id"]
    )
    assert (
        h["client"].post(f"/v1/conversations/{cid}/quality-upgrade", headers=h["a"]).status_code
        == 200
    )
    assert config(h, sid, continuity=True).status_code == 201
    with h["sessions"].begin() as db:
        db.scalar(select(Episode).where(Episode.scope_id == sid)).summary = {
            "text": "Invented Mars trip"
        }
    response = send(h, cid, "Mira tea discussion?")
    assert response.status_code == 200
    rid = response.json()["request_id"]
    snapshot = h["client"].get(f"/v1/requests/{rid}/learning", headers=h["a"]).json()["learning"]
    assert snapshot["continuity_reason"] == "ranked_exact_original_sources_v2"
    assert snapshot["continuity"][0]["evidence"]["quote"] == n["content"]
    assert "Invented Mars" not in str(h["provider"].calls[-1])
    diagnostic = (
        h["client"].get(f"/v1/requests/{rid}/quality-context", headers=h["a"]).json()["policy"]
    )
    assert diagnostic["continuity_reason"] == "ranked_exact_original_sources_v2"
    assert config(h, sid, "off", 1).status_code == 201
    assert send(h, cid, "Mira tea discussion?", rid).json() == response.json()
    assert send(h, cid, "Mira tea discussion?").status_code == 200
    assert "Untrusted source-linked continuity" not in str(h["provider"].calls[-1])


def test_failed_retry_and_unsupported_prompt_never_receive_new_policy(harness):
    from ada.providers import ProviderError

    h = harness
    cid, _ = make_conversation(h)
    h["provider"].error = ProviderError("fixture_error")
    rid = str(uuid4())
    assert send(h, cid, "original question", rid).status_code == 502
    assert (
        h["client"].post(f"/v1/conversations/{cid}/quality-upgrade", headers=h["a"]).status_code
        == 200
    )
    h["provider"].error = None
    assert send(h, cid, "original question", rid).status_code == 409
    with h["sessions"].begin() as db:
        db.get(Conversation, cid).prompt_version = "unsupported-future-v99"
    assert (
        h["client"].post(f"/v1/conversations/{cid}/quality-upgrade", headers=h["a"]).status_code
        == 409
    )
