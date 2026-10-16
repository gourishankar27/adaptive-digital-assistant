"""Phase20 pre-upgrade recovery; all databases and content are disposable."""

import hashlib
import io
import json
import zipfile
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Column, String, Table, create_engine, event, text
from sqlalchemy.engine import Engine, make_url
from test_recovery import recovery_database as recovery_database

from ada.api import create_app
from ada.auth import create_user, rotate_token
from ada.config import Settings
from ada.db import connect
from ada.inventory import content_tables
from ada.models import Base
from ada.operations import RecoveryError, backup, read_artifact, unpack, write_artifact
from ada.providers import Completion, FakeProvider


def archive(manifest, dump=b"synthetic dump"):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as bundle:
        bundle.writestr("manifest.json", json.dumps(manifest))
        bundle.writestr("database.dump", dump)
    return output.getvalue()


def test_legacy_format_cannot_be_misread_as_current_or_unknown():
    from ada.legacy_recovery import unpack_0005

    dump = b"synthetic dump"
    manifest = {
        "format": "ada-postgres-legacy-0005-v1",
        "head": "0005",
        "tables": {},
        "dump_sha256": hashlib.sha256(dump).hexdigest(),
        "snapshot_at": 1,
    }
    assert unpack_0005(archive(manifest))[0] == manifest
    with pytest.raises(RecoveryError):
        unpack(archive(manifest))
    for changed in (
        {"head": "0016"},
        {"format": "ada-postgres-backup-v1"},
        {"dump_sha256": "0" * 64},
        {"tables": []},
    ):
        with pytest.raises(RecoveryError):
            unpack_0005(archive(manifest | changed))
    with pytest.raises(RecoveryError):
        unpack_0005(archive([]))


def test_unknown_owner_table_requires_explicit_erasure_classification():
    from ada.errors import ServiceError

    table = Table(
        "unclassified_phase20_fixture",
        Base.metadata,
        Column("owner_id", String(36), primary_key=True),
    )
    try:
        with pytest.raises(ServiceError, match="deletion_inventory_unavailable"):
            content_tables()
    finally:
        Base.metadata.remove(table)


def test_recovery_policy_rejects_unreviewed_heads_and_tables():
    from ada.recovery_policy import validate_inventory

    with pytest.raises(RecoveryError):
        validate_inventory("0016", set())
    with pytest.raises(RecoveryError):
        validate_inventory("0005", {"users", "alembic_version", "unknown_private_table"})


def test_postgresql_binary_major_is_checked_before_dump(monkeypatch):
    import ada.operations as operations

    class Connection:
        def execute(self, *_):
            return self

        def scalar_one(self):
            return "180006"

    monkeypatch.setattr(operations, "pg_tool", lambda *_: b"pg_dump (PostgreSQL) 17.9")
    with pytest.raises(RecoveryError):
        operations.check_pg_tools(Connection(), Path("synthetic-bin"), {})


def test_current_unpack_rejects_malformed_manifest_without_database_access():
    for manifest in ([], None, {"format": "ada-postgres-backup-v1", "head": "0016"}):
        with pytest.raises(RecoveryError):
            unpack(archive(manifest))


def test_encrypted_write_failure_is_never_a_success_receipt(tmp_path, monkeypatch):
    import ada.operations as operations

    def full_disk(_):
        raise OSError("synthetic disk full")

    monkeypatch.setattr(operations.os, "fsync", full_disk)
    with pytest.raises(OSError):
        operations.write_artifact(
            tmp_path / "partial.adaenc", b"synthetic", "Synthetic phrase only"
        )


