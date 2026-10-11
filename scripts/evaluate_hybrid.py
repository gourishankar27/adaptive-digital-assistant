"""Reproducible comparative evaluation on disposable, migrated databases only.

Fixture vectors measure wiring/invariants, not embedding model quality. Ollama
mode requires an explicitly installed model and full digest; never downloads it.
Reports contain synthetic case keys/metrics rather than private text or tokens.
"""

import argparse
import json
import os
import statistics
import tempfile
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4, uuid5

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.embedding_models import EmbeddingEntry
from ada.entities import EntityService
from ada.entity_contracts import EntityInput
from ada.evidence import content_hash
from ada.memory import ClaimInput, MemoryService, NoteInput, SupersedeInput
from ada.models import DocumentChunk, DocumentSearch, DocumentUpload, Scope, Source, SourceVersion
from ada.providers import FakeProvider
from ada.search import normalize

ROOT = Path(__file__).resolve().parents[1]


def evaluation_id(key, suffix):
    # Stable ordering for tie/MRR reproducibility, with a per-run collision suffix.
    stable = uuid5(UUID("d4b7d0b0-7091-4c7f-a90e-76768a454d58"), key)
    return UUID(hex=stable.hex[:20] + suffix[:12])


class FixtureEmbeddings:
    """Hand-specified synonym concepts. Imported only by explicit evaluation/tests."""

    concepts = (
        ("train", "rail"),
        ("bike", "cycle"),
        ("tea", "sipping"),
        ("battery", "electrical", "power", "outage", "recovery"),
    )

    def embed(self, texts, *, query=False):
        return [
            [float(any(w in t.lower() for w in words)) for words in self.concepts] + [0.1]
            for t in texts
        ]


