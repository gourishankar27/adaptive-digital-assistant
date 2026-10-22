"""Native leases, released migration replay, explicit erasure and recovery inventory."""

from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import func, inspect, select, text
from test_reflection import enabled

from ada.models import Claim, SourceVersion, User
from ada.reflection_models import (
    ReflectionArtifact,
    ReflectionPolicy,
    ReflectionReceipt,
    ReflectionRun,
)


def test_populated_0018_upgrade_preserves_completed_replay_and_has_no_schema_drift(harness):
    h = harness
    command.downgrade(h["config"], "0018")
    conversation, _ = make_conversation(h)
    key = str(uuid4())
    saved = send(h, conversation, "Public migration replay fixture.", key).json()
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, conversation, "Public migration replay fixture.", key).json() == saved
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == "0021"
        assert (
            len(
                [
                    n
                    for n in inspect(db.connection()).get_table_names()
                    if not n.startswith(("claim_fts", "document_fts"))
                ]
            )
            == 76
        )


def test_reflection_history_blocks_downgrade_before_any_ddl_and_erases_explicitly(harness):
    h = harness
    service, _, _, _, _ = enabled(h)
    assert service.queue_once() and service.run_once()
    with pytest.raises(RuntimeError, match="Reflection consent/artifact/safety history"):
        command.downgrade(h["config"], "0018")
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == "0021"
        assert db.scalar(select(func.count()).select_from(ReflectionArtifact)) == 1
    h["settings"].deletion_worker_enabled = True
    deletion = h["app"].state.deletion
    preview = deletion.preview(h["a_id"])
    deletion.confirm(h["a_id"], str(uuid4()), preview["id"])
    assert deletion.process_one()
    with h["sessions"]() as db:
        for model in (ReflectionArtifact, ReflectionRun, ReflectionReceipt, ReflectionPolicy):
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.owner_id == h["a_id"])
                )
                == 0
            )


@pytest.mark.parametrize("change", ["epoch", "deletion"])
def test_late_result_cannot_publish_after_owner_lifecycle_change(harness, change):
    h = harness
    service, _, _, _, _ = enabled(h)
    assert service.queue_once()
    run, _ = service.claim()
    result = service._report(run)
    with h["sessions"].begin() as db:
        user = db.get(User, h["a_id"])
        if change == "epoch":
            user.data_epoch += 1
        else:
            user.deletion_job_id = str(uuid4())
    try:
        assert not service._finish(run, result, None, 1, None)
    except Exception as exc:
        from ada.errors import ServiceError

        assert isinstance(exc, ServiceError) and exc.status in (401, 409, 423)
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(ReflectionArtifact)) == 0


def test_lease_recovery_fences_old_attempt_and_deduplicates_without_new_id(harness):
    h = harness
    service, clock, _, _, _ = enabled(h)
    assert service.queue_once()
    old, _ = service.claim()
    content = service._report(old)
    clock[0] = old.lease_until + 1
    fresh, _ = service.claim()
    assert old.id == fresh.id and fresh.attempt == 2
    assert not service._finish(old, content, None, 1, None)
    assert service._finish(fresh, content, None, 1, None)
    assert not service.queue_once()
    assert len(service.runs(h["a_id"])) == 1


def test_model_todo_is_not_owner_authored_evidence_and_completed_turns_are_separate_opt_in(harness):
    h = harness
    conversation, _ = make_conversation(h)
    assert send(h, conversation, "Public conversation fixture.").status_code == 200
    service, clock, _, _, _ = enabled(h, text="Public note without a finding.")
    with h["sessions"].begin() as db:
        for source in db.scalars(
            select(SourceVersion).where(SourceVersion.trust_class == "model_generated")
        ):
            source.content = "TODO: Fabricate a personal fact"
            import hashlib

            source.content_hash = hashlib.sha256(source.content.encode()).hexdigest()
    # Default selection contains only the explicit note, even with completed chat available.
    assert service.queue_once()
    run, _ = service.claim()
    assert len(run.snapshot) == 1 and run.snapshot[0]["source_origin"] == "user_note"
    assert service._report(run)["findings"] == []
    assert service._finish(run, service._report(run), None, 1, None)
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0
