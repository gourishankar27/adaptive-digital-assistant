"""Small synthetic retrieval evaluation; no LLM and no production database writes."""

import argparse
import json
import os
import statistics
import tempfile
import time
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4, uuid5

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url

from ada.auth import create_user
from ada.db import connect
from ada.evidence import content_hash
from ada.memory import ClaimInput, MemoryService, NoteInput, SupersedeInput
from ada.models import Claim, Scope, SourceVersion
from ada.retrieval import lock_scope_for_retrieval, plan_query, retrieve

ROOT = Path(__file__).resolve().parents[1]


def run_benchmark(sessions, fixture_path=None):
    fixture = json.loads(
        (fixture_path or ROOT / "evaluations/retrieval-v1.json").read_text(encoding="utf-8")
    )
    suffix = uuid4().hex
    owner, _ = create_user(sessions, "Evaluation Alice " + suffix)
    bob, _ = create_user(sessions, "Evaluation Bob " + suffix)
    scopes = {}
    with sessions.begin() as db:
        for name, user in (("main", owner), ("other", owner), ("bob", bob)):
            scope = Scope(owner_id=user, kind="project", name="Synthetic evaluation " + name)
            db.add(scope)
            db.flush()
            scopes[name] = (user, scope.id)
    memory, claims = MemoryService(sessions), {}
    for item in fixture["claims"]:
        user, scope_id = scopes[item.get("scope", "main")]
        source, _ = memory.note(user, scope_id, NoteInput(source_id=uuid4(), content=item["quote"]))
        common = {
            "claim_id": uuid5(UUID(scope_id), item["key"]),
            "source_version_id": source["id"],
            "span_start": 0,
            "span_end": len(item["quote"]),
            "value": item["value"],
        }
        at = item.get("valid_from", "2025-01-01T00:00:00Z")
        if "supersedes" in item:
            claim, _ = memory.supersede(
                user, claims[item["supersedes"]], SupersedeInput(**common, effective_at=at)
            )
        else:
            claim, _ = memory.add(
                user,
                scope_id,
                ClaimInput(
                    **common,
                    subject=item["subject"],
                    predicate=item["predicate"],
                    kind=item.get("kind", "fact"),
                    valid_from=at,
                ),
            )
        claims[item["key"]] = claim["id"]
    logical = {value: key for key, value in claims.items()}
    recalls, reciprocal, timings, details = [], [], [], []
    evidence_checked, evidence_valid, scope_violations, negative_failures = 0, 0, 0, 0
    owner, scope_id = scopes["main"]
    for case in fixture["queries"]:
        at = (
            None
            if case.get("natural_time")
            else datetime.fromisoformat(case.get("as_of", fixture["as_of"]).replace("Z", "+00:00"))
        )
        started = time.perf_counter_ns()
        with sessions.begin() as db:
            lock_scope_for_retrieval(db, owner, scope_id)
            result = retrieve(
                db, owner, scope_id, plan_query(case["query"], at), limit=5, budget_bytes=6000
            )
            selected = result["selected"]
            found = [logical[item["claim_id"]] for item in selected]
            for item in selected:
                evidence_checked += 1
                claim = db.get(Claim, item["claim_id"])
                source = db.scalar(
                    select(SourceVersion).where(
                        SourceVersion.id == item["evidence"]["source_version_id"]
                    )
                )
                scope_violations += int(claim.owner_id != owner or claim.scope_id != scope_id)
                evidence = item["evidence"]
                evidence_valid += int(
                    source.content[evidence["span_start"] : evidence["span_end"]]
                    == evidence["quote"]
                    and source.content_hash
                    == evidence["content_hash"]
                    == content_hash(source.content)
                )
        elapsed = (time.perf_counter_ns() - started) / 1_000_000
        timings.append(elapsed)
        expected = set(case["expected"])
        if expected:
            recalls.append(len(expected & set(found)) / len(expected))
            first = next((i for i, key in enumerate(found, 1) if key in expected), None)
            reciprocal.append(1 / first if first else 0)
        else:
            negative_failures += int(bool(found))
        if "time_mode" in case:
            negative_failures += int(result["plan"]["time_mode"] != case["time_mode"])
        details.append(
            {
                "case": case["key"],
                "query": case["query"],
                "expected": case["expected"],
                "retrieved": found,
                "time_mode": result["plan"]["time_mode"],
                "latency_ms": round(elapsed, 3),
            }
        )
    ordered = sorted(timings)
    return {
        "fixture_version": fixture["version"],
        "retrieval_version": result["version"],
        "backend": sessions.kw["bind"].dialect.name,
        "claims": len(claims),
        "positive_queries": len(recalls),
        "negative_queries": len(details) - len(recalls),
        "k": 5,
        "budget_bytes": 6000,
        "metrics": {
            "recall_at_5": round(statistics.mean(recalls), 4),
            "mrr_at_5": round(statistics.mean(reciprocal), 4),
            "exact_evidence_coverage": round(evidence_valid / evidence_checked, 4)
            if evidence_checked
            else 0,
            "scope_violations": scope_violations,
            "negative_query_failures": negative_failures,
            "median_latency_ms": round(statistics.median(timings), 3),
            "p95_latency_ms": round(ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)], 3),
        },
        "limitations": [
            "Small synthetic fixtures, not production relevance or latency measurements.",
            "Two semantic paraphrases deliberately have no lexical overlap and may be missed.",
            "No LLM was run; this does not measure answer correctness or citation entailment.",
            "The retrieval diagnostic budget is 6000 bytes; default chat memory is 2200 bytes.",
        ],
        "cases": details,
    }


def evaluate(output, postgres=False):
    admin, schema, engine = None, None, None
    previous = os.environ.get("ADA_DATABASE_URL")
    with tempfile.TemporaryDirectory(prefix="ada-retrieval-eval-") as directory:
        try:
            if postgres:
                raw = os.environ.get("ADA_TEST_DATABASE_URL")
                if not raw:
                    raise ValueError(
                        "Set ADA_TEST_DATABASE_URL to a dedicated test PostgreSQL database."
                    )
                schema = "ada_eval_" + uuid4().hex
                admin = create_engine(raw)
                with admin.begin() as conn:
                    conn.execute(text(f'CREATE SCHEMA "{schema}"'))
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
                with admin.begin() as conn:
                    conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
                admin.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluations/latest.json")
    parser.add_argument("--postgres", action="store_true")
    args = parser.parse_args()
    try:
        report = evaluate(args.output.resolve(), args.postgres)
    except ValueError as exc:
        parser.exit(1, str(exc) + "\n")
    if report["metrics"]["scope_violations"] or report["metrics"]["negative_query_failures"]:
        parser.exit(1, "Retrieval isolation evaluation failed.\n")


if __name__ == "__main__":
    main()
