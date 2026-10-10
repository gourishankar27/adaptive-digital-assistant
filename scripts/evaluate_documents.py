"""Small exact-excerpt document corpus; disposable database and no inference.

The README paragraph is a real repository artifact. Other text, dates, accounts
and scope labels are synthetic. Neither is independent factual verification.
"""

import argparse
import json
import os
import statistics
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from ada.auth import create_user
from ada.db import connect
from ada.documents import DocumentService
from ada.evidence import content_hash
from ada.memory import time_ms
from ada.models import DocumentUpload, Scope, SourceVersion
from ada.retrieval import lock_scope_for_retrieval, plan_query, retrieve

ROOT = Path(__file__).resolve().parents[1]


def run_benchmark(sessions, fixture_path=None):
    fixture = json.loads(
        (fixture_path or ROOT / "evaluations/document-retrieval-v1.json").read_text(
            encoding="utf-8"
        )
    )
    suffix = uuid4().hex
    owner, _ = create_user(sessions, "Document evaluation Alice " + suffix)
    bob, _ = create_user(sessions, "Document evaluation Bob " + suffix)
    scopes = {}
    with sessions.begin() as db:
        for key, user in (("main", owner), ("other", owner), ("bob", bob)):
            row = Scope(owner_id=user, kind="project", name="Synthetic document evaluation " + key)
            db.add(row)
            db.flush()
            scopes[key] = (user, row.id)
    storage, documents, texts = DocumentService(sessions), {}, {}
    for item in fixture["documents"]:
        user, sid = scopes[item.get("scope", "main")]
        source_id = (
            documents[item["source_key"]]["source_id"] if "source_key" in item else str(uuid4())
        )
        value = item["text"] + item.get("repeat_character", "") * item.get("repeat_count", 0)
        at = time_ms(datetime(2025, 1, item["published_day"], tzinfo=UTC))
        expires = item.get("available_to_day")
        # An explicit fixture clock gives reproducible historical version tests.
        # Upload/reservation/parser/publish code itself is the actual implementation.
        with patch("ada.documents.now_ms", return_value=at):
            receipt, _ = storage.upload(
                user,
                sid,
                str(uuid4()),
                value.encode("utf-8"),
                source_id=source_id,
                filename=item["filename"],
                media_type=item["media_type"],
                available_from=at,
                available_to=time_ms(datetime(2025, 1, expires, tzinfo=UTC)) if expires else None,
            )
        if receipt["state"] != "ready":
            raise AssertionError("Evaluation document did not publish")
        documents[item["key"]], texts[item["key"]] = receipt, value
    logical = {row["source_version_id"]: key for key, row in documents.items()}
    expected_items = {item["key"]: item for item in fixture["documents"]}
    recalls, reciprocal, details, timings = [], [], [], []
    exact, checked, scope_violations, negative_failures, excerpt_failures = 0, 0, 0, 0, 0
    owner, sid = scopes["main"]
    for case in fixture["queries"]:
        at = (
            None
            if case.get("natural_time")
            else datetime.fromisoformat(case.get("as_of", fixture["as_of"]).replace("Z", "+00:00"))
        )
        started = time.perf_counter_ns()
        with sessions.begin() as db:
            lock_scope_for_retrieval(db, owner, sid)
            result = retrieve(
                db,
                owner,
                sid,
                plan_query(case["query"], at),
                limit=5,
                budget_bytes=case.get("budget_bytes", 6000),
                use_documents=case.get("use_documents", True),
            )
            found = [logical[item["source_version_id"]] for item in result["document_selected"]]
            for item in result["document_selected"]:
                checked += 1
                source = db.get(SourceVersion, item["source_version_id"])
                upload = db.get(DocumentUpload, (owner, item["upload_id"]))
                evidence = item["evidence"]
                scope_violations += int(
                    upload is None
                    or source.owner_id != owner
                    or source.scope_id != sid
                    or upload.scope_id != sid
                )
                exact += int(
                    source.content[evidence["span_start"] : evidence["span_end"]]
                    == evidence["quote"]
                    and source.content_hash
                    == evidence["content_hash"]
                    == content_hash(source.content)
                    and item["origin"] == "imported_document"
                    and item["trust_class"] == "imported_untrusted"
                )
                key = logical[item["source_version_id"]]
                excerpt_failures += int(evidence["quote"] != texts[key])
            # Candidate snapshots must also be owner/scope filtered, not just final selections.
            for candidate in result["document_candidates"]:
                source = db.get(SourceVersion, candidate["source_version_id"])
                scope_violations += int(source.owner_id != owner or source.scope_id != sid)
        elapsed = (time.perf_counter_ns() - started) / 1_000_000
        timings.append(elapsed)
        expected = set(case["expected"])
        if expected:
            recalls.append(len(expected & set(found)) / len(expected))
            first = next((rank for rank, key in enumerate(found, 1) if key in expected), None)
            reciprocal.append(1 / first if first else 0)
        else:
            negative_failures += int(bool(found))
        if "time_mode" in case:
            negative_failures += int(result["plan"]["time_mode"] != case["time_mode"])
        details.append(
            {
                "case": case["key"],
                "expected": case["expected"],
                "retrieved": found,
                "input_kinds": [expected_items[key]["input_kind"] for key in found],
                "time_mode": result["plan"]["time_mode"],
                "latency_ms": round(elapsed, 3),
            }
        )
    ordered = sorted(timings)
    return {
        "fixture_version": fixture["version"],
        "backend": sessions.kw["bind"].dialect.name,
        "documents": len(documents),
        "positive_queries": len(recalls),
        "negative_queries": len(details) - len(recalls),
        "k": 5,
        "provenance": fixture["provenance"],
        "metrics": {
            "recall_at_5": round(statistics.mean(recalls), 4),
            "mrr_at_5": round(statistics.mean(reciprocal), 4),
            "exact_evidence_coverage": round(exact / checked, 4) if checked else 0,
            "known_excerpt_failures": excerpt_failures,
            "scope_violations": scope_violations,
            "negative_query_failures": negative_failures,
            "median_latency_ms": round(statistics.median(timings), 3),
            "p95_latency_ms": round(ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)], 3),
        },
        "limitations": [
            "One real repository-owned excerpt; other content and every account/date are synthetic.",
            "Small lexical corpus, not production relevance or latency evidence.",
            "No inference, answer quality, citation entailment, PDF or embeddings measured.",
            "Historical upload times use an explicit fixture clock, not a production time override.",
        ],
        "cases": details,
    }


