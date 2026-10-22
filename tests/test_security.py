"""Owner/credential/deletion boundaries through actual HTTP on migrated databases."""

import importlib
from uuid import uuid4

import pytest
from sqlalchemy import select, text

from ada.models import Request, User
from ada.schema import SCHEMA_HEAD


def enroll(h, headers=None, **extra):
    h["settings"].device_enrollment_enabled = True
    return h["client"].post(
        "/v1/security/credentials",
        headers=headers or h["a"],
        json={"operation_id": str(uuid4()), "label": "Synthetic phone", **extra},
    )


def device_header(result):
    return {"Authorization": "Bearer " + result.json()["token"]}


def conversation(h, headers=None):
    headers = headers or h["a"]
    profile = h["client"].post("/v1/personalities", headers=headers, json={}).json()
    return (
        h["client"]
        .post("/v1/conversations", headers=headers, json={"personality_id": profile["id"]})
        .json()
    )


def test_legacy_tokens_remain_compatible_and_enrollment_is_configured(harness):
    h = harness
    assert h["client"].get("/v1/me", headers=h["a"]).json()["id"] == h["a_id"]
    body = {"operation_id": str(uuid4()), "label": "Synthetic phone"}
    assert h["client"].post("/v1/security/credentials", json=body).status_code == 401
    denied = h["client"].post("/v1/security/credentials", headers=h["a"], json=body)
    assert denied.status_code == 503
    assert denied.json()["detail"] == "device_enrollment_disabled"


def test_device_digest_only_owner_binding_and_no_role_claim(harness):
    h = harness
    issued = enroll(h)
    assert issued.status_code == 201
    credential = issued.json()["credential"]
    key = credential["id"]
    token = issued.json()["token"]
    assert token and "token_hash" not in credential
    assert h["client"].get("/v1/me", headers=device_header(issued)).json()["id"] == h["a_id"]
    listed = h["client"].get("/v1/security/credentials", headers=h["a"])
    assert listed.status_code == 200
    if token in listed.text:
        raise AssertionError("Credential secret appeared in metadata")
    assert "token_hash" not in listed.text
    assert h["client"].get("/v1/security/credentials", headers=h["b"]).json() == []
    assert (
        h["client"].post(f"/v1/security/credentials/{key}/revoke", headers=h["b"]).status_code
        == 404
    )
    assert h["client"].get("/v1/admin/me", headers=device_header(issued)).status_code == 403
    assert enroll(h, owner_id=h["b_id"], role="admin").status_code == 422
    with h["sessions"]() as db:
        digest = db.scalar(
            text("SELECT token_hash FROM device_credentials WHERE id=:key"), {"key": key}
        )
        if digest == token:
            raise AssertionError("Credential was stored without hashing")
        assert len(digest) == 64


def test_enrollment_replay_never_stores_or_reissues_plaintext_secret(harness):
    h = harness
    h["settings"].device_enrollment_enabled = True
    body = {"operation_id": str(uuid4()), "label": "Synthetic tablet"}
    issued = h["client"].post("/v1/security/credentials", headers=h["a"], json=body)
    assert issued.status_code == 201
    replay = h["client"].post("/v1/security/credentials", headers=h["a"], json=body)
    assert replay.status_code == 200
    assert replay.json()["credential"] == issued.json()["credential"]
    assert replay.json()["token"] is None
    changed = h["client"].post(
        "/v1/security/credentials", headers=h["a"], json={**body, "label": "Changed"}
    )
    assert changed.status_code == 409


