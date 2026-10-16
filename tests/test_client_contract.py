"""Exercise real HTTP outputs against the checked-in OpenAPI, using synthetic data."""

import hashlib
import json
import os
import re
from pathlib import Path, PureWindowsPath
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete

from ada.models import Conversation, RetrievalTrace
from ada.personality import PROMPT_VERSION
from ada.providers import Completion, ProviderError

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "contracts" / "openapi.json"
FIXTURES = ROOT / "contracts" / "fixtures"


def assert_schema(value, schema, document):
    """Validate the JSON Schema keywords emitted here, independently of DTO models.

    This small test helper is intentionally limited to this exported contract; it
    is not a general JSON Schema implementation or a production validator.
    """
    if "$ref" in schema:
        target = document
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return assert_schema(value, target, document)
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                assert_schema(value, option, document)
            except (AssertionError, ValueError):
                continue
            return
        raise AssertionError(f"No schema alternative matched {type(value).__name__}")
    expected = schema.get("type")
    types = {
        "null": lambda v: v is None,
        "boolean": lambda v: type(v) is bool,
        "integer": lambda v: type(v) is int,
        "number": lambda v: type(v) in (int, float),
        "string": lambda v: isinstance(v, str),
        "array": lambda v: isinstance(v, list),
        "object": lambda v: isinstance(v, dict),
    }
    if expected:
        assert types[expected](value), f"Expected {expected}, got {type(value).__name__}"
    if "enum" in schema:
        assert value in schema["enum"]
    if "const" in schema:
        assert value == schema["const"]
    if expected == "object":
        assert set(schema.get("required", ())) <= value.keys()
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert value.keys() <= properties.keys()
        for key, item in value.items():
            if key in properties:
                assert_schema(item, properties[key], document)
            elif isinstance(schema.get("additionalProperties"), dict):
                assert_schema(item, schema["additionalProperties"], document)
    elif expected == "array":
        for item in value:
            assert_schema(item, schema.get("items", {}), document)
    elif expected == "string":
        if schema.get("format") == "uuid":
            assert str(UUID(value)) == value
        if "pattern" in schema:
            assert re.search(schema["pattern"], value)
        assert len(value) >= schema.get("minLength", 0)
        assert len(value) <= schema.get("maxLength", len(value))
    elif expected in ("number", "integer"):
        assert value >= schema.get("minimum", value)
        assert value <= schema.get("maximum", value)
        if schema.get("format") == "int64":
            assert -(2**63) <= value < 2**63


def response_schema(document, path, method, status):
    return document["paths"][path][method]["responses"][str(status)]["content"]["application/json"][
        "schema"
    ]


