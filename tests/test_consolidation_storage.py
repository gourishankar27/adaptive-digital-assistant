from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import event, func, inspect, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from test_consolidation import enqueue, job, prepared
from test_memory import add, note, scope

from ada.consolidation import ConsolidationService
from ada.consolidation_contracts import ConsolidationInput
from ada.consolidation_models import ConsolidationSource, Episode
from ada.errors import ServiceError
from ada.models import ClaimSearch, Source, SourceVersion
from ada.schema import SCHEMA_HEAD


def test_lower_imported_source_guard_preflights_before_any_downgrade_ddl(harness):
    h = harness
    s = scope(h)
    with h["sessions"].begin() as db:
        db.add(Source(owner_id=h["a_id"], scope_id=s, kind="imported_document"))
    with pytest.raises(RuntimeError, match="Document evidence exists"):
        command.downgrade(h["config"], "0004")
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_HEAD
        assert "episode_contexts" in inspect(db.connection()).get_table_names()
        assert db.scalar(select(func.count()).select_from(Source)) == 1


def test_shutdown_during_generation_keeps_lease_for_tracked_restart(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    provider.hook = service.stop
    assert service.run_once()
    pending = job(h, body["job_id"]).json()
    assert pending["status"] == "running" and pending["receipt"] is None
    assert h["client"].get(f"/v1/scopes/{s}/episodes", headers=h["a"]).json() == []
    provider.hook = None
    restarted = ConsolidationService(
        h["sessions"],
        provider,
        service.proposals,
        service.capacity,
        clock=lambda: pending["lease_until"] + 1,
    )
    assert restarted.run_once()
    assert job(h, body["job_id"]).json()["attempt"] == 2 and provider.calls == 2


def test_restart_after_claim_expiry_fences_old_attempt_and_replays_commit(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    assert enqueue(h, s, body).status_code == 201
    old = service.claim()  # Crash immediately after durable reservation, before inference.
    assert old.status == "running" and old.attempt == 1
    assert not service.run_once() and provider.calls == 0
    time = old.lease_until + 1
    restarted = ConsolidationService(
        h["sessions"], provider, service.proposals, service.capacity, clock=lambda: time
    )
    assert restarted.run_once()
    with pytest.raises(ServiceError, match="consolidation_superseded"):
        service.finish(old, service._generate(old))
    saved = job(h, body["job_id"]).json()
    assert saved["status"] == "completed" and saved["attempt"] == 2
    assert not restarted.run_once()
    assert enqueue(h, s, body).json() == saved
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Episode)) == 1


