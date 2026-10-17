"""Bounded complete conflict groups and upgrade reservation fences."""

from conftest import make_conversation, send
from sqlalchemy import select
from test_memory import add, note, scope
from test_quality_phase23 import window

from ada.models import Conversation, PromptChange
from ada.providers import Completion


def test_interval_candidate_truncation_and_half_open_edges(harness):
    h = harness
    sid = scope(h)
    for i in range(65):
        source = note(h, sid, f"Synthetic language value {i}.")
        assert (
            add(
                h, sid, source, value=f"language-{i}", valid_from="2025-06-01T07:00:00Z"
            ).status_code
            == 201
        )
    result = window(h, sid).json()
    assert result["candidate_pool_truncated"] and result["selected"] == []
    other = scope(h, name="Boundary examples")
    source = note(h, other)
    assert add(h, other, source, valid_from="2025-06-02T07:00:00Z").status_code == 201
    assert window(h, other).json()["selected"] == []


def test_quality_upgrade_rejects_active_attempt_without_mutating_prompt(harness):
    h = harness
    cid, _ = make_conversation(h)
    results = []

    def provider(messages):
        results.append(
            h["client"].post(f"/v1/conversations/{cid}/quality-upgrade", headers=h["a"]).status_code
        )
        return Completion("Public synthetic answer", "fixture", 1, 1)

    h["provider"].complete = provider
    assert send(h, cid).status_code == 200
    assert results == [409]
    with h["sessions"]() as db:
        assert db.get(Conversation, cid).prompt_version == "ada-baseline-v4"
        assert db.scalar(select(PromptChange).where(PromptChange.conversation_id == cid)) is None