def test_legacy_populated_restore_then_upgrade_preserves_replay(
    recovery_database, tmp_path, monkeypatch
):
    from test_document_api import upload
    from test_memory import add, note
    from test_security import conversation

    from ada.legacy_recovery import backup_0005, restore_0005, unpack_0005

    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    settings = Settings(database_url=url, provider="fake", consolidation_worker_enabled=False)
    owner, token = create_user(sessions, "Legacy fixture owner")

    class CitingFixture(FakeProvider):
        def complete(self, messages):
            return Completion("Synthetic saved reference [M1].", self.model)

    with TestClient(create_app(settings, CitingFixture(), sessions)) as client:
        h = {
            "client": client,
            "sessions": sessions,
            "a_id": owner,
            "a": {"Authorization": "Bearer " + token},
        }
        conv = conversation(h)
        source = note(h, conv["scope_id"], "Synthetic legacy atlas uses cobalt.")
        assert (
            add(
                h, conv["scope_id"], source, subject="atlas", predicate="color", value="cobalt"
            ).status_code
            == 201
        )
        assert (
            upload(h, conv["scope_id"], b"Synthetic legacy document cobalt.\n").status_code == 201
        )
        body = {"request_id": str(uuid4()), "content": "Synthetic atlas color cobalt"}
        saved = client.post(f"/v1/conversations/{conv['id']}/messages", headers=h["a"], json=body)
        assert saved.status_code == 200
        original = saved.json()
        assert original["citations"]
    config = Config("alembic.ini")
    command.downgrade(config, "0005")
    with engine.connect() as conn:
        original_hash = conn.execute(
            text("SELECT content_hash FROM source_versions WHERE id=:id"), {"id": source["id"]}
        ).scalar_one()
        original_rows = conn.execute(text("SELECT count(*) FROM requests")).scalar_one()
    phrase = "Synthetic legacy recovery phrase only"
    with pytest.raises(RecoveryError):
        backup(url, binary, tmp_path, phrase, settings)
    receipt = backup_0005(url, binary, tmp_path, phrase)
    assert "\\" not in receipt["artifact"]
    manifest, _ = unpack_0005(read_artifact(receipt["artifact"], phrase))
    assert manifest["tables"]["requests"]["rows"] == original_rows
    assert manifest["tables"]["document_uploads"]["rows"] == 1
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE phase20_unclassified (owner_id text)"))
    try:
        with pytest.raises(RecoveryError):
            backup_0005(url, binary, tmp_path, phrase)
    finally:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE phase20_unclassified"))
    wrong = "ada_restore_legacy_" + uuid4().hex[:12]
    with pytest.raises(RecoveryError):
        restore_0005(url, binary, wrong, receipt["artifact"], "Wrong synthetic phrase only")
    with engine.connect() as conn:
        assert not conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname=:name"), {"name": wrong}
        ).first()
    target = "ada_restore_legacy_" + uuid4().hex[:12]
    owned.append(target)
    result = restore_0005(url, binary, target, receipt["artifact"], phrase)
    assert result["quarantined"] and result["reconciliation_required"]
    (tmp_path / "legacy-metrics.json").write_text(
        json.dumps(
            {
                "backup_seconds": receipt["seconds"],
                "restore_seconds": result["seconds"],
                "tables": len(manifest["tables"]),
                "requests": original_rows,
                "snapshot_at": receipt["snapshot_at"],
                "data_loss_boundary": "exported committed snapshot",
            }
        ),
        encoding="utf-8",
    )
    restored_url = make_url(url).set(database=target).render_as_string(hide_password=False)
    recovered_engine, recovered_sessions = connect(restored_url)
    try:
        with recovered_engine.connect() as conn:
            assert (
                conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0005"
            )
            assert (
                conn.execute(
                    text("SELECT content_hash FROM source_versions WHERE id=:id"),
                    {"id": source["id"]},
                ).scalar_one()
                == original_hash
            )
        monkeypatch.setenv("ADA_DATABASE_URL", restored_url)

        # Real PostgreSQL transactional DDL must roll the whole interrupted upgrade back.
        def interrupt_upgrade(conn, cursor, statement, parameters, context, executemany):
            if "CREATE TABLE expression_preferences" in statement:
                raise RuntimeError("Synthetic migration interruption")

        event.listen(Engine, "before_cursor_execute", interrupt_upgrade)
        try:
            with pytest.raises(RuntimeError, match="Synthetic migration interruption"):
                command.upgrade(config, "head")
        finally:
            event.remove(Engine, "before_cursor_execute", interrupt_upgrade)
        with recovered_engine.connect() as conn:
            assert (
                conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0005"
            )
        command.upgrade(config, "head")
        command.check(config)
        fresh = rotate_token(recovered_sessions, "Legacy fixture owner")
        with TestClient(
            create_app(
                Settings(
                    database_url=restored_url, provider="fake", consolidation_worker_enabled=False
                ),
                FakeProvider(),
                recovered_sessions,
            )
        ) as client:
            assert client.get("/v1/me", headers=h["a"]).status_code == 401
            replay = client.post(
                f"/v1/conversations/{conv['id']}/messages",
                headers={"Authorization": "Bearer " + fresh},
                json=body,
            )
            assert replay.status_code == 200 and replay.json() == original
        with pytest.raises(RecoveryError):
            restore_0005(url, binary, target, receipt["artifact"], phrase)
        with pytest.raises(RecoveryError):
            restore_0005(url, binary, "production", receipt["artifact"], phrase)
    finally:
        recovered_engine.dispose()
    # An authenticated but inconsistent manifest must leave the restored target quarantined.
    bad_manifest, dump = unpack_0005(read_artifact(receipt["artifact"], phrase))
    bad_manifest["tables"]["requests"]["sha256"] = "0" * 64
    corrupt = write_artifact(tmp_path / "inconsistent.adaenc", archive(bad_manifest, dump), phrase)
    bad_target = "ada_restore_legacy_" + uuid4().hex[:12]
    owned.append(bad_target)
    with pytest.raises(RecoveryError):
        restore_0005(url, binary, bad_target, corrupt, phrase)
    failed = create_engine(make_url(url).set(database=bad_target))
    try:
        with failed.connect() as conn:
            assert (
                conn.execute(
                    text("SELECT token_hash FROM users WHERE id=:id"), {"id": owner}
                ).scalar_one()
                != hashlib.sha256(token.encode()).hexdigest()
            )
    finally:
        failed.dispose()
    # Recovery never updates the source installation, even its credential.
    with engine.connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0005"
        assert (
            conn.execute(
                text("SELECT token_hash FROM users WHERE id=:id"), {"id": owner}
            ).scalar_one()
            == hashlib.sha256(token.encode()).hexdigest()
        )
    engine.dispose()
