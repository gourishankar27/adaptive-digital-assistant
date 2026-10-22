"""Actual PostgreSQL leases and authority races; no external notifications."""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import func, inspect, select, text
from test_curiosity import enabled, policy
from test_schedules import BASE, setup_schedule

from ada.admin import set_admin_grant
from ada.errors import ServiceError
from ada.models import Event, User
from ada.schedule_contracts import SchedulePolicyWrite
from ada.schedule_models import Schedule, ScheduleConsent, ScheduleInboxItem, ScheduleOccurrence
from ada.scheduling import LEASE_MS, SchedulingService


def inbox(h):
    response = h["client"].get("/v1/scheduling/inbox", headers=h["a"])
    assert response.status_code == 200, response.text
    return response.json()


def test_native_concurrent_claim_and_expired_attempt_fencing(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Multi-claimer correctness needs PostgreSQL owner row locks")
    service, _, key, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    with ThreadPoolExecutor(max_workers=2) as pool:
        claims = list(pool.map(lambda _: service.claim(), range(2)))
    live = [claim for claim in claims if claim and not claim.get("terminal")]
    assert len(live) == 1
    service.clock = lambda: BASE + 61000 + LEASE_MS + 1
    recovered = service.claim()
    assert recovered["attempt"] == 2 and recovered["id"] == live[0]["id"]
    assert not service.publish(live[0])
    assert service.publish(recovered)
    assert not service.publish(recovered)
    assert len(inbox(h)) == 1
    assert (
        h["client"].get(f"/v1/schedules/{key}/occurrences", headers=h["a"]).json()[0]["attempt"]
        == 2
    )


def test_crash_retry_is_bounded_and_restart_does_not_repeat_delivery(harness):
    h = harness
    service, _, key, _, _ = setup_schedule(h)
    for n in range(3):
        service.clock = lambda n=n: BASE + 61000 + n * (LEASE_MS + 1)
        assert service.claim()["attempt"] == n + 1
    service.clock = lambda: BASE + 61000 + 3 * (LEASE_MS + 1)
    assert service.claim()["terminal"]
    assert not inbox(h)
    states = h["client"].get(f"/v1/schedules/{key}/occurrences", headers=h["a"]).json()
    assert states[0]["state"] == "failed" and states[0]["reason"] == "attempt_limit"
    restarted = SchedulingService(h["sessions"], h["settings"], service.curiosity, service.clock)
    assert not restarted.run_once()


@pytest.mark.parametrize(
    "event", ["device_revoke", "device_rotate", "password_reset", "all_sessions", "epoch"]
)
def test_revocation_after_claim_suppresses_publication(harness, event):
    h = harness
    security, passwords = h["app"].state.security, h["app"].state.passwords
    if event.startswith("device"):
        h["settings"].device_enrollment_enabled = True
        issued, _ = security.enroll(h["a_id"], str(uuid4()), "Public fixture device", 1)
        h["a"] = {"Authorization": "Bearer " + issued["token"]}
    elif event in ("password_reset", "all_sessions"):
        passwords.set_password(h["a_id"], "alice", "Public synthetic passphrase 123")
        issued_session = passwords.login("alice", "Public synthetic passphrase 123")
        h["a"] = {"Authorization": "Bearer " + issued_session["access_token"]}
    service, _, key, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    claim = service.claim()
    if event == "device_revoke":
        security.revoke(h["a_id"], issued["credential"]["id"])
    elif event == "device_rotate":
        security.enroll(h["a_id"], str(uuid4()), "Rotated fixture", 1, issued["credential"]["id"])
    elif event == "password_reset":
        passwords.set_password(h["a_id"], "alice", "Changed public synthetic phrase 123")
    elif event == "all_sessions":
        passwords.revoke(h["a_id"])
    else:
        with h["sessions"].begin() as db:
            db.get(User, h["a_id"]).data_epoch += 1
    assert not service.publish(claim)
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(ScheduleInboxItem)) == 0
        assert db.get(Schedule, (h["a_id"], key)).status == "paused"


def test_password_session_logout_and_expiry_do_not_cancel_explicit_grant(harness):
    h = harness
    passwords = h["app"].state.passwords
    passwords.set_password(h["a_id"], "alice", "Public synthetic passphrase 123")
    session = passwords.login("alice", "Public synthetic passphrase 123")
    legacy = h["a"]
    h["a"] = {"Authorization": "Bearer " + session["access_token"]}
    service, _, _, _, _ = setup_schedule(h)
    passwords.revoke(h["a_id"], session["session_id"])
    h["a"] = legacy
    service.clock = lambda: BASE + 61000
    assert service.run_once()
    assert len(inbox(h)) == 1