def run_benchmark(sessions, mode="fixture"):
    data = json.loads((ROOT / "evaluations/hybrid-retrieval-v1.json").read_text(encoding="utf-8"))
    run_suffix = uuid4().hex
    owner, token = create_user(sessions, "Hybrid Alice " + run_suffix)
    bob, _ = create_user(sessions, "Hybrid Bob " + uuid4().hex)
    scopes = {}
    with sessions.begin() as db:
        for key, principal in (("main", owner), ("other", owner), ("bob", bob)):
            scope = Scope(owner_id=principal, kind="project", name="Synthetic " + key)
            db.add(scope)
            db.flush()
            scopes[key] = (principal, scope.id)
    memory, entities, logical, claims = MemoryService(sessions), EntityService(sessions), {}, {}
    for item in data["claims"]:
        principal, scope = scopes[item.get("scope", "main")]
        evidence, _ = memory.note(
            principal, scope, NoteInput(source_id=uuid4(), content=item["quote"])
        )
        common = {
            "claim_id": evaluation_id("claim:" + item["key"], run_suffix),
            "source_version_id": evidence["id"],
            "span_start": 0,
            "span_end": len(item["quote"]),
            "value": item["value"],
        }
        if item.get("entity"):
            receipt, _ = entities.create(
                principal,
                scope,
                EntityInput(
                    operation_id=uuid4(), entity_id=uuid4(), label=item["entity"], kind="person"
                ),
            )
            common["subject_entity_id"] = receipt["entity"]["id"]
        if "supersedes" in item:
            result, _ = memory.supersede(
                principal,
                claims[item["supersedes"]],
                SupersedeInput(**common, effective_at=item["valid_from"]),
            )
        else:
            result, _ = memory.add(
                principal,
                scope,
                ClaimInput(
                    **common,
                    subject=item["subject"],
                    predicate=item["predicate"],
                    valid_from=item.get("valid_from", "2025-01-01T00:00:00Z"),
                ),
            )
        claims[item["key"]] = result["id"]
        logical[result["id"]] = item["key"]
    for item in data["documents"]:
        principal, scope = scopes[item.get("scope", "main")]
        sid, vid, uid, cid = [str(uuid4()) for _ in range(4)]
        cid = str(evaluation_id("document:" + item["key"], run_suffix))
        passage = item["quote"]
        raw, digest = passage.encode(), content_hash(passage)
        at = int(
            datetime.fromisoformat(item["available"].replace("Z", "+00:00")).timestamp() * 1000
        )
        with sessions.begin() as db:
            db.add(
                Source(
                    id=sid,
                    owner_id=principal,
                    scope_id=scope,
                    kind="imported_document",
                    created_at=at,
                )
            )
            db.flush()
            db.add(
                SourceVersion(
                    id=vid,
                    owner_id=principal,
                    scope_id=scope,
                    source_id=sid,
                    version=1,
                    content=passage,
                    content_hash=digest,
                    trust_class="imported_untrusted",
                    created_at=at,
                )
            )
            db.flush()
            db.add(
                DocumentUpload(
                    owner_id=principal,
                    id=uid,
                    scope_id=scope,
                    source_id=sid,
                    source_version_id=vid,
                    version=1,
                    filename="synthetic.txt",
                    media_type="text/plain",
                    input_hash=digest,
                    raw_hash=digest,
                    raw_bytes=raw,
                    raw_size=len(raw),
                    state="ready",
                    chunk_count=1,
                    attempt=1,
                    available_from=at,
                    published_at=at,
                    created_at=at,
                    started_at=at,
                )
            )
            db.flush()
            db.add(
                DocumentChunk(
                    id=cid,
                    owner_id=principal,
                    scope_id=scope,
                    upload_id=uid,
                    source_id=sid,
                    source_version_id=vid,
                    ordinal=1,
                    span_start=0,
                    span_end=len(passage),
                    quote=passage,
                    content_hash=digest,
                    quote_hash=digest,
                    line_start=1,
                    line_end=1,
                )
            )
            db.flush()
            db.add(
                DocumentSearch(
                    chunk_id=cid, owner_id=principal, scope_id=scope, search_text=normalize(passage)
                )
            )
        logical[cid] = item["key"]
    settings = Settings(embedding_enabled=False)
    if mode == "fixture":
        settings.embedding_digest, settings.embedding_dimensions = "f" * 64, 5
        settings.embedding_min_similarity = 0.95
    app = create_app(settings, FakeProvider(), sessions)
    semantic = app.state.chat.semantic
    reports = {}
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer " + token}
        scope = scopes["main"][1]
        for channel in ("lexical", "hybrid"):
            settings.embedding_enabled = channel == "hybrid" and mode != "disabled"
            if channel == "hybrid" and settings.embedding_enabled:
                if mode == "fixture":
                    semantic.provider = FixtureEmbeddings()
                built = client.post(f"/v1/scopes/{scope}/semantic-index/rebuild", headers=headers)
                if built.status_code != 200:
                    raise RuntimeError("Synthetic index rebuild failed: " + str(built.status_code))
            recall, rr, times, details, fallbacks, integrity, violations, negatives = (
                [],
                [],
                [],
                [],
                0,
                0,
                0,
                0,
            )
            tracemalloc.start()
            for case in data["queries"]:
                started = time.perf_counter_ns()
                body = {
                    "query": case["query"],
                    "as_of": case.get("as_of", data["as_of"]),
                    "use_documents": case.get("documents", False),
                    "limit": 5,
                    "budget_bytes": 12000,
                }
                if case.get("time_mode") == "needs_date":
                    body.pop("as_of")
                response = client.post(f"/v1/scopes/{scope}/retrieve", headers=headers, json=body)
                if response.status_code != 200:
                    raise RuntimeError("Synthetic retrieval failed: " + str(response.status_code))
                result = response.json()
                cards = result["selected"] + result["document_selected"]
                found = [
                    logical.get(c.get("claim_id", c.get("chunk_id")), "unexpected") for c in cards
                ]
                for card in cards:
                    ev = card["evidence"]
                    with sessions() as db:
                        source = db.get(SourceVersion, ev["source_version_id"])
                        valid = (
                            source.owner_id == owner
                            and source.scope_id == scope
                            and source.content[ev["span_start"] : ev["span_end"]] == ev["quote"]
                            and content_hash(source.content)
                            == source.content_hash
                            == ev["content_hash"]
                        )
                    integrity += int(valid)
                    violations += int(not valid)
                expected = set(case["expected"])
                if expected:
                    recall.append(len(expected & set(found)) / len(expected))
                    first = next((i for i, key in enumerate(found, 1) if key in expected), None)
                    rr.append(1 / first if first else 0)
                elif case["key"] != "ambiguous_entities":
                    negatives += int(bool(found))
                violations += len(set(found) & set(case.get("forbidden", [])))
                violations += int(
                    "time_mode" in case and result["plan"]["time_mode"] != case["time_mode"]
                )
                state = result["plan"].get("semantic", {}).get("state", "disabled")
                fallbacks += int(state == "degraded")
                elapsed = (time.perf_counter_ns() - started) / 1_000_000
                times.append(elapsed)
                details.append(
                    {
                        "case": case["key"],
                        "expected": case["expected"],
                        "selected": found,
                        "semantic_state": state,
                    }
                )
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            reports[channel] = {
                "recall_at_5": round(statistics.mean(recall), 4),
                "mrr_at_5": round(statistics.mean(rr), 4),
                "exact_evidence_checked": integrity,
                "isolation_or_integrity_violations": violations,
                "negative_failures": negatives,
                "fallback_rate": fallbacks / len(data["queries"]),
                "median_latency_ms": round(statistics.median(times), 3),
                "max_latency_ms": round(max(times), 3),
                "python_peak_bytes": peak,
                "cases": details,
            }
    with sessions() as db:
        entries = db.scalars(
            select(EmbeddingEntry).where(
                EmbeddingEntry.owner_id == owner, EmbeddingEntry.scope_id == scope
            )
        ).all()
        vector_bytes = sum(len(json.dumps(e.vector).encode()) for e in entries)
    return {
        "dataset": data["version"],
        "provenance": data["provenance"],
        "provider": mode,
        "backend": sessions.kw["bind"].dialect.name,
        "model": settings.embedding_model
        if mode == "ollama"
        else ("explicit_fixture_concepts" if mode == "fixture" else None),
        "model_digest": settings.embedding_digest if mode != "disabled" else None,
        "dimensions": settings.embedding_dimensions,
        "namespace": semantic.namespace,
        "entries": len(entries),
        "vector_json_bytes": vector_bytes,
        "results": reports,
        "activation": "disabled by default; fixture benefit is not evidence of real-model quality",
        "limits": [
            "13 synthetic questions; no real private ADA content or answer entailment",
            "Python tracemalloc excludes database and GPU allocations",
            "Exact scope limit 256 items/1 MiB conservative content bound; no ANN",
            "Real-model resource and relevance measurements required before operator activation",
        ],
    }


