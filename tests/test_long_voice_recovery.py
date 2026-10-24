"""New narrative lineage survives encrypted native restore and owner erasure."""

# ruff: noqa: F811 -- explicit imported pytest fixture.
import json
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from test_long_voice import body, post
from test_recovery import recovery_database  # noqa: F401
from test_security import conversation
from test_streaming import ControlledStream, wait_state

from ada.api import create_app
from ada.auth import create_user, rotate_token
from ada.config import Settings
from ada.db import connect
from ada.long_voice import LongVoiceInput
from ada.operations import backup, deletion_ledger, read_artifact, restore, unpack, write_artifact


def test_native_narrative_restore_replay_and_latest_owner_deletion(recovery_database, tmp_path):
    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    owner, token = create_user(sessions, "Public narrative recovery owner")
    settings = Settings(database_url=url, provider="fake", consolidation_worker_enabled=False)
    provider = ControlledStream()
    provider.release.set()
    app = create_app(settings, provider, sessions)
    phrase = "Public narrative encrypted recovery fixture"
    try:
        with TestClient(app) as client:
            h = {"client": client, "app": app, "a": {"Authorization": "Bearer " + token}}
            cid = conversation(h)["id"]
            value = body()
            assert post(h, cid, value).status_code == 202
            original = wait_state(h, value["request_id"], "completed")
            route = f"/v1/requests/{value['request_id']}/long-voice-input"
            lineage = client.get(route, headers=h["a"]).json()
            artifact = backup(url, binary, tmp_path, phrase, settings)["artifact"]
            manifest, _ = unpack(read_artifact(artifact, phrase))
            assert manifest["head"] == "0022" and "long_voice_inputs" in manifest["tables"]
            with sessions() as db:
                ledger = deletion_ledger(db.connection())
            ledger_path = write_artifact(
                tmp_path / "ledger.adaenc", json.dumps(ledger).encode(), phrase
            )
            target = "ada_restore_" + uuid4().hex[:12]
            owned.append(target)
            restore(url, binary, target, artifact, ledger_path, phrase)
            restored_url = make_url(url).set(database=target).render_as_string(hide_password=False)
            restored_engine, restored_sessions = connect(restored_url)
            try:
                rotated = rotate_token(restored_sessions, "Public narrative recovery owner")
                restored_provider = ControlledStream()
                restored_app = create_app(settings, restored_provider, restored_sessions)
                with TestClient(restored_app) as restored_client:
                    restored_h = {
                        "client": restored_client,
                        "a": {"Authorization": "Bearer " + rotated},
                    }
                    assert restored_client.get(route, headers=h["a"]).status_code == 401
                    assert restored_client.get(route, headers=restored_h["a"]).json() == lineage
                    assert post(restored_h, cid, value).status_code == 202
                    assert (
                        wait_state(restored_h, value["request_id"], "completed")["result"]
                        == original["result"]
                    )
                    assert not restored_provider.calls
            finally:
                restored_engine.dispose()
            settings.deletion_worker_enabled = True
            preview = client.post("/v1/security/deletion-previews", headers=h["a"]).json()
            assert preview["counts"]["long_voice_inputs"] == 1
            deletion = {
                "job_id": str(uuid4()),
                "preview_id": preview["id"],
                "confirmation": "erase_saved_content",
            }
            assert (
                client.post("/v1/security/deletions", headers=h["a"], json=deletion).status_code
                == 202
            )
            assert app.state.deletion.process_one()
            with sessions() as db:
                assert db.scalar(select(func.count()).select_from(LongVoiceInput)) == 0
                latest = deletion_ledger(db.connection())
            latest_path = write_artifact(
                tmp_path / "latest.adaenc", json.dumps(latest).encode(), phrase
            )
            erased_target = "ada_restore_" + uuid4().hex[:12]
            owned.append(erased_target)
            restore(url, binary, erased_target, artifact, latest_path, phrase)
            erased_engine, erased_sessions = connect(
                make_url(url).set(database=erased_target).render_as_string(hide_password=False)
            )
            try:
                with erased_sessions() as db:
                    assert (
                        db.scalar(
                            select(func.count())
                            .select_from(LongVoiceInput)
                            .where(LongVoiceInput.owner_id == owner)
                        )
                        == 0
                    )
            finally:
                erased_engine.dispose()
    finally:
        engine.dispose()