def test_question_uses_existing_consent_quota_and_no_model_or_factual_write(harness):
    h = harness
    enabled(h)
    service, _, _, _, profile = setup_schedule(h, kind="curiosity_question", text="", topic="work")
    service.clock = lambda: BASE + 61000
    assert service.run_once()
    item = inbox(h)[0]
    assert item["kind"] == "curiosity_question" and item["question_id"]
    assert not h["provider"].calls
    opened = h["client"].post(
        f"/v1/scheduling/inbox/{item['id']}/open",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "conversation_id": str(uuid4()),
            "personality_id": profile,
        },
    )
    assert opened.status_code == 200, opened.text
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Event)) == 0


def test_question_policy_change_between_claim_and_publish(harness):
    h = harness
    enabled(h)
    service, _, _, _, _ = setup_schedule(h, kind="curiosity_question", text="", topic="work")
    service.clock = lambda: BASE + 61000
    claim = service.claim()
    enabled(h, frequency="rare")
    assert not service.publish(claim)
    assert not inbox(h)


def test_dispatcher_restart_and_replayed_ack_are_durable(harness):
    h = harness
    original, _, _, _, _ = setup_schedule(h)
    restarted = SchedulingService(
        h["sessions"], h["settings"], original.curiosity, lambda: BASE + 61000
    )
    assert restarted.run_once()
    assert not restarted.run_once()
    assert len(inbox(h)) == 1


def test_admin_can_read_only_aggregate_scheduling_metadata(harness):
    h = harness
    setup_schedule(h)
    c = h["client"]
    assert c.get("/v1/admin/scheduling", headers=h["a"]).status_code == 403
    set_admin_grant(h["sessions"], h["a_id"], True)
    result = c.get("/v1/admin/scheduling", headers=h["a"])
    assert result.status_code == 200, result.text
    assert set(result.json()) == {
        "globally_enabled",
        "worker_running",
        "process_error_count",
        "last_error_code",
        "schedules",
        "occurrences",
        "inbox",
        "updated_at",
    }
    assert result.json()["schedules"] == {"active": 1}
    assert "notebook" not in result.text


def test_schedule_inventory_erasure_and_old_replay_populated_upgrade(harness):
    h = harness
    cid, _ = make_conversation(h)
    body = {"request_id": str(uuid4()), "content": "Public unchanged request replay."}
    saved = send(h, cid, body["content"], body["request_id"]).json()
    command.downgrade(h["config"], "0017")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, cid, body["content"], body["request_id"]).json() == saved
    service, _, _, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    service.run_once()
    with h["sessions"]() as db:
        names = inspect(db.connection()).get_table_names()
        assert (
            len([name for name in names if not name.startswith(("claim_fts", "document_fts"))])
            == 74
        )
    with pytest.raises(RuntimeError, match="Schedule history"):
        command.downgrade(h["config"], "0017")
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == "0020"
    h["settings"].deletion_worker_enabled = True
    deletion = h["app"].state.deletion
    preview = deletion.preview(h["a_id"])
    deletion.confirm(h["a_id"], str(uuid4()), preview["id"])
    assert deletion.process_one()
    with h["sessions"]() as db:
        for model in (Schedule, ScheduleConsent, ScheduleOccurrence, ScheduleInboxItem):
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.owner_id == h["a_id"])
                )
                == 0
            )


def test_stale_authenticated_actor_cannot_reenable_schedule_consent(harness):
    from ada.auth import rotate_token

    h = harness
    service, _, _, _, _ = setup_schedule(h)
    principal = h["app"].state.security.authenticate(h["a"]["Authorization"].split()[1])
    rotate_token(h["sessions"], "Alice")
    revision = service.policy(h["a_id"])["revision"]
    with pytest.raises(ServiceError) as error:
        service.write_policy(
            h["a_id"],
            SchedulePolicyWrite(operation_id=uuid4(), expected_revision=revision, enabled=True),
            principal,
        )
    assert error.value.status == 401


def test_old_question_pruning_keeps_scheduler_inbox_consistent(harness):
    h = harness
    enabled(h)
    service, _, _, _, _ = setup_schedule(h, kind="curiosity_question", text="", topic="work")
    service.clock = lambda: BASE + 61000
    service.run_once()
    assert len(inbox(h)) == 1
    policy(h, enabled=False)
    service.clock = lambda: BASE + 32 * 86400000
    enabled(h)
    result = inbox(h)
    assert len(result) == 1 and result[0]["text"] is None


