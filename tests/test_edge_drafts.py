"""Device signatures never grant factual, tool or server-response authority."""

import base64
from uuid import uuid4

from conftest import make_conversation
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from ada.edge import signing_message


def test_disabled_local_runtime_and_sync_never_fabricate_a_working_flow(harness):
    h = harness
    assert h["client"].get("/v1/capabilities", headers=h["a"]).json()["edge_inference"] is False
    result = h["client"].post(
        "/v1/edge/devices/" + str(uuid4()),
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "label": "Public test installation",
            "public_key": "invalid",
            "review": "confirm",
        },
    )
    assert result.status_code in (422, 503)


def test_device_owner_signature_sequence_duplicate_and_revocation(harness):
    h = harness
    h["settings"].edge_draft_sync_enabled = True
    cid, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    key = ec.generate_private_key(ec.SECP256R1())
    device = str(uuid4())
    public = base64.b64encode(
        key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    ).decode()
    enrolled = h["client"].post(
        "/v1/edge/devices/" + device,
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "label": "Public test installation",
            "public_key": public,
            "review": "confirm",
        },
    )
    assert enrolled.status_code == 200
    from ada.edge import MODEL_DIGEST, MODEL_ID, RUNTIME
    from ada.evidence import content_hash

    pid = str(uuid4())
    body = {
        "proposal_id": pid,
        "device_id": device,
        "device_revision": 1,
        "sequence": 1,
        "task": "offline_reply",
        "model_id": MODEL_ID,
        "model_digest": MODEL_DIGEST,
        "runtime": RUNTIME,
        "prompt": "Public polite reply request",
        "prompt_hash": content_hash("Public polite reply request"),
        "output": "Public untrusted draft.",
        "sources": [],
        "signature": "",
    }
    body["signature"] = base64.b64encode(
        key.sign(signing_message(scope, body), ec.ECDSA(hashes.SHA256()))
    ).decode()
    path = f"/v1/scopes/{scope}/edge/proposals/{pid}"
    result = h["client"].post(path, headers=h["a"], json=body)
    assert result.status_code == 200 and result.json()["trust_class"] == "model_generated"
    assert h["client"].post(path, headers=h["a"], json=body).json() == result.json()
    assert (
        h["client"].post(path, headers=h["a"], json=body | {"output": "Changed"}).status_code == 409
    )
    assert h["client"].get("/v1/edge/proposals/" + pid, headers=h["b"]).status_code == 404
    revoked = h["client"].post(
        "/v1/edge/devices/" + device + "/revoke",
        headers=h["a"],
        json={"operation_id": str(uuid4()), "expected_revision": 1, "review": "confirm"},
    )
    assert revoked.status_code == 200
    assert h["client"].post(path, headers=h["a"], json=body).status_code == 410
