"""Phase23 public comparison in disposable data. Never evaluates application chats."""

import argparse
import hashlib
import json
import os
import statistics
import tempfile
import time
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.engine import make_url

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.evidence import content_hash
from ada.memory import ClaimInput, MemoryService, NoteInput, SupersedeInput
from ada.models import Claim, ClaimSearch, DocumentChunk, Event, Request, Scope, SourceVersion
from ada.providers import FakeProvider, OllamaProvider
from ada.schema import SCHEMA_HEAD

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "evaluations/answer-quality-phase23-v1.json"
MANIFEST = ROOT / "evaluations/answer-quality-manifest-v1.json"


def digest(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_corpus():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (
        manifest.get("version") != "ada-answer-quality-manifest-v1"
        or manifest.get("corpus") != "evaluations/answer-quality-phase23-v1.json"
        or manifest.get("sha256") != digest(CORPUS)
    ):
        raise ValueError("Frozen Phase23 corpus changed; create a new explicit version")
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    if corpus.get("version") != "ada-answer-quality-phase23-v1":
        raise ValueError("Unsupported answer-quality corpus version")
    return corpus


def seed(sessions, client, data):
    owner, token = create_user(sessions, "Synthetic Phase23 Alice " + uuid4().hex)
    bob, _ = create_user(sessions, "Synthetic Phase23 Bob " + uuid4().hex)
    headers = {"Authorization": "Bearer " + token}
    scopes = {}
    with sessions.begin() as db:
        for name, user in (("main", owner), ("other", owner), ("bob", bob)):
            row = Scope(owner_id=user, name="Public synthetic " + name, kind="project")
            db.add(row)
            db.flush()
            scopes[name] = (user, row.id)
    personality = client.post("/v1/personalities", headers=headers, json={}).json()["id"]

    def conversation():
        return client.post(
            "/v1/conversations",
            headers=headers,
            json={"personality_id": personality, "scope_id": scopes["main"][1]},
        ).json()["id"]

    memory, claims, logical = MemoryService(sessions), {}, {}
    for item in data["claims"]:
        user, sid = scopes[item.get("scope", "main")]
        if item.get("chat_source"):
            cid, rid = conversation(), str(uuid4())
            r = client.post(
                f"/v1/conversations/{cid}/messages",
                headers=headers,
                json={"request_id": rid, "content": item["quote"], "use_memory": False},
            )
            if r.status_code != 200:
                raise ValueError("Synthetic source turn failed")
            with sessions() as db:
                event = db.scalar(
                    select(Event).where(
                        Event.owner_id == user, Event.request_id == rid, Event.role == "user"
                    )
                )
                source = db.get(SourceVersion, event.id)
                source_id = source.id
        else:
            source, _ = memory.note(user, sid, NoteInput(source_id=uuid4(), content=item["quote"]))
            source_id = source["id"]
        common = dict(
            claim_id=uuid4(),
            source_version_id=source_id,
            span_start=0,
            span_end=len(item["quote"]),
            value=item["value"],
        )
        if "supersedes" in item:
            row, _ = memory.supersede(
                user,
                claims[item["supersedes"]],
                SupersedeInput(**common, effective_at=item["valid_from"]),
            )
        else:
            row, _ = memory.add(
                user,
                sid,
                ClaimInput(
                    **common,
                    subject=item["subject"],
                    predicate=item["predicate"],
                    kind="fact",
                    valid_from=item.get("valid_from", "2025-01-01T00:00:00Z"),
                ),
            )
        claims[item["key"]], logical[row["id"]] = row["id"], item["key"]
        if item.get("delete"):
            # Test-only erasure of this exact synthetic leaf, never a production operation.
            with sessions.begin() as db:
                db.execute(delete(ClaimSearch).where(ClaimSearch.claim_id == row["id"]))
                db.delete(db.get(Claim, row["id"]))
                db.flush()
                db.delete(db.get(SourceVersion, source_id))
    sid = scopes["main"][1]
    r = client.post(
        f"/v1/scopes/{sid}/documents/uploads/{uuid4()}",
        headers={**headers, "Content-Type": "text/plain"},
        params={"source_id": str(uuid4()), "filename": "synthetic-manual.txt"},
        content=data["document"].encode(),
    )
    if r.status_code != 201:
        raise ValueError("Synthetic document failed")
    with sessions() as db:
        for chunk in db.scalars(select(DocumentChunk).where(DocumentChunk.owner_id == owner)):
            logical[chunk.id] = "document"
    return owner, headers, conversation, logical


def run(sessions, settings, mode):
    data = load_corpus()
    app = create_app(settings, FakeProvider(), sessions)
    rows = []
    with TestClient(app) as client:
        owner, headers, conversation, logical = seed(sessions, client, data)
        histories = {}
        for version in ("ada-baseline-v4", "ada-baseline-v5"):
            cid = conversation()
            histories[version] = cid
            original = (
                "The LARKSPUR archive validation code is SAPPHIRE47. "
                + "This is volatile context for this chat only. " * 5
            )
            for index in range(19):
                content = (
                    original
                    if index == 0
                    else f"Unrelated synthetic row {index}. "
                    + "General weather discussion and ordinary filler. " * 3
                )
                r = client.post(
                    f"/v1/conversations/{cid}/messages",
                    headers=headers,
                    json={"request_id": str(uuid4()), "content": content, "use_memory": False},
                )
                if r.status_code != 200:
                    raise ValueError("Synthetic history seed failed")
        app.state.chat.provider = OllamaProvider(settings) if mode == "ollama" else FakeProvider()
        for case in data["cases"]:
            for version in ("ada-baseline-v4", "ada-baseline-v5"):
                cid = histories[version] if case.get("history") else conversation()
                if version.endswith("v5"):
                    r = client.post(f"/v1/conversations/{cid}/quality-upgrade", headers=headers)
                    if r.status_code != 200:
                        raise ValueError("Synthetic upgrade failed")
                body = {
                    "request_id": str(uuid4()),
                    "content": case["query"] + " Answer in at most two sentences.",
                    "use_documents": bool(case.get("documents")),
                }
                if not case.get("natural_time"):
                    body["as_of"] = case.get("as_of", data["as_of"])
                started = time.perf_counter()
                response = client.post(
                    f"/v1/conversations/{cid}/messages", headers=headers, json=body
                )
                elapsed = (time.perf_counter() - started) * 1000
                if response.status_code != 200:
                    raise ValueError("Synthetic generation failed")
                result = response.json()
                trace = client.get(
                    f"/v1/requests/{body['request_id']}/retrieval", headers=headers
                ).json()
                cards = trace["selected"] + trace["document_selected"]
                found = [
                    logical.get(c.get("claim_id", c.get("chunk_id")), "unexpected") for c in cards
                ]
                with sessions() as db:
                    request = db.get(Request, (owner, body["request_id"]))
                    history_found = bool(
                        case.get("history_marker")
                        and any(
                            case["history_marker"] in m["content"] for m in request.messages[:-1]
                        )
                    )
                    for card in cards:
                        ev = card["evidence"]
                        source = db.get(SourceVersion, ev["source_version_id"])
                        if (
                            source is None
                            or source.owner_id != owner
                            or source.scope_id != trace["scope_id"]
                        ):
                            raise ValueError("Owner/scope invariant failed")
                        if (
                            source.content[ev["span_start"] : ev["span_end"]] != ev["quote"]
                            or content_hash(source.content) != ev["content_hash"]
                        ):
                            raise ValueError("Exact evidence invariant failed")
                    prompt_bytes = sum(len(m["content"].encode()) + 64 for m in request.messages)
                if set(found) & set(case.get("forbidden", [])):
                    raise ValueError("Forbidden source reached context")
                expected = set(case["expected"])
                recall = len(expected & set(found)) / len(expected) if expected else None
                rr = (
                    next((1 / index for index, key in enumerate(found, 1) if key in expected), 0)
                    if expected
                    else None
                )
                row = dict(
                    case=case["id"],
                    split=case["split"],
                    prompt=version,
                    selected=found,
                    citation_map={card["label"]: key for card, key in zip(cards, found)},
                    expected=case["expected"],
                    recall=recall,
                    reciprocal_rank=rr,
                    exact_spans=True,
                    latency_ms=round(elapsed, 3),
                    prompt_bytes=prompt_bytes,
                    history_marker_supplied=history_found,
                    answer=result["response"],
                    usefulness=None,
                    citation_entailment=None,
                    uncertainty=None,
                    rubric=case["rubric"],
                    context_failure="insufficient_context"
                    if (expected and recall < 1) or (case.get("history") and not history_found)
                    else None,
                )
                rows.append(row)
                print(
                    json.dumps({"case": case["id"], "prompt": version, "status": "completed"}),
                    flush=True,
                )
    summary = {}
    for split in ("development", "holdout"):
        summary[split] = {}
        for version in ("ada-baseline-v4", "ada-baseline-v5"):
            group = [r for r in rows if r["split"] == split and r["prompt"] == version]
            positive = [r for r in group if r["recall"] is not None]
            times = sorted(r["latency_ms"] for r in group)
            summary[split][version] = dict(
                n=len(group),
                positive_n=len(positive),
                recall=round(statistics.mean(r["recall"] for r in positive), 4),
                mrr=round(statistics.mean(r["reciprocal_rank"] for r in positive), 4),
                median_latency_ms=round(statistics.median(times), 3),
                max_latency_ms=max(times),
                usefulness=None,
                citation_entailment=None,
                explanation="No semantic grade until explicit qualitative review; markers are not entailment.",
            )
    return dict(
        version="ada-answer-quality-comparison-v1",
        corpus_sha256=digest(CORPUS),
        schema_head=SCHEMA_HEAD,
        provider=mode,
        model=settings.ollama_model if mode == "ollama" else "explicit_fake_provider",
        summary=summary,
        cases=rows,
        ownership_or_deleted_source_leaks=0,
        exact_evidence_failures=0,
    )


def evaluate(output, mode="fixture", postgres=False):
    prior = os.environ.get("ADA_DATABASE_URL")
    engine = admin = schema = None
    settings = Settings(
        consolidation_worker_enabled=False,
        deletion_worker_enabled=False,
        embedding_enabled=False,
        browser_origin=None,
        output_tokens=192,
    )
    digest_value = None
    if mode == "ollama":
        models = httpx.get(settings.ollama_url + "/api/tags", timeout=10, trust_env=False).json()[
            "models"
        ]
        installed = next((m for m in models if m["name"] == settings.ollama_model), None)
        if not installed:
            raise ValueError("Configured model is not installed; no download attempted")
        digest_value = installed["digest"]
    with tempfile.TemporaryDirectory(prefix="ada-phase23-public-") as directory:
        try:
            url = "sqlite:///" + (Path(directory) / "evaluation.db").as_posix()
            if postgres:
                raw = os.environ.get("ADA_TEST_DATABASE_URL", "")
                parsed = make_url(raw)
                if (
                    parsed.database != "ada_phase2_test"
                    or parsed.get_backend_name() != "postgresql"
                ):
                    raise ValueError("Dedicated test database required")
                schema = "ada_quality23_" + uuid4().hex
                admin = create_engine(raw)
                with admin.begin() as db:
                    db.execute(text(f'CREATE SCHEMA "{schema}"'))
                url = parsed.update_query_dict(
                    {"options": "-csearch_path=" + schema}
                ).render_as_string(hide_password=False)
            os.environ["ADA_DATABASE_URL"] = url
            command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
            settings.database_url = url
            engine, sessions = connect(url)
            tracemalloc.start()
            report = run(sessions, settings, mode)
            _, peak = tracemalloc.get_traced_memory()
            report.update(
                measured_at_utc=datetime.now(UTC).isoformat(),
                backend=engine.dialect.name,
                model_digest=digest_value,
                python_peak_bytes=peak,
                limits=[
                    "16 public synthetic cases; 8 development/8 regression holdout, not unseen-training-data proof",
                    "Python peak excludes database/native/GPU/process allocations",
                    "Current recorded valid-time history, not historical knowledge reconstruction",
                    "No private data, live changes, model download or semantic activation",
                    "Fixture generation does not measure answer usefulness/entailment",
                    "Prompt default stays v4; v5 requires explicit audited upgrade",
                ],
            )
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            return report
        finally:
            tracemalloc.stop()
            if engine is not None:
                engine.dispose()
            if admin is not None:
                with admin.begin() as db:
                    db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
                admin.dispose()
            if prior is None:
                os.environ.pop("ADA_DATABASE_URL", None)
            else:
                os.environ["ADA_DATABASE_URL"] = prior


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("fixture", "ollama"), default="fixture")
    parser.add_argument("--postgres", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path(".pytest_cache/answer-quality-phase23.json")
    )
    args = parser.parse_args()
    try:
        evaluate(args.output, args.provider, args.postgres)
    except Exception:
        parser.exit(1, "Public Phase23 evaluation failed; private diagnostics suppressed.\n")


if __name__ == "__main__":
    main()
