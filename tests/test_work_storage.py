"""Native schema, revision isolation, erasure and encrypted work recovery."""

import json
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import func, inspect, select, text
from sqlalchemy.engine import make_url
from test_recovery import recovery_database  # noqa: F401
from test_work import body, save, setup

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.operations import backup, deletion_ledger, read_artifact, restore, unpack, write_artifact
from ada.providers import FakeProvider
from ada.work_models import WorkBrief, WorkItem, WorkReceipt, WorkRevision


def test_populated_0019_upgrade_replay_and_schema_drift(harness):
    from conftest import make_conversation, send

    h = harness
    command.downgrade(h["config"], "0019")
    cid, _ = make_conversation(h)
    key = str(uuid4())
    saved = send(h, cid, "Public phase30 migration replay.", key).json()
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, cid, "Public phase30 migration replay.", key).json() == saved
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


def test_work_downgrade_refuses_history_and_explicit_erasure_removes_all_content(harness):
    h = harness
    _, scope = setup(h)
    key = str(uuid4())
    assert save(h, scope, key, body()).status_code == 200
    with pytest.raises(RuntimeError, match="Work history"):
        command.downgrade(h["config"], "0019")
    h["settings"].deletion_worker_enabled = True
    service = h["app"].state.deletion
    preview = service.preview(h["a_id"])
    service.confirm(h["a_id"], str(uuid4()), preview["id"])
    assert service.process_one()
    with h["sessions"]() as db:
        for model in [WorkItem, WorkRevision, WorkReceipt, WorkBrief]:
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.owner_id == h["a_id"])
                )
                == 0
            )


def test_brief_alias_recovery_revision_cache_epoch_and_late_original_sources(harness):
    from ada.models import User

    h = harness
    _, scope = setup(h)
    key = str(uuid4())
    value = body()
    assert save(h, scope, key, value).status_code == 200
    request = {
        "operation_id": str(uuid4()),
        "scope_ids": [scope],
        "item_ids": [key],
        "day": "2026-10-22",
        "timezone": "America/Phoenix",
    }
    first = h["client"].post("/v1/work/briefs", headers=h["a"], json=request).json()
    another = request | {"operation_id": str(uuid4())}
    second = h["client"].post("/v1/work/briefs", headers=h["a"], json=another).json()
    assert second == first
    assert (
        h["client"].get(f"/v1/work/briefs/{another['operation_id']}", headers=h["a"]).json()
        == first
    )
    assert (
        save(
            h, scope, key, body(expected_revision=1, fields=value["fields"] | {"status": "done"})
        ).status_code
        == 200
    )
    latest = (
        h["client"]
        .post("/v1/work/briefs", headers=h["a"], json=request | {"operation_id": str(uuid4())})
        .json()
    )
    assert latest["items"][0]["task"]["fields"]["status"] == "done"
    assert (
        h["client"]
        .get(f"/v1/work/briefs/{first['id']}", headers=h["a"])
        .json()["items"][0]["task"]["fields"]["status"]
        == "planned"
    )
    assert h["client"].get(f"/v1/work/briefs/{first['id']}", headers=h["b"]).status_code == 404
    with h["sessions"].begin() as db:
        db.get(User, h["a_id"]).data_epoch += 1
    assert h["client"].get(f"/v1/work/briefs/{first['id']}", headers=h["a"]).status_code == 410