def test_rotate_and_revoke_cannot_resume_private_operations(harness):
    h = harness
    issued = enroll(h)
    assert issued.status_code == 201
    key = issued.json()["credential"]["id"]
    old = device_header(issued)
    rotated = h["client"].post(
        f"/v1/security/credentials/{key}/rotate",
        headers=h["a"],
        json={"operation_id": str(uuid4()), "label": "Synthetic replacement"},
    )
    assert rotated.status_code == 201
    assert h["client"].get("/v1/me", headers=old).status_code == 401
    assert h["client"].post("/v1/scopes", headers=old, json={"name": "No write"}).status_code == 401
    new = device_header(rotated)
    assert h["client"].get("/v1/me", headers=new).json()["id"] == h["a_id"]
    new_key = rotated.json()["credential"]["id"]
    first = h["client"].post(f"/v1/security/credentials/{new_key}/revoke", headers=h["a"])
    assert first.status_code == 200
    assert (
        h["client"].post(f"/v1/security/credentials/{new_key}/revoke", headers=h["a"]).json()
        == first.json()
    )
    assert h["client"].get("/v1/me", headers=new).status_code == 401
    assert h["client"].get("/v1/me", headers=h["a"]).status_code == 200


def test_expired_device_token_is_not_a_principal(harness):
    h = harness
    issued = enroll(h)
    assert issued.status_code == 201
    with h["sessions"].begin() as db:
        db.execute(
            text("UPDATE device_credentials SET expires_at=created_at+1 WHERE id=:key"),
            {"key": issued.json()["credential"]["id"]},
        )
    assert h["client"].get("/v1/me", headers=device_header(issued)).status_code == 401


def test_private_body_and_rate_limits_have_sanitized_errors(harness):
    h = harness
    response = h["client"].post("/v1/scopes", headers=h["a"], content=b"x" * (512 * 1024 + 1))
    assert response.status_code == 413 and response.json()["detail"] == "request_too_large"
    h["settings"].private_read_limit_per_minute = 2
    h["app"].state.security_gate.reset_rates()
    assert h["client"].get("/v1/me", headers=h["a"]).status_code == 200
    assert h["client"].get("/v1/me", headers=h["a"]).status_code == 200
    blocked = h["client"].get("/v1/me", headers=h["a"])
    assert blocked.status_code == 429 and blocked.headers["Retry-After"]
    assert h["client"].get("/v1/me", headers=h["b"]).status_code == 200
    assert h["client"].get("/health/live").status_code == 200


def test_deletion_requires_fresh_preview_explicit_confirmation_and_owner(harness):
    h = harness
    h["settings"].deletion_worker_enabled = True
    conversation(h)
    preview = h["client"].post("/v1/security/deletion-previews", headers=h["a"])
    assert preview.status_code == 201
    body = {
        "job_id": str(uuid4()),
        "preview_id": preview.json()["id"],
        "confirmation": "erase_saved_content",
    }
    assert h["client"].post("/v1/security/deletions", headers=h["b"], json=body).status_code == 404
    assert (
        h["client"]
        .post("/v1/security/deletions", headers=h["a"], json={**body, "confirmation": "yes"})
        .status_code
        == 422
    )
    h["client"].post("/v1/scopes", headers=h["a"], json={"name": "After preview"})
    stale = h["client"].post("/v1/security/deletions", headers=h["a"], json=body)
    assert stale.status_code == 409