def write_synthetic_fixtures(cases):
    """Opt-in regeneration from the HTTP flow below; never capture real accounts."""
    ids = {}

    def sanitize(value, key=""):
        if isinstance(value, dict):
            result = {k: sanitize(v, k) for k, v in value.items()}
            if type(value.get("created_at")) is int and type(value.get("expires_at")) is int:
                result["expires_at"] = (
                    result["created_at"] + value["expires_at"] - value["created_at"]
                )
            return result
        if isinstance(value, list):
            return [sanitize(v, key) for v in value]
        if isinstance(value, str):
            try:
                UUID(value)
            except ValueError:
                return value
            return ids.setdefault(value, str(UUID(int=len(ids) + 1)))
        if (
            key in ("created_at", "as_of", "expires_at", "approved_at")
            and type(value) is int
            and value > 1_760_000_000_000
        ):
            return 1_791_417_600_000
        if key == "retrieval_ms":
            return 0
        return value

    FIXTURES.mkdir(exist_ok=True)
    entries = []
    for name, path, method, response in cases:
        filename = name + ".json"
        (FIXTURES / filename).write_text(
            json.dumps(sanitize(response.json()), indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        entries.append(
            {"file": filename, "path": path, "method": method, "status": response.status_code}
        )
    manifest = {
        "format": "ada-contract-fixtures-v1",
        "provenance": {
            "generator": "tests/test_client_contract.py::test_actual_responses_match_export",
            "environment": "FastAPI TestClient, migrated disposable SQLite, synthetic accounts",
            "provider": "test-only deterministic completion; no network inference",
            "sanitization": "UUIDs replaced consistently; created/current timestamps and elapsed retrieval normalized",
            "legacy": "Synthetic baseline-v2 snapshot and completed request with its trace removed",
            "content": "Invented public examples, never private chats or user source quotes",
        },
        "fixtures": entries,
    }
    (FIXTURES / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def test_actual_responses_match_export(harness):
    h, cases = harness, []
    document = json.loads(OPENAPI.read_text(encoding="utf-8"))
    assert h["app"].openapi() == document, "Regenerate contracts/openapi.json"

    def call(name, path, method="get", *, actual=None, status=200, **kwargs):
        response = getattr(h["client"], method)(actual or path, headers=h["a"], **kwargs)
        assert response.status_code == status, response.text
        assert_schema(response.json(), response_schema(document, path, method, status), document)
        cases.append((name, path, method, response))
        return response.json()

    call("health-live", "/health/live")
    call("health-ready", "/health/ready")
    call("user-current", "/v1/me")
    call("capabilities-current", "/v1/capabilities")
    p = call("personality-current", "/v1/personalities", "post", status=201, json={})
    call("personalities-current", "/v1/personalities")
    s = call("scope-current", "/v1/scopes", "post", status=201, json={"name": "Synthetic project"})
    sid = s["id"]
    call("scopes-current", "/v1/scopes")
    call("scope-detail", "/v1/scopes/{scope_id}", actual=f"/v1/scopes/{sid}")
    c = call(
        "conversation-current",
        "/v1/conversations",
        "post",
        status=201,
        json={"personality_id": p["id"], "scope_id": sid, "title": "Synthetic contract example"},
    )
    cid = c["id"]
    call("conversations-current", "/v1/conversations", params={"limit": 1, "offset": 0})
    call(
        "conversation-detail",
        "/v1/conversations/{conversation_id}",
        actual=f"/v1/conversations/{cid}",
    )
    notes = "/v1/scopes/{scope_id}/notes"
    note_body = {"source_id": str(uuid4()), "content": "\U0001f642 We choose Python."}
    n = call(
        "source-current",
        notes,
        "post",
        actual=f"/v1/scopes/{sid}/notes",
        status=201,
        json=note_body,
    )
    assert (
        call("source-replay", notes, "post", actual=f"/v1/scopes/{sid}/notes", json=note_body) == n
    )
    call(
        "sources-current",
        "/v1/scopes/{scope_id}/source-versions",
        actual=f"/v1/scopes/{sid}/source-versions",
    )
    call(
        "source-detail",
        "/v1/source-versions/{source_version_id}",
        actual=f"/v1/source-versions/{n['id']}",
    )
    claim_body = {
        "claim_id": str(uuid4()),
        "source_version_id": n["id"],
        "subject": "ADA",
        "predicate": "language",
        "value": "Python",
        "kind": "decision",
        "span_start": 2,
        "span_end": len(n["content"]),
        "valid_from": "2025-01-01T00:00:00Z",
    }
    claims = "/v1/scopes/{scope_id}/claims"
    old = call(
        "claim-current",
        claims,
        "post",
        actual=f"/v1/scopes/{sid}/claims",
        status=201,
        json=claim_body,
    )
    assert old["evidence"]["quote"] == "We choose Python."
    assert (
        call("claim-replay", claims, "post", actual=f"/v1/scopes/{sid}/claims", json=claim_body)
        == old
    )
    sibling = call(
        "source-conflict",
        notes,
        "post",
        actual=f"/v1/scopes/{sid}/notes",
        status=201,
        json={"source_id": str(uuid4()), "content": "We choose Rust."},
    )
    call(
        "claim-conflict",
        claims,
        "post",
        actual=f"/v1/scopes/{sid}/claims",
        status=201,
        json=claim_body
        | {
            "claim_id": str(uuid4()),
            "source_version_id": sibling["id"],
            "value": "Rust",
            "span_start": 0,
            "span_end": len(sibling["content"]),
        },
    )
    retrieval = call(
        "retrieval-direct",
        "/v1/scopes/{scope_id}/retrieve",
        "post",
        actual=f"/v1/scopes/{sid}/retrieve",
        json={"query": "Python"},
    )
    assert len(retrieval["selected"]) == 2
    unranked = next(item for item in retrieval["candidates"] if item["channels"] == ["slot_check"])
    assert "score" not in unranked and "term_coverage" not in unranked
    assert "prompt_limit_bytes" not in retrieval["budget"]
    original_complete = h["provider"].complete
    h["provider"].complete = lambda _: Completion(
        "Synthetic answer [M1], unavailable [M99].", "test-v1", 10, 5
    )
    rid = str(uuid4())
    messages = "/v1/conversations/{conversation_id}/messages"
    message_body = {"request_id": rid, "content": "Python"}
    answer = call(
        "request-current",
        messages,
        "post",
        actual=f"/v1/conversations/{cid}/messages",
        json=message_body,
    )
    assert [item["label"] for item in answer["citations"]] == ["M1"]
    assert answer["citation_warnings"] == ["unknown_label:M99"]
    call("request-status", "/v1/requests/{request_id}", actual=f"/v1/requests/{rid}")
    call(
        "retrieval-current",
        "/v1/requests/{request_id}/retrieval",
        actual=f"/v1/requests/{rid}/retrieval",
    )
    events = call(
        "events-current",
        "/v1/conversations/{conversation_id}/events",
        actual=f"/v1/conversations/{cid}/events",
    )
    assert [item["role"] for item in events] == ["user", "assistant"]
    assert [item["trust_class"] for item in events] == ["user_explicit", "model_generated"]
    page = call(
        "events-page",
        "/v1/conversations/{conversation_id}/events",
        actual=f"/v1/conversations/{cid}/events",
        params={"limit": 1, "offset": 1},
    )
    assert page == events[1:]
    replacement = call(
        "source-correction",
        notes,
        "post",
        actual=f"/v1/scopes/{sid}/notes",
        status=201,
        json={"source_id": str(uuid4()), "content": "We choose Java."},
    )
    correction = {
        "claim_id": str(uuid4()),
        "source_version_id": replacement["id"],
        "value": "Java",
        "span_start": 0,
        "span_end": len(replacement["content"]),
        "effective_at": "2025-06-01T00:00:00Z",
    }
    supersede = "/v1/claims/{claim_id}/supersede"
    corrected = call(
        "claim-correction",
        supersede,
        "post",
        actual=f"/v1/claims/{old['id']}/supersede",
        status=201,
        json=correction,
    )
    assert (
        call(
            "correction-replay",
            supersede,
            "post",
            actual=f"/v1/claims/{old['id']}/supersede",
            json=correction,
        )
        == corrected
    )
    prior = call("claim-superseded", "/v1/claims/{claim_id}", actual=f"/v1/claims/{old['id']}")
    assert prior["status"] == "superseded" and prior["superseded_by"] == corrected["id"]
    call("claims-history", claims, actual=f"/v1/scopes/{sid}/claims", params={"history": True})
    assert (
        call(
            "request-replay",
            messages,
            "post",
            actual=f"/v1/conversations/{cid}/messages",
            json=message_body,
        )
        == answer
    )
    with h["sessions"].begin() as db:
        row = db.get(Conversation, cid)
        row.prompt_version, row.system_prompt = "ada-baseline-v2", "Synthetic saved legacy prompt"
        row.personality_snapshot = row.personality_snapshot | {
            "legacy_note": "Synthetic retained snapshot"
        }
    legacy = call(
        "conversation-legacy",
        "/v1/conversations/{conversation_id}",
        actual=f"/v1/conversations/{cid}",
    )
    assert legacy["personality"]["legacy_note"] == "Synthetic retained snapshot"
    legacy_id = str(uuid4())
    call(
        "request-legacy-prompt",
        messages,
        "post",
        actual=f"/v1/conversations/{cid}/messages",
        json={"request_id": legacy_id, "content": "Python"},
    )
    disabled = call(
        "retrieval-legacy-prompt",
        "/v1/requests/{request_id}/retrieval",
        actual=f"/v1/requests/{legacy_id}/retrieval",
    )
    assert disabled["plan"]["reason"] == "prompt_upgrade_required" and disabled["selected"] == []
    with h["sessions"].begin() as db:
        db.execute(
            delete(RetrievalTrace).where(
                RetrievalTrace.owner_id == h["a_id"], RetrievalTrace.request_id == legacy_id
            )
        )
    missing = call(
        "request-legacy", "/v1/requests/{request_id}", actual=f"/v1/requests/{legacy_id}"
    )
    assert missing["citations"] == [] and missing["status"] == "completed"
    call(
        "error-missing-trace",
        "/v1/requests/{request_id}/retrieval",
        actual=f"/v1/requests/{legacy_id}/retrieval",
        status=404,
    )
    upgraded = call(
        "prompt-upgrade",
        "/v1/conversations/{conversation_id}/prompt-upgrade",
        "post",
        actual=f"/v1/conversations/{cid}/prompt-upgrade",
    )
    assert (
        upgraded["prompt_version"] == PROMPT_VERSION
        # One completed legacy chat plus the explicit prompt upgrade.
        and upgraded["revision"] == legacy["revision"] + 2
    )
    h["provider"].complete, h["provider"].error = (
        original_complete,
        ProviderError("provider_timeout"),
    )
    failed_id = str(uuid4())
    call(
        "error-provider",
        messages,
        "post",
        actual=f"/v1/conversations/{cid}/messages",
        status=502,
        json={"request_id": failed_id, "content": "Synthetic failure"},
    )
    failed = call("request-failed", "/v1/requests/{request_id}", actual=f"/v1/requests/{failed_id}")
    assert failed["status"] == "failed" and failed["response"] is None
    h["provider"].error = None
    call(
        "error-conflict",
        messages,
        "post",
        actual=f"/v1/conversations/{cid}/messages",
        status=409,
        json=message_body | {"content": "Different input"},
    )
    call(
        "error-size",
        messages,
        "post",
        actual=f"/v1/conversations/{cid}/messages",
        status=413,
        json={"request_id": str(uuid4()), "content": "\U0001f642" * 2000},
    )
    error = call(
        "error-validation",
        messages,
        "post",
        actual=f"/v1/conversations/{cid}/messages",
        status=422,
        json={
            "request_id": str(uuid4()),
            "content": "private-validation-marker",
            "use_memory": "private-credential-marker",
        },
    )
    assert "private-validation-marker" not in json.dumps(error)
    assert "private-credential-marker" not in json.dumps(error)
    assert all(set(item) == {"type", "loc", "msg"} for item in error["detail"])
    call(
        "error-query",
        claims,
        actual=f"/v1/scopes/{sid}/claims",
        status=422,
        params={"subject": "bad\x00value"},
    )
    capacity = h["app"].state.chat.capacity
    assert capacity.acquire(blocking=False) and capacity.acquire(blocking=False)
    try:
        call(
            "error-capacity",
            messages,
            "post",
            actual=f"/v1/conversations/{cid}/messages",
            status=503,
            json={"request_id": str(uuid4()), "content": "Synthetic capacity test"},
        )
        assert cases[-1][3].headers["Retry-After"] == "3"
    finally:
        capacity.release()
        capacity.release()
    auth = h["client"].get("/v1/me")
    assert auth.status_code == 401 and auth.headers["WWW-Authenticate"] == "Bearer"
    assert_schema(auth.json(), response_schema(document, "/v1/me", "get", 401), document)
    cases.append(("error-auth", "/v1/me", "get", auth))
    # Typing must not strip additive keys from already saved trace snapshots.
    with h["sessions"].begin() as db:
        trace = db.get(RetrievalTrace, (h["a_id"], rid))
        trace.budget = trace.budget | {"snapshot_extension": 7}
        trace.candidates = [item | {"snapshot_extension": "retained"} for item in trace.candidates]
    extended = call(
        "retrieval-additive",
        "/v1/requests/{request_id}/retrieval",
        actual=f"/v1/requests/{rid}/retrieval",
    )
    assert extended["budget"]["snapshot_extension"] == 7
    assert all(item["snapshot_extension"] == "retained" for item in extended["candidates"])
    preference_key = str(uuid4())
    expression_receipt = call(
        "expression-preference-receipt",
        "/v1/preferences/{kind}/{target_id}",
        "post",
        actual=f"/v1/preferences/conversation/{cid}",
        status=201,
        json={
            "operation_id": preference_key,
            "expected_revision": 0,
            "values": {"verbosity": "concise", "humor": "none"},
            "dynamic_enabled": True,
        },
    )
    call(
        "preferences-current",
        "/v1/preferences/{kind}/{target_id}",
        actual=f"/v1/preferences/conversation/{cid}",
    )
    expression = call(
        "expression-current",
        "/v1/conversations/{conversation_id}/expression",
        actual=f"/v1/conversations/{cid}/expression",
    )
    call(
        "expression-receipt",
        "/v1/expression-receipts/{operation_id}",
        actual=f"/v1/expression-receipts/{preference_key}",
    )
    call(
        "expression-request-legacy",
        "/v1/requests/{request_id}/expression",
        actual=f"/v1/requests/{rid}/expression",
    )
    expression_rid = str(uuid4())
    call(
        "expression-chat",
        "/v1/conversations/{conversation_id}/messages",
        "post",
        actual=f"/v1/conversations/{cid}/messages",
        json={
            "request_id": expression_rid,
            "content": "Synthetic expression follow-up",
            "use_memory": False,
        },
    )
    call(
        "expression-request-current",
        "/v1/requests/{request_id}/expression",
        actual=f"/v1/requests/{expression_rid}/expression",
    )
    call(
        "expression-signal-receipt",
        "/v1/conversations/{conversation_id}/expression/signals",
        "post",
        actual=f"/v1/conversations/{cid}/expression/signals",
        status=201,
        json={
            "operation_id": str(uuid4()),
            "session_id": expression["session_id"],
            "source_request_id": expression_rid,
            "reviewed": True,
            "reason": "reviewed_model_signal",
            "vector": {"warmth": 100},
        },
    )
    call(
        "expression-reset-receipt",
        "/v1/conversations/{conversation_id}/expression/reset",
        "post",
        actual=f"/v1/conversations/{cid}/expression/reset",
        status=201,
        json={"operation_id": str(uuid4()), "session_id": expression["session_id"]},
    )
    assert expression_receipt["expression"]["preferences"]["verbosity"] == "concise"
    learning_key = str(uuid4())
    call(
        "learning-config-receipt",
        "/v1/scopes/{scope_id}/learning/config",
        "post",
        actual=f"/v1/scopes/{sid}/learning/config",
        status=201,
        json={"operation_id": learning_key, "expected_revision": 0, "status": "enrolled"},
    )
    for i, content in enumerate(
        ("Concise plans help.", "Brief coding replies please.", "Compact review explanations work.")
    ):
        reply = h["client"].post(
            f"/v1/conversations/{cid}/messages",
            headers=h["a"],
            json={"request_id": str(uuid4()), "content": content},
        )
        assert reply.status_code == 200
        events = h["client"].get(f"/v1/conversations/{cid}/events", headers=h["a"]).json()
        event = next(
            x
            for x in events
            if x["request_id"] == reply.json()["request_id"] and x["role"] == "user"
        )
        source = (
            h["client"]
            .get(f"/v1/source-versions/{event['source_version_id']}", headers=h["a"])
            .json()
        )
        call(
            f"learning-observation-{i + 1}",
            "/v1/scopes/{scope_id}/learning/observations",
            "post",
            actual=f"/v1/scopes/{sid}/learning/observations",
            status=201,
            json={
                "operation_id": str(uuid4()),
                "source": {
                    "source_version_id": source["id"],
                    "version": source["version"],
                    "content_hash": source["content_hash"],
                    "span_start": 0,
                    "span_end": len(source["content"]),
                },
                "values": {"verbosity": "concise"},
                "confidence_class": "repeated_observation",
            },
        )
    learned = call(
        "learning-state", "/v1/scopes/{scope_id}/learning", actual=f"/v1/scopes/{sid}/learning"
    )
    proposal = learned["proposals"][0]
    assert proposal["eligible"] and proposal["independent_count"] == 3
    review_key = str(uuid4())
    call(
        "learning-review-receipt",
        "/v1/scopes/{scope_id}/learning/reviews",
        "post",
        actual=f"/v1/scopes/{sid}/learning/reviews",
        status=201,
        json={
            "operation_id": review_key,
            "proposal_id": proposal["id"],
            "expected_revision": proposal["revision"],
            "decision": "approve",
            "account_wide": False,
            "reviewed": True,
        },
    )
    call(
        "learning-receipt",
        "/v1/learning-receipts/{operation_id}",
        actual=f"/v1/learning-receipts/{review_key}",
    )
    call(
        "learning-state-approved",
        "/v1/scopes/{scope_id}/learning",
        actual=f"/v1/scopes/{sid}/learning",
    )
    call(
        "learning-request-legacy",
        "/v1/requests/{request_id}/learning",
        actual=f"/v1/requests/{rid}/learning",
    )
    call(
        "learning-request",
        "/v1/requests/{request_id}/learning",
        actual=f"/v1/requests/{reply.json()['request_id']}/learning",
    )
    call(
        "learning-reset-receipt",
        "/v1/scopes/{scope_id}/learning/reset",
        "post",
        actual=f"/v1/scopes/{sid}/learning/reset",
        status=201,
        json={"operation_id": str(uuid4()), "expected_revision": 1},
    )
    call(
        "learning-state-reset",
        "/v1/scopes/{scope_id}/learning",
        actual=f"/v1/scopes/{sid}/learning",
    )
    import threading
    import time

    gate = threading.Event()

    class ContractStream(type(h["provider"])):
        def stream(self, messages, cancel):
            if messages[-1]["content"] in (
                "Synthetic complete stream",
                "Reviewed synthetic kettle 🫖 wording",
            ):
                yield "Synthetic completed stream."
                yield Completion("Synthetic completed stream.", self.model, 10, 5)
            else:
                gate.wait(5)
                yield "Synthetic provisional [M"
                cancel.wait(5)

    h["app"].state.chat.provider = ContractStream()
    call("capabilities-streaming", "/v1/capabilities")
    stream_id = str(uuid4())
    call(
        "stream-started",
        "/v1/conversations/{conversation_id}/stream-requests",
        "post",
        actual=f"/v1/conversations/{cid}/stream-requests",
        status=202,
        json={"request_id": stream_id, "content": "Synthetic stream checkpoint"},
    )
    gate.set()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = h["client"].get(f"/v1/requests/{stream_id}/stream-status", headers=h["a"]).json()
        if state["provisional"]:
            break
        time.sleep(0.01)
    assert state["provisional"]
    call(
        "stream-current",
        "/v1/requests/{request_id}/stream-status",
        actual=f"/v1/requests/{stream_id}/stream-status",
    )
    call(
        "stream-cancel-receipt",
        "/v1/requests/{request_id}/cancel",
        "post",
        actual=f"/v1/requests/{stream_id}/cancel",
        json={"attempt": 1},
    )
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = h["client"].get(f"/v1/requests/{stream_id}/stream-status", headers=h["a"]).json()
        if state["stream_state"] == "cancelled":
            break
        time.sleep(0.01)
    assert state["stream_state"] == "cancelled"
    call(
        "stream-cancelled",
        "/v1/requests/{request_id}/stream-status",
        actual=f"/v1/requests/{stream_id}/stream-status",
    )
    call("request-cancelled", "/v1/requests/{request_id}", actual=f"/v1/requests/{stream_id}")
    call(
        "stream-legacy",
        "/v1/requests/{request_id}/stream-status",
        actual=f"/v1/requests/{rid}/stream-status",
    )
    complete_id = str(uuid4())
    h["client"].post(
        f"/v1/conversations/{cid}/stream-requests",
        headers=h["a"],
        json={"request_id": complete_id, "content": "Synthetic complete stream"},
    )
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = h["client"].get(f"/v1/requests/{complete_id}/stream-status", headers=h["a"]).json()
        if state["stream_state"] == "completed":
            break
        time.sleep(0.01)
    assert state["stream_state"] == "completed"
    call(
        "stream-completed",
        "/v1/requests/{request_id}/stream-status",
        actual=f"/v1/requests/{complete_id}/stream-status",
    )
    voice_id = str(uuid4())
    call(
        "voice-started",
        "/v1/conversations/{conversation_id}/voice-requests",
        "post",
        status=202,
        actual=f"/v1/conversations/{cid}/voice-requests",
        json={
            "request_id": voice_id,
            "content": "Reviewed synthetic kettle 🫖 wording",
            "review": "approve",
            "transcript": {
                "transcript_id": str(uuid4()),
                "engine_id": "android_on_device",
                "engine_version": "Android 16 API 36 (client reported)",
                "language": "en-US",
                "duration_ms": 3200,
                "original_text": "Generated synthetic cattle 🫖 wording",
            },
        },
    )
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = h["client"].get(f"/v1/requests/{voice_id}/stream-status", headers=h["a"]).json()
        if state["stream_state"] == "completed":
            break
        time.sleep(0.01)
    assert state["stream_state"] == "completed"
    call(
        "voice-lineage",
        "/v1/requests/{request_id}/voice-input",
        actual=f"/v1/requests/{voice_id}/voice-input",
    )
    call(
        "voice-inputs",
        "/v1/conversations/{conversation_id}/voice-inputs",
        actual=f"/v1/conversations/{cid}/voice-inputs",
    )
    # Security fixtures use a separate synthetic owner; preserve all earlier snapshots.
    from ada.auth import create_user

    security_owner, security_token = create_user(h["sessions"], "Synthetic security fixture")
    h["a"] = {"Authorization": "Bearer " + security_token}
    h["a_id"] = security_owner
    h["settings"].device_enrollment_enabled = True
    h["settings"].deletion_worker_enabled = True  # Explicit manual processing in this test.
    call("security-status", "/v1/security/status")
    issue_body = {"operation_id": str(uuid4()), "label": "Synthetic fixture device"}
    issued = h["client"].post("/v1/security/credentials", headers=h["a"], json=issue_body)
    if issued.status_code != 201:
        raise AssertionError("Synthetic credential enrollment failed")
    call("credential-replay", "/v1/security/credentials", "post", json=issue_body)
    key = issued.json()["credential"]["id"]
    call("device-credentials", "/v1/security/credentials")
    rotate_body = {"operation_id": str(uuid4()), "label": "Synthetic rotated device"}
    rotated = h["client"].post(
        f"/v1/security/credentials/{key}/rotate", headers=h["a"], json=rotate_body
    )
    if rotated.status_code != 201:
        raise AssertionError("Synthetic credential rotation failed")
    call(
        "credential-rotation-replay",
        "/v1/security/credentials/{credential_id}/rotate",
        "post",
        actual=f"/v1/security/credentials/{key}/rotate",
        json=rotate_body,
    )
    call(
        "credential-revoked",
        "/v1/security/credentials/{credential_id}/revoke",
        "post",
        actual=f"/v1/security/credentials/{rotated.json()['credential']['id']}/revoke",
    )
    preview = call("deletion-preview", "/v1/security/deletion-previews", "post", status=201)
    deletion_body = {
        "job_id": str(uuid4()),
        "preview_id": preview["id"],
        "confirmation": "erase_saved_content",
    }
    call("deletion-queued", "/v1/security/deletions", "post", status=202, json=deletion_body)
    h["app"].state.deletion.process_one()
    call(
        "deletion-completed",
        "/v1/security/deletions/{job_id}",
        actual=f"/v1/security/deletions/{deletion_body['job_id']}",
    )
    call("deletion-history", "/v1/security/deletions")
    if os.environ.get("ADA_UPDATE_CONTRACT_FIXTURES") == "1" and h["backend"] == "sqlite":
        write_synthetic_fixtures(cases)


def test_exported_contract_enforces_owner_boundary(harness):
    from conftest import make_conversation, send
    from test_memory import add, note

    h = harness
    document = json.loads(OPENAPI.read_text(encoding="utf-8"))
    cid, _ = make_conversation(h)
    sid = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    source = note(h, sid)
    claim = add(h, sid, source).json()
    rid = str(uuid4())
    assert send(h, cid, "Synthetic owner boundary", rid).status_code == 200
    resources = {
        "/v1/conversations/{conversation_id}": f"/v1/conversations/{cid}",
        "/v1/conversations/{conversation_id}/events": f"/v1/conversations/{cid}/events",
        "/v1/requests/{request_id}": f"/v1/requests/{rid}",
        "/v1/requests/{request_id}/retrieval": f"/v1/requests/{rid}/retrieval",
        "/v1/scopes/{scope_id}": f"/v1/scopes/{sid}",
        "/v1/scopes/{scope_id}/source-versions": f"/v1/scopes/{sid}/source-versions",
        "/v1/scopes/{scope_id}/claims": f"/v1/scopes/{sid}/claims",
        "/v1/source-versions/{source_version_id}": f"/v1/source-versions/{source['id']}",
        "/v1/claims/{claim_id}": f"/v1/claims/{claim['id']}",
    }
    for path, actual in resources.items():
        for headers, status in ((h["b"], 404), ({}, 401)):
            response = h["client"].get(actual, headers=headers)
            assert response.status_code == status
            assert_schema(response.json(), response_schema(document, path, "get", status), document)
            assert (
                "Synthetic owner boundary" not in response.text
                and source["content"] not in response.text
            )
    for path in ("/v1/conversations", "/v1/personalities", "/v1/scopes"):
        response = h["client"].get(path, headers=h["b"])
        assert response.json() == []
        assert_schema(response.json(), response_schema(document, path, "get", 200), document)


def test_synthetic_fixtures_match_export_and_use_portable_paths():
    document = json.loads(OPENAPI.read_text(encoding="utf-8"))
    manifest = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["fixtures"]:
        assert "\\" not in entry["file"] and "\\" not in entry["path"]
        assert PureWindowsPath(entry["file"]).as_posix() == entry["file"]
        assert not Path(entry["file"]).is_absolute() and ".." not in Path(entry["file"]).parts
        payload = json.loads((FIXTURES / entry["file"]).read_text(encoding="utf-8"))
        assert_schema(
            payload,
            response_schema(document, entry["path"], entry["method"], entry["status"]),
            document,
        )
    source = json.loads((FIXTURES / "source-current.json").read_text(encoding="utf-8"))
    assert source["content_hash"] == hashlib.sha256(source["content"].encode()).hexdigest()
    schema = response_schema(document, "/v1/me", "get", 200)
    with pytest.raises(AssertionError):
        assert_schema({"name": "Missing owner UUID"}, schema, document)
    with pytest.raises((AssertionError, ValueError)):
        assert_schema({"id": "not-a-uuid", "name": "Malformed UUID"}, schema, document)
