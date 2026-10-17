"""Loopback browser fixture: dedicated PostgreSQL database, disposable schema only.

Credentials arrive in environment variables; no recording or remote fixture controls.
The local role action uses the same grant service as ADA's operator CLI.
"""

import argparse
import os
import re
import socket
from pathlib import Path
from uuid import uuid4

import uvicorn
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, text, update
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

from ada.admin import set_admin_grant
from ada.api import create_app
from ada.auth import token_hash
from ada.config import Settings
from ada.db import connect
from ada.models import Request, RetrievalTrace, User
from ada.providers import FakeProvider, OllamaProvider

OPERATORS = ["00000000-0000-0000-0000-000000000201", "00000000-0000-0000-0000-000000000202"]
OWNERS = ["00000000-0000-0000-0000-000000000101", "00000000-0000-0000-0000-000000000102"]
SHARED_REQUEST = "00000000-0000-0000-0000-000000000010"
FAILED_REQUEST = "00000000-0000-0000-0000-000000000011"
ROOT = Path(__file__).resolve().parents[1]


def test_database():
    schema = os.environ.get("ADA_WEB_TEST_SCHEMA", "")
    if not re.fullmatch(r"ada_web_test_[0-9a-f]{32}", schema):
        raise SystemExit("Supply a unique disposable ADA_WEB_TEST_SCHEMA.")
    explicit = os.environ.get("ADA_TEST_DATABASE_URL")
    url = make_url(explicit or Settings(_env_file=ROOT / ".env").database_url)
    if url.get_backend_name() != "postgresql":
        raise SystemExit("Browser integration requires dedicated PostgreSQL.")
    if explicit and url.database != "ada_phase2_test":
        raise SystemExit("ADA_TEST_DATABASE_URL must name ada_phase2_test.")
    # Never connect to the application DB: derive only its local connection settings.
    url = url.set(database="ada_phase2_test").difference_update_query(["options"])
    scoped = url.update_query_dict({"options": f"-csearch_path={schema}"})
    return schema, url, scoped.render_as_string(hide_password=False)


def drop_schema():
    schema, raw, _ = test_database()
    engine = create_engine(raw)
    try:
        with engine.begin() as db:
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
    finally:
        engine.dispose()


