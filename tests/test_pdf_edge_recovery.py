"""Native encrypted recovery retains PDF projections and revokes draft signing authority."""

# ruff: noqa: F811 -- imported pytest fixtures are explicit dependencies.

import json
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pdf_fixtures import text_pdf
from sqlalchemy import select
from sqlalchemy.engine import make_url
from test_edge_failures import enrolled, proposal, sync
from test_pdf_flow import pdf_parser, post_pdf  # noqa: F401
from test_recovery import recovery_database  # noqa: F401

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.edge_models import EdgeDevice, EdgeProposal
from ada.models import DocumentUpload, SourceVersion
from ada.operations import backup, deletion_ledger, read_artifact, restore, unpack, write_artifact
from ada.pdfs import projection_hash
from ada.providers import FakeProvider


def test_populated_0020_upgrade_preserves_old_replay_and_refuses_pdf_downgrade(harness, pdf_parser):  # noqa: F811
    from conftest import make_conversation, send

    h = harness
    command.downgrade(h["config"], "0020")
    cid, _ = make_conversation(h)
    old_id = str(uuid4())
    before = send(h, cid, "Public release compatibility fixture", old_id).json()
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, cid, "Public release compatibility fixture", old_id).json() == before
    scope = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    h["app"].state.pdfs.parser = pdf_parser
    result = post_pdf(h, scope, text_pdf())
    assert result.json()["state"] == "ready"
    with pytest.raises(RuntimeError, match="PDF history"):
        command.downgrade(h["config"], "0020")
    command.check(h["config"])
    assert send(h, cid, "Public release compatibility fixture", old_id).json() == before


def test_native_v7_pdf_original_and_device_draft_restore_quarantine(
    recovery_database, tmp_path, pdf_parser
):  # noqa: F811
    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    owner, token = create_user(sessions, "Public PDF edge recovery owner")
    settings = Settings(database_url=url, provider="fake", consolidation_worker_enabled=False)
    app = create_app(settings, FakeProvider(), sessions)
    app.state.pdfs.parser = pdf_parser
    raw = text_pdf(("Public recovery page one.", "Public recovery page two."))
    try:
        with TestClient(app) as client:
            h = {
                "app": app,
                "settings": settings,
                "sessions": sessions,
                "client": client,
                "a_id": owner,
                "a": {"Authorization": "Bearer " + token},
            }
            scope, key, device, _ = enrolled(h)
            upload = post_pdf(h, scope, raw).json()
            assert upload["state"] == "ready"
            draft = proposal(scope, key, device)
            assert sync(h, scope, draft).status_code == 200
        phrase = "Public synthetic PDF edge recovery phrase"
        artifact = backup(url, binary, tmp_path, phrase, settings)["artifact"]
        manifest, _ = unpack(read_artifact(artifact, phrase))
        assert manifest["head"] == "0022" and manifest["format"] == "ada-postgres-backup-v8"
        assert len(manifest["tables"]) == 77
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
                row = db.get(DocumentUpload, (owner, upload["id"]))
                source = db.scalar(
                    select(SourceVersion).where(SourceVersion.id == upload["source_version_id"])
                )
                assert row.raw_bytes == raw and len(row.extraction["pages"]) == 2
                assert projection_hash(row, source.content) == source.content_hash
                assert db.get(EdgeProposal, (owner, draft["proposal_id"])).output == draft["output"]
                registration = db.get(EdgeDevice, (owner, device))
                assert registration.revoked_at is not None and registration.revision == 2
        finally:
            restored_engine.dispose()
    finally:
        engine.dispose()


def test_released_0020_v6_restore_then_upgrade(recovery_database, tmp_path, monkeypatch):
    url, binary, owned = recovery_database
    config = Config("alembic.ini")
    command.downgrade(config, "0020")
    engine, sessions = connect(url)
    phrase = "Public synthetic released v6 restore phrase"
    try:
        create_user(sessions, "Public retained v6 owner")
        artifact = backup(url, binary, tmp_path, phrase, Settings(database_url=url))["artifact"]
        manifest, _ = unpack(read_artifact(artifact, phrase))
        assert (
            manifest["head"] == "0020"
            and manifest["format"] == "ada-postgres-backup-v6"
            and len(manifest["tables"]) == 74
        )
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "v6-ledger.adaenc", json.dumps(ledger).encode(), phrase
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
