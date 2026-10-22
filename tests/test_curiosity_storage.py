"""Populated upgrades, real owner locks, private erasure and quarantined recovery."""

import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from test_curiosity import create, enabled, question, scope_for
from test_recovery import recovery_database  # noqa: F401

from ada.api import create_app
from ada.auth import create_user, rotate_token
from ada.config import Settings
from ada.curiosity_models import CuriosityPolicy, CuriosityQuestion, CuriosityReceipt
from ada.db import connect
from ada.operations import backup, deletion_ledger, read_artifact, restore, unpack, write_artifact
from ada.providers import FakeProvider
from ada.schema import SCHEMA_HEAD


def test_native_owner_quota_serializes_across_scopes(harness):
    from conftest import make_conversation

    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Owner-wide curiosity quota requires PostgreSQL row locks")
    enabled(h)
    scopes = [scope_for(h, make_conversation(h)[0]) for _ in range(3)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(
            pool.map(lambda scope: create(h, scope, topic="interests")[0].status_code, scopes)
        )
    assert sorted(results) == [200, 200, 429]


def test_curiosity_erase_closes_all_private_inventory(harness):
    from conftest import make_conversation

    h = harness
    enabled(h)
    cid, _ = make_conversation(h)
    q = question(h, create(h, scope_for(h, cid))[0].json())
    h["settings"].deletion_worker_enabled = True
    service = h["app"].state.deletion
    preview = service.preview(h["a_id"])
    service.confirm(h["a_id"], str(uuid4()), preview["id"])
    assert service.process_one()
    with h["sessions"]() as db:
        for model in (CuriosityPolicy, CuriosityQuestion, CuriosityReceipt):
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.owner_id == h["a_id"])
                )
                == 0
            )
    assert h["client"].get("/v1/curiosity/questions/" + q["id"], headers=h["a"]).status_code == 404
    assert not h["client"].get("/v1/curiosity/policy", headers=h["a"]).json()["settings"]["enabled"]


def test_populated_upgrade_preserves_chat_and_refuses_curiosity_downgrade(harness):
    from conftest import make_conversation, send

    h = harness
    cid, _ = make_conversation(h)
    body = {"request_id": str(uuid4()), "content": "Public migration replay."}
    saved = send(h, cid, body["content"], body["request_id"]).json()
    command.downgrade(h["config"], "0016")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, cid, body["content"], body["request_id"]).json() == saved
    assert not h["client"].get("/v1/curiosity/policy", headers=h["a"]).json()["settings"]["enabled"]
    enabled(h)
    assert create(h, scope_for(h, cid))[0].status_code == 200
    with pytest.raises(RuntimeError, match="Curiosity history"):
        command.downgrade(h["config"], "0016")
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_HEAD


@pytest.mark.parametrize("head", ["0016", "0017"])
def test_native_versioned_recovery_preserves_replay_and_quarantines_curiosity(
    recovery_database,  # noqa: F811
    tmp_path,
    monkeypatch,
    head,
):
    from alembic.config import Config

    url, binary, owned = recovery_database

    engine, sessions = connect(url)
    settings = Settings(database_url=url, provider="fake", consolidation_worker_enabled=False)
    owner, token = create_user(sessions, "Public curiosity recovery owner")
    app = create_app(settings, FakeProvider(), sessions)
    headers = {"Authorization": "Bearer " + token}
    try:
        with TestClient(app) as client:
            h = {"client": client, "a": headers}
            profile = client.post("/v1/personalities", headers=headers, json={}).json()
            conv = client.post(
                "/v1/conversations", headers=headers, json={"personality_id": profile["id"]}
            ).json()
            rid = str(uuid4())
            original_response = client.post(
                f"/v1/conversations/{conv['id']}/messages",
                headers=headers,
                json={"request_id": rid, "content": "A public synthetic recovery statement."},
            )
            assert original_response.status_code == 200
            original = original_response.json()
            if head == "0017":
                enabled(h)
                q = question(h, create(h, conv["scope_id"])[0].json())
                command.downgrade(Config("alembic.ini"), "0017")
            else:
                command.downgrade(Config("alembic.ini"), "0016")
        phrase = "Public synthetic recovery passphrase"
        saved = backup(url, binary, tmp_path, phrase, settings)
        manifest, _ = unpack(read_artifact(saved["artifact"], phrase))
        assert manifest["head"] == head
        assert manifest["format"] == (
            "ada-postgres-backup-v3" if head == "0017" else "ada-postgres-backup-v2"
        )
        assert len(manifest["tables"]) == (60 if head == "0017" else 57)
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        assert restore(url, binary, target, saved["artifact"], ledger_path, phrase)["quarantined"]
        restored_url = make_url(url).set(database=target).render_as_string(hide_password=False)
        monkeypatch.setenv("ADA_DATABASE_URL", restored_url)
        command.upgrade(Config("alembic.ini"), "head")
        command.check(Config("alembic.ini"))
        restored_engine, restored = connect(restored_url)
        try:
            fresh = rotate_token(restored, "Public curiosity recovery owner")
            restored_app = create_app(
                Settings(
                    database_url=restored_url, provider="fake", consolidation_worker_enabled=False
                ),
                FakeProvider(),
                restored,
            )
            with TestClient(restored_app) as client:
                assert client.get(f"/v1/requests/{rid}", headers=headers).status_code == 401
                new = {"Authorization": "Bearer " + fresh}
                assert client.get(f"/v1/requests/{rid}", headers=new).json() == original
                assert not client.get("/v1/curiosity/policy", headers=new).json()["settings"][
                    "enabled"
                ]
                if head == "0017":
                    assert (
                        client.get("/v1/curiosity/questions/" + q["id"], headers=new).json()["text"]
                        is None
                    )
        finally:
            restored_engine.dispose()
    finally:
        engine.dispose()
