"""Follow-up remains explicit and existing consent/dispatcher authority remains effective."""

from uuid import uuid4

from test_curiosity import enabled
from test_schedule_time import definition
from test_schedules import BASE, setup_schedule
from test_work import body, save, setup


def test_question_requires_consent_and_task_completion_suppresses_draft(harness):
    h = harness
    _, scope = setup(h)
    key, value = str(uuid4()), body()
    assert save(h, scope, key, value).status_code == 200
    action = {
        "operation_id": str(uuid4()),
        "expected_revision": 1,
        "policy_revision": 1,
        "topic": "work",
        "review": "confirm",
    }
    assert (
        h["client"].post(f"/v1/work/{key}/followup", headers=h["a"], json=action).status_code == 409
    )
    policy = enabled(h)
    action["policy_revision"] = policy["revision"]
    result = h["client"].post(f"/v1/work/{key}/followup", headers=h["a"], json=action)
    assert result.status_code == 200
    assert (
        h["client"].post(f"/v1/work/{key}/followup", headers=h["a"], json=action).json()
        == result.json()
    )
    question = result.json()["question_id"]
    output = h["client"].get(f"/v1/curiosity/questions/{question}", headers=h["a"]).json()
    assert value["fields"]["description"] in output["text"]
    assert output["policy"]["generator"] == "ada-work-question-v1"
    assert (
        save(
            h, scope, key, body(expected_revision=2, fields=value["fields"] | {"status": "done"})
        ).status_code
        == 200
    )
    assert (
        h["client"].get(f"/v1/curiosity/questions/{question}", headers=h["a"]).json()["state"]
        == "dismissed"
    )


def test_task_reminder_preview_cannot_bypass_work_binding_or_revive_completed_task(harness):
    h = harness
    scheduler, scope, _, _, _ = setup_schedule(h)
    work = h["app"].state.work
    work.clock = lambda: BASE
    key, value = str(uuid4()), body()
    assert save(h, scope, key, value).status_code == 200
    preview = {
        "operation_id": str(uuid4()),
        "expected_revision": 1,
        "definition": definition(text=value["fields"]["description"]),
    }
    result = h["client"].post(f"/v1/work/{key}/reminder-preview", headers=h["a"], json=preview)
    assert result.status_code == 200
    confirm = {
        "operation_id": str(uuid4()),
        "expected_revision": 1,
        "preview_id": preview["operation_id"],
        "consent_revision": scheduler.policy(h["a_id"])["revision"],
        "schedule_id": str(uuid4()),
        "expected_generation": 0,
        "review": "confirm",
    }
    plain = {
        k: v for k, v in confirm.items() if k not in ("expected_revision", "schedule_id", "review")
    }
    assert (
        h["client"]
        .post(f"/v1/schedules/{confirm['schedule_id']}/confirm", headers=h["a"], json=plain)
        .status_code
        == 409
    )
    assert (
        h["client"]
        .post(f"/v1/work/{key}/reminder-confirm", headers=h["a"], json=confirm)
        .status_code
        == 200
    )
    assert (
        h["client"]
        .post(f"/v1/work/{key}/reminder-confirm", headers=h["a"], json=confirm)
        .status_code
        == 200
    )
    assert (
        save(
            h, scope, key, body(expected_revision=2, fields=value["fields"] | {"status": "done"})
        ).status_code
        == 200
    )
    schedule = h["client"].get(f"/v1/schedules/{confirm['schedule_id']}", headers=h["a"]).json()
    assert schedule["state"] == "paused"
    for action in ("snooze", "reauthorize"):
        mutation = {
            "operation_id": str(uuid4()),
            "expected_generation": schedule["generation"],
            "action": action,
        }
        if action == "snooze":
            mutation["until"] = "2026-10-20T16:00:00Z"
        assert (
            h["client"]
            .post(f"/v1/schedules/{schedule['id']}/actions", headers=h["a"], json=mutation)
            .status_code
            == 409
        )


def test_expired_or_changed_task_preview_cannot_create_reminder(harness):
    h = harness
    scheduler, scope, _, _, _ = setup_schedule(h)
    h["app"].state.work.clock = lambda: BASE
    key, value = str(uuid4()), body()
    assert save(h, scope, key, value).status_code == 200
    preview = {
        "operation_id": str(uuid4()),
        "expected_revision": 1,
        "definition": definition(text=value["fields"]["description"]),
    }
    assert (
        h["client"]
        .post(f"/v1/work/{key}/reminder-preview", headers=h["a"], json=preview)
        .status_code
        == 200
    )
    assert (
        save(
            h,
            scope,
            key,
            body(expected_revision=1, fields=value["fields"] | {"status": "dismissed"}),
        ).status_code
        == 200
    )
    confirm = {
        "operation_id": str(uuid4()),
        "expected_revision": 1,
        "preview_id": preview["operation_id"],
        "consent_revision": scheduler.policy(h["a_id"])["revision"],
        "schedule_id": str(uuid4()),
        "expected_generation": 0,
        "review": "confirm",
    }
    assert (
        h["client"]
        .post(f"/v1/work/{key}/reminder-confirm", headers=h["a"], json=confirm)
        .status_code
        == 409
    )
