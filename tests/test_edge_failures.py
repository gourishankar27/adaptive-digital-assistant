"""Real signatures, owned evidence, epoch fencing and native sequence races."""

import base64
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import func, select
from test_memory import note
from test_proposals import pin
from test_work import setup

from ada.edge import MODEL_DIGEST, MODEL_ID, RUNTIME, signing_message
from ada.edge_models import EdgeDevice, EdgeProposal
from ada.evidence import content_hash
from ada.models import Claim, SourceVersion, User


def enrolled(h):
    h["settings"].edge_draft_sync_enabled = True
    _, scope = setup(h)
    key = ec.generate_private_key(ec.SECP256R1())
    device, operation = str(uuid4()), str(uuid4())
    public = base64.b64encode(
        key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    ).decode()
    body = {
        "operation_id": operation,
        "label": "Public device failure study",
        "public_key": public,
        "review": "confirm",
    }
    response = h["client"].post("/v1/edge/devices/" + device, headers=h["a"], json=body)
    assert response.status_code == 200
    return scope, key, device, body


def proposal(scope, key, device, **changes):
    body = {
        "proposal_id": str(uuid4()),
        "device_id": device,
        "device_revision": 1,
        "sequence": 1,
        "task": "offline_reply",
        "model_id": MODEL_ID,
        "model_digest": MODEL_DIGEST,
        "runtime": RUNTIME,
        "prompt": "Public reply request",
        "prompt_hash": content_hash("Public reply request"),
        "output": "Public generated draft.",
        "sources": [],
        "signature": "",
        **changes,
    }
    body["signature"] = base64.b64encode(
        key.sign(signing_message(scope, body), ec.ECDSA(hashes.SHA256()))
    ).decode()
    return body


def sync(h, scope, body, who="a"):
    return h["client"].post(
        f"/v1/scopes/{scope}/edge/proposals/{body['proposal_id']}", headers=h[who], json=body
    )


def test_signature_scope_hash_source_deletion_and_no_model_authority(harness):
    h = harness
    scope, key, device, enrollment = enrolled(h)
    assert (
        h["client"]
        .post("/v1/edge/devices/" + str(uuid4()), headers=h["a"], json=enrollment)
        .status_code
        == 409
    )
    assert (
        h["client"]
        .post(
            "/v1/edge/devices/" + str(uuid4()),
            headers=h["a"],
            json=enrollment | {"operation_id": str(uuid4())},
        )
        .status_code
        == 409
    )
    body = proposal(scope, key, device)
    assert sync(h, scope, body | {"output": "Forged"}).status_code == 422
    assert sync(h, scope, proposal(scope, key, device, prompt_hash="0" * 64)).status_code == 409
    assert sync(h, scope, body, "b").status_code == 404
    source = note(h, scope, "Public original source pin. 😀")
    invalid = proposal(scope, key, device, sources=[pin(source) | {"content_hash": "0" * 64}])
    assert sync(h, scope, invalid).status_code in (409, 422)
    valid = proposal(scope, key, device, sources=[pin(source)])
    assert sync(h, scope, valid).status_code == 200
    assert sync(h, scope, proposal(scope, key, device, sequence=1)).status_code == 409
    with h["sessions"].begin() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0
        db.get(SourceVersion, source["id"]).content = "Changed original source"
    assert h["client"].get(
        "/v1/edge/proposals/" + valid["proposal_id"], headers=h["a"]
    ).status_code in (409, 410, 422)
    with h["sessions"].begin() as db:
        db.get(User, h["a_id"]).data_epoch += 1
    assert sync(h, scope, proposal(scope, key, device, sequence=2)).status_code == 410
    assert (
        h["client"].get("/v1/edge/proposals/" + valid["proposal_id"], headers=h["a"]).status_code
        == 410
    )


def test_native_sequence_race_has_one_receipt_and_erasure_closes_inventory(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Native owner-row sequence serialization")
    scope, key, device, _ = enrolled(h)
    rows = [proposal(scope, key, device), proposal(scope, key, device)]
    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(lambda body: sync(h, scope, body).status_code, rows)) == [200, 409]
    h["settings"].deletion_worker_enabled = True
    deletion = h["app"].state.deletion
    preview = deletion.preview(h["a_id"])
    deletion.confirm(h["a_id"], str(uuid4()), preview["id"])
    assert deletion.process_one()
    with h["sessions"]() as db:
        for model in (EdgeDevice, EdgeProposal):
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.owner_id == h["a_id"])
                )
                == 0
            )
