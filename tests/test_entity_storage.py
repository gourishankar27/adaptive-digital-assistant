from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from test_entities import alias, entity
from test_memory import add, note

from ada.entities import EntityService
from ada.entity_contracts import MergeInput
from ada.entity_models import EntityAlias, EntitySelfLink
from ada.errors import ServiceError
from ada.models import Claim


def instant(ms):
    return datetime.fromtimestamp(ms / 1000, UTC).isoformat(timespec="milliseconds")


def owned_scope(h):
    conv, _ = make_conversation(h)
    return conv, h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]


def test_database_foreign_scope_alias_self_and_claim_references_rejected(harness):
    h = harness
    _, scope = owned_scope(h)
    other = h["client"].post("/v1/scopes", headers=h["a"], json={"name": "Other"}).json()["id"]
    eid = entity(h, other).json()["entity"]["id"]
    for model in (EntityAlias, EntitySelfLink):
        fields = {"id": str(uuid4()), "owner_id": h["a_id"], "scope_id": scope, "entity_id": eid}
        if model == EntityAlias:
            fields.update(label="Forged", normalized_key="forged", canonical=False)
        with pytest.raises(IntegrityError), h["sessions"].begin() as db:
            db.add(model(**fields))
    evidence = note(h, scope, "Synthetic assertion.")
    claim = add(h, scope, evidence).json()
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.get(Claim, claim["id"]).subject_entity_id = eid


def test_populated_0005_upgrade_preserves_string_claim_hash_prompt_and_replay(harness):
    h = harness
    conv, scope = owned_scope(h)
    evidence = note(h, scope, "Synthetic atlas setting is cobalt.")
    claim = add(h, scope, evidence, subject="Atlas", predicate="setting", value="cobalt").json()
    saved = send(h, conv, "Atlas setting").json()
    with h["sessions"]() as db:
        before = db.get(Claim, claim["id"]).write_hash
    command.downgrade(h["config"], "0005")
    with h["sessions"]() as db:
        assert (
            db.execute(
                text("SELECT write_hash FROM claims WHERE id=:id"), {"id": claim["id"]}
            ).scalar_one()
            == before
        )
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    with h["sessions"]() as db:
        row = db.get(Claim, claim["id"])
        assert row.subject_entity_id is None and row.write_hash == before
    assert send(h, conv, "Atlas setting", saved["request_id"]).json() | {
        "replayed": False
    } == saved | {"replayed": False}
    entity(h, scope)
    with pytest.raises(RuntimeError, match="refusing a lossy downgrade"):
        command.downgrade(h["config"], "0005")
    # Newer discardable indexes can already have reversed when the retained
    # identity migration refuses. Restore head without changing identity data.
    command.upgrade(h["config"], "head")
    command.check(h["config"])


def test_rename_resolution_respects_knowledge_time_and_retains_raw_aliases(harness):
    h = harness
    _, scope = owned_scope(h)
    created = entity(h, scope, "Old Name").json()
    eid = created["entity"]["id"]
    before = created["created_at"]
    after = before + 1000
    body = {"operation_id": str(uuid4()), "label": "New Name", "expected_revision": 0}
    with patch("ada.entities.now_ms", return_value=after):
        renamed = h["client"].post(f"/v1/entities/{eid}/rename", headers=h["a"], json=body)
    assert renamed.status_code == 201
    path = f"/v1/scopes/{scope}/entities/resolve"
    old = (
        h["client"]
        .post(path, headers=h["a"], json={"name": "Old Name", "as_of": instant(before)})
        .json()
    )
    assert old["state"] == "resolved" and old["candidates"][0]["label"] == "Old Name"
    assert (
        h["client"]
        .post(path, headers=h["a"], json={"name": "New Name", "as_of": instant(before)})
        .json()["state"]
        == "absent"
    )
    assert (
        h["client"]
        .post(path, headers=h["a"], json={"name": "Old Name", "as_of": instant(after)})
        .json()["state"]
        == "absent"
    )
    history = h["client"].get(f"/v1/entities/{eid}/aliases", headers=h["a"]).json()
    assert {r["label"] for r in history} == {"Old Name", "New Name"}
    assert (
        h["client"].post(f"/v1/entities/{eid}/rename", headers=h["a"], json=body).json()
        == renamed.json()
    )


def test_alias_quota_failure_has_no_audit_or_partial_alias(harness, monkeypatch):
    h = harness
    _, scope = owned_scope(h)
    created = entity(h, scope).json()
    monkeypatch.setattr("ada.entities.MAX_ALIASES", 1)
    rejected = alias(h, created["entity"]["id"], "Extra")
    assert rejected.status_code == 413
    assert (
        len(
            h["client"]
            .get(f"/v1/entities/{created['entity']['id']}/aliases", headers=h["a"])
            .json()
        )
        == 1
    )
    assert len(h["client"].get(f"/v1/scopes/{scope}/entity-audit", headers=h["a"]).json()) == 1


def test_concurrent_opposite_merges_cannot_create_redirect_cycle(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("PostgreSQL scope row locks required")
    _, scope = owned_scope(h)
    a = entity(h, scope, "One").json()["entity"]["id"]
    b = entity(h, scope, "Two").json()["entity"]["id"]
    service = EntityService(h["sessions"])
    ab, ba = service.preview(h["a_id"], a, b), service.preview(h["a_id"], b, a)

    def merge(source, target, preview):
        try:
            service.mutate(
                h["a_id"],
                source,
                "merge",
                MergeInput(
                    operation_id=uuid4(), target_id=target, preview_token=preview["preview_token"]
                ),
            )
            return 201
        except ServiceError as err:
            return err.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [pool.submit(merge, a, b, ab), pool.submit(merge, b, a, ba)]
        assert sorted(r.result(timeout=10) for r in results) == [201, 409]
    rows = service.list(h["a_id"], scope)
    assert sum(r["redirect_id"] is not None for r in rows) == 1