def test_deletion_erases_private_copies_and_tombstones_replay_not_other_owner(harness):
    h = harness
    h["settings"].deletion_worker_enabled = True
    a = conversation(h)
    b = conversation(h, h["b"])
    request_id = str(uuid4())
    h["client"].post(
        f"/v1/conversations/{a['id']}/messages",
        headers=h["a"],
        json={"request_id": request_id, "content": "Synthetic deletion fixture"},
    )
    before_peer = h["client"].get(f"/v1/conversations/{b['id']}", headers=h["b"]).json()
    preview = h["client"].post("/v1/security/deletion-previews", headers=h["a"])
    assert preview.status_code == 201
    body = {
        "job_id": str(uuid4()),
        "preview_id": preview.json()["id"],
        "confirmation": "erase_saved_content",
    }
    queued = h["client"].post("/v1/security/deletions", headers=h["a"], json=body)
    assert queued.status_code == 202
    assert (
        h["client"]
        .post("/v1/scopes", headers=h["a"], json={"name": "Blocked while pending"})
        .status_code
        == 409
    )
    h["app"].state.deletion.process_one()
    result = h["client"].get(f"/v1/security/deletions/{body['job_id']}", headers=h["a"])
    assert result.status_code == 200 and result.json()["status"] == "completed"
    assert result.json()["backups_may_retain_content"] is True
    assert (
        h["client"].get(f"/v1/security/deletions/{body['job_id']}", headers=h["b"]).status_code
        == 404
    )
    assert h["client"].get(f"/v1/requests/{request_id}", headers=h["a"]).status_code == 410
    replay = h["client"].post(
        f"/v1/conversations/{a['id']}/messages",
        headers=h["a"],
        json={"request_id": request_id, "content": "Synthetic deletion fixture"},
    )
    assert replay.status_code == 410
    assert h["client"].get(f"/v1/conversations/{b['id']}", headers=h["b"]).json() == before_peer
    assert (
        h["client"].post("/v1/security/deletions", headers=h["a"], json=body).json()
        == result.json()
    )
    with h["sessions"]() as db:
        assert db.scalar(select(User.id).where(User.id == h["a_id"])) == h["a_id"]
        assert db.scalar(select(Request.id).where(Request.owner_id == h["a_id"])) is None


def test_deletion_does_not_race_admitted_generation(harness):
    h = harness
    row = conversation(h)
    # Persisted active work is sufficient to block confirmation, even without a live observer.
    with h["sessions"].begin() as db:
        from ada.models import Request

        db.add(
            Request(
                owner_id=h["a_id"],
                id=str(uuid4()),
                conversation_id=row["id"],
                content_hash="0" * 64,
                status="running",
                attempt=1,
                provider="recording",
                model="test-v1",
                messages=[],
                base_revision=0,
            )
        )
    response = h["client"].post("/v1/security/deletion-previews", headers=h["a"])
    assert response.status_code == 409


def test_self_rotation_and_self_revocation_acknowledgements(harness):
    h = harness
    issued = enroll(h)
    old = device_header(issued)
    key = issued.json()["credential"]["id"]
    replacement = h["client"].post(
        f"/v1/security/credentials/{key}/rotate",
        headers=old,
        json={"operation_id": str(uuid4()), "label": "Replacement"},
    )
    assert replacement.status_code == 201
    assert h["client"].get("/v1/me", headers=old).status_code == 401
    new = device_header(replacement)
    key = replacement.json()["credential"]["id"]
    assert (
        h["client"].post(f"/v1/security/credentials/{key}/revoke", headers=new).status_code == 200
    )
    assert h["client"].get("/v1/me", headers=new).status_code == 401


def test_late_revocation_suppresses_admitted_private_response(harness):
    h = harness
    issued = enroll(h)
    key = issued.json()["credential"]["id"]

    @h["app"].get("/v1/security/test-late-read")
    def late_read():
        h["app"].state.security.revoke(h["a_id"], key)
        return {"content": "Synthetic private response"}

    result = h["client"].get("/v1/security/test-late-read", headers=device_header(issued))
    assert result.status_code == 401
    assert result.json() == {"detail": "invalid_token"}


def test_hostile_json_and_malformed_request_id_are_bounded(harness):
    h = harness
    result = h["client"].post(
        "/v1/scopes",
        headers={**h["a"], "Content-Type": "application/json"},
        content="[" * 100 + "0" + "]" * 100,
    )
    assert result.status_code == 400
    assert h["client"].get("/v1/requests/" + "-" * 36, headers=h["a"]).status_code == 422


