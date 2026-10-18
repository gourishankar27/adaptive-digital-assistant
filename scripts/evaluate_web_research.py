"""Explicit public pilot: isolated broker -> immutable W snapshot -> local native answer.

Only a dedicated disposable test database and already installed local model are used.
No application data, model download, live server restart or deployment.
"""

import argparse
import json
import os
from pathlib import Path
from uuid import uuid4

import httpx
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.evidence import content_hash
from ada.providers import OllamaProvider
from ada.schema import SCHEMA_HEAD
from ada.web_broker import DockerWebBroker

ROOT = Path(__file__).resolve().parents[1]


def evaluate(manifest, output):
    parsed = make_url(os.environ["ADA_TEST_DATABASE_URL"])
    if parsed.database != "ada_phase2_test" or parsed.get_backend_name() != "postgresql":
        raise ValueError("Dedicated PostgreSQL fixture required")
    settings = Settings(
        consolidation_worker_enabled=False,
        deletion_worker_enabled=False,
        web_research_enabled=False,
    )
    if settings.ollama_url != "http://127.0.0.1:11434":
        raise ValueError("Installed loopback model required")
    tags = httpx.get(settings.ollama_url + "/api/tags", trust_env=False, timeout=5).json()["models"]
    model = next((m for m in tags if m["name"] == settings.ollama_model), None)
    if model is None:
        raise ValueError("Installed model required; no download")
    broker = DockerWebBroker(manifest)
    if not broker.available:
        raise ValueError("Isolated broker required")
    schema = "ada_research24_" + uuid4().hex
    admin = create_engine(parsed)
    engine = None
    prior = os.environ.get("ADA_DATABASE_URL")
    try:
        with admin.begin() as db:
            db.execute(text(f'CREATE SCHEMA "{schema}"'))
        url = parsed.update_query_dict({"options": "-csearch_path=" + schema}).render_as_string(
            hide_password=False
        )
        os.environ["ADA_DATABASE_URL"] = url
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        settings.database_url = url
        engine, sessions = connect(url)
        _, token = create_user(sessions, "Public synthetic research validation")
        app = create_app(settings, OllamaProvider(settings), sessions)
        app.state.research.broker = broker
        with TestClient(app) as client:
            headers = {"Authorization": "Bearer " + token}

            def post(path, body):
                response = client.post(path, headers=headers, json=body)
                if response.status_code != 200 and response.status_code != 201:
                    raise ValueError("Synthetic research HTTP failure")
                return response.json()

            profile = post("/v1/personalities", {})
            conv = post("/v1/conversations", {"personality_id": profile["id"]})
            run = post(
                f"/v1/conversations/{conv['id']}/research-runs",
                {
                    "id": str(uuid4()),
                    "question": "Which timezone database does Python ZoneInfo use?",
                    "kind": "fetch",
                    "target": "https://docs.python.org/3/library/zoneinfo.html",
                },
            )
            preview = run["calls"][0]["preview"]
            path = "/v1/research-runs/" + run["id"]
            ready = post(
                path + "/approve",
                {
                    "id": str(uuid4()),
                    "call_id": preview["id"],
                    "preview_hash": preview["preview_hash"],
                },
            )
            if ready["state"] != "ready" or not ready["citations"]:
                raise ValueError("Public pilot inaccessible; no model answer attempted")
            card = ready["citations"][0]
            snapshot = client.get(path + "/sources/" + card["receipt_id"], headers=headers).json()
            ev = card["evidence"]
            assert content_hash(snapshot["text"]) == ev["content_hash"]
            assert snapshot["text"][ev["span_start"] : ev["span_end"]] == ev["quote"]
            completed = post(path + "/answer", {})
            assert completed["state"] == "completed"
            assert post(path + "/answer", {}) == completed
            assert client.get(path, headers=headers).json() == completed
            answer = completed["response"]
            report = {
                "version": "ada-web-native-pilot-v1",
                "model": model["name"],
                "digest": model["digest"],
                "image_id": broker.image,
                "backend": "postgresql18",
                "schema_head": SCHEMA_HEAD,
                "exact_source_verified": True,
                "completed_replay_equal": True,
                "native_answer_mentions_iana": "IANA" in answer,
                "native_answer_uses_w1": "[W1]" in answer,
                "citation_warnings": completed["citation_warnings"],
                "limits": "One public native pilot; markers are not general accuracy/entailment or injection-proofing",
            }
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report))
    finally:
        if engine is not None:
            engine.dispose()
        with admin.begin() as db:
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        admin.dispose()
        if prior is None:
            os.environ.pop("ADA_DATABASE_URL", None)
        else:
            os.environ["ADA_DATABASE_URL"] = prior


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".pytest_cache/web-native-pilot.json"))
    args = parser.parse_args()
    try:
        evaluate(args.manifest, args.output)
    except Exception:
        parser.exit(
            1, "Public research pilot could not be verified; private diagnostics suppressed.\n"
        )
