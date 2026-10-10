"""Bounded real HTTP document flow; all text/accounts below are synthetic."""

import hashlib
import json
from uuid import uuid4

from conftest import make_conversation
from test_client_contract import assert_schema, response_schema


def upload(
    h, scope, raw, *, who="a", upload_id=None, source_id=None, filename="example.md", **params
):
    return h["client"].post(
        f"/v1/scopes/{scope}/documents/uploads/{upload_id or uuid4()}",
        headers=h[who] | {"Content-Type": "text/markdown; charset=utf-8"},
        params={"source_id": source_id or str(uuid4()), "filename": filename, **params},
        content=raw,
    )


def test_owned_raw_upload_exact_reads_replay_and_legacy_isolation(harness):
    h = harness
    cid, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    text = "\ufeff# Synthetic launch\r\nOrbit 🙂 café e\u0301\r\nLiteral <script> data.\r\n"
    raw = text.encode("utf-8")
    uid, sid = str(uuid4()), str(uuid4())
    response = upload(h, scope, raw, upload_id=uid, source_id=sid)
    assert response.status_code == 201, response.text
    receipt = response.json()
    document = h["app"].openapi()
    assert_schema(
        receipt,
        response_schema(
            document, "/v1/scopes/{scope_id}/documents/uploads/{upload_id}", "post", 201
        ),
        document,
    )
    assert receipt["state"] == "ready" and receipt["origin"] == "imported_document"
    assert receipt["trust_class"] == "imported_untrusted"
    assert receipt["raw_hash"] == hashlib.sha256(raw).hexdigest()
    assert receipt["raw_size"] == len(raw)
    replay = upload(h, scope, raw, upload_id=uid, source_id=sid)
    assert replay.status_code == 200 and replay.json() == receipt
    assert upload(h, scope, raw + b"x", upload_id=uid, source_id=sid).status_code == 409
    version_id = receipt["source_version_id"]
    version_path = f"/v1/document-versions/{version_id}"
    version = h["client"].get(version_path, headers=h["a"])
    assert version.status_code == 200 and version.json()["content"] == text
    assert_schema(
        version.json(),
        response_schema(document, "/v1/document-versions/{source_version_id}", "get", 200),
        document,
    )
    assert version.headers["cache-control"] == "no-store"
    chunks = h["client"].get(version_path + "/chunks", headers=h["a"]).json()
    assert_schema(
        chunks,
        response_schema(document, "/v1/document-versions/{source_version_id}/chunks", "get", 200),
        document,
    )
    assert chunks
    assert "".join(c["quote"] for c in chunks) == text
    for chunk in chunks:
        assert text[chunk["span_start"] : chunk["span_end"]] == chunk["quote"]
    download = h["client"].get(version_path + "/raw", headers=h["a"])
    assert download.content == raw and download.headers["x-content-type-options"] == "nosniff"
    assert "attachment" in download.headers["content-disposition"]
    for path in (
        version_path,
        version_path + "/chunks",
        version_path + "/raw",
        f"/v1/document-uploads/{uid}",
        f"/v1/documents/{sid}/versions",
    ):
        assert h["client"].get(path).status_code == 401
        assert h["client"].get(path, headers=h["b"]).status_code == 404
    assert h["client"].get(f"/v1/source-versions/{version_id}", headers=h["a"]).status_code == 404
    legacy_sources = h["client"].get(f"/v1/scopes/{scope}/source-versions", headers=h["a"]).json()
    assert version_id not in {source["id"] for source in legacy_sources}
    claims = h["client"].post(
        f"/v1/scopes/{scope}/claims",
        headers=h["a"],
        json={
            "claim_id": str(uuid4()),
            "source_version_id": version_id,
            "span_start": 0,
            "span_end": len(text),
            "subject": "launch",
            "predicate": "name",
            "value": "Orbit",
        },
    )
    assert claims.status_code == 422 and claims.json()["detail"] == "source_not_user_evidence"
    # Real HTTP opt-in -> reserved context -> typed citation -> original replay.
    rid = str(uuid4())
    body = {"request_id": rid, "content": "Orbit [D1]", "use_documents": True}
    answer = h["client"].post(f"/v1/conversations/{cid}/messages", headers=h["a"], json=body)
    assert answer.status_code == 200, answer.text
    assert answer.json()["citations"] == []
    assert answer.json()["document_citations"][0]["source_version_id"] == version_id
    assert answer.json()["document_citations"][0]["evidence"]["quote"] == text
    assert_schema(
        answer.json(),
        response_schema(document, "/v1/conversations/{conversation_id}/messages", "post", 200),
        document,
    )
    replacement = upload(h, scope, b"Orbit replacement document.\n", source_id=sid)
    assert replacement.status_code == 201 and replacement.json()["version"] == 2
    replay = h["client"].post(f"/v1/conversations/{cid}/messages", headers=h["a"], json=body)
    assert replay.json() == answer.json()
    changed = h["client"].post(
        f"/v1/conversations/{cid}/messages", headers=h["a"], json=body | {"use_documents": False}
    )
    assert changed.status_code == 409


def test_upload_http_bounds_and_safe_failures(harness):
    h = harness
    cid, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    # Actual streamed bytes, not a trusted filename or Content-Length claim.
    too_big = upload(h, scope, b"x" * (256 * 1024 + 1))
    assert too_big.status_code == 413
    assert upload(h, scope, b"safe", filename="../private.md").status_code == 422
    failed = upload(h, scope, b"%PDF-1.7\nmalformed private payload")
    assert failed.status_code in (201, 415, 422)
    assert "malformed private payload" not in failed.text
    if failed.status_code == 201:
        receipt = failed.json()
        assert receipt["state"] == "failed" and receipt["error_code"]
        assert (
            h["client"]
            .get(f"/v1/document-versions/{receipt['source_version_id']}", headers=h["a"])
            .status_code
            == 404
        )
    assert upload(h, scope, b"safe", who="b").status_code == 404


def test_document_capability_and_openapi_keep_existing_claim_contract(harness):
    h = harness
    caps = h["client"].get("/v1/capabilities", headers=h["a"]).json()
    assert caps["document_ingestion"] == "text_markdown_v1"
    assert caps["document_uploads"] and caps["document_retrieval"] and caps["document_citations"]
    assert caps["document_max_bytes"] == 256 * 1024
    schemas = h["app"].openapi()["components"]["schemas"]
    assert schemas["ChatInput"]["properties"]["use_documents"]["default"] is False
    assert schemas["CitationOutput"]["properties"]["origin"]["const"] == "user_asserted"
    assert schemas["SourceVersionOutput"]["properties"]["trust_class"]["enum"] == [
        "user_explicit",
        "model_generated",
    ]
    assert schemas["DocumentUploadOutput"]["properties"]["available_from"]["format"] == "int64"
    assert json.dumps(schemas["DocumentCitationOutput"]).find("claim_id") == -1
