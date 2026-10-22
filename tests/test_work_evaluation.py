"""Held-out public/synthetic workflows; no inferred tasks or human-acceptance claim."""

from uuid import uuid4

from conftest import send
from test_work import body, save, setup

from ada.admin import set_admin_grant
from ada.models import SourceVersion


def test_balanced_personal_and_project_goal_workflow_and_no_admin_reader(harness):
    h = harness
    _, personal = setup(h)
    project, op = str(uuid4()), str(uuid4())
    intent = {"operation_id": op, "name": "Public held-out development project"}
    created = h["client"].post(f"/v1/work/projects/{project}", headers=h["a"], json=intent)
    assert created.status_code == 200 and created.json()["scope_id"] == project
    assert (
        h["client"].post(f"/v1/work/projects/{project}", headers=h["a"], json=intent).json()
        == created.json()
    )
    goal, task, decision = str(uuid4()), str(uuid4()), str(uuid4())
    assert (
        save(
            h,
            project,
            goal,
            body(
                fields={"kind": "goal", "description": "Prepare a public demo", "status": "planned"}
            ),
        ).status_code
        == 200
    )
    assert (
        save(
            h,
            project,
            task,
            body(
                fields={
                    "kind": "task",
                    "description": "Review the public example",
                    "goal_id": goal,
                    "status": "planned",
                }
            ),
        ).status_code
        == 200
    )
    assert (
        save(
            h,
            personal,
            decision,
            body(
                fields={
                    "kind": "task",
                    "description": "Choose a public practice time",
                    "status": "unknown",
                }
            ),
        ).status_code
        == 200
    )
    brief = {
        "operation_id": str(uuid4()),
        "scope_ids": [personal, project],
        "item_ids": [task, decision],
        "day": "2026-10-22",
        "timezone": "America/Phoenix",
    }
    result = h["client"].post("/v1/work/briefs", headers=h["a"], json=brief)
    assert result.status_code == 200 and result.json()["needs_decision"] == 1
    assert {i["task"]["scope_id"] for i in result.json()["items"]} == {project, personal}
    set_admin_grant(h["sessions"], h["b_id"], True)
    assert h["client"].get(f"/v1/work/{task}", headers=h["b"]).status_code == 404
    assert h["client"].post("/v1/work/briefs", headers=h["b"], json=brief).status_code == 404
    assert h["client"].get(f"/v1/work/receipts/{uuid4()}", headers=h["a"]).status_code == 404


def test_repeated_time_requires_explicit_occurrence_and_keeps_two_instants(harness):
    h = harness
    _, scope = setup(h)
    values = []
    for fold in ["first", "second"]:
        key = str(uuid4())
        value = body(
            fields=body()["fields"]
            | {"due_local": "2026-11-01T01:30", "timezone": "America/New_York", "fold": fold}
        )
        assert save(h, scope, key, value).status_code == 200
        values.append(h["client"].get(f"/v1/work/{key}", headers=h["a"]).json()["due_at"])
    assert values[1] - values[0] == 3600000


def test_due_time_transition_invalidates_brief_cache_without_rewriting_old_snapshot(harness):
    from datetime import datetime, timezone

    from ada.models import now_ms

    h = harness
    _, scope = setup(h)
    clock = [now_ms()]
    h["app"].state.work.clock = lambda: clock[0]
    local = datetime.fromtimestamp((clock[0] + 3600000) / 1000, timezone.utc).strftime(
        "%Y-%m-%dT%H:%M"
    )
    key = str(uuid4())
    assert (
        save(
            h, scope, key, body(fields=body()["fields"] | {"due_local": local, "timezone": "UTC"})
        ).status_code
        == 200
    )
    request = {
        "operation_id": str(uuid4()),
        "scope_ids": [scope],
        "item_ids": [key],
        "day": "2026-10-22",
        "timezone": "UTC",
    }
    first = h["client"].post("/v1/work/briefs", headers=h["a"], json=request).json()
    assert not first["items"][0]["overdue"]
    clock[0] += 7200000
    second = (
        h["client"]
        .post("/v1/work/briefs", headers=h["a"], json=request | {"operation_id": str(uuid4())})
        .json()
    )
    assert second["items"][0]["overdue"] and second["id"] != first["id"]
    assert (
        not h["client"]
        .get(f"/v1/work/briefs/{first['id']}", headers=h["a"])
        .json()["items"][0]["overdue"]
    )


def test_changed_future_or_cross_owner_source_cannot_supply_a_work_context(harness):
    from conftest import make_conversation

    h = harness
    cid, scope = setup(h)
    r = send(h, cid, "Public held-out source.").json()
    event = next(
        x
        for x in h["client"].get(f"/v1/conversations/{cid}/events", headers=h["a"]).json()
        if x["role"] == "assistant"
    )
    source = (
        h["client"].get(f"/v1/source-versions/{event['source_version_id']}", headers=h["a"]).json()
    )
    pin = {
        "source_version_id": source["id"],
        "version": source["version"],
        "content_hash": source["content_hash"],
        "span_start": 0,
        "span_end": len(source["content"]),
    }
    key = str(uuid4())
    value = body(fields=body()["fields"] | {"pins": [pin], "origin_request_id": r["request_id"]})
    assert save(h, scope, key, value).status_code == 200
    with h["sessions"].begin() as db:
        db.get(SourceVersion, source["id"]).content = "Changed public synthetic source"
    detail = h["client"].get(f"/v1/work/{key}", headers=h["a"]).json()
    assert detail["sources"] == [] and detail["source_unavailable"] == "original_source_unavailable"

    new = body(fields=value["fields"])
    assert (
        h["client"]
        .post(f"/v1/scopes/{scope}/work/{uuid4()}/preview", headers=h["a"], json=new)
        .status_code
        == 409
    )
    other, _ = make_conversation(h, "b")
    other_scope = h["client"].get(f"/v1/conversations/{other}", headers=h["b"]).json()["scope_id"]
    cross = body(fields=body()["fields"] | {"pins": [pin]})
    assert (
        h["client"]
        .post(f"/v1/scopes/{other_scope}/work/{uuid4()}/preview", headers=h["b"], json=cross)
        .status_code
        == 404
    )
    with h["sessions"].begin() as db:
        original = db.get(SourceVersion, source["id"])
        original.content = source["content"]
        original.created_at = h["app"].state.work.clock() + 60000
    assert (
        h["client"]
        .post(f"/v1/scopes/{scope}/work/{uuid4()}/preview", headers=h["a"], json=new)
        .status_code
        == 409
    )
    with h["sessions"].begin() as db:
        db.delete(db.get(SourceVersion, source["id"]))
    detail = h["client"].get(f"/v1/work/{key}", headers=h["a"]).json()
    assert detail["sources"] == [] and detail["source_unavailable"] == "original_source_unavailable"


def test_due_preview_is_invalidated_by_changed_timezone_rules(harness, monkeypatch):
    import ada.work as work

    h = harness
    _, scope = setup(h)
    key, value = (
        str(uuid4()),
        body(
            fields=body()["fields"]
            | {"due_local": "2026-11-01T01:30", "timezone": "America/New_York", "fold": "first"}
        ),
    )
    preview = h["client"].post(f"/v1/scopes/{scope}/work/{key}/preview", headers=h["a"], json=value)
    assert preview.status_code == 200
    value["preview_hash"] = preview.json()["preview_hash"]
    monkeypatch.setattr(work, "TIMEZONE_DATA", "synthetic_changed_rules")
    assert (
        h["client"].post(f"/v1/scopes/{scope}/work/{key}", headers=h["a"], json=value).status_code
        == 409
    )
