"""Frozen public catalogue/relevance/source/feedback checks in disposable SQLite.

--native adds one installed loopback Ollama answer; no download, web request,
application database, real owner history or inferred helpfulness rating.
"""

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.curiosity_contracts import CuriositySettings
from ada.db import connect
from ada.evidence import record_source
from ada.models import Claim, Event, SourceVersion
from ada.providers import FakeProvider, OllamaProvider
from ada.schema import SCHEMA_HEAD

ROOT = Path(__file__).resolve().parents[1]


def evaluate(output, native=False):
    corpus = ROOT / "evaluations/curiosity-cases-v1.json"
    cases = json.loads(corpus.read_text(encoding="utf-8"))
    native_settings, model = None, None
    if native:
        native_settings = Settings()
        origin = urlsplit(native_settings.ollama_url)
        if origin.hostname not in ("127.0.0.1", "localhost") or origin.scheme != "http":
            raise ValueError("Only installed loopback Ollama is eligible")
        tags = httpx.get(native_settings.ollama_url + "/api/tags", timeout=5).json()["models"]
        model = next(item for item in tags if item["name"] == native_settings.ollama_model)
    report = {
        "version": "ada-curiosity-results-v1",
        "corpus_sha256": hashlib.sha256(corpus.read_bytes()).hexdigest(),
        "schema": SCHEMA_HEAD,
        "generator": "ada-question-catalog-v1",
        "results": [],
        "native": None,
        "limits": "Topic/trace assertions and synthetic feedback; not independent relevance, factual entailment or real owner helpfulness. One optional native sample is not general model quality.",
    }
    prior = os.environ.get("ADA_DATABASE_URL")
    cache = ROOT / ".pytest_cache/phase25"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        for group in ("development", "holdout"):
            for case in cases[group]:
                with tempfile.TemporaryDirectory(
                    prefix="curiosity-public-", dir=cache
                ) as directory:
                    assert Path(directory).resolve().is_relative_to(cache.resolve())
                    url = "sqlite:///" + (Path(directory) / "ada.db").as_posix()
                    os.environ["ADA_DATABASE_URL"] = url
                    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
                    engine, sessions = connect(url)
                    use_native = native and case["kind"] == "answer"
                    settings = Settings(
                        _env_file=None,
                        database_url=url,
                        provider="ollama" if use_native else "fake",
                        consolidation_worker_enabled=False,
                        ollama_url=native_settings.ollama_url
                        if use_native
                        else "http://127.0.0.1:11434",
                        ollama_model=native_settings.ollama_model
                        if use_native
                        else "deterministic-test-v1",
                    )
                    provider = OllamaProvider(settings) if use_native else FakeProvider()
                    app = create_app(settings, provider, sessions)
                    owner, token = create_user(sessions, "Public curiosity case owner")
                    headers = {"Authorization": "Bearer " + token}
                    try:
                        with TestClient(app) as client:

                            def get(path):
                                response = client.get(path, headers=headers)
                                assert response.status_code == 200
                                return response.json()

                            def post(path, body, expected=200):
                                response = client.post(path, headers=headers, json=body)
                                assert response.status_code == expected
                                return response.json()

                            profile = post("/v1/personalities", {}, 201)
                            conv = post("/v1/conversations", {"personality_id": profile["id"]}, 201)
                            options = CuriositySettings(
                                enabled=True, frequency="every_reply"
                            ).model_dump()
                            if case["kind"] == "personal":
                                options["depth"] = "personal"
                                options["topics"][case["topic"]] = "enabled"
                            policy = post(
                                "/v1/curiosity/policy",
                                {
                                    "operation_id": str(uuid4()),
                                    "expected_revision": 0,
                                    "settings": options,
                                },
                            )
                            body = {
                                "operation_id": str(uuid4()),
                                "policy_revision": policy["policy_revision"],
                                "channel": "inbox",
                                "topic": case["topic"],
                            }
                            sid = None
                            if case["kind"] in ("source", "stale"):
                                with sessions.begin() as db:
                                    source = record_source(
                                        db,
                                        owner=owner,
                                        scope_id=conv["scope_id"],
                                        content=case["text"],
                                        kind="user_note",
                                    )
                                    sid = source.id
                                body["source"] = {
                                    "source_version_id": sid,
                                    "span_start": 0,
                                    "span_end": len(case["text"]),
                                }
                            if case["kind"] == "chat":
                                rid = str(uuid4())
                                post(
                                    f"/v1/conversations/{conv['id']}/messages",
                                    {"request_id": rid, "content": case["text"]},
                                )
                                body.update(channel="chat", request_id=rid)
                            path = f"/v1/scopes/{conv['scope_id']}/curiosity/questions"
                            result = post(path, body, 409 if case["kind"] == "blocked" else 200)
                            checks = {"topic_permission": True}
                            if case["kind"] != "blocked":
                                qpath = "/v1/curiosity/questions/" + result["question_id"]
                                q = get(qpath)
                                checks.update(
                                    single_catalogue_question=q["text"].count("?") == 1,
                                    relevant_topic=q["topic"] == case["topic"],
                                )
                                if sid:
                                    pin = q["source"]
                                    checks["exact_original_premise"] = (
                                        pin["quote"] == case["text"]
                                        and pin["content_hash"]
                                        == hashlib.sha256(case["text"].encode()).hexdigest()
                                    )
                                else:
                                    checks["no_inferred_premise"] = q["source"] is None
                                if case["kind"] == "stale":
                                    with sessions.begin() as db:
                                        db.get(SourceVersion, sid).content_hash = "0" * 64
                                    checks["stale_premise_hidden"] = get(qpath)["text"] is None
                                if case["kind"] == "repeat":
                                    post(
                                        qpath + "/actions",
                                        {"operation_id": str(uuid4()), "action": "skip"},
                                    )
                                    second = post(path, body | {"operation_id": str(uuid4())})
                                    checks["not_repeated_after_skip"] = (
                                        get("/v1/curiosity/questions/" + second["question_id"])[
                                            "text"
                                        ]
                                        != q["text"]
                                    )
                                    checks["skip_measured"] = (
                                        get("/v1/curiosity/metrics")["skipped"] == 1
                                    )
                                if case["kind"] == "answer":
                                    cid = str(uuid4())
                                    post(
                                        qpath + "/open",
                                        {
                                            "operation_id": str(uuid4()),
                                            "conversation_id": cid,
                                            "personality_id": profile["id"],
                                        },
                                    )
                                    checks["opening_did_not_invent_user"] = (
                                        get(f"/v1/conversations/{cid}/events") == []
                                    )
                                    answer = {
                                        "operation_id": str(uuid4()),
                                        "request_id": str(uuid4()),
                                        "text": case["text"],
                                    }
                                    response = post(qpath + "/answer", answer)
                                    checks["ordinary_answer_completed"] = (
                                        response["state"] == "completed"
                                    )
                                    checks["duplicate_answer_replay"] = (
                                        post(qpath + "/answer", answer) == response
                                    )
                                    events = get(f"/v1/conversations/{cid}/events")
                                    checks["one_exact_owner_statement"] = [
                                        e["content"] for e in events if e["role"] == "user"
                                    ] == [case["text"]]
                                    post(
                                        qpath + "/actions",
                                        {"operation_id": str(uuid4()), "action": "helpful"},
                                    )
                                    metrics = get("/v1/curiosity/metrics")
                                    checks["synthetic_feedback_measured"] = (
                                        metrics["answered"] == metrics["helpful"] == 1
                                    )
                                    if use_native:
                                        saved = get("/v1/requests/" + answer["request_id"])
                                        (cache / "native-public-answer.txt").write_text(
                                            saved["response"], encoding="utf-8"
                                        )
                                        report["native"] = {
                                            "model": model["name"],
                                            "digest": model["digest"],
                                            "completed_replay": True,
                                            "sample_count": 1,
                                        }
                                with sessions() as db:
                                    checks["no_factual_claims"] = (
                                        db.scalar(select(func.count()).select_from(Claim)) == 0
                                    )
                                    checks["no_invented_user_events"] = (
                                        case["kind"] in ("chat", "answer")
                                        or db.scalar(
                                            select(func.count())
                                            .select_from(Event)
                                            .where(Event.role == "user")
                                        )
                                        == 0
                                    )
                            assert all(checks.values())
                            report["results"].append(
                                {"id": case["id"], "set": group, "checks": checks, "passed": True}
                            )
                    finally:
                        engine.dispose()
    finally:
        if prior is None:
            os.environ.pop("ADA_DATABASE_URL", None)
        else:
            os.environ["ADA_DATABASE_URL"] = prior
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"public_cases_passed": len(report["results"]), "native": report["native"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "evaluations/curiosity-results-v1.json"
    )
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args()
    try:
        evaluate(args.output, args.native)
    except Exception:
        parser.exit(1, "Public curiosity evaluation failed; private diagnostics suppressed.\n")