def test_native_process_crash_leaves_a_committed_lease_for_recovery(harness):
    import subprocess
    import sys

    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Abrupt process/lease recovery uses native PostgreSQL")
    service, _, _, _, _ = setup_schedule(h)
    code = """import os
from ada.api import create_app
from ada.config import Settings
from ada.providers import FakeProvider
app=create_app(Settings(_env_file=None, database_url=os.environ["ADA_DATABASE_URL"], provider="fake", scheduler_enabled=True, consolidation_worker_enabled=False), FakeProvider())
app.state.scheduling.clock=lambda: %d
claim=app.state.scheduling.claim()
os._exit(17 if claim and not claim.get("terminal") else 18)
""" % (BASE + 61000)
    crashed = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20)
    assert crashed.returncode == 17
    with h["sessions"]() as db:
        occurrence = db.scalar(
            select(ScheduleOccurrence).where(ScheduleOccurrence.owner_id == h["a_id"])
        )
        assert occurrence.status == "running" and occurrence.attempt == 1
    service.clock = lambda: BASE + 61000 + LEASE_MS + 1
    assert service.run_once()
    assert len(inbox(h)) == 1


def test_snooze_and_edit_cancel_old_attempts_without_losing_the_latest_item(harness):
    from test_schedule_time import definition

    h = harness
    service, scope, key, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    old = service.claim()
    until = "2026-10-20T16:00:00Z"
    c = h["client"]
    result = c.post(
        f"/v1/schedules/{key}/actions",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_generation": 1,
            "action": "snooze",
            "until": until,
        },
    )
    assert result.status_code == 200
    assert not service.publish(old) and not service.run_once()
    service.clock = lambda: BASE + 62 * 60000
    assert service.run_once() and len(inbox(h)) == 1
    preview_id = str(uuid4())
    preview = c.post(
        f"/v1/scopes/{scope}/schedules/preview",
        headers=h["a"],
        json={
            "operation_id": preview_id,
            "definition": definition(
                text="Edited public reminder.", start_local="2026-10-21T08:00"
            ),
        },
    )
    assert preview.status_code == 200
    confirmed = c.post(
        f"/v1/schedules/{key}/confirm",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "preview_id": preview_id,
            "expected_generation": 2,
            "consent_revision": service.policy(h["a_id"])["revision"],
        },
    )
    assert confirmed.status_code == 200
    service.clock = lambda: BASE + 86400000 + 61000
    assert service.run_once()
    assert {row["text"] for row in inbox(h)} == {"Edited public reminder.", definition()["text"]}


@pytest.mark.parametrize("change_digest", [False, True])
def test_source_changed_after_claim_is_not_delivered(harness, change_digest, monkeypatch):
    from test_memory import note
    from test_schedule_time import definition

    from ada.models import SourceVersion

    h = harness
    enabled(h)
    service, scope, old_key, _, _ = setup_schedule(h)
    c = h["client"]
    paused = c.post(
        f"/v1/schedules/{old_key}/actions",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_generation": 1,
            "action": "pause",
        },
    )
    assert paused.status_code == 200
    # The schedule uses a synthetic calendar; source creation must use it too.
    monkeypatch.setattr("ada.evidence.now_ms", lambda: BASE - 1000)
    source = note(h, scope, "Public original for scheduled review.")
    preview_id = str(uuid4())
    preview = c.post(
        f"/v1/scopes/{scope}/schedules/preview",
        headers=h["a"],
        json={
            "operation_id": preview_id,
            "definition": definition(
                kind="curiosity_question",
                text="",
                topic="work",
                source={
                    "source_version_id": source["id"],
                    "span_start": 0,
                    "span_end": len(source["content"]),
                },
            ),
        },
    )
    assert preview.status_code == 200
    key = str(uuid4())
    confirmed = c.post(
        f"/v1/schedules/{key}/confirm",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "preview_id": preview_id,
            "expected_generation": 0,
            "consent_revision": service.policy(h["a_id"])["revision"],
        },
    )
    assert confirmed.status_code == 200
    service.clock = lambda: BASE + 61000
    claim = service.claim()
    with h["sessions"].begin() as db:
        version = db.get(SourceVersion, source["id"])
        version.content = source["content"].replace("Public", "Edited")
        if change_digest:
            from ada.evidence import content_hash

            version.content_hash = content_hash(version.content)
    assert not service.publish(claim) and not inbox(h)


def test_backward_clock_edit_then_snooze_keeps_the_new_plan(harness):
    from test_schedule_time import definition

    h = harness
    service, scope, key, _, _ = setup_schedule(h, frequency="once", count=1)
    service.clock = lambda: BASE + 61000
    assert service.run_once()
    service.clock = lambda: BASE - 86400000
    preview_id = str(uuid4())
    c = h["client"]
    preview = c.post(
        f"/v1/scopes/{scope}/schedules/preview",
        headers=h["a"],
        json={
            "operation_id": preview_id,
            "definition": definition(
                text="New reviewed public plan.",
                start_local="2026-10-19T09:00",
                frequency="once",
                count=1,
            ),
        },
    )
    assert preview.status_code == 200
    confirmed = c.post(
        f"/v1/schedules/{key}/confirm",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "preview_id": preview_id,
            "expected_generation": 1,
            "consent_revision": service.policy(h["a_id"])["revision"],
        },
    )
    assert confirmed.status_code == 200
    snoozed = c.post(
        f"/v1/schedules/{key}/actions",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_generation": 2,
            "action": "snooze",
            "until": "2026-10-19T16:30:00Z",
        },
    )
    assert snoozed.status_code == 200
    service.clock = lambda: BASE - 86400000 + 3 * 3600000
    assert service.run_once()
    assert any(item["text"] == "New reviewed public plan." for item in inbox(h))