def test_deletion_crash_lease_recovery_and_epoch(harness):
    from ada.inventory import content_tables
    from ada.models import now_ms
    from ada.security_models import DeletionJob

    h = harness
    h["settings"].deletion_worker_enabled = True
    conversation(h)
    preview = h["client"].post("/v1/security/deletion-previews", headers=h["a"]).json()
    body = {
        "job_id": str(uuid4()),
        "preview_id": preview["id"],
        "confirmation": "erase_saved_content",
    }
    assert h["client"].post("/v1/security/deletions", headers=h["a"], json=body).status_code == 202
    with h["sessions"].begin() as db:
        row = db.get(DeletionJob, (h["a_id"], body["job_id"]))
        row.status = "running"
        row.attempt = 1
        row.lease_until = now_ms() - 1
    assert h["app"].state.deletion.process_one()
    assert (
        h["client"]
        .get("/v1/security/deletions/" + body["job_id"], headers=h["a"])
        .json()["attempt"]
        == 2
    )
    assert h["client"].get("/v1/security/status", headers=h["a"]).json()["data_epoch"] == 1
    with h["sessions"]() as db:
        from sqlalchemy import func

        assert all(
            db.scalar(select(func.count()).select_from(t).where(t.c.owner_id == h["a_id"])) == 0
            for t in content_tables()
        )


# Each case populates real installed feature graphs before exercising the shared erasure path.
FEATURE_SEEDS = [
    ("test_semantic_retrieval", "test_exact_semantic_index_reuse_paraphrase_and_stale_hash"),
    ("test_memory", "test_temporal_correction_is_atomic_and_half_open"),
    ("test_document_api", "test_owned_raw_upload_exact_reads_replay_and_legacy_isolation"),
    ("test_entities", "test_merge_preview_replay_undo_and_original_request_snapshot"),
    (
        "test_proposals",
        "test_unreviewed_proposal_is_not_memory_and_approval_is_atomic_exact_replay",
    ),
    ("test_agents", "test_tool_is_only_executed_after_exact_owned_approval_and_receipt_replays"),
    ("test_consolidation", "test_generated_episode_exact_mapping_no_claims_and_frozen_context"),
    ("test_expression", "test_preference_precedence_frozen_profiles_and_explicit_future_update"),
    ("test_learning", "test_three_independent_interactions_review_override_pause_reset_replay"),
    ("test_voice", "test_explicit_review_creates_separate_generated_and_endorsed_lineage"),
]


@pytest.mark.parametrize("module,function", FEATURE_SEEDS)
def test_deletion_propagates_installed_feature_graph(harness, module, function):
    from sqlalchemy import func

    from ada.inventory import content_tables

    h = harness
    getattr(importlib.import_module(module), function)(h)
    h["settings"].deletion_worker_enabled = True
    with h["sessions"]() as db:
        peer = {
            t.name: db.scalar(select(func.count()).select_from(t).where(t.c.owner_id == h["b_id"]))
            for t in content_tables()
        }
    preview = h["client"].post("/v1/security/deletion-previews", headers=h["a"])
    assert preview.status_code == 201
    body = {
        "job_id": str(uuid4()),
        "preview_id": preview.json()["id"],
        "confirmation": "erase_saved_content",
    }
    assert h["client"].post("/v1/security/deletions", headers=h["a"], json=body).status_code == 202
    h["app"].state.deletion.process_one()
    assert (
        h["client"].get("/v1/security/deletions/" + body["job_id"], headers=h["a"]).json()["status"]
        == "completed"
    )
    with h["sessions"]() as db:
        assert all(
            db.scalar(select(func.count()).select_from(t).where(t.c.owner_id == h["a_id"])) == 0
            for t in content_tables()
        )
        assert peer == {
            t.name: db.scalar(select(func.count()).select_from(t).where(t.c.owner_id == h["b_id"]))
            for t in content_tables()
        }
        if h["backend"] == "sqlite":
            assert db.scalar(text("SELECT COUNT(*) FROM claim_fts")) == db.scalar(
                text("SELECT COUNT(*) FROM claim_search")
            )
            assert db.scalar(text("SELECT COUNT(*) FROM document_fts")) == db.scalar(
                text("SELECT COUNT(*) FROM document_search")
            )


