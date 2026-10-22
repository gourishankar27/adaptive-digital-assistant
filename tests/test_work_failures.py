"""Failure responses preserve privacy and cannot imply a saved commitment."""

from uuid import uuid4

from sqlalchemy.exc import OperationalError
from test_work import body, save, setup


def test_database_failure_is_sanitized_and_never_claimed_saved(harness, monkeypatch):
    h = harness
    _, scope = setup(h)

    def broken(*args):
        raise OperationalError(
            "synthetic statement",
            {"text": "sensitive synthetic sentinel"},
            RuntimeError("synthetic failure"),
        )

    monkeypatch.setattr(h["app"].state.work, "write", broken)
    result = h["client"].post(f"/v1/scopes/{scope}/work/{uuid4()}", headers=h["a"], json=body())
    assert result.status_code == 503 and result.json() == {"detail": "work_storage_unavailable"}
    assert "sentinel" not in result.text


def test_privacy_epoch_invalidates_work_rows_before_list_or_mutation(harness):
    from ada.models import User

    h = harness
    _, scope = setup(h)
    key = str(uuid4())
    value = body()
    assert save(h, scope, key, value).status_code == 200
    with h["sessions"].begin() as db:
        db.get(User, h["a_id"]).data_epoch += 1
    assert h["client"].get(f"/v1/scopes/{scope}/work", headers=h["a"]).json() == []
    assert h["client"].get(f"/v1/work/{key}", headers=h["a"]).status_code == 410
    assert (
        h["client"]
        .post(
            f"/v1/scopes/{scope}/work/{key}/preview",
            headers=h["a"],
            json=body(expected_revision=1, fields=value["fields"]),
        )
        .status_code
        == 410
    )


def test_revoked_token_cannot_submit_reserved_work(harness):
    from ada.auth import rotate_token

    h = harness
    _, scope = setup(h)
    key = str(uuid4())
    value = body()
    preview = h["client"].post(f"/v1/scopes/{scope}/work/{key}/preview", headers=h["a"], json=value)
    assert preview.status_code == 200
    value["preview_hash"] = preview.json()["preview_hash"]
    rotate_token(h["sessions"], "Alice")
    assert (
        h["client"].post(f"/v1/scopes/{scope}/work/{key}", headers=h["a"], json=value).status_code
        == 401
    )


def test_unrepresentable_calendar_projection_returns_validation_not_partial_brief(harness):
    h = harness
    _, scope = setup(h)
    key = str(uuid4())
    value = body(fields=body()["fields"] | {"due_local": "0001-01-01T00:00", "timezone": "UTC"})
    assert save(h, scope, key, value).status_code == 200
    result = h["client"].post(
        "/v1/work/briefs",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "scope_ids": [scope],
            "item_ids": [key],
            "day": "2026-10-22",
            "timezone": "America/Phoenix",
        },
    )
    assert result.status_code == 422
