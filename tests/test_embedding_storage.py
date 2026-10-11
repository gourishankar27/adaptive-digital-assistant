import json
from pathlib import Path
from uuid import uuid4

from alembic import command
from sqlalchemy import select
from test_semantic_retrieval import query, rebuild, setup

from ada.models import Claim, RetrievalTrace, SourceVersion


def test_populated_upgrade_check_discardable_downgrade_and_frozen_history(harness):
    from conftest import send

    h = harness
    conv, scope, claim, service = setup(h)
    service.settings.embedding_enabled = False
    saved = send(h, conv, "Mira commute", str(uuid4())).json()
    with h["sessions"]() as db:
        original_hash = db.get(Claim, claim["id"]).write_hash
        source_content = db.get(SourceVersion, claim["evidence"]["source_version_id"]).content
    command.downgrade(h["config"], "0006")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert (
        send(h, conv, "Mira commute", saved["request_id"]).json()["response"] == saved["response"]
    )
    service.settings.embedding_enabled = True
    assert rebuild(h, scope).status_code == 200
    semantic_saved = send(h, conv, "rail journey", str(uuid4())).json()
    with h["sessions"]() as db:
        trace = db.get(RetrievalTrace, (h["a_id"], semantic_saved["request_id"]))
        original_plan = json.dumps(trace.plan, sort_keys=True)
    command.downgrade(h["config"], "0006")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    with h["sessions"]() as db:
        assert db.get(Claim, claim["id"]).write_hash == original_hash
        assert (
            db.get(SourceVersion, claim["evidence"]["source_version_id"]).content == source_content
        )
        assert (
            json.dumps(
                db.get(RetrievalTrace, (h["a_id"], semantic_saved["request_id"])).plan,
                sort_keys=True,
            )
            == original_plan
        )
    assert (
        send(h, conv, "rail journey", semantic_saved["request_id"]).json()["response"]
        == semantic_saved["response"]
    )
    assert query(h, scope).json()["plan"]["semantic"]["reason"] == "index_incomplete_or_stale"


def test_exact_search_capacity_at_256_items_768_dimensions_and_257_fallback(harness):
    import time
    import tracemalloc

    from test_memory import add, note

    from ada.embedding_models import EmbeddingEntry

    h = harness
    _, scope, _, service = setup(h)
    for i in range(255):
        assert (
            add(
                h,
                scope,
                note(h, scope, f"Synthetic capacity item {i} takes a train."),
                subject=f"Traveler {i}",
                predicate="transport",
                value="train",
            ).status_code
            == 201
        )
    service.settings.embedding_dimensions = 768
    batches = []

    class CapacityProvider:
        def embed(self, texts, *, query=False):
            assert h["sessions"].kw["bind"].pool.checkedout() == 0
            batches.append(len(texts))
            return [[1.0] + [0.0] * 767 for _ in texts]

    service.provider = CapacityProvider()
    tracemalloc.start()
    started = time.perf_counter_ns()
    built = rebuild(h, scope)
    build_ms = (time.perf_counter_ns() - started) / 1_000_000
    assert built.status_code == 200 and built.json()["indexed"] == 256
    assert batches == [8] * 32
    started = time.perf_counter_ns()
    result = query(h, scope).json()
    query_ms = (time.perf_counter_ns() - started) / 1_000_000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert result["plan"]["semantic"]["indexed"] == 256
    assert len(result["candidates"]) == 64
    with h["sessions"]() as db:
        assert len(db.scalars(select(EmbeddingEntry)).all()) == 256
    assert (
        add(
            h,
            scope,
            note(h, scope, "Synthetic item 257 takes a train."),
            subject="Traveler 257",
            predicate="transport",
            value="train",
        ).status_code
        == 201
    )
    assert query(h, scope).json()["plan"]["semantic"]["reason"] == "scope_work_bound"
    assert rebuild(h, scope).status_code == 503
    report = {
        "backend": h["backend"],
        "provider": "synthetic constant vectors",
        "items": 256,
        "dimensions": 768,
        "batch_count": 32,
        "build_ms": round(build_ms, 3),
        "query_ms": round(query_ms, 3),
        "python_peak_bytes": peak,
        "257": "lexical fallback; rebuild rejected",
        "limits": "tracemalloc excludes database/GPU; no real-model inference or production capacity claim",
    }
    destination = (
        Path(__file__).resolve().parents[1]
        / ".pytest_cache"
        / f"hybrid-capacity-{h['backend']}.json"
    )
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
