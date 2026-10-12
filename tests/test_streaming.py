import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from ada.admin import set_admin_grant
from ada.models import Event, Request, now_ms
from ada.providers import Completion, ProviderError
from ada.service import recover_stale
from ada.stream_models import StreamAttempt, StreamEvent
from ada.streaming import StreamingService


class ControlledStream:
    id, model = "controlled_stream", "test-stream-v1"

    def __init__(self, delayed_stop=False, error=False):
        self.entered = threading.Event()
        self.release = threading.Event()
        self.stopped = threading.Event()
        self.cancel_seen = threading.Event()
        self.delayed_stop = delayed_stop
        self.error = error
        self.calls = []

    def stream(self, messages, cancel):
        self.calls.append(messages)
        try:
            yield "Provisional 🫖 [M"
            self.entered.set()
            while not self.release.wait(0.01):
                if cancel.is_set():
                    self.cancel_seen.set()
                    if not self.delayed_stop:
                        return
            if self.error:
                raise ProviderError("provider_unavailable")
            yield "1] complete."
            yield Completion("Provisional 🫖 [M1] complete.", self.model, 10, 5)
        finally:
            self.stopped.set()


def attach(h, **kwargs):
    provider = ControlledStream(**kwargs)
    h["app"].state.chat.provider = provider
    return provider


def submit(h, cid, rid=None, who="a", content="Synthetic streaming turn"):
    rid = rid or str(uuid4())
    result = h["client"].post(
        f"/v1/conversations/{cid}/stream-requests",
        headers=h[who],
        json={"request_id": rid, "content": content},
    )
    return rid, result


def status(h, rid, who="a"):
    return h["client"].get(f"/v1/requests/{rid}/stream-status", headers=h[who])


def wait_state(h, rid, expected):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        result = status(h, rid)
        if result.status_code == 200 and result.json()["stream_state"] == expected:
            return result.json()
        time.sleep(0.01)
    raise AssertionError(f"stream did not reach {expected}")


def test_consent_auth_and_cancel_hold_capacity_until_provider_stops(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h, delayed_stop=True)
    rid, started = submit(h, cid)
    assert started.status_code == 202
    assert p.entered.wait(5)
    assert status(h, rid, "b").status_code == 404
    assert (
        h["client"]
        .post(f"/v1/requests/{rid}/cancel", headers=h["b"], json={"attempt": 1})
        .status_code
        == 404
    )
    assert h["client"].post(f"/v1/requests/{rid}/cancel", json={"attempt": 1}).status_code == 401
    cancel = h["client"].post(f"/v1/requests/{rid}/cancel", headers=h["a"], json={"attempt": 1})
    assert cancel.status_code == 200 and cancel.json()["outcome"] == "requested"
    assert p.cancel_seen.wait(5)
    assert wait_state(h, rid, "cancel_requested")["result"]["status"] == "running"
    assert h["app"].state.chat.capacity._value == 1
    with h["sessions"]() as db:
        assert (
            db.scalar(select(func.count()).select_from(Event).where(Event.request_id == rid)) == 1
        )
    p.release.set()
    final = wait_state(h, rid, "cancelled")
    assert final["result"]["status"] == "failed"
    assert final["result"]["error_code"] == "request_cancelled"
    assert final["result"]["response"] is None
    assert p.stopped.is_set()
    deadline = time.monotonic() + 5
    while h["app"].state.chat.capacity._value != 2 and time.monotonic() < deadline:
        time.sleep(0.01)
    assert h["app"].state.chat.capacity._value == 2
    assert (
        h["client"].post(f"/v1/requests/{rid}/cancel", headers=h["a"], json={"attempt": 1}).json()
        == cancel.json()
    )
    assert (
        h["client"]
        .post(f"/v1/requests/{rid}/cancel", headers=h["a"], json={"attempt": 2})
        .status_code
        == 409
    )


