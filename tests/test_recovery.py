"""Authenticated encryption and native PostgreSQL restore rehearsal, never a live DB."""

import json
import os
import time
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from ada.api import create_app
from ada.auth import create_user, rotate_token
from ada.config import Settings
from ada.db import connect
from ada.operations import (
    RecoveryError,
    backup,
    deletion_ledger,
    read_artifact,
    restore,
    seal,
    unpack,
    unseal,
    write_artifact,
)


def test_artifact_authentication_bounds_and_exclusive_creation(tmp_path, monkeypatch):
    from ada.operations import default_destination

    phrase = "Synthetic recovery phrase only"
    payload = b"Synthetic private content"
    encrypted = seal(payload, phrase)
    assert unseal(encrypted, phrase) == payload
    assert payload not in encrypted
    with pytest.raises(RecoveryError):
        unseal(encrypted, "wrong synthetic phrase")
    with pytest.raises(RecoveryError):
        unseal(encrypted[:-1] + bytes([encrypted[-1] ^ 1]), phrase)
    with pytest.raises(RecoveryError):
        seal(payload, "short")
    path = tmp_path / "backup.adaenc"
    write_artifact(path, payload, phrase)
    with pytest.raises(FileExistsError):
        write_artifact(path, b"replacement", phrase)
    assert read_artifact(path, phrase) == payload
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert default_destination() == tmp_path / "ADA" / "backups"
    with pytest.raises(RecoveryError):
        unpack(b"not a zip archive")


def test_standalone_recovery_import_registers_entire_private_inventory():
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from ada.inventory import content_tables; assert len(content_tables()) == 45",
        ],
        capture_output=True,
        timeout=15,
    )
    if result.returncode:
        raise AssertionError("Standalone recovery inventory registration failed")


def test_released_0015_artifact_restores_quarantined_then_upgrades(
    recovery_database, tmp_path, monkeypatch
):
    url, binary, owned = recovery_database
    config = Config("alembic.ini")
    command.downgrade(config, "0015")
    engine, sessions = connect(url)
    owner, legacy = create_user(sessions, "Public 0015 recovery owner")
    phrase = "Public synthetic recovery passphrase"
    try:
        receipt = backup(url, binary, tmp_path, phrase, Settings(database_url=url))
        manifest, _ = unpack(read_artifact(receipt["artifact"], phrase))
        assert manifest["head"] == "0015" and manifest["format"] == "ada-postgres-backup-v1"
        assert len(manifest["tables"]) == 54
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        restore(url, binary, target, receipt["artifact"], ledger_path, phrase)
        restored_url = make_url(url).set(database=target).render_as_string(hide_password=False)
        monkeypatch.setenv("ADA_DATABASE_URL", restored_url)
        command.upgrade(config, "head")
        command.check(config)
        restored, restored_sessions = connect(restored_url)
        try:
            from ada.auth import token_hash
            from ada.login_models import PasswordCredential
            from ada.models import User

            with restored_sessions() as db:
                assert db.get(User, owner).token_hash != token_hash(legacy)
                assert db.get(PasswordCredential, owner) is None
        finally:
            restored.dispose()
    finally:
        engine.dispose()


@pytest.fixture
def recovery_database(monkeypatch):
    raw = os.environ.get("ADA_TEST_DATABASE_URL")
    binary = os.environ.get("ADA_TEST_PG_BIN")
    if not raw or not binary:
        pytest.skip("Native isolated PostgreSQL URL and binary folder required")
    source_name = "ada_recovery_fixture_" + uuid4().hex[:12]
    parsed = make_url(raw).set(query={})
    admin = create_engine(parsed.set(database="postgres"), isolation_level="AUTOCOMMIT")
    owned = [source_name]
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{source_name}" TEMPLATE template0'))
    source_url = parsed.set(database=source_name).render_as_string(hide_password=False)
    monkeypatch.setenv("ADA_DATABASE_URL", source_url)
    command.upgrade(Config("alembic.ini"), "head")
    try:
        yield source_url, binary, owned
    finally:
        with admin.connect() as conn:
            for name in owned:
                conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin.dispose()