def test_crash_before_publication_commit_no_partial_output_then_tracked_retry(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    assert enqueue(h, s, body).status_code == 201

    def fail(db):
        raise SQLAlchemyError("synthetic-private-output")

    def install():
        event.listen(h["sessions"].class_, "before_commit", fail)

    provider.hook = install
    try:
        with pytest.raises(SQLAlchemyError):
            service.run_once()
    finally:
        event.remove(h["sessions"].class_, "before_commit", fail)
    value = job(h, body["job_id"]).json()
    assert value["status"] == "running" and value["receipt"] is None
    assert h["client"].get(f"/v1/scopes/{s}/episodes", headers=h["a"]).json() == []
    provider.hook = None
    service.clock = lambda: value["lease_until"] + 1
    assert service.run_once() and provider.calls == 2
    assert job(h, body["job_id"]).json()["attempt"] == 2


def test_crash_after_commit_does_not_regenerate_or_duplicate(harness, monkeypatch):
    h = harness
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    original = service.finish

    def crash(*args):
        original(*args)
        raise RuntimeError("synthetic-after-commit")

    monkeypatch.setattr(service, "finish", crash)
    with pytest.raises(RuntimeError, match="after-commit"):
        service.run_once()
    assert job(h, body["job_id"]).json()["status"] == "completed"
    assert not service.run_once() and provider.calls == 1


def test_three_expired_attempts_terminal_receipt_without_untracked_work(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    for attempt in range(1, 4):
        reserved = service.claim()
        assert reserved.attempt == attempt
        service.clock = lambda lease=reserved.lease_until: lease + 1
    assert service.run_once()
    value = job(h, body["job_id"]).json()
    assert value["status"] == "failed" and value["error_code"] == "consolidation_attempt_limit"
    assert value["receipt"]["episode_id"] is None and provider.calls == 0


def test_populated_upgrade_old_replay_schema_check_and_preflight(harness):
    h = harness
    c, _ = make_conversation(h)
    saved = send(h, c).json()
    command.downgrade(h["config"], "0009")
    assert send(h, c, request_id=saved["request_id"]).json() == saved
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    service.run_once()
    with pytest.raises(RuntimeError, match="Populated consolidation history"):
        command.downgrade(h["config"], "0008")
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_HEAD
        assert db.scalar(select(func.count()).select_from(Episode)) == 1
    assert send(h, c, request_id=saved["request_id"]).json() == saved


def test_native_source_owner_scope_and_conversation_references(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    other = scope(h, who="b")
    foreign = note(h, other, who="b")
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(
            ConsolidationSource(
                owner_id=h["a_id"],
                job_id=body["job_id"],
                ordinal=4,
                scope_id=s,
                source_version_id=foreign["id"],
                source_hash=foreign["content_hash"],
                conversation_id=None,
                event_id=None,
            )
        )
        db.flush()


def test_index_job_rebuild_is_scoped_atomic_and_stale_preserves_prior_index(harness):
    h = harness
    s, n, _, service, provider = prepared(h)
    assert add(h, s, n).status_code == 201
    other = scope(h, name="other")
    assert add(h, other, note(h, other)).status_code == 201
    body = {"job_id": str(uuid4()), "kind": "lexical_rebuild", "sources": []}
    assert enqueue(h, s, body).status_code == 201
    with h["sessions"].begin() as db:
        original = db.scalar(select(ClaimSearch).where(ClaimSearch.scope_id == s))
        original.search_text = "synthetic damaged derived projection"
    assert service.run_once() and provider.calls == 0
    assert job(h, body["job_id"]).json()["receipt"]["indexed_claims"] == 1
    with h["sessions"]() as db:
        assert "damaged" not in db.scalar(
            select(ClaimSearch.search_text).where(ClaimSearch.scope_id == s)
        )
        assert db.scalar(select(func.count()).select_from(ClaimSearch)) == 2
    more = note(h, s, "Other synthetic evidence")
    assert add(h, s, more, predicate="other").status_code == 201
    body = body | {"job_id": str(uuid4())}
    enqueue(h, s, body)
    with h["sessions"].begin() as db:
        db.get(SourceVersion, n["id"]).content = "tampered"
    assert service.run_once()
    assert job(h, body["job_id"]).json()["status"] == "stale"
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(ClaimSearch)) == 3


def test_postgres_duplicate_enqueue_and_worker_claim_serialization(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Real PostgreSQL row locks required")
    s, n, body, service, provider = prepared(h)
    barrier = Barrier(2)

    def reserve(_):
        barrier.wait()
        return service.enqueue(h["a_id"], s, ConsolidationInput.model_validate(body))

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(reserve, range(2)))
    assert sum(created for _, created in results) == 1
    entered, release = Event(), Event()

    def pause():
        entered.set()
        assert release.wait(10)

    provider.hook = pause
    with ThreadPoolExecutor(2) as pool:
        first = pool.submit(service.run_once)
        assert entered.wait(10)
        assert pool.submit(service.run_once).result(10) is False
        release.set()
        assert first.result(10)
    assert provider.calls == 1
    assert job(h, body["job_id"]).json()["attempt"] == 1


def test_worker_lifecycle_processes_explicit_job_and_stops(harness):
    h = harness
    s, n, body, service, provider = prepared(h)
    enqueue(h, s, body)
    done = Event()
    original = service.finish

    def finish(*args):
        original(*args)
        done.set()

    service.finish = finish
    service.start()
    try:
        assert done.wait(10)
        assert job(h, body["job_id"]).json()["status"] == "completed"
    finally:
        service.stop()
    assert service._thread is None and provider.calls == 1