def test_revoked_device_cannot_receive_next_sse_batch(harness):
    from starlette.responses import StreamingResponse

    h = harness
    issued = enroll(h)
    key = issued.json()["credential"]["id"]

    @h["app"].get("/v1/security/test-stream")
    def stream():
        def batches():
            yield "event: ready\ndata: {}\n\n"
            h["app"].state.security.revoke(h["a_id"], key)
            yield 'event: private\ndata: {"content":"Synthetic stale output"}\n\n'

        return StreamingResponse(batches(), media_type="text/event-stream")

    result = h["client"].get("/v1/security/test-stream", headers=device_header(issued))
    assert "event: access_lost" in result.text
    assert "Synthetic stale output" not in result.text


def test_populated_0014_upgrade_and_downgrade_guard(harness):
    from alembic import command

    h = harness
    row = conversation(h)
    rid = str(uuid4())
    body = {"request_id": rid, "content": "Synthetic archived snapshot"}
    original = (
        h["client"]
        .post(f"/v1/conversations/{row['id']}/messages", headers=h["a"], json=body)
        .json()
    )
    command.downgrade(h["config"], "0014")
    command.upgrade(h["config"], "head")
    assert (
        h["client"]
        .post(f"/v1/conversations/{row['id']}/messages", headers=h["a"], json=body)
        .json()
        == original
    )
    assert enroll(h).status_code == 201
    with pytest.raises(RuntimeError):
        command.downgrade(h["config"], "0014")
    with h["sessions"]() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_HEAD


def test_ambiguous_authorization_cannot_mix_principals(harness):
    h = harness
    response = h["client"].get(
        "/v1/me",
        headers=[
            ("Authorization", h["a"]["Authorization"]),
            ("Authorization", h["b"]["Authorization"]),
        ],
    )
    assert response.status_code == 401


def test_native_concurrent_enrollment_has_one_secret_and_exact_metadata(harness):
    from concurrent.futures import ThreadPoolExecutor

    if harness["backend"] != "postgres":
        pytest.skip("Native owner row locking requires PostgreSQL")
    h = harness
    h["settings"].device_enrollment_enabled = True
    operation = str(uuid4())

    def submit():
        return h["client"].post(
            "/v1/security/credentials",
            headers=h["a"],
            json={"operation_id": operation, "label": "Concurrent synthetic device"},
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: submit(), range(2)))
    assert sorted(r.status_code for r in results) == [200, 201]
    assert sum(r.json()["token"] is not None for r in results) == 1
    assert results[0].json()["credential"] == results[1].json()["credential"]


def test_deletion_failure_rolls_back_all_private_rows_and_publishes_fixed_receipt(
    harness, monkeypatch
):
    from sqlalchemy.exc import OperationalError

    from ada.inventory import content_tables

    h = harness
    h["settings"].deletion_worker_enabled = True
    conversation(h)
    preview = h["client"].post("/v1/security/deletion-previews", headers=h["a"]).json()
    body = {
        "job_id": str(uuid4()),
        "preview_id": preview["id"],
        "confirmation": "erase_saved_content",
    }
    assert h["client"].post("/v1/security/deletions", headers=h["a"], json=body).status_code == 202
    original = content_tables()

    def broken_inventory():
        for table in original:
            yield table
            raise OperationalError("Synthetic erasure failure", {}, None)

    with monkeypatch.context() as patch:
        patch.setattr("ada.deletion.content_tables", broken_inventory)
        h["app"].state.deletion.process_one()
    result = h["client"].get("/v1/security/deletions/" + body["job_id"], headers=h["a"]).json()
    assert result["status"] == "failed" and result["error_code"] == "deletion_storage_failed"
    service = h["app"].state.deletion
    with h["sessions"]() as db:
        assert service._counts(db, h["a_id"]) == preview["counts"]
        assert db.get(User, h["a_id"]).data_epoch == 0
    assert h["client"].post("/v1/security/deletions", headers=h["a"], json=body).json() == result
