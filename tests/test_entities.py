from uuid import uuid4

from conftest import make_conversation, send
from test_memory import add, note


def entity(h, scope, label="Alex", kind="person", who="a"):
    return h["client"].post(
        f"/v1/scopes/{scope}/entities",
        headers=h[who],
        json={
            "operation_id": str(uuid4()),
            "entity_id": str(uuid4()),
            "label": label,
            "kind": kind,
        },
    )


def alias(h, eid, label):
    return h["client"].post(
        f"/v1/entities/{eid}/aliases",
        headers=h["a"],
        json={"operation_id": str(uuid4()), "alias_id": str(uuid4()), "label": label},
    )


def test_entities_are_scoped_ambiguous_and_unicode_explicit(harness):
    h = harness
    conv, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]
    first = entity(h, scope, "Alex One")
    assert first.status_code == 201
    eid = first.json()["entity"]["id"]
    other = entity(h, scope, "Alex Two").json()["entity"]["id"]
    assert alias(h, eid, "ＡＬＥＸ").status_code == 201
    assert alias(h, other, "alex").status_code == 201
    resolved = h["client"].post(
        f"/v1/scopes/{scope}/entities/resolve", headers=h["a"], json={"name": "Alex"}
    )
    assert resolved.json()["state"] == "ambiguous"
    assert {r["id"] for r in resolved.json()["candidates"]} == {eid, other}
    chosen = h["client"].post(
        f"/v1/scopes/{scope}/entities/resolve",
        headers=h["a"],
        json={"name": "Alex", "selected_id": eid},
    )
    assert chosen.json()["state"] == "resolved" and chosen.json()["entity_id"] == eid
    assert h["client"].get(f"/v1/entities/{eid}", headers=h["b"]).status_code == 404
    assert entity(h, scope, who="b").status_code == 404
    assert (
        h["client"]
        .post(
            f"/v1/scopes/{scope}/entities/self",
            headers=h["a"],
            json={"operation_id": str(uuid4()), "entity_id": eid, "owner_id": h["b_id"]},
        )
        .status_code
        == 422
    )
    assert (
        h["client"]
        .post(f"/v1/scopes/{scope}/entities/resolve", headers=h["a"], json={"self_reference": True})
        .json()["state"]
        == "absent"
    )


def test_merge_preview_replay_undo_and_original_request_snapshot(harness):
    h = harness
    conv, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]
    a = entity(h, scope, "Ada Project", "project").json()["entity"]["id"]
    b = entity(h, scope, "Assistant Project", "project").json()["entity"]["id"]
    evidence = note(h, scope, "Ada Project uses cobalt.")
    claim = add(
        h, scope, evidence, subject="Ada Project", predicate="material", value="cobalt"
    ).json()
    body = {"operation_id": str(uuid4()), "entity_id": a, "expected_entity_id": None}
    link = h["client"].post(f"/v1/claims/{claim['id']}/entity", headers=h["a"], json=body)
    assert link.status_code == 201
    saved = send(h, conv, "Ada Project material cobalt").json()
    preview = (
        h["client"]
        .get(f"/v1/entities/{a}/merge-preview", headers=h["a"], params={"target_id": b})
        .json()
    )
    merged = {
        "operation_id": str(uuid4()),
        "target_id": b,
        "preview_token": preview["preview_token"],
    }
    assert (
        h["client"].post(f"/v1/entities/{a}/merge", headers=h["a"], json=merged).status_code == 201
    )
    assert (
        h["client"].post(f"/v1/entities/{a}/merge", headers=h["a"], json=merged).status_code == 200
    )
    assert h["client"].get(f"/v1/entities/{a}", headers=h["a"]).json()["redirect_id"] == b
    assert (
        h["client"]
        .get(f"/v1/entities/{b}/merge-preview", headers=h["a"], params={"target_id": a})
        .status_code
        == 409
    )
    replay = send(h, conv, "Ada Project material cobalt", saved["request_id"]).json()
    assert replay | {"replayed": False} == saved | {"replayed": False}
    old = h["client"].get(f"/v1/claims/{claim['id']}", headers=h["a"]).json()
    assert old["subject"] == claim["subject"] and old["evidence"] == claim["evidence"]
    undo = h["client"].post(
        f"/v1/entities/{a}/undo-merge", headers=h["a"], json={"operation_id": str(uuid4())}
    )
    assert undo.status_code == 201
    assert h["client"].get(f"/v1/entities/{a}", headers=h["a"]).json()["redirect_id"] is None


def test_optional_claim_reference_requires_owned_scope_and_binds_write_hash(harness):
    h = harness
    conv, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]
    eid = entity(h, scope, "Atlas", "project").json()["entity"]["id"]
    evidence = note(h, scope, "Atlas uses cobalt.")
    body = {
        "claim_id": str(uuid4()),
        "source_version_id": evidence["id"],
        "span_start": 0,
        "span_end": len(evidence["content"]),
        "subject": "Raw Atlas",
        "predicate": "material",
        "value": "cobalt",
        "subject_entity_id": eid,
    }
    path = f"/v1/scopes/{scope}/claims"
    created = h["client"].post(path, headers=h["a"], json=body)
    assert created.status_code == 201 and created.json()["subject_entity_id"] == eid
    assert h["client"].post(path, headers=h["a"], json=body).status_code == 200
    assert (
        h["client"].post(path, headers=h["a"], json=body | {"subject_entity_id": None}).status_code
        == 409
    )
    other = h["client"].post("/v1/scopes", headers=h["a"], json={"name": "Other"}).json()["id"]
    foreign = entity(h, other, "Atlas", "project").json()["entity"]["id"]
    assert (
        h["client"]
        .post(
            path,
            headers=h["a"],
            json=body | {"claim_id": str(uuid4()), "subject_entity_id": foreign},
        )
        .status_code
        == 404
    )


def test_alias_retrieval_keeps_ambiguity_and_exact_frozen_evidence(harness):
    h = harness
    conv, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{conv}", headers=h["a"]).json()["scope_id"]
    e1 = entity(h, scope, "Research", "project").json()["entity"]["id"]
    evidence = note(h, scope, "The research build uses cobalt. 😀")
    claim = add(h, scope, evidence, subject="Research", predicate="material", value="cobalt").json()
    h["client"].post(
        f"/v1/claims/{claim['id']}/entity",
        headers=h["a"],
        json={"operation_id": str(uuid4()), "entity_id": e1, "expected_entity_id": None},
    )
    alias(h, e1, "ＡＤＡ")
    path = f"/v1/scopes/{scope}/retrieve"
    found = h["client"].post(path, headers=h["a"], json={"query": "ADA"}).json()
    assert [r["claim_id"] for r in found["selected"]] == [claim["id"]]
    assert found["selected"][0]["evidence"] == claim["evidence"]
    assert found["selected"][0]["entity"]["id"] == e1
    assert "entity_alias" in found["candidates"][0]["channels"]
    e2 = entity(h, scope, "Other research", "project").json()["entity"]["id"]
    alias(h, e2, "ada")
    ambiguous = h["client"].post(path, headers=h["a"], json={"query": "ADA"}).json()
    assert ambiguous["selected"] == []
    assert ambiguous["plan"]["entity_resolution"][0]["state"] == "ambiguous"
    assert (
        h["client"]
        .post(path, headers=h["a"], json={"query": "ADA", "budget_bytes": 0})
        .json()["budget"]["memory_used_bytes"]
        == 0
    )
