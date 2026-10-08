import hashlib
from uuid import uuid4

import pytest
from alembic import command
from conftest import send
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from ada.models import Conversation, Event, Personality, Request, Scope, SourceVersion, now_ms


def test_populated_phase0_upgrade_preserves_history_ids_and_replay(harness):
    h = harness
    command.downgrade(h["config"], "0001")
    conversation, profile, scope, request_id = [str(uuid4()) for _ in range(4)]
    timestamp = now_ms()
    content, response, old_prompt = "I prefer Python. 🙂", "Old saved answer", "Phase 0 baseline"
    event_ids = [str(uuid4()), str(uuid4())]
    with h["sessions"].begin() as db:
        db.execute(
            Personality.__table__.insert().values(
                id=profile,
                owner_id=h["a_id"],
                name="ADA",
                style="direct",
                warmth="warm",
                detail="balanced",
                created_at=timestamp,
            )
        )
        db.execute(
            Conversation.__table__.insert().values(
                id=conversation,
                owner_id=h["a_id"],
                personality_id=profile,
                scope_id=scope,
                scope_kind="personal",
                title="Old conversation",
                personality_snapshot={
                    "name": "ADA",
                    "style": "direct",
                    "warmth": "warm",
                    "detail": "balanced",
                },
                system_prompt=old_prompt,
                prompt_version="ada-baseline-v1",
                revision=1,
                created_at=timestamp,
            )
        )
        db.execute(
            Request.__table__.insert().values(
                id=request_id,
                owner_id=h["a_id"],
                conversation_id=conversation,
                content_hash=hashlib.sha256(content.encode()).hexdigest(),
                status="completed",
                attempt=1,
                base_revision=0,
                messages=[
                    {"role": "system", "content": old_prompt},
                    {"role": "user", "content": content},
                ],
                provider="old-provider",
                model="old-model",
                response=response,
                created_at=timestamp,
                started_at=timestamp,
                finished_at=timestamp + 1,
            )
        )
        for event_id, role, value, trust in (
            (event_ids[0], "user", content, "user_explicit"),
            (event_ids[1], "assistant", response, "model_generated"),
        ):
            db.execute(
                Event.__table__.insert().values(
                    id=event_id,
                    owner_id=h["a_id"],
                    conversation_id=conversation,
                    request_id=request_id,
                    role=role,
                    content=value,
                    trust_class=trust,
                    created_at=timestamp,
                )
            )
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    with h["sessions"]() as db:
        assert db.get(Conversation, conversation).system_prompt == old_prompt
        assert db.get(Conversation, conversation).scope_id == scope
        assert db.get(Scope, scope).name == "Old conversation"
        assert db.scalar(select(func.count()).select_from(Event)) == 2
        versions = db.scalars(select(SourceVersion)).all()
        assert {v.id for v in versions} == set(event_ids)
        for version in versions:
            assert version.scope_id == scope and version.owner_id == h["a_id"]
            assert version.content_hash == hashlib.sha256(version.content.encode()).hexdigest()
        assert db.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0003"
    replay = send(h, conversation, content, request_id)
    assert replay.status_code == 200 and replay.json()["response"] == response
    assert h["provider"].calls == []
    assert (
        h["client"].get(f"/v1/conversations/{conversation}/events", headers=h["a"]).status_code
        == 200
    )
    # This named/unnamed Phase 0 CHECK must survive SQLite's table rebuild.
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.execute(
            Event.__table__.insert().values(
                id=str(uuid4()),
                owner_id=h["a_id"],
                conversation_id=conversation,
                request_id=request_id,
                role="system",
                content="bad",
                trust_class="user_explicit",
            )
        )