def test_durable_replay_terminal_commit_and_legacy_retry(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    rid, result = submit(h, cid)
    assert result.status_code == 202 and p.entered.wait(5)
    assert submit(h, cid, rid)[1].status_code == 202
    assert submit(h, cid, rid, content="different")[1].status_code == 409
    p.release.set()
    final = wait_state(h, rid, "completed")
    assert len(p.calls) == 1
    response = h["client"].get(f"/v1/requests/{rid}/stream?attempt=1&after=0", headers=h["a"])
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    events = [
        json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")
    ]
    assert [e["sequence"] for e in events] == sorted({e["sequence"] for e in events})
    assert events[0]["type"] == "started" and events[-1]["type"] == "completed"
    cursor = events[-2]["sequence"]
    replay = h["client"].get(f"/v1/requests/{rid}/stream?attempt=1&after={cursor}", headers=h["a"])
    assert replay.text.count("data: ") == 1
    assert send(h, cid, "Synthetic streaming turn", rid).json() == final["result"]
    assert (
        h["client"]
        .post(f"/v1/requests/{rid}/cancel", headers=h["a"], json={"attempt": 1})
        .json()["outcome"]
        == "already_terminal"
    )
    with h["sessions"]() as db:
        assert (
            db.scalar(select(func.count()).select_from(Event).where(Event.request_id == rid)) == 2
        )
        assert db.get(Request, (h["a_id"], rid)).response == "Provisional 🫖 [M1] complete."


def test_provider_failure_then_cancelled_retry_keeps_snapshot(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h, error=True)
    rid, r = submit(h, cid)
    assert r.status_code == 202 and p.entered.wait(5)
    p.release.set()
    assert wait_state(h, rid, "failed")["result"]["error_code"] == "provider_unavailable"
    p2 = attach(h)
    assert submit(h, cid, rid)[1].status_code == 202 and p2.entered.wait(5)
    assert p2.calls == p.calls
    h["client"].post(f"/v1/requests/{rid}/cancel", headers=h["a"], json={"attempt": 2})
    assert wait_state(h, rid, "cancelled")["result"]["attempt"] == 2


def test_retention_checkpoint_expired_cursor_and_native_constraints(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    rid, r = submit(h, cid)
    assert r.status_code == 202 and p.entered.wait(5)
    manager = h["app"].state.streaming
    for _ in range(270):
        assert manager._delta((h["a_id"], rid, 1), "x")
    checkpoint = status(h, rid).json()
    assert checkpoint["replay_after"] > 0 and len(checkpoint["provisional"]) > 270
    assert (
        h["client"].get(f"/v1/requests/{rid}/stream?attempt=1&after=0", headers=h["a"]).status_code
        == 409
    )
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count()).select_from(StreamEvent).where(StreamEvent.request_id == rid)
            )
            == 256
        )
    h["client"].post(f"/v1/requests/{rid}/cancel", headers=h["a"], json={"attempt": 1})
    final = wait_state(h, rid, "cancelled")
    assert len(final["provisional"]) > 270 and final["result"]["response"] is None
    assert (
        h["client"]
        .get(f"/v1/requests/{rid}/stream?attempt=1&after={final['sequence'] + 1}", headers=h["a"])
        .status_code
        == 409
    )
    with h["sessions"].begin() as db:
        db.get(StreamAttempt, (h["a_id"], rid, 1)).finished_at = 1
    assert (
        h["client"]
        .get(f"/v1/requests/{rid}/stream?attempt=1&after={final['sequence']}", headers=h["a"])
        .status_code
        == 409
    )


def test_restart_interrupts_and_fences_old_worker_publication(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    rid, r = submit(h, cid)
    assert r.status_code == 202 and p.entered.wait(5)
    replacement = StreamingService(h["app"].state.chat)
    replacement.recover()
    final = wait_state(h, rid, "interrupted")
    assert final["result"]["error_code"] == "interrupted"
    assert not replacement._delta((h["a_id"], rid, 1), "late")
    p.release.set()
    assert p.stopped.wait(5)
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(Event)
                .where(Event.request_id == rid, Event.role == "assistant")
            )
            == 0
        )
    p2 = attach(h)
    assert submit(h, cid, rid)[1].status_code == 202 and p2.entered.wait(5)
    assert p2.calls == p.calls
    p2.release.set()
    assert wait_state(h, rid, "completed")["result"]["attempt"] == 2


