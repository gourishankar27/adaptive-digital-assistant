"""Research snapshots use the released erasure/encrypted recovery inventory."""

import json
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from test_recovery import recovery_database  # noqa: F401
from test_web_research import PublicFixtureBroker, approve, prepare

from ada.agent_models import AgentApproval, AgentReceipt, AgentRun, AgentStep
from ada.api import create_app
from ada.auth import create_user, rotate_token
from ada.config import Settings
from ada.db import connect
from ada.operations import backup, deletion_ledger, restore, write_artifact
from ada.providers import FakeProvider


def test_research_is_erased_with_all_approved_urls_and_exact_snapshots(harness):
    h = harness
    _, _, _, run = prepare(h)
    assert approve(h, run)[0].status_code == 200
    assert (
        h["client"].post(f"/v1/research-runs/{run['id']}/answer", headers=h["a"]).status_code == 200
    )
    h["settings"].deletion_worker_enabled = True
    service = h["app"].state.deletion
    preview = service.preview(h["a_id"])
    service.confirm(h["a_id"], str(uuid4()), preview["id"])
    assert service.process_one()
    with h["sessions"]() as db:
        for model in (AgentRun, AgentStep, AgentApproval, AgentReceipt):
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.owner_id == h["a_id"])
                )
                == 0
            )


def test_populated_research_encrypted_restore_preserves_sources_and_revokes_credentials(
    recovery_database,  # noqa: F811
    tmp_path,
):
    url, binary, owned = recovery_database
    engine, sessions = connect(url)
    settings = Settings(database_url=url, provider="fake", consolidation_worker_enabled=False)
    owner, token = create_user(sessions, "Public research recovery owner")
    app = create_app(settings, FakeProvider(), sessions)
    app.state.research.broker = PublicFixtureBroker()
    try:
        with TestClient(app) as client:
            headers = {"Authorization": "Bearer " + token}
            profile = client.post("/v1/personalities", headers=headers, json={}).json()
            conv = client.post(
                "/v1/conversations", headers=headers, json={"personality_id": profile["id"]}
            ).json()
            run = client.post(
                f"/v1/conversations/{conv['id']}/research-runs",
                headers=headers,
                json={
                    "id": str(uuid4()),
                    "question": "Public ZoneInfo question",
                    "kind": "fetch",
                    "target": "https://docs.python.org/3/library/zoneinfo.html",
                },
            ).json()
            preview = run["calls"][0]["preview"]
            path = "/v1/research-runs/" + run["id"]
            assert (
                client.post(
                    path + "/approve",
                    headers=headers,
                    json={
                        "id": str(uuid4()),
                        "call_id": preview["id"],
                        "preview_hash": preview["preview_hash"],
                    },
                ).status_code
                == 200
            )
            completed = client.post(path + "/answer", headers=headers).json()
            assert completed["state"] == "completed"
        phrase = "Public synthetic research recovery passphrase"
        artifact = backup(url, binary, tmp_path, phrase, settings)
        with sessions() as db:
            ledger = deletion_ledger(db.connection())
        ledger_path = write_artifact(
            tmp_path / "ledger.adaenc", json.dumps(ledger).encode(), phrase
        )
        target = "ada_restore_" + uuid4().hex[:12]
        owned.append(target)
        restore(url, binary, target, artifact["artifact"], ledger_path, phrase)
        restored_url = make_url(url).set(database=target).render_as_string(hide_password=False)
        restored_engine, restored_sessions = connect(restored_url)
        try:
            restored = create_app(settings, FakeProvider(), restored_sessions)
            with TestClient(restored) as client:
                assert client.get(path, headers=headers).status_code == 401
                fresh = rotate_token(restored_sessions, "Public research recovery owner")
                response = client.get(path, headers={"Authorization": "Bearer " + fresh})
                assert response.status_code == 200 and response.json() == completed
                card = completed["citations"][0]
                assert (
                    client.get(
                        path + "/sources/" + card["receipt_id"],
                        headers={"Authorization": "Bearer " + fresh},
                    ).json()["citation"]
                    == card
                )
        finally:
            restored_engine.dispose()
    finally:
        engine.dispose()