def evaluate(output, postgres=False):
    admin, schema, engine = None, None, None
    previous = os.environ.get("ADA_DATABASE_URL")
    with tempfile.TemporaryDirectory(prefix="ada-document-eval-") as directory:
        try:
            if postgres:
                raw = os.environ.get("ADA_TEST_DATABASE_URL")
                if not raw:
                    raise ValueError(
                        "Set ADA_TEST_DATABASE_URL to a dedicated PostgreSQL test database."
                    )
                schema = "ada_doc_eval_" + uuid4().hex
                admin = create_engine(raw)
                with admin.begin() as connection:
                    connection.execute(text(f'CREATE SCHEMA "{schema}"'))
                url = (
                    make_url(raw)
                    .update_query_dict({"options": f"-csearch_path={schema}"})
                    .render_as_string(hide_password=False)
                )
            else:
                url = "sqlite:///" + str(Path(directory) / "evaluation.db")
            os.environ["ADA_DATABASE_URL"] = url
            command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
            engine, sessions = connect(url)
            report = run_benchmark(sessions)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(json.dumps(report["metrics"], indent=2))
            print(f"Report: {output}")
            return report
        finally:
            if previous is None:
                os.environ.pop("ADA_DATABASE_URL", None)
            else:
                os.environ["ADA_DATABASE_URL"] = previous
            if engine:
                engine.dispose()
            if admin:
                with admin.begin() as connection:
                    connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
                admin.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".pytest_cache/document-evaluation.json"
    )
    parser.add_argument("--postgres", action="store_true")
    args = parser.parse_args()
    try:
        report = evaluate(args.output.resolve(), args.postgres)
    except ValueError as error:
        parser.exit(1, str(error) + "\n")
    metrics = report["metrics"]
    if (
        metrics["scope_violations"]
        or metrics["negative_query_failures"]
        or metrics["known_excerpt_failures"]
    ):
        parser.exit(1, "Document retrieval invariants failed.\n")


if __name__ == "__main__":
    main()