def seed(sessions, url, failed_provider):
    credentials = [
        os.environ.get(key, "")
        for key in (
            "ADA_WEB_TEST_TOKEN",
            "ADA_WEB_TEST_SECOND_TOKEN",
            "ADA_WEB_TEST_ORDINARY_TOKEN",
        )
    ]
    if any(not token or len(token) > 200 for token in credentials):
        raise SystemExit("Supply ephemeral browser test credentials in the environment.")
    with sessions.begin() as db:
        for index, (identity, credential) in enumerate(
            zip([*OPERATORS, OWNERS[0]], credentials, strict=True)
        ):
            db.add(
                User(
                    id=identity, name=f"Browser fixture {index}", token_hash=token_hash(credential)
                )
            )
        db.add(
            User(id=OWNERS[1], name="Browser fixture owner 2", token_hash=token_hash(uuid4().hex))
        )
    for identity in OPERATORS:
        set_admin_grant(sessions, identity, True)
    settings = Settings(
        database_url=url, provider="fake", max_parallel=1, consolidation_worker_enabled=False
    )
    app = create_app(settings, FakeProvider(), sessions)
    if os.environ.get("ADA_WEB_TEST_PASSWORD"):
        app.state.passwords.set_password(
            OPERATORS[0], "synthetic-admin", os.environ["ADA_WEB_TEST_PASSWORD"]
        )
        app.state.passwords.set_password(
            OPERATORS[1], "synthetic-admin-two", os.environ["ADA_WEB_TEST_PASSWORD"]
        )
        app.state.passwords.set_password(
            OWNERS[0], "synthetic-owner", os.environ["ADA_WEB_TEST_PASSWORD"]
        )
    with TestClient(app) as client:
        # Synthetic owners are seeded using actual owned HTTP contracts.
        for index, identity in enumerate(OWNERS):
            credential = credentials[2] if index == 0 else uuid4().hex
            if index == 1:
                with sessions.begin() as db:
                    db.get(User, identity).token_hash = token_hash(credential)
            headers = {"Authorization": f"Bearer {credential}"}
            personality = client.post("/v1/personalities", headers=headers, json={})
            assert personality.status_code == 201
            conversation = client.post(
                "/v1/conversations",
                headers=headers,
                json={"personality_id": personality.json()["id"]},
            )
            assert conversation.status_code == 201
            conversation_id = conversation.json()["id"]
            job = client.post(
                f"/v1/scopes/{conversation.json()['scope_id']}/consolidation-jobs",
                headers=headers,
                json={"job_id": str(uuid4()), "kind": "lexical_rebuild", "sources": []},
            )
            assert job.status_code == 201
            if index == 0:
                assert app.state.consolidation.run_once()
            for request in [
                SHARED_REQUEST,
                *([str(uuid4()) for _ in range(12)] if index == 0 else []),
            ]:
                response = client.post(
                    f"/v1/conversations/{conversation_id}/messages",
                    headers=headers,
                    json={
                        "request_id": request,
                        "content": "Synthetic browser verification input.",
                    },
                )
                assert response.status_code == 200
            if index == 1:
                with TestClient(create_app(settings, failed_provider, sessions)) as failed_client:
                    response = failed_client.post(
                        f"/v1/conversations/{conversation_id}/messages",
                        headers=headers,
                        json={
                            "request_id": FAILED_REQUEST,
                            "content": "Synthetic provider failure verification.",
                        },
                    )
                    assert response.status_code == 502
    # Explicit missing-trace fixture; never alter application history.
    with sessions.begin() as db:
        db.execute(
            delete(RetrievalTrace).where(
                RetrievalTrace.owner_id == OWNERS[1], RetrievalTrace.request_id == SHARED_REQUEST
            )
        )
        db.execute(
            update(Request)
            .where(Request.owner_id == OWNERS[0], Request.id == SHARED_REQUEST)
            .values(input_tokens=0, output_tokens=0)
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=18763)
    parser.add_argument("--action", choices=["revoke", "grant", "cleanup"])
    args = parser.parse_args()
    if args.action == "cleanup":
        drop_schema()
        return
    schema, raw, url = test_database()
    if args.action:
        engine, sessions = connect(url)
        try:
            set_admin_grant(sessions, OPERATORS[0], args.action == "grant")
        finally:
            engine.dispose()
        return
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    engine = create_engine(raw)
    try:
        with engine.begin() as db:
            db.execute(text(f'CREATE SCHEMA "{schema}"'))
    finally:
        engine.dispose()
    app_engine = None
    try:
        os.environ["ADA_DATABASE_URL"] = url
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        app_engine, sessions = connect(url)
        # Bind without listening: actual local TCP connection refusal, no live model.
        with socket.socket() as unavailable:
            unavailable.bind(("127.0.0.1", 0))
            settings = Settings(
                database_url=url,
                provider="ollama",
                ollama_url=f"http://127.0.0.1:{unavailable.getsockname()[1]}",
                ollama_model="browser-test-unavailable",
                max_parallel=1,
                consolidation_worker_enabled=False,
            )
            provider = OllamaProvider(settings)
            seed(sessions, url, provider)
            uvicorn.run(
                create_app(settings, provider, sessions),
                host="127.0.0.1",
                port=args.port,
                workers=1,
                access_log=False,
                log_level="error",
            )
    finally:
        if app_engine:
            app_engine.dispose()
        drop_schema()


if __name__ == "__main__":
    try:
        main()
    except SQLAlchemyError:
        raise SystemExit(
            "Disposable PostgreSQL verification failed. Check test connectivity."
        ) from None
