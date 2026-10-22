"""Private selection/publication fences and cooperative foreground priority."""

import hashlib
import threading
import time
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from test_reflection import SAFE_RESOURCES, enabled

from ada.models import Claim, SourceVersion
from ada.reflection_models import ReflectionProviderState


def test_all_worker_switches_are_required(harness):
    service, _, _, _, _ = enabled(harness)
    service.settings.consolidation_worker_enabled = False
    assert not service.queue_once()


def test_source_changed_after_lease_suppresses_publication(harness):
    service, _, _, source, _ = enabled(harness)
    assert service.queue_once()
    run, _ = service.claim()
    result = service._report(run)
    with harness["sessions"].begin() as db:
        row = db.get(SourceVersion, source["id"])
        row.content = "Changed public material."
        row.content_hash = hashlib.sha256(row.content.encode()).hexdigest()
    assert not service._finish(run, result, None, 2, None)
    assert harness["client"].get("/v1/reflection/artifacts", headers=harness["a"]).json() == []


def test_source_payload_is_not_read_with_unknown_resources(harness, monkeypatch):
    service, _, _, _, _ = enabled(harness)
    service.resources = lambda: SAFE_RESOURCES | {"memory_available_percent": None}
    monkeypatch.setattr(
        service.consolidation,
        "_sources",
        lambda *a: pytest.fail("Private source loaded before safety check"),
    )
    assert not service.queue_once()


def test_automation_off_suppresses_queued_reflection(harness):
    service, _, _, _, _ = enabled(harness)
    assert service.queue_once()
    policy = service.scheduler.policy(harness["a_id"])
    body = {"operation_id": str(uuid4()), "expected_revision": policy["revision"], "enabled": False}
    assert (
        harness["client"].post("/v1/scheduling/policy", headers=harness["a"], json=body).status_code
        == 200
    )
    assert not service.run_once()
    assert not service.policy(harness["a_id"])["settings"]["enabled"]


def test_foreign_scope_and_hidden_authority_are_rejected(harness):
    _, _, s, _, _ = enabled(harness)
    body = {
        "operation_id": str(uuid4()),
        "expected_revision": 0,
        "settings": {"enabled": True, "scope_ids": [s]},
    }
    response = harness["client"].post("/v1/reflection/policy", headers=harness["b"], json=body)
    assert response.status_code == 404
    body["owner_id"] = harness["a_id"]
    assert (
        harness["client"].post("/v1/reflection/policy", headers=harness["b"], json=body).status_code
        == 422
    )


