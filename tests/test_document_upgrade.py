import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from test_document_storage import scope, upload
from test_memory import add, note

from ada.documents import DocumentService
from ada.models import Conversation, RetrievalTrace, Source, SourceVersion
from ada.personality import build_prompt


def test_populated_0004_upgrade_preserves_exact_evidence_prompt_and_completed_replay(harness):
    h = harness
    conversation, _ = make_conversation(h)
    with h["sessions"].begin() as db:
        conv = db.get(Conversation, conversation)
        conv.prompt_version = "ada-baseline-v3"
        conv.system_prompt = build_prompt(conv.personality_snapshot, version="ada-baseline-v3")
        scope_id = conv.scope_id
    evidence = note(h, scope_id, "Synthetic atlas specifies cobalt. 🙂")
    claim = add(
        h, scope_id, evidence, subject="Synthetic atlas", predicate="setting", value="cobalt"
    ).json()
    saved = send(h, conversation, "Synthetic atlas setting cobalt")
    assert saved.status_code == 200
    request_id = saved.json()["request_id"]
    with h["sessions"]() as db:
        old_prompt = db.get(Conversation, conversation).system_prompt
        trace = db.get(RetrievalTrace, (h["a_id"], request_id))
        before = (trace.plan, trace.candidates, trace.selected, trace.budget)
    command.downgrade(h["config"], "0004")
    assert h["client"].get("/health/ready").status_code == 503
    # Populated released-schema rows are still present before the new migration.
    with h["sessions"]() as db:
        assert (
            db.execute(
                text("SELECT content_hash FROM source_versions WHERE id = :id"),
                {"id": evidence["id"]},
            ).scalar_one()
            == evidence["content_hash"]
        )
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    with h["sessions"]() as db:
        assert db.get(Conversation, conversation).system_prompt == old_prompt
        assert db.get(Conversation, conversation).prompt_version == "ada-baseline-v3"
        trace = db.get(RetrievalTrace, (h["a_id"], request_id))
        assert (trace.plan, trace.candidates, trace.selected, trace.budget) == before
        assert trace.document_candidates == [] and trace.document_selected == []
        version = db.get(SourceVersion, evidence["id"])
        assert (
            version.content == evidence["content"]
            and version.content_hash == evidence["content_hash"]
        )
        assert db.scalar(select(Source).where(Source.id == version.source_id)).kind == "user_note"
    replay = send(h, conversation, "Synthetic atlas setting cobalt", request_id)
    assert replay.status_code == 200
    assert replay.json() | {"replayed": False} == saved.json() | {"replayed": False}
    assert h["client"].get(f"/v1/claims/{claim['id']}", headers=h["a"]).json() == claim
    # The legacy chat-event origin condition remains strict after parent rebuilds.
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(Source(owner_id=h["a_id"], scope_id=scope_id, kind="chat_event"))


def test_document_downgrade_refuses_before_destroying_private_upload(harness):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    receipt, _ = upload(service, h, s)
    with pytest.raises(RuntimeError, match="refusing a lossy downgrade"):
        command.downgrade(h["config"], "0004")
    assert service.get(h["a_id"], s, receipt["id"]) == receipt
    assert (
        service.raw(h["a_id"], s, receipt["source_version_id"])[0]
        == b"Synthetic atlas cobalt setting.\n"
    )
    # An empty newer migration may already have reversed before 0005 refuses.
    # Restore the current head without modifying the preserved document data.
    command.upgrade(h["config"], "head")
    command.check(h["config"])
