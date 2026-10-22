"""Question identity, owner-wide deduplication and erasure quiescence."""

from uuid import uuid4

import pytest
from conftest import make_conversation
from sqlalchemy import func, select
from test_curiosity import enabled as questions_enabled
from test_document_api import upload
from test_memory import note, scope
from test_reflection import enabled

from ada.curiosity import CATALOG
from ada.curiosity_models import CuriosityQuestion
from ada.errors import ServiceError


def test_question_template_is_deduplicated_across_owned_scopes(harness):
    h = harness
    questions_enabled(h)
    service, clock, _, _, _ = enabled(h, kinds=["question"])
    assert service.queue_once() and service.run_once()
    other_scope = scope(h, name="Another public scope")
    note(h, other_scope, "Another original public statement.")
    p = service.policy(h["a_id"])
    r = h["client"].post(
        "/v1/reflection/policy",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_revision": p["revision"],
            "settings": p["settings"] | {"scope_ids": [other_scope]},
        },
    )
    assert r.status_code == 200
    clock[0] += 901000
    assert service.queue_once() and service.run_once()
    assert len(service.artifacts(h["a_id"])) == 1


def test_open_never_substitutes_a_changed_catalogue_question(harness, monkeypatch):
    h = harness
    questions_enabled(h)
    service, clock, selected, _, _ = enabled(h, kinds=["question"])
    assert upload(h, selected, b"Public synthetic imported selection.").status_code == 201
    p = service.policy(h["a_id"])
    r = h["client"].post(
        "/v1/reflection/policy",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_revision": p["revision"],
            "settings": p["settings"] | {"source_types": ["imported_documents"]},
        },
    )
    assert r.status_code == 200
    clock[0] += 901000
    assert service.queue_once() and service.run_once()
    artifact = service.artifacts(h["a_id"])[0]
    assert artifact["content"]["question"]["source"] is None
    monkeypatch.setitem(CATALOG, "work", ("A different public catalogue question?",))
    _, personality = make_conversation(h)
    response = h["client"].post(
        f"/v1/reflection/artifacts/{artifact['id']}/actions",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "action": "open_question",
            "conversation_id": str(uuid4()),
            "personality_id": personality,
        },
    )
    assert response.status_code == 409
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(CuriosityQuestion)) == 0


def test_owner_deletion_preview_rejects_a_running_reflection_publisher(harness):
    h = harness
    service, _, _, _, _ = enabled(h)
    assert service.queue_once()
    run, _ = service.claim()
    with pytest.raises(ServiceError) as error:
        h["app"].state.deletion.preview(h["a_id"])
    assert error.value.status == 409
    assert service._finish(run, service._report(run), None, 1, None)


def test_foreground_arrival_during_selection_stops_new_dispatch(harness, monkeypatch):
    h = harness
    service, _, _, _, _ = enabled(h)
    original = service.consolidation._sources

    def arriving(*args, **kwargs):
        selected = original(*args, **kwargs)
        service.activity(h["a_id"])
        return selected

    monkeypatch.setattr(service.consolidation, "_sources", arriving)
    assert not service.queue_once()
    assert service.runs(h["a_id"]) == []


def test_discarded_question_retains_dedup_metadata_without_private_payload(harness):
    h = harness
    questions_enabled(h)
    service, clock, selected, _, _ = enabled(h, kinds=["question"])
    assert service.queue_once() and service.run_once()
    artifact = service.artifacts(h["a_id"])[0]
    r = h["client"].post(
        f"/v1/reflection/artifacts/{artifact['id']}/actions",
        headers=h["a"],
        json={"operation_id": str(uuid4()), "action": "dismiss"},
    )
    assert r.status_code == 200
    assert service.artifact(h["a_id"], artifact["id"])["content"] is None
    note(h, selected, "Another public note after dismissal.")
    clock[0] += 901000
    assert service.queue_once() and service.run_once()
    assert len(service.artifacts(h["a_id"])) == 1
