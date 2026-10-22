"""Small public synthetic acceptance corpus, not a personal-memory accuracy claim."""

from uuid import uuid4

import pytest
from sqlalchemy import func, select
from test_curiosity import enabled as questions_enabled
from test_memory import add, note
from test_reflection import enabled

from ada.models import Claim


@pytest.mark.parametrize(
    "case,expected",
    [("same_value", 0), ("different_subject", 0), ("nonoverlap", 0), ("overlap", 1)],
)
def test_report_conflict_corpus_never_selects_a_hidden_truth(harness, case, expected):
    h = harness
    service, clock, scope, first, _ = enabled(h, text="Public atlas marker is blue.")
    second = note(h, scope, "Public atlas marker is green.")
    a = add(
        h,
        scope,
        first,
        subject="atlas",
        predicate="color",
        value="blue",
        valid_from="2020-01-01T00:00:00Z",
        valid_to="2022-01-01T00:00:00Z" if case == "nonoverlap" else None,
    )
    b = add(
        h,
        scope,
        second,
        subject="notebook" if case == "different_subject" else "atlas",
        predicate="color",
        value="blue" if case == "same_value" else "green",
        valid_from="2022-01-01T00:00:00Z",
    )
    assert a.status_code == 201 and b.status_code == 201
    clock[0] += 901000
    assert service.queue_once() and service.run_once()
    result = service.artifacts(h["a_id"])[0]["content"]["findings"]
    assert len(result) == expected
    if expected:
        assert result[0]["category"] == "possible_change_or_conflict"
        assert len(result[0]["support"]) == 2 and len(result[0]["claim_ids"]) == 2
        assert "no truth was selected" in result[0]["text"]
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 2


def test_owner_keeps_useful_report_and_discard_preserves_original_evidence(harness):
    h = harness
    service, _, _, original, _ = enabled(h)
    assert service.queue_once() and service.run_once()
    artifact = service.artifacts(h["a_id"])[0]
    assert len(artifact["content"]["findings"]) == 1
    path = f"/v1/reflection/artifacts/{artifact['id']}/actions"
    keep = h["client"].post(
        path, headers=h["a"], json={"operation_id": str(uuid4()), "action": "keep"}
    )
    assert keep.status_code == 200
    assert service.artifact(h["a_id"], artifact["id"])["state"] == "kept"
    dismiss = h["client"].post(
        path, headers=h["a"], json={"operation_id": str(uuid4()), "action": "dismiss"}
    )
    assert dismiss.status_code == 200
    assert service.artifact(h["a_id"], artifact["id"])["content"] is None
    source = h["client"].get(f"/v1/source-versions/{original['id']}", headers=h["a"])
    assert source.status_code == 200 and source.json()["content"] == original["content"]


def test_changed_source_does_not_repeat_an_already_drafted_question(harness):
    h = harness
    questions_enabled(h)
    service, clock, scope, _, _ = enabled(h, kinds=["question"])
    assert service.queue_once() and service.run_once()
    assert len(service.artifacts(h["a_id"])) == 1
    note(h, scope, "Another public original statement.")
    clock[0] += 901000
    assert service.queue_once() and service.run_once()
    assert len(service.artifacts(h["a_id"])) == 1
    assert service.runs(h["a_id"])[0]["reason"] == "no_useful_findings"
