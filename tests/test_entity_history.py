from unittest.mock import patch
from uuid import uuid4

from conftest import send
from test_entities import alias, entity
from test_entity_storage import instant, owned_scope
from test_memory import add, correct, note

from ada.entity_models import Entity, EntityAlias
from ada.models import now_ms
from ada.providers import Completion, ProviderError


def post(h, path, body):
    return h["client"].post(path, headers=h["a"], json=body)


def test_explicit_self_scope_and_foreign_selection_never_grant_authority(harness):
    h = harness
    _, scope = owned_scope(h)
    eid = entity(h, scope, "User").json()["entity"]["id"]
    path = f"/v1/scopes/{scope}/entities/resolve"
    assert post(h, path, {"self_reference": True}).json()["state"] == "absent"
    assert post(h, path, {"name": "missing", "selected_id": eid}).status_code == 422
    other = h["client"].post("/v1/scopes", headers=h["a"], json={"name": "Other"}).json()["id"]
    foreign = entity(h, other, "User").json()["entity"]["id"]
    assert (
        post(
            h,
            f"/v1/scopes/{scope}/entities/self",
            {"operation_id": str(uuid4()), "entity_id": foreign},
        ).status_code
        == 404
    )
    bound = post(
        h, f"/v1/scopes/{scope}/entities/self", {"operation_id": str(uuid4()), "entity_id": eid}
    )
    assert bound.status_code == 201 and bound.json()["entity"]["is_self"]
    assert post(h, path, {"self_reference": True}).json()["entity_id"] == eid
    assert (
        post(h, f"/v1/scopes/{other}/entities/resolve", {"self_reference": True}).json()["state"]
        == "absent"
    )
    assert h["client"].get("/v1/admin/overview", headers=h["a"]).status_code == 403
    for private_path in (
        f"/v1/entities/{eid}",
        f"/v1/entities/{eid}/aliases",
        f"/v1/scopes/{scope}/entity-audit",
        f"/v1/entity-operations/{bound.json()['id']}",
    ):
        assert h["client"].get(private_path).status_code == 401
        assert h["client"].get(private_path, headers=h["b"]).status_code == 404


def test_stale_preview_changed_links_and_cross_scope_merge_are_atomic(harness):
    h = harness
    _, scope = owned_scope(h)
    a = entity(h, scope, "One").json()["entity"]["id"]
    b = entity(h, scope, "Two").json()["entity"]["id"]
    preview = (
        h["client"]
        .get(f"/v1/entities/{a}/merge-preview", headers=h["a"], params={"target_id": b})
        .json()
    )
    alias(h, b, "New explicit alias")
    operation = str(uuid4())
    body = {"operation_id": operation, "target_id": b, "preview_token": preview["preview_token"]}
    assert post(h, f"/v1/entities/{a}/merge", body).status_code == 409
    assert h["client"].get(f"/v1/entity-operations/{operation}", headers=h["a"]).status_code == 404
    assert h["client"].get(f"/v1/entities/{a}", headers=h["a"]).json()["redirect_id"] is None
    other = h["client"].post("/v1/scopes", headers=h["a"], json={"name": "Other"}).json()["id"]
    foreign = entity(h, other).json()["entity"]["id"]
    assert (
        h["client"]
        .get(f"/v1/entities/{a}/merge-preview", headers=h["a"], params={"target_id": foreign})
        .status_code
        == 404
    )
    claim = add(h, scope, note(h, scope), subject="Original raw").json()
    link = {"operation_id": str(uuid4()), "entity_id": a, "expected_entity_id": None}
    assert post(h, f"/v1/claims/{claim['id']}/entity", link).status_code == 201
    assert (
        post(
            h,
            f"/v1/claims/{claim['id']}/entity",
            link | {"operation_id": str(uuid4()), "entity_id": b},
        ).status_code
        == 409
    )
    assert post(h, f"/v1/claims/{claim['id']}/entity", link).status_code == 200