def test_disabled_grant_does_not_load_schedule_payload(harness):
    from sqlalchemy import event

    h = harness
    service, _, _, _, _ = setup_schedule(h)
    with h["sessions"].begin() as db:
        db.get(ScheduleConsent, h["a_id"]).enabled = False
    statements = []
    engine = h["sessions"].kw["bind"]

    def observed(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)  # SQL shape only; never parameters or private values.

    event.listen(engine, "before_cursor_execute", observed)
    try:
        service.clock = lambda: BASE + 61000
        assert service.claim()["terminal"]
    finally:
        event.remove(engine, "before_cursor_execute", observed)
    assert not any(
        "schedules.definition" in statement or "schedules.source_snapshot" in statement
        for statement in statements
    )


def test_native_inbox_read_does_not_wait_for_scope_write_lock(harness):
    from ada.models import Scope

    h = harness
    if h["backend"] != "postgres":
        pytest.skip("MVCC read/write concurrency requires native PostgreSQL")
    service, scope, _, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    service.run_once()
    db = h["sessions"]()
    transaction = db.begin()
    pool = ThreadPoolExecutor(max_workers=1)
    try:
        db.scalar(
            select(Scope).where(Scope.owner_id == h["a_id"], Scope.id == scope).with_for_update()
        )
        read = pool.submit(lambda: h["client"].get("/v1/scheduling/inbox", headers=h["a"]))
        result = read.result(timeout=2)
        assert result.status_code == 200
    finally:
        transaction.rollback()
        pool.shutdown(wait=True)
        db.close()


def test_owner_can_page_through_inbox_and_occurrence_history(harness):
    h = harness
    service, _, key, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    service.run_once()
    service.clock = lambda: BASE + 86400000 + 61000
    service.run_once()
    c = h["client"]
    first = c.get("/v1/scheduling/inbox?limit=1&offset=0", headers=h["a"]).json()
    second = c.get("/v1/scheduling/inbox?limit=1&offset=1", headers=h["a"]).json()
    assert len(first) == len(second) == 1 and first[0]["id"] != second[0]["id"]
    assert c.get("/v1/scheduling/inbox?offset=2", headers=h["a"]).json() == []
    assert c.get("/v1/scheduling/inbox?limit=1", headers=h["b"]).json() == []
    receipts = c.get(f"/v1/schedules/{key}/occurrences?limit=1&offset=1", headers=h["a"]).json()
    assert len(receipts) == 1
    assert c.get("/v1/scheduling/inbox?offset=-1", headers=h["a"]).status_code == 422


def test_supervised_inbox_dispatch_does_not_wait_for_provider_or_inference_idle(
    harness, tmp_path, monkeypatch
):
    import threading
    from contextlib import nullcontext
    from types import SimpleNamespace

    import uvicorn

    from ada import host_supervisor as host
    from ada.api import create_app
    from ada.providers import FakeProvider

    supervised = create_app(harness["settings"], FakeProvider(), harness["sessions"])
    ready = threading.Event()
    snapshot = {
        "observed_at": host.timestamp(),
        "discretionary_pause": None,
        "provider": "unreachable",
        "database": "ready",
    }

    def observe(*args):
        ready.set()
        return snapshot

    monkeypatch.setattr(host, "observe", observe)
    monkeypatch.setattr(host, "admission_owner", lambda *args: nullcontext())
    monkeypatch.setattr("ada.api.create_app", lambda settings: supervised)

    async def serve(server):
        assert ready.wait(2)
        assert not supervised.state.consolidation.discretionary_allowed()
        gate = supervised.state.scheduling.discretionary_allowed
        assert gate(), (
            "Non-inference inbox delivery incorrectly needs provider readiness/quiet time"
        )
        snapshot["discretionary_pause"] = "disk_pressure"
        assert not gate()
        snapshot["discretionary_pause"] = None
        snapshot["database"] = "unavailable"
        assert not gate()
        snapshot["database"] = "ready"
        snapshot["observed_at"] = host.timestamp() - 6001
        assert not gate()
        server.should_exit = True

    monkeypatch.setattr(uvicorn.Server, "serve", serve)
    config = SimpleNamespace(poll_seconds=2, quiet_seconds=60, port=18423, shutdown_seconds=5)
    host.serve(config, tmp_path, harness["settings"], "public-schedule-wiring")
