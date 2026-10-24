"""Real encrypted current-head backup and isolated native restore quarantine scheduling grants."""

import json
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import make_url
from test_recovery import recovery_database  # noqa: F401
from test_schedules import BASE, setup_schedule

from ada.api import create_app
from ada.auth import create_user, rotate_token
from ada.config import Settings
from ada.db import connect
from ada.operations import backup, deletion_ledger, read_artifact, restore, unpack, write_artifact
from ada.providers import FakeProvider
from ada.schedule_models import Schedule, ScheduleConsent, ScheduleOccurrence


def test_native_encrypted_recovery_quarantines_running_and_future_schedules(
    recovery_database,  # noqa: F811
    tmp_path,
):
    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    settings = Settings(
        database_url=url,
        provider="fake",
        consolidation_worker_enabled=False,
        scheduler_enabled=False,
    )
    owner, credential = create_user(sessions, "Public scheduling recovery owner")
    app = create_app(settings, FakeProvider(), sessions)
    h = {
        "app": app,
        "sessions": sessions,
        "settings": settings,
        "a_id": owner,
        "a": {"Authorization": "Bearer " + credential},
    }
    try:
        with TestClient(app) as client:
            h["client"] = client
            service, _, key, _, _ = setup_schedule(h)
            service.clock = lambda: BASE + 61000
            claim = service.claim()
            assert claim and claim["attempt"] == 1
        phrase = "Public synthetic scheduling recovery phrase"
        saved = backup(url, binary, tmp_path, phrase, settings)
        manifest, _ = unpack(read_artifact(saved["artifact"], phrase))
        assert manifest["head"] == "0022" and manifest["format"] == "ada-postgres-backup-v8"
        assert len(manifest["tables"]) == 77
        assert set(
            (
                "schedule_consents",
                "schedules",
                "schedule_occurrences",
                "schedule_inbox",
                "schedule_receipts",
            )
        ) <= set(manifest["tables"])
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        assert restore(url, binary, target, saved["artifact"], ledger_path, phrase)["quarantined"]
        restored_url = make_url(url).set(database=target).render_as_string(hide_password=False)
        restored_engine, restored = connect(restored_url)
        try:
            with restored() as db:
                assert not db.get(ScheduleConsent, owner).enabled
                schedule = db.get(Schedule, (owner, key))
                assert schedule.status == "quarantined" and schedule.generation == 2
                occurrence = db.scalar(
                    select(ScheduleOccurrence).where(ScheduleOccurrence.owner_id == owner)
                )
                assert (
                    occurrence.status == "suppressed"
                    and occurrence.lease_token is None
                    and occurrence.lease_until is None
                )
            fresh = rotate_token(restored, "Public scheduling recovery owner")
            restored_settings = Settings(
                database_url=restored_url,
                provider="fake",
                scheduler_enabled=False,
                consolidation_worker_enabled=False,
            )
            restored_app = create_app(restored_settings, FakeProvider(), restored)
            with TestClient(restored_app) as client:
                old_result = client.get("/v1/me", headers=h["a"])
                assert old_result.status_code == 401
                new = {"Authorization": "Bearer " + fresh}
                result = client.get("/v1/scheduling/policy", headers=new)
                assert result.status_code == 200 and not result.json()["enabled"]
                restored_settings.scheduler_enabled = True
                assert not restored_app.state.scheduling.run_once()
        finally:
            restored_engine.dispose()
    finally:
        engine.dispose()