def test_historical_merge_undo_correction_and_original_replay(harness):
    h = harness
    conv, scope = owned_scope(h)
    a = entity(h, scope, "Atlas", "project").json()["entity"]["id"]
    b = entity(h, scope, "Research", "project").json()["entity"]["id"]
    alias(h, a, "ＡＤＡ")
    claim = add(
        h,
        scope,
        note(h, scope, "Synthetic original uses cobalt. 😀"),
        subject="Raw Atlas",
        subject_entity_id=a,
    ).json()
    h["provider"].complete = lambda messages: Completion("Synthetic answer [M1].", "test")
    old = send(h, conv, "ADA").json()
    assert old["citations"][0]["entity"]["id"] == a
    at = now_ms() + 1000
    with patch("ada.entities.now_ms", return_value=at):
        preview = (
            h["client"]
            .get(f"/v1/entities/{a}/merge-preview", headers=h["a"], params={"target_id": b})
            .json()
        )
        assert (
            post(
                h,
                f"/v1/entities/{a}/merge",
                {
                    "operation_id": str(uuid4()),
                    "target_id": b,
                    "preview_token": preview["preview_token"],
                },
            ).status_code
            == 201
        )
    path = f"/v1/scopes/{scope}/retrieve"
    before = post(h, path, {"query": "ADA", "as_of": instant(at - 1)}).json()["selected"][0]
    after = post(h, path, {"query": "ADA", "as_of": instant(at)}).json()["selected"][0]
    assert before["entity"]["id"] == a and after["entity"]["id"] == b
    assert before["evidence"] == after["evidence"] == claim["evidence"]
    with patch("ada.entities.now_ms", return_value=at + 1000):
        assert (
            post(h, f"/v1/entities/{a}/undo-merge", {"operation_id": str(uuid4())}).status_code
            == 201
        )
    assert (
        post(h, path, {"query": "ADA", "as_of": instant(at + 1000)}).json()["selected"][0][
            "entity"
        ]["id"]
        == a
    )
    evidence = note(h, scope, "Synthetic replacement prefers copper.")
    replacement = correct(h, claim, evidence, subject_entity_id=b)
    assert replacement.status_code == 201 and replacement.json()["subject_entity_id"] == b
    assert send(h, conv, "ADA", old["request_id"]).json() | {"replayed": False} == old | {
        "replayed": False
    }
    no_mapping = correct(
        h, replacement.json(), evidence, value="Other", effective_at="2030-01-01T00:00:00Z"
    )
    assert no_mapping.status_code == 201 and no_mapping.json()["subject_entity_id"] is None


def test_long_query_contract_and_ambiguity_budget_remain_bounded(harness):
    h = harness
    _, scope = owned_scope(h)
    for name in ("One", "Two"):
        eid = entity(h, scope, name).json()["entity"]["id"]
        alias(h, eid, "shared")
        add(h, scope, note(h, scope), subject_entity_id=eid)
    path = f"/v1/scopes/{scope}/retrieve"
    result = post(h, path, {"query": "shared", "budget_bytes": 600}).json()
    assert result["selected"] == [] and result["budget"]["memory_used_bytes"] <= 600
    assert result["plan"]["entity_resolution"][0]["state"] == "ambiguous"
    assert post(h, path, {"query": "x" * 4000}).status_code == 200


def test_truncated_alias_choices_withhold_unlisted_linked_identity(harness):
    h = harness
    _, scope = owned_scope(h)
    ids = [str(uuid4()) for _ in range(65)]
    at = now_ms()
    with h["sessions"].begin() as db:
        db.add_all(
            [
                Entity(
                    id=eid,
                    owner_id=h["a_id"],
                    scope_id=scope,
                    label="Shared",
                    normalized_key="shared",
                    kind="person",
                    revision=0,
                    created_at=at,
                )
                for eid in ids
            ]
        )
        db.flush()
        db.add_all(
            [
                EntityAlias(
                    id=f"00000000-0000-0000-0000-{i:012d}",
                    owner_id=h["a_id"],
                    scope_id=scope,
                    entity_id=eid,
                    label="Shared",
                    normalized_key="shared",
                    canonical=True,
                    created_at=at,
                )
                for i, eid in enumerate(ids)
            ]
        )
    claim = add(
        h,
        scope,
        note(h, scope, "Shared synthetic evidence."),
        subject="Shared",
        subject_entity_id=ids[-1],
    )
    assert claim.status_code == 201
    result = post(h, f"/v1/scopes/{scope}/retrieve", {"query": "Shared"}).json()
    resolution = result["plan"]["entity_resolution"][0]
    assert resolution["state"] == "ambiguous" and resolution["truncated"]
    assert ids[-1] not in {r["id"] for r in resolution["candidates"]}
    assert result["selected"] == [] and result["candidates"] == []


def test_failed_chat_keeps_original_entity_resolution_after_rename(harness):
    h = harness
    conv, scope = owned_scope(h)
    eid = entity(h, scope, "Research", "project").json()["entity"]["id"]
    alias(h, eid, "ADA")
    add(h, scope, note(h, scope), subject_entity_id=eid)
    rid = str(uuid4())
    h["provider"].error = ProviderError("ollama_timeout")
    assert send(h, conv, "ADA", rid).status_code == 502
    original = h["provider"].calls[-1]
    current = h["client"].get(f"/v1/entities/{eid}", headers=h["a"]).json()
    assert (
        post(
            h,
            f"/v1/entities/{eid}/rename",
            {
                "operation_id": str(uuid4()),
                "label": "New explicit name",
                "expected_revision": current["revision"],
            },
        ).status_code
        == 201
    )
    h["provider"].error = None
    h["provider"].complete = lambda messages: (
        h["provider"].calls.append(messages) or Completion("Synthetic [M1].", "test")
    )
    retried = send(h, conv, "ADA", rid)
    assert retried.status_code == 200
    assert h["provider"].calls[-1] == original
    assert retried.json()["citations"][0]["entity"]["label"] == "Research"