def test_populated_0012_upgrade_check_replay_and_guarded_downgrade(harness):
    h = harness
    cid, _ = make_conversation(h)
    old = send(h, cid, "Old completed snapshot").json()
    command.downgrade(h["config"], "0012")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, cid, "Old completed snapshot", old["request_id"]).json() == old
    p = attach(h)
    rid, r = submit(h, cid)
    assert r.status_code == 202 and p.entered.wait(5)
    p.release.set()
    wait_state(h, rid, "completed")
    with pytest.raises(RuntimeError, match="Streaming history"):
        command.downgrade(h["config"], "0012")
    assert status(h, rid).json()["stream_state"] == "completed"


def test_native_owner_constraints_strict_cancel_and_metadata_only_admin(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    rid, r = submit(h, cid)
    assert r.status_code == 202 and p.entered.wait(5)
    for field, value in (("state", "approved"), ("sequence", -1)):
        with pytest.raises(IntegrityError), h["sessions"].begin() as db:
            setattr(db.get(StreamAttempt, (h["a_id"], rid, 1)), field, value)
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(
            StreamEvent(
                owner_id=h["b_id"],
                request_id=rid,
                attempt=1,
                sequence=1,
                kind="delta",
                payload={"text": "forged"},
                created_at=1,
            )
        )
    for body in (
        {"attempt": True},
        {"attempt": 0},
        {"attempt": 1, "owner_id": h["a_id"]},
        {"attempt": 1, "force": True},
    ):
        assert (
            h["client"].post(f"/v1/requests/{rid}/cancel", headers=h["a"], json=body).status_code
            == 422
        )
    set_admin_grant(h["sessions"], h["b_id"], True)
    detail = h["client"].get(f"/v1/admin/requests/{h['a_id']}/{rid}", headers=h["b"])
    assert detail.status_code == 200 and detail.json()["stream"]["state"] == "running"
    assert set(detail.json()["stream"]) == {
        "state",
        "sequence",
        "replay_after",
        "created_at",
        "finished_at",
    }
    assert "Provisional" not in detail.text and "Synthetic streaming" not in detail.text
    assert status(h, rid, "b").status_code == 404
    p.release.set()
    wait_state(h, rid, "completed")


def test_terminal_write_failure_is_interrupted_on_status_not_fake_success(harness, monkeypatch):
    import ada.streaming as module

    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    rid, r = submit(h, cid)
    assert r.status_code == 202 and p.entered.wait(5)

    def broken(*args, **kwargs):
        raise RuntimeError("synthetic publication failure")

    monkeypatch.setattr(module, "record_chat_event", broken)
    p.release.set()
    assert p.stopped.wait(5)
    deadline = time.monotonic() + 5
    while h["app"].state.streaming.workers and time.monotonic() < deadline:
        time.sleep(0.01)
    final = wait_state(h, rid, "interrupted")
    assert final["result"]["response"] is None and final["result"]["error_code"] == "interrupted"
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(Event)
                .where(Event.request_id == rid, Event.role == "assistant")
            )
            == 0
        )


