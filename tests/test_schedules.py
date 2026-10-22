"""Owner consent, exact operations and fenced inbox delivery over real HTTP."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from conftest import make_conversation
from sqlalchemy import func, select
from test_schedule_time import definition

from ada.models import Event

BASE = int(datetime(2026, 10, 20, 14, 59, tzinfo=timezone.utc).timestamp() * 1000)


def setup_schedule(h, **changes):
    client = h["client"]
    policy = client.get("/v1/scheduling/policy", headers=h["a"])
    assert policy.status_code == 200, policy.text
    service = h["app"].state.scheduling
    service.clock = lambda: BASE
    service.curiosity.clock = lambda: service.clock()
    service.settings.scheduler_enabled = True
    if not policy.json()["enabled"]:
        result = client.post(
            "/v1/scheduling/policy",
            headers=h["a"],
            json={
                "operation_id": str(uuid4()),
                "expected_revision": policy.json()["revision"],
                "enabled": True,
            },
        )
        assert result.status_code == 200, result.text
    cid, profile = make_conversation(h)
    scope = client.get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    body = {"operation_id": str(uuid4()), "definition": definition(**changes)}
    preview = client.post(f"/v1/scopes/{scope}/schedules/preview", headers=h["a"], json=body)
    assert preview.status_code == 200, preview.text
    key = str(uuid4())
    confirm = {
        "operation_id": str(uuid4()),
        "preview_id": body["operation_id"],
        "expected_generation": 0,
        "consent_revision": client.get("/v1/scheduling/policy", headers=h["a"]).json()["revision"],
    }
    result = client.post(f"/v1/schedules/{key}/confirm", headers=h["a"], json=confirm)
    assert result.status_code == 200, result.text
    return service, scope, key, confirm, profile


def test_preview_confirmation_replay_conflict_and_wrong_owner(harness):
    h = harness
    service, scope, key, confirm, _ = setup_schedule(h)
    c = h["client"]
    original = c.get(f"/v1/scheduling/receipts/{confirm['operation_id']}", headers=h["a"]).json()
    assert c.post(f"/v1/schedules/{key}/confirm", headers=h["a"], json=confirm).json() == original
    assert (
        c.post(
            f"/v1/schedules/{key}/confirm",
            headers=h["a"],
            json=confirm | {"expected_generation": 9},
        ).status_code
        == 409
    )
    assert c.get(f"/v1/schedules/{key}", headers=h["b"]).status_code == 404
    assert c.get(f"/v1/scopes/{scope}/schedules", headers=h["b"]).status_code == 404
    assert c.get("/v1/scheduling/inbox").status_code == 401
    assert not service.run_once()


def test_durable_inbox_ack_open_never_fabricates_user_turn(harness):
    h = harness
    service, _, key, _, profile = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    assert service.run_once()
    assert not service.run_once()
    c = h["client"]
    items = c.get("/v1/scheduling/inbox", headers=h["a"]).json()
    assert len(items) == 1 and items[0]["text"] == definition()["text"]
    item = items[0]["id"]
    assert (
        c.post(
            f"/v1/scheduling/inbox/{item}/actions",
            headers=h["b"],
            json={"operation_id": str(uuid4()), "action": "acknowledge"},
        ).status_code
        == 404
    )
    ack = {"operation_id": str(uuid4()), "action": "acknowledge"}
    saved = c.post(f"/v1/scheduling/inbox/{item}/actions", headers=h["a"], json=ack)
    assert saved.status_code == 200
    assert (
        c.post(f"/v1/scheduling/inbox/{item}/actions", headers=h["a"], json=ack).json()
        == saved.json()
    )
    opened = {
        "operation_id": str(uuid4()),
        "conversation_id": str(uuid4()),
        "personality_id": profile,
    }
    r = c.post(f"/v1/scheduling/inbox/{item}/open", headers=h["a"], json=opened)
    assert r.status_code == 200, r.text
    assert (
        c.post(f"/v1/scheduling/inbox/{item}/open", headers=h["a"], json=opened).json() == r.json()
    )
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Event)) == 0
    assert (
        c.get(f"/v1/schedules/{key}/occurrences", headers=h["a"]).json()[0]["state"] == "delivered"
    )


def test_catch_up_only_latest_and_backward_clock_does_not_duplicate(harness):
    h = harness
    service, _, key, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 2 * 86400000 + 61000
    assert service.run_once()
    c = h["client"]
    assert len(c.get("/v1/scheduling/inbox", headers=h["a"]).json()) == 1
    receipts = c.get(f"/v1/schedules/{key}/occurrences", headers=h["a"]).json()
    assert sum(r["state"] == "delivered" for r in receipts) == 1
    assert sum(r["reason"] == "missed_latest_only" for r in receipts) == 2
    service.clock = lambda: BASE + 61000
    assert not service.run_once()


def test_pause_between_claim_and_publish_fences_late_delivery(harness):
    h = harness
    service, _, key, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    claimed = service.claim()
    assert claimed is not None
    result = h["client"].post(
        f"/v1/schedules/{key}/actions",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_generation": 1,
            "action": "pause",
        },
    )
    assert result.status_code == 200, result.text
    service.publish(claimed)
    assert h["client"].get("/v1/scheduling/inbox", headers=h["a"]).json() == []


def test_quiet_hours_defer_latest_instead_of_delivering(harness):
    h = harness
    service, _, _, _, _ = setup_schedule(h, allowed_start=8 * 60, allowed_end=9 * 60)
    service.clock = lambda: BASE + 3 * 3600000
    service.run_once()
    assert h["client"].get("/v1/scheduling/inbox", headers=h["a"]).json() == []
    service.clock = lambda: BASE + 86400000 + 61000
    assert service.run_once()
    assert len(h["client"].get("/v1/scheduling/inbox", headers=h["a"]).json()) == 1


def test_owner_off_and_global_stop_are_independent(harness):
    h = harness
    service, _, _, _, _ = setup_schedule(h)
    service.clock = lambda: BASE + 61000
    service.settings.scheduler_enabled = False
    assert not service.run_once()
    service.settings.scheduler_enabled = True
    policy = h["client"].get("/v1/scheduling/policy", headers=h["a"]).json()
    result = h["client"].post(
        "/v1/scheduling/policy",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_revision": policy["revision"],
            "enabled": False,
        },
    )
    assert result.status_code == 200
    service.run_once()
    assert h["client"].get("/v1/scheduling/inbox", headers=h["a"]).json() == []


@pytest.mark.parametrize(
    "changes",
    [
        dict(
            timezone="UTC",
            start_local="9999-12-31T12:00",
            frequency="daily",
            count=2,
            expires_at="9999-12-31T23:00:00Z",
        ),
        dict(
            timezone="UTC",
            start_local="9999-12-31T12:00",
            frequency="weekly",
            count=2,
            expires_at="9999-12-31T23:00:00Z",
        ),
        dict(
            timezone="Etc/GMT-14",
            start_local="0001-01-01T00:00",
            frequency="once",
            count=1,
            expires_at="0001-01-02T00:00:00Z",
        ),
    ],
)
def test_calendar_range_error_is_422_and_does_not_reserve_an_operation(harness, changes):
    _, scope, key, _, _ = setup_schedule(harness)
    op = str(uuid4())
    client = harness["client"]
    auth = harness["a"]
    response = client.post(
        f"/v1/scopes/{scope}/schedules/preview",
        headers=auth,
        json={"operation_id": op, "definition": definition(**changes)},
    )
    assert response.status_code == 422
    assert client.get(f"/v1/scheduling/receipts/{op}", headers=auth).status_code == 404
    assert client.get(f"/v1/schedules/{key}", headers=auth).json()["state"] == "active"