def test_no_finding_is_an_honest_empty_report(harness):
    service, _, _, _, _ = enabled(harness, text="A public ordinary note without an open marker.")
    assert service.queue_once() and service.run_once()
    items = service.artifacts(harness["a_id"])
    assert items[0]["content"]["findings"] == []
    assert items[0]["rationale"] == "no_useful_findings"
    with harness["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


class ControlledProvider:
    key = hashlib.sha256(b"public-synthetic-reflection-provider-v1").hexdigest()

    def __init__(self, ignore=False):
        self.started = threading.Event()
        self.release = threading.Event()
        self.ignore = ignore

    def generate(self, run, consolidation, cancel, deadline):
        self.started.set()
        (self.release if self.ignore else cancel).wait(5)
        return {
            "summary": {
                "sections": [{"text": "A generated public navigation draft.", "support": run.pins}],
                "tags": ["public"],
                "omissions": [],
            }
        }


def summary(h, ignore=False):
    # Configure a test-only attestation; production needs its own measured native probe.
    service, clock, s, source, op = enabled(h)
    service.settings.max_parallel = 1
    service.settings.reflection_summary_enabled = True
    service.chat.capacity = threading.BoundedSemaphore(1)
    provider = ControlledProvider(ignore)
    service.provider = provider
    with h["sessions"].begin() as db:
        db.add(
            ReflectionProviderState(
                id=provider.key, ready=True, reason="synthetic_fixture", observed_at=clock[0]
            )
        )
    policy = service.policy(h["a_id"])
    body = {
        "operation_id": str(uuid4()),
        "expected_revision": policy["revision"],
        "settings": policy["settings"] | {"job_kinds": ["summary"]},
    }
    assert h["client"].post("/v1/reflection/policy", headers=h["a"], json=body).status_code == 200
    clock[0] += 901000
    assert service.queue_once()
    return service, clock, provider


def test_foreground_preempts_background_without_new_inference_slot(harness):
    service, _, provider = summary(harness)
    worker = threading.Thread(target=service.run_once)
    worker.start()
    assert provider.started.wait(3)
    began = time.monotonic()
    assert service.chat.acquire_foreground(harness["a_id"])
    assert time.monotonic() - began < 2
    service.chat.capacity.release()
    worker.join(3)
    assert not worker.is_alive()
    assert not service.artifacts(harness["a_id"])
    rows = service.runs(harness["a_id"])
    assert rows[0]["state"] == "queued" and rows[0]["reason"] == "foreground_arrival"


def test_ignored_cancellation_suspends_class_and_keeps_capacity_until_return(harness):
    service, _, provider = summary(harness, ignore=True)
    service.cancel_budget_seconds = 0.05
    worker = threading.Thread(target=service.run_once)
    worker.start()
    try:
        assert provider.started.wait(3)
        service.activity(harness["a_id"])
        end = time.monotonic() + 2
        while time.monotonic() < end:
            with harness["sessions"]() as db:
                ready = db.get(ReflectionProviderState, provider.key).ready
            if not ready:
                break
            time.sleep(0.02)
        assert not ready
        assert not service.chat.capacity.acquire(blocking=False)
    finally:
        provider.release.set()
        worker.join(3)
    assert not worker.is_alive() and not service.summary_available()
    assert not service.artifacts(harness["a_id"])
    with harness["sessions"]() as db:
        assert db.get(ReflectionProviderState, provider.key).reason == "provider_cancel_ignored"


def test_native_duplicate_claim_has_one_lease(harness):
    if harness["settings"].database_url.startswith("sqlite"):
        pytest.skip("Native reflection owner/row lease serialization requires PostgreSQL")
    service, _, _, _, _ = enabled(harness)
    assert service.queue_once()
    barrier = threading.Barrier(2)
    results = []

    def claim():
        barrier.wait()
        results.append(service.claim())

    workers = [threading.Thread(target=claim) for _ in range(2)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(5)
    assert all(not worker.is_alive() for worker in workers)
    assert sum(value is not None for value in results) == 1


def test_resource_sampling_never_holds_an_owner_transaction(harness):
    from sqlalchemy import event

    service, _, _, _, _ = enabled(harness)
    engine = harness["sessions"].kw["bind"]
    opened = set()

    def begin(connection):
        opened.add(id(connection))

    def end(connection):
        opened.discard(id(connection))

    def sample():
        assert not opened, "A potentially slow sensor probe held an owner transaction"
        return dict(SAFE_RESOURCES)

    event.listen(engine, "begin", begin)
    event.listen(engine, "commit", end)
    event.listen(engine, "rollback", end)
    service.resources = sample
    try:
        assert service.queue_once()
        assert service.run_once()
    finally:
        event.remove(engine, "begin", begin)
        event.remove(engine, "commit", end)
        event.remove(engine, "rollback", end)


def imported(h, expired=False):
    from test_document_api import upload

    from ada.models import DocumentUpload

    service, clock, s, _, _ = enabled(h)
    result = upload(h, s, b"Public imported navigation material.")
    assert result.status_code == 201
    with h["sessions"].begin() as db:
        row = db.scalar(select(DocumentUpload).where(DocumentUpload.owner_id == h["a_id"]))
        row.available_to = clock[0] - 1 if expired else clock[0] + 902000
    policy = service.policy(h["a_id"])
    body = {
        "operation_id": str(uuid4()),
        "expected_revision": policy["revision"],
        "settings": policy["settings"] | {"source_types": ["user_notes", "imported_documents"]},
    }
    response = h["client"].post("/v1/reflection/policy", headers=h["a"], json=body)
    assert response.status_code == 200
    clock[0] += 901000
    return service, clock


def test_expired_import_is_omitted_without_poisoning_other_sources(harness):
    service, _ = imported(harness, expired=True)
    assert service.queue_once() and service.run_once()
    item = service.artifacts(harness["a_id"])[0]
    assert len(item["sources"]) == 1
    assert item["sources"][0]["trust_class"] == "user_explicit"
    assert item["omissions"]["unavailable"] == 1


def test_import_expiring_during_lease_cannot_be_published(harness):
    service, clock = imported(harness)
    assert service.queue_once()
    run, _ = service.claim()
    content = service._report(run)
    clock[0] += 2000
    assert not service._finish(run, content, None, 2, None)
    assert not service.artifacts(harness["a_id"])


def test_late_publication_after_off_reads_metadata_only(harness):
    from sqlalchemy import event

    service, _, _, _, _ = enabled(harness)
    assert service.queue_once()
    run, _ = service.claim()
    content = service._report(run)
    policy = service.policy(harness["a_id"])
    body = {
        "operation_id": str(uuid4()),
        "expected_revision": policy["revision"],
        "settings": policy["settings"] | {"enabled": False},
    }
    result = harness["client"].post("/v1/reflection/policy", headers=harness["a"], json=body)
    assert result.status_code == 200
    queries = []
    engine = harness["sessions"].kw["bind"]

    def capture(connection, cursor, statement, parameters, context, executemany):
        queries.append(statement.lower().replace(chr(34), ""))

    event.listen(engine, "before_cursor_execute", capture)
    try:
        assert not service._finish(run, content, None, 2, None)
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert not any("reflection_runs.snapshot" in q or "reflection_runs.pins" in q for q in queries)


@pytest.mark.parametrize(
    "field,value",
    [
        ("ac_power", False),
        ("thermal_c", 80),
        ("memory_available_percent", 0),
        ("disk_free_bytes", 0),
    ],
)
def test_resource_pressure_after_lease_suppresses_publication(harness, field, value):
    service, _, _, _, _ = enabled(harness)
    assert service.queue_once()
    run, _ = service.claim()
    content = service._report(run)
    service.resources = lambda: SAFE_RESOURCES | {field: value}
    assert not service._finish(run, content, None, 1, None)
    assert not service.artifacts(harness["a_id"])


def test_revoking_origin_device_fences_running_draft(harness):
    from test_security import device_header, enroll

    h = harness
    issued = enroll(h)
    device = device_header(issued)
    original = h["a"]
    h["a"] = device
    try:
        service, _, _, _, _ = enabled(h)
        assert service.queue_once()
        run, _ = service.claim()
        content = service._report(run)
        revoked = h["client"].post(
            f"/v1/security/credentials/{issued.json()['credential']['id']}/revoke", headers=original
        )
        assert revoked.status_code == 200
        assert not service._finish(run, content, None, 1, None)
        assert not service.artifacts(h["a_id"])
    finally:
        h["a"] = original


def test_reflection_off_has_a_reserved_receipt_even_at_capacity(harness, monkeypatch):
    h = harness
    service, _, _, _, _ = enabled(h)
    monkeypatch.setattr("ada.reflection.MAX_RECEIPTS", 2)
    p = service.policy(h["a_id"])
    body = {
        "operation_id": str(uuid4()),
        "expected_revision": p["revision"],
        "settings": p["settings"],
    }
    result = h["client"].post("/v1/reflection/policy", headers=h["a"], json=body)
    assert result.status_code == 413
    body["operation_id"] = str(uuid4())
    body["settings"]["enabled"] = False
    result = h["client"].post("/v1/reflection/policy", headers=h["a"], json=body)
    assert result.status_code == 200 and not service.policy(h["a_id"])["settings"]["enabled"]


def test_policy_set_order_does_not_invent_new_source_set_run(harness):
    h = harness
    service, clock, _, _, _ = enabled(h)

    def save(types):
        p = service.policy(h["a_id"])
        r = h["client"].post(
            "/v1/reflection/policy",
            headers=h["a"],
            json={
                "operation_id": str(uuid4()),
                "expected_revision": p["revision"],
                "settings": p["settings"] | {"source_types": types},
            },
        )
        assert r.status_code == 200
        clock[0] += 901000

    save(["user_notes", "imported_documents"])
    assert service.queue_once() and service.run_once()
    save(["imported_documents", "user_notes"])
    assert not service.queue_once()


@pytest.mark.parametrize("code", ["provider_unavailable", "reflection_model_changed"])
def test_offline_or_changed_model_never_publishes(harness, code):
    from ada.providers import ProviderError

    service, _, provider = summary(harness)

    def fail(*args):
        raise ProviderError(code)

    provider.generate = fail
    assert service.run_once()
    assert not service.artifacts(harness["a_id"])
    if code == "reflection_model_changed":
        assert not service.summary_available()


def test_native_process_crash_before_publication_recovers_the_original_run(harness):
    import subprocess
    import sys

    from ada.reflection_models import ReflectionRun

    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Abrupt process recovery requires native PostgreSQL")
    service, clock, _, _, _ = enabled(h)
    assert service.queue_once()
    code = """import os
from ada.api import create_app
from ada.config import Settings
from ada.providers import FakeProvider
app=create_app(Settings(_env_file=None, database_url=os.environ["ADA_DATABASE_URL"], provider="fake", reflection_enabled=True, scheduler_enabled=True, consolidation_worker_enabled=True), FakeProvider())
s=app.state.reflection
s.clock=lambda: %d
s._boot=s._last_activity=s.clock()-901000
s.resources=lambda: {"ac_power":True,"memory_available_percent":80,"disk_free_bytes":10737418240,"thermal_c":40}
claim=s.claim()
os._exit(17 if claim else 18)
""" % clock[0]
    crashed = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20)
    assert crashed.returncode == 17
    with h["sessions"]() as db:
        run = db.scalar(select(ReflectionRun))
        assert run.status == "running" and run.attempt == 1
        identifier = run.id
        clock[0] = run.lease_until + 1
    assert service.run_once()
    assert service.runs(h["a_id"])[0]["id"] == identifier
    assert len(service.artifacts(h["a_id"])) == 1