def test_native_encrypted_v6_work_snapshot_survives_restore(recovery_database, tmp_path):  # noqa: F811
    from test_curiosity import enabled
    from test_schedule_time import definition
    from test_schedules import BASE, setup_schedule

    from ada.curiosity_models import CuriosityPolicy
    from ada.schedule_models import Schedule, ScheduleConsent

    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    settings = Settings(
        database_url=url,
        provider="fake",
        scheduler_enabled=False,
        consolidation_worker_enabled=False,
    )
    owner, token = create_user(sessions, "Public work recovery owner")
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
            scheduler, scope, _, _, _ = setup_schedule(h)
            app.state.work.clock = lambda: BASE
            key = str(uuid4())
            value = body()
            assert save(h, scope, key, value).status_code == 200
            policy = enabled(h)
            followup = client.post(
                f"/v1/work/{key}/followup",
                headers=h["a"],
                json={
                    "operation_id": str(uuid4()),
                    "expected_revision": 1,
                    "policy_revision": policy["revision"],
                    "topic": "work",
                    "review": "confirm",
                },
            )
            assert followup.status_code == 200
            question_id = followup.json()["question_id"]
            preview = client.post(
                f"/v1/work/{key}/reminder-preview",
                headers=h["a"],
                json={
                    "operation_id": str(uuid4()),
                    "expected_revision": 2,
                    "definition": definition(text=value["fields"]["description"]),
                },
            )
            assert preview.status_code == 200
            schedule_id = str(uuid4())
            confirmed = client.post(
                f"/v1/work/{key}/reminder-confirm",
                headers=h["a"],
                json={
                    "operation_id": str(uuid4()),
                    "expected_revision": 2,
                    "preview_id": preview.json()["operation_id"],
                    "consent_revision": scheduler.policy(owner)["revision"],
                    "schedule_id": schedule_id,
                    "expected_generation": 0,
                    "review": "confirm",
                },
            )
            assert confirmed.status_code == 200
            b = {
                "operation_id": str(uuid4()),
                "scope_ids": [scope],
                "item_ids": [key],
                "day": "2026-10-22",
                "timezone": "UTC",
            }
            assert client.post("/v1/work/briefs", headers=h["a"], json=b).status_code == 200
        phrase = "Public synthetic work recovery phrase"
        artifact = backup(url, binary, tmp_path, phrase, settings)["artifact"]
        manifest, _ = unpack(read_artifact(artifact, phrase))
        assert manifest["head"] == "0021" and manifest["format"] == "ada-postgres-backup-v7"
        assert len(manifest["tables"]) == 76 and manifest["tables"]["work_items"]["rows"] == 1
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
                row = db.get(WorkItem, (owner, key))
                assert (
                    row.revision == 3
                    and row.status == "planned"
                    and row.fields["description"] == value["fields"]["description"]
                    and row.question_id == question_id
                    and row.schedule_id == schedule_id
                )
                assert not db.get(CuriosityPolicy, owner).settings["enabled"]
                assert not db.get(ScheduleConsent, owner).enabled
                assert db.get(Schedule, (owner, schedule_id)).status == "quarantined"
                assert db.scalar(select(func.count()).select_from(WorkBrief)) == 1
                assert db.scalar(select(func.count()).select_from(WorkRevision)) == 3
        finally:
            restored_engine.dispose()
    finally:
        engine.dispose()


def test_released_0019_v5_remains_restorable_and_upgrades(recovery_database, tmp_path, monkeypatch):  # noqa: F811
    from alembic.config import Config

    url, binary, owned = recovery_database
    config = Config("alembic.ini")
    command.downgrade(config, "0019")
    engine, sessions = connect(url)
    try:
        create_user(sessions, "Public released v5 work-upgrade owner")
        phrase = "Public synthetic released v5 recovery phrase"
        artifact = backup(url, binary, tmp_path, phrase, Settings(database_url=url))["artifact"]
        manifest, _ = unpack(read_artifact(artifact, phrase))
        assert (
            manifest["head"] == "0019"
            and manifest["format"] == "ada-postgres-backup-v5"
            and len(manifest["tables"]) == 70
        )
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "v5-ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        assert restore(url, binary, target, artifact, ledger_path, phrase)["quarantined"]
        monkeypatch.setenv(
            "ADA_DATABASE_URL",
            make_url(url).set(database=target).render_as_string(hide_password=False),
        )
        command.upgrade(config, "head")
        command.check(config)
    finally:
        engine.dispose()