def test_populated_restore_replay_revocation_and_latest_deletion_ledger(
    recovery_database, tmp_path
):
    from conftest import RecordingProvider
    from test_document_api import upload
    from test_memory import add, note
    from test_security import conversation, device_header, enroll

    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    settings = Settings(database_url=url, provider="fake", consolidation_worker_enabled=False)
    provider = RecordingProvider()
    app = create_app(settings, provider, sessions)
    a_id, a_token = create_user(sessions, "Recovery Alice")
    b_id, b_token = create_user(sessions, "Recovery Bob")
    phrase = "Synthetic recovery phrase only"
    with TestClient(app) as client:
        h = {
            "client": client,
            "app": app,
            "settings": settings,
            "sessions": sessions,
            "provider": provider,
            "a_id": a_id,
            "b_id": b_id,
            "a": {"Authorization": "Bearer " + a_token},
            "b": {"Authorization": "Bearer " + b_token},
        }
        a = conversation(h)
        b = conversation(h, h["b"])
        source = note(h, a["scope_id"], "Synthetic recovery atlas uses cobalt.")
        claim = add(h, a["scope_id"], source, subject="atlas", predicate="color", value="cobalt")
        assert claim.status_code == 201
        document = upload(h, a["scope_id"], b"Synthetic recovery document cobalt.\n")
        assert document.status_code == 201
        device = enroll(h)
        assert device.status_code == 201
        key = device.json()["credential"]["id"]
        assert (
            client.post(f"/v1/security/credentials/{key}/revoke", headers=h["a"]).status_code == 200
        )
        assert client.get("/v1/me", headers=device_header(device)).status_code == 401
        rid, bid = str(uuid4()), str(uuid4())
        body = {"request_id": rid, "content": "Which color does the atlas use?"}
        original = client.post(f"/v1/conversations/{a['id']}/messages", headers=h["a"], json=body)
        assert original.status_code == 200
        original_json = original.json()
        peer_body = {"request_id": bid, "content": "Synthetic peer recovery"}
        peer = client.post(
            f"/v1/conversations/{b['id']}/messages", headers=h["b"], json=peer_body
        ).json()
        import importlib

        from test_security import FEATURE_SEEDS

        for number, (module, function) in enumerate(FEATURE_SEEDS):
            # Existing feature invariants require an initially empty database. Populate
            # each isolated schema, then copy its UUID-bound graph into the drill DB.
            schema = "recovery_seed_" + uuid4().hex[:12]
            with engine.begin() as conn:
                conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            seed_url = (
                make_url(url)
                .update_query_dict({"options": f"-csearch_path={schema}"})
                .render_as_string(hide_password=False)
            )
            with pytest.MonkeyPatch.context() as patch:
                patch.setenv("ADA_DATABASE_URL", seed_url)
                command.upgrade(Config("alembic.ini"), "head")
            seed_engine, seed_sessions = connect(seed_url)
            seed_settings = Settings(
                database_url=seed_url, provider="fake", consolidation_worker_enabled=False
            )
            seed_provider = RecordingProvider()
            seed_app = create_app(seed_settings, seed_provider, seed_sessions)
            owner, token = create_user(seed_sessions, f"Recovery feature {number}")
            other, other_token = create_user(seed_sessions, f"Recovery peer {number}")
            try:
                with TestClient(seed_app) as seed_client:
                    seeded = {
                        "client": seed_client,
                        "app": seed_app,
                        "sessions": seed_sessions,
                        "settings": seed_settings,
                        "provider": seed_provider,
                        "backend": "postgres",
                        "a_id": owner,
                        "b_id": other,
                        "a": {"Authorization": "Bearer " + token},
                        "b": {"Authorization": "Bearer " + other_token},
                    }
                    getattr(importlib.import_module(module), function)(seeded)
                    if module == "test_semantic_retrieval":
                        semantic = importlib.import_module(module)
                        _, scope, _, _ = semantic.setup(seeded)
                        assert semantic.rebuild(seeded, scope).json()["indexed"] == 1
                from ada.inventory import CONTENT_TABLES
                from ada.models import Base

                with engine.begin() as conn:
                    for table in Base.metadata.sorted_tables:
                        if table.name == "users" or table.name in CONTENT_TABLES:
                            conn.execute(
                                text(
                                    f'INSERT INTO public."{table.name}" SELECT * FROM "{schema}"."{table.name}"'
                                )
                            )
            finally:
                seed_engine.dispose()
                with engine.begin() as conn:
                    conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        app.state.passwords.set_password(a_id, "recovery-alice", "Public recovery passphrase only")
        password_session = app.state.passwords.login(
            "recovery-alice", "Public recovery passphrase only"
        )
        receipt = backup(url, binary, tmp_path, phrase, settings)
        artifact = Path(receipt["artifact"])
        manifest, _ = unpack(read_artifact(artifact, phrase))
        assert manifest["tables"]["requests"]["rows"] >= 2
        assert manifest["tables"]["document_uploads"]["rows"] >= 1
        for table in ("voice_inputs", "consolidation_jobs", "agent_runs", "embedding_entries"):
            assert manifest["tables"][table]["rows"] > 0
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        recovered = restore(url, binary, target, artifact, ledger_path, phrase)
        assert recovered["quarantined"]
        restored_url = make_url(url).set(database=target).render_as_string(hide_password=False)
        restored_engine, restored_sessions = connect(restored_url)
        try:
            with restored_sessions() as db:
                assert (
                    db.scalar(
                        text("SELECT verifier FROM password_credentials WHERE owner_id=:owner"),
                        {"owner": a_id},
                    )
                    is None
                )
                assert (
                    db.scalar(
                        text("SELECT revoked_at FROM login_sessions WHERE id=:session"),
                        {"session": password_session["session_id"]},
                    )
                    is not None
                )
                assert (
                    db.scalar(
                        text("SELECT revoked_at FROM device_credentials WHERE id=:key"),
                        {"key": key},
                    )
                    is not None
                )
            restored_token = rotate_token(restored_sessions, "Recovery Alice")
            restored_provider = RecordingProvider()
            restored_provider.error = RuntimeError("Completed replay must not call inference")
            restored_app = create_app(
                Settings(
                    database_url=restored_url, provider="fake", consolidation_worker_enabled=False
                ),
                restored_provider,
                restored_sessions,
            )
            with TestClient(restored_app) as restored_client:
                headers = {"Authorization": "Bearer " + restored_token}
                assert restored_client.get("/v1/me", headers=h["a"]).status_code == 401
                replay = restored_client.post(
                    f"/v1/conversations/{a['id']}/messages", headers=headers, json=body
                )
                assert replay.status_code == 200 and replay.json() == original_json
                assert not restored_provider.calls
        finally:
            restored_engine.dispose()
        settings.deletion_worker_enabled = True
        preview = client.post("/v1/security/deletion-previews", headers=h["a"]).json()
        deletion_body = {
            "job_id": str(uuid4()),
            "preview_id": preview["id"],
            "confirmation": "erase_saved_content",
        }
        assert (
            client.post("/v1/security/deletions", headers=h["a"], json=deletion_body).status_code
            == 202
        )
        assert app.state.deletion.process_one()
        with sessions() as db:
            latest = deletion_ledger(db.connection())
        latest_path = write_artifact(
            tmp_path / "latest-ledger.adaenc", json.dumps(latest).encode(), phrase
        )
        target2 = "ada_restore_" + uuid4().hex[:12]
        owned.append(target2)
        restore(url, binary, target2, artifact, latest_path, phrase)
        recovered_engine, recovered_sessions = connect(
            make_url(url).set(database=target2).render_as_string(hide_password=False)
        )
        try:
            with recovered_sessions() as db:
                assert (
                    db.scalar(
                        text("SELECT COUNT(*) FROM requests WHERE owner_id=:owner"), {"owner": a_id}
                    )
                    == 0
                )
                assert (
                    db.scalar(
                        text("SELECT COUNT(*) FROM deleted_requests WHERE owner_id=:owner"),
                        {"owner": a_id},
                    )
                    == 1
                )
                assert (
                    db.scalar(text("SELECT response FROM requests WHERE id=:key"), {"key": bid})
                    is not None
                )
                assert (
                    db.scalar(
                        text("SELECT status FROM deletion_jobs WHERE owner_id=:owner"),
                        {"owner": a_id},
                    )
                    == "completed"
                )
            restored_peer = rotate_token(recovered_sessions, "Recovery Bob")
            with TestClient(
                create_app(
                    Settings(
                        database_url=make_url(url)
                        .set(database=target2)
                        .render_as_string(hide_password=False),
                        provider="fake",
                        consolidation_worker_enabled=False,
                    ),
                    RecordingProvider(),
                    recovered_sessions,
                )
            ) as check:
                assert (
                    check.get(
                        f"/v1/requests/{bid}", headers={"Authorization": "Bearer " + restored_peer}
                    ).json()
                    == peer
                )
        finally:
            recovered_engine.dispose()
        # Authentication/tamper failures happen before database creation; no overwrite allowed.
        with pytest.raises(RecoveryError):
            restore(url, binary, target, artifact, latest_path, phrase)
        with pytest.raises(RecoveryError):
            restore(url, binary, "production", artifact, latest_path, phrase)
        with pytest.raises(RecoveryError):
            restore(
                url, binary, "ada_restore_wrong", artifact, latest_path, "wrong synthetic phrase"
            )
        (tmp_path / "recovery-metrics.json").write_text(
            json.dumps(
                {
                    "backup_seconds": receipt["seconds"],
                    "restore_seconds": recovered["seconds"],
                    "snapshot_at": receipt["snapshot_at"],
                    "measured_at": int(time.time() * 1000),
                    "tables": receipt["tables"],
                    "data_loss_boundary": "committed exported snapshot; latest supplied deletion ledger",
                }
            )
        )
    engine.dispose()
