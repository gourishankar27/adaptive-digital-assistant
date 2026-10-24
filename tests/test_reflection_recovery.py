"""Real encrypted backup v5 quarantine and released v4 compatibility."""

import json
from uuid import uuid4

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import make_url
from test_curiosity import enabled as questions_enabled
from test_recovery import recovery_database  # noqa: F401
from test_reflection import enabled

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.operations import backup, deletion_ledger, read_artifact, restore, unpack, write_artifact
from ada.providers import FakeProvider
from ada.reflection_models import (
    ReflectionArtifact,
    ReflectionPolicy,
    ReflectionProviderState,
    ReflectionRun,
)


def test_native_encrypted_reflection_restore_is_paused_and_requires_new_probe(
    recovery_database,  # noqa: F811
    tmp_path,
):
    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    settings = Settings(
        database_url=url,
        provider="fake",
        scheduler_enabled=False,
        consolidation_worker_enabled=False,
    )
    owner, token = create_user(sessions, "Public reflection recovery owner")
    app = create_app(settings, FakeProvider(), sessions)
    h = {
        "app": app,
        "settings": settings,
        "sessions": sessions,
        "a_id": owner,
        "a": {"Authorization": "Bearer " + token},
    }
    try:
        with TestClient(app) as client:
            h["client"] = client
            questions_enabled(h)
            service, clock, _, _, _ = enabled(h, kinds=["question"])
            assert service.queue_once() and service.run_once()
            policy = service.policy(owner)
            changed = client.post(
                "/v1/reflection/policy",
                headers=h["a"],
                json={
                    "operation_id": str(uuid4()),
                    "expected_revision": policy["revision"],
                    "settings": policy["settings"] | {"job_kinds": ["report"]},
                },
            )
            assert changed.status_code == 200
            clock[0] += 901000
            assert service.queue_once()
            claimed = service.claim()
            assert claimed is not None
            running_id = claimed[0].id
            with sessions.begin() as db:
                db.add(
                    ReflectionProviderState(
                        id="a" * 64, ready=True, reason="synthetic_fixture", observed_at=clock[0]
                    )
                )
        phrase = "Public synthetic reflection recovery phrase"
        artifact = backup(url, binary, tmp_path, phrase, settings)["artifact"]
        manifest, _ = unpack(read_artifact(artifact, phrase))
        assert manifest["head"] == "0022" and manifest["format"] == "ada-postgres-backup-v8"
        assert len(manifest["tables"]) == 77 and manifest["tables"]["reflection_runs"]["rows"] == 2
        assert manifest["tables"]["reflection_artifacts"]["rows"] == 1
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        assert restore(url, binary, target, artifact, ledger_path, phrase)["quarantined"]
        restored_engine, restored = connect(
            make_url(url).set(database=target).render_as_string(hide_password=False)
        )
        try:
            with restored() as db:
                p = db.get(ReflectionPolicy, owner)
                assert (
                    not p.enabled
                    and not p.settings["enabled"]
                    and p.last_decision == "restored_quarantine"
                )
                run = db.get(ReflectionRun, (owner, running_id))
                assert (
                    run.status == "quarantined"
                    and run.lease_token is None
                    and run.lease_until is None
                )
                assert not db.get(ReflectionProviderState, "a" * 64).ready
                draft = db.scalar(select(ReflectionArtifact))
                assert draft.question_template == "work.source"
                assert draft.content["question"]["template_key"] == draft.question_template
        finally:
            restored_engine.dispose()
    finally:
        engine.dispose()


def test_released_0018_v4_artifact_remains_restorable(recovery_database, tmp_path, monkeypatch):  # noqa: F811
    url, binary, owned = recovery_database
    config = Config("alembic.ini")
    command.downgrade(config, "0018")
    engine, sessions = connect(url)
    try:
        create_user(sessions, "Public released v4 owner")
        phrase = "Public synthetic old v4 recovery phrase"
        artifact = backup(url, binary, tmp_path, phrase, Settings(database_url=url))["artifact"]
        manifest, _ = unpack(read_artifact(artifact, phrase))
        assert manifest["head"] == "0018" and manifest["format"] == "ada-postgres-backup-v4"
        assert len(manifest["tables"]) == 65
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "old-ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        restore(url, binary, target, artifact, ledger_path, phrase)
        monkeypatch.setenv(
            "ADA_DATABASE_URL",
            make_url(url).set(database=target).render_as_string(hide_password=False),
        )
        command.upgrade(config, "head")
        command.check(config)
    finally:
        engine.dispose()