def evaluate(output, mode="fixture", postgres=False):
    previous = os.environ.get("ADA_DATABASE_URL")
    admin = engine = schema = None
    with tempfile.TemporaryDirectory(prefix="ada-hybrid-eval-") as directory:
        try:
            if postgres:
                raw = os.environ.get("ADA_TEST_DATABASE_URL")
                if not raw:
                    raise ValueError("Set ADA_TEST_DATABASE_URL to a dedicated test database")
                test_url = make_url(raw)
                if (
                    test_url.get_backend_name() != "postgresql"
                    or test_url.database != "ada_phase2_test"
                ):
                    raise ValueError(
                        "Hybrid evaluation requires the dedicated ada_phase2_test database"
                    )
                schema = "ada_eval_" + uuid4().hex
                admin = create_engine(raw)
                with admin.begin() as db:
                    db.execute(text(f'CREATE SCHEMA "{schema}"'))
                url = test_url.update_query_dict(
                    {"options": f"-csearch_path={schema}"}
                ).render_as_string(hide_password=False)
            else:
                url = "sqlite:///" + str(Path(directory) / "evaluation.db")
            os.environ["ADA_DATABASE_URL"] = url
            command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
            engine, sessions = connect(url)
            report = run_benchmark(sessions, mode)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(
                json.dumps(
                    {
                        key: {k: v for k, v in value.items() if k != "cases"}
                        for key, value in report["results"].items()
                    },
                    indent=2,
                )
            )
            return report
        finally:
            if previous is None:
                os.environ.pop("ADA_DATABASE_URL", None)
            else:
                os.environ["ADA_DATABASE_URL"] = previous
            if engine:
                engine.dispose()
            if admin:
                with admin.begin() as db:
                    db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
                admin.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("disabled", "fixture", "ollama"), default="fixture")
    parser.add_argument("--postgres", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(".pytest_cache/hybrid-evaluation.json"))
    args = parser.parse_args()
    evaluate(args.output, args.provider, args.postgres)
