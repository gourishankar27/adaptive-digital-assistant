import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.providers import Completion

ROOT = Path(__file__).resolve().parents[1]


class RecordingProvider:
    id, model = "recording", "test-v1"

    def __init__(self):
        self.calls = []
        self.error = None

    def complete(self, messages):
        self.calls.append(messages)
        if self.error:
            raise self.error
        return Completion("Answer: " + messages[-1]["content"], self.model, 10, 5)


@pytest.fixture(params=["sqlite", "postgres"])
def harness(request, tmp_path, monkeypatch):
    admin, schema = None, None
    if request.param == "postgres":
        raw = os.environ.get("ADA_TEST_DATABASE_URL")
        if not raw:
            pytest.skip("ADA_TEST_DATABASE_URL not supplied")
        schema = "ada_test_" + uuid4().hex
        admin = create_engine(raw)
        with admin.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        url = (
            make_url(raw)
            .update_query_dict({"options": f"-csearch_path={schema}"})
            .render_as_string(hide_password=False)
        )
    else:
        url = f"sqlite:///{tmp_path / 'ada.db'}"
    monkeypatch.setenv("ADA_DATABASE_URL", url)
    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")
    engine, sessions = connect(url)
    settings = Settings(
        database_url=url,
        provider="fake",
        max_parallel=2,
        consolidation_worker_enabled=False,
        scheduler_enabled=False,
        # Owner .env opt-ins must never activate real optional boundaries in fixtures.
        web_research_enabled=False,
        pdf_ingestion_enabled=False,
        edge_draft_sync_enabled=False,
    )
    provider = RecordingProvider()
    app = create_app(settings, provider, sessions)
    a_id, a_token = create_user(sessions, "Alice")
    b_id, b_token = create_user(sessions, "Bob")
    with TestClient(app) as client:
        yield {
            "client": client,
            "app": app,
            "provider": provider,
            "sessions": sessions,
            "settings": settings,
            "config": config,
            "backend": request.param,
            "a_id": a_id,
            "b_id": b_id,
            "a": {"Authorization": f"Bearer {a_token}"},
            "b": {"Authorization": f"Bearer {b_token}"},
        }
    engine.dispose()
    if admin:
        with admin.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


def make_conversation(h, who="a", **personality):
    c = h["client"]
    p = c.post("/v1/personalities", headers=h[who], json=personality)
    assert p.status_code == 201, p.text
    r = c.post("/v1/conversations", headers=h[who], json={"personality_id": p.json()["id"]})
    assert r.status_code == 201, r.text
    return r.json()["id"], p.json()["id"]


def send(h, conversation, content="hello", request_id=None, who="a"):
    return h["client"].post(
        f"/v1/conversations/{conversation}/messages",
        headers=h[who],
        json={"request_id": request_id or str(uuid4()), "content": content},
    )