def test_native_cancel_complete_race_commits_exactly_one_winner(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Native PostgreSQL row locks required")
    cid, _ = make_conversation(h)
    p = attach(h)
    rid, r = submit(h, cid)
    assert r.status_code == 202 and p.entered.wait(5)
    with ThreadPoolExecutor(2) as pool:
        cancel = pool.submit(h["app"].state.streaming.cancel, h["a_id"], rid, 1)
        p.release.set()
        receipt = cancel.result(5)
    deadline = time.monotonic() + 5
    while (
        status(h, rid).json()["stream_state"] in ("running", "cancel_requested")
        and time.monotonic() < deadline
    ):
        time.sleep(0.01)
    final = status(h, rid).json()
    assert final["stream_state"] == (
        "cancelled" if receipt["outcome"] == "requested" else "completed"
    )
    with h["sessions"]() as db:
        assert db.scalar(
            select(func.count())
            .select_from(Event)
            .where(Event.request_id == rid, Event.role == "assistant")
        ) == int(final["stream_state"] == "completed")


def test_operator_recovery_fences_live_stream_without_releasing_provider_capacity(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h, delayed_stop=True)
    rid, response = submit(h, cid)
    assert response.status_code == 202 and p.entered.wait(5)
    try:
        assert recover_stale(h["sessions"], now_ms() + 1000) == 1
        checkpoint = status(h, rid).json()
        assert checkpoint["stream_state"] == "interrupted"
        assert checkpoint["result"]["status"] == "failed"
        assert checkpoint["result"]["error_code"] == "interrupted"
        events, terminal = h["app"].state.streaming.events(h["a_id"], rid, 1, 0)
        assert terminal and events[-1]["type"] == "interrupted"
        assert h["app"].state.chat.capacity._value == 1
    finally:
        p.release.set()
        assert p.stopped.wait(5)
    assert wait_state(h, rid, "interrupted")["result"]["response"] is None
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(Event)
                .where(Event.request_id == rid, Event.role == "assistant")
            )
            == 0
        )


def test_owner_history_limit_rolls_back_new_request_and_admission(harness, monkeypatch):
    import ada.streaming as module

    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    rid, response = submit(h, cid)
    assert response.status_code == 202 and p.entered.wait(5)
    p.release.set()
    wait_state(h, rid, "completed")
    monkeypatch.setattr(module, "MAX_OWNER_ATTEMPTS", 1, raising=False)
    next_id, rejected = submit(h, cid)
    assert rejected.status_code == 413 and rejected.json()["detail"] == "stream_history_limit"
    with h["sessions"]() as db:
        assert db.get(Request, (h["a_id"], next_id)) is None
        assert (
            db.scalar(select(func.count()).select_from(Event).where(Event.request_id == next_id))
            == 0
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(StreamAttempt)
                .where(StreamAttempt.request_id == next_id)
            )
            == 0
        )
    assert status(h, rid).json()["stream_state"] == "completed"


def test_request_attempt_limit_preserves_failed_snapshot_and_attempt(harness, monkeypatch):
    import ada.streaming as module

    h = harness
    cid, _ = make_conversation(h)
    p = attach(h, error=True)
    rid, response = submit(h, cid)
    assert response.status_code == 202 and p.entered.wait(5)
    p.release.set()
    previous = wait_state(h, rid, "failed")
    monkeypatch.setattr(module, "MAX_REQUEST_ATTEMPTS", 1)
    assert submit(h, cid, rid)[1].status_code == 413
    assert status(h, rid).json() == previous
    with h["sessions"]() as db:
        assert (
            db.scalar(select(func.count()).select_from(Event).where(Event.request_id == rid)) == 1
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(StreamAttempt)
                .where(StreamAttempt.request_id == rid)
            )
            == 1
        )


def test_expired_attempt_cannot_publish_even_without_a_late_delta(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)

    def final_only(messages, cancel):
        try:
            yield "Synthetic checkpoint"
            p.entered.set()
            p.release.wait(5)
            yield Completion("Synthetic checkpoint", p.model)
        finally:
            p.stopped.set()

    p.stream = final_only
    rid, response = submit(h, cid)
    assert response.status_code == 202 and p.entered.wait(5)
    with h["sessions"].begin() as db:
        db.get(StreamAttempt, (h["a_id"], rid, 1)).deadline_at = 1
    p.release.set()
    deadline = time.monotonic() + 5
    while h["app"].state.streaming.workers and time.monotonic() < deadline:
        time.sleep(0.01)
    final = status(h, rid).json()
    assert final["stream_state"] == "failed" and final["result"]["error_code"] == "provider_timeout"
    assert final["result"]["response"] is None
    assert h["app"].state.chat.capacity._value == 2
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(Event)
                .where(Event.request_id == rid, Event.role == "assistant")
            )
            == 0
        )
