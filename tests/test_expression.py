import copy
import threading
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import select, text

from ada.models import Conversation, Request
from ada.providers import ProviderError


def preference(h, kind, target, values, revision=0, **options):
    return h["client"].post(
        f"/v1/preferences/{kind}/{target}",
        headers=h["a"],
        json={
            "operation_id": str(uuid4()),
            "expected_revision": revision,
            "values": values,
            **options,
        },
    )


def state(h, conversation, who="a"):
    r = h["client"].get(f"/v1/conversations/{conversation}/expression", headers=h[who])
    assert r.status_code == 200, r.text
    return r.json()


def test_preference_precedence_frozen_profiles_and_explicit_future_update(harness):
    h = harness
    cid, pid = make_conversation(h)
    with h["sessions"]() as db:
        scope = db.get(Conversation, cid).scope_id
        original = db.get(Conversation, cid).personality_snapshot
    assert preference(h, "account", h["a_id"], {"verbosity": "concise"}).status_code == 201
    assert (
        preference(h, "scope", scope, {"verbosity": "detailed", "humor": "none"}).status_code == 201
    )
    assert preference(h, "profile", pid, {"verbosity": "balanced"}).status_code == 201
    assert state(h, cid)["active"] is False  # No behind-history propagation.
    result = preference(h, "conversation", cid, {"formality": "formal"})
    assert result.status_code == 201, result.text
    s = state(h, cid)
    assert s["preferences"]["verbosity"] == "balanced"
    assert s["origins"]["verbosity"] == "profile"
    assert s["preferences"]["formality"] == "formal"
    assert s["origins"]["formality"] == "conversation"
    with h["sessions"]() as db:
        assert db.get(Conversation, cid).personality_snapshot == original
    assert preference(h, "account", h["a_id"], {"verbosity": "detailed"}, 1).status_code == 201
    assert state(h, cid)["preferences"] == s["preferences"]
    result = preference(h, "conversation", cid, {}, 1)
    assert result.status_code == 201
    assert state(h, cid)["origins"]["formality"] == "personality"
    created = (
        h["client"].post("/v1/conversations", headers=h["a"], json={"personality_id": pid}).json()
    )
    assert state(h, created["id"])["origins"]["verbosity"] == "profile"


@pytest.mark.parametrize(
    "bad",
    [
        {"admin": True},
        {"truth": "override"},
        {"tools": ["shell"]},
        {"verbosity": "unbounded"},
        {"humor": True},
        {"initiative": "execute"},
    ],
)
def test_preferences_reject_permission_truth_and_unknown_inputs(harness, bad):
    h = harness
    cid, _ = make_conversation(h)
    assert preference(h, "conversation", cid, bad).status_code == 422
    assert state(h, cid)["active"] is False


def test_exact_receipts_owner_isolation_and_stale_edit(harness):
    h = harness
    cid, pid = make_conversation(h)
    body = {"operation_id": str(uuid4()), "expected_revision": 0, "values": {"humor": "light"}}
    path = f"/v1/preferences/conversation/{cid}"
    first = h["client"].post(path, headers=h["a"], json=body)
    assert first.status_code == 201
    assert h["client"].post(path, headers=h["a"], json=body).json() == first.json()
    changed = {**body, "values": {"humor": "none"}}
    assert h["client"].post(path, headers=h["a"], json=changed).status_code == 409
    assert preference(h, "conversation", cid, {"humor": "none"}).status_code == 409
    for p in [
        path,
        f"/v1/preferences/profile/{pid}",
        f"/v1/preferences/account/{h['a_id']}",
        f"/v1/conversations/{cid}/expression",
        f"/v1/expression-receipts/{body['operation_id']}",
    ]:
        assert h["client"].get(p, headers=h["b"]).status_code == 404
        assert h["client"].get(p).status_code == 401
    assert h["client"].post(path, headers=h["b"], json=body).status_code == 404


def test_bounded_signals_single_turn_reset_expiry_and_retry_snapshot(harness, monkeypatch):
    h = harness
    cid, _ = make_conversation(h)
    assert preference(h, "conversation", cid, {}, dynamic_enabled=True).status_code == 201
    rid = str(uuid4())
    assert send(h, cid, request_id=rid).status_code == 200
    s = state(h, cid)
    body = {
        "operation_id": str(uuid4()),
        "session_id": s["session_id"],
        "source_request_id": rid,
        "reviewed": True,
        "reason": "reviewed_model_signal",
        "vector": {"warmth": 999, "energy": -999},
    }
    path = f"/v1/conversations/{cid}/expression/signals"
    r = h["client"].post(path, headers=h["a"], json=body)
    assert r.status_code == 201, r.text
    adjusted = state(h, cid)
    assert adjusted["vector"]["warmth"] == s["vector"]["warmth"] + 10
    assert adjusted["vector"]["energy"] == s["vector"]["energy"] - 10
    assert h["client"].post(path, headers=h["a"], json=body).json() == r.json()
    assert (
        h["client"]
        .post(path, headers=h["a"], json={**body, "operation_id": str(uuid4())})
        .status_code
        == 409
    )
    frozen = h["client"].get(f"/v1/requests/{rid}/expression", headers=h["a"]).json()
    assert frozen["expression"]["vector"] == s["vector"]
    assert send(h, cid, request_id=rid).status_code == 200
    assert h["client"].get(f"/v1/requests/{rid}/expression", headers=h["a"]).json() == frozen
    monkeypatch.setattr("ada.expression.now_ms", lambda: adjusted["expires_at"] + 1)
    expired = state(h, cid)
    assert expired["expired"] and expired["vector"] == expired["defaults"]
    assert (
        h["client"]
        .post(path, headers=h["a"], json={**body, "operation_id": str(uuid4())})
        .status_code
        == 409
    )
    assert send(h, cid, request_id=str(uuid4())).status_code == 200
    renewed = state(h, cid)
    assert renewed["session_id"] != s["session_id"]
    reset = {"operation_id": str(uuid4()), "session_id": renewed["session_id"]}
    assert (
        h["client"]
        .post(f"/v1/conversations/{cid}/expression/reset", headers=h["a"], json=reset)
        .status_code
        == 201
    )
    assert state(h, cid)["session_id"] != renewed["session_id"]


@pytest.mark.parametrize(
    "change",
    [
        {"reviewed": False},
        {"vector": {"admin": 1}},
        {"vector": {"focus": True}},
        {"vector": {"energy": float("inf")}},
        {"reason": "diagnosis"},
    ],
)
def test_malformed_signal_cannot_change_state(harness, change):
    h = harness
    cid, _ = make_conversation(h)
    preference(h, "conversation", cid, {}, dynamic_enabled=True)
    rid = str(uuid4())
    send(h, cid, request_id=rid)
    before = state(h, cid)
    body = {
        "operation_id": str(uuid4()),
        "session_id": before["session_id"],
        "source_request_id": rid,
        "reviewed": True,
        "reason": "user_selected",
        "vector": {"focus": 70},
        **change,
    }
    # JSON itself cannot represent non-finite numbers; exercise an invalid string instead.
    if change.get("vector", {}).get("energy") == float("inf"):
        body["vector"] = {"energy": "Infinity"}
    assert (
        h["client"]
        .post(f"/v1/conversations/{cid}/expression/signals", headers=h["a"], json=body)
        .status_code
        == 422
    )
    assert state(h, cid)["vector"] == before["vector"]


def test_failed_retry_keeps_expression_and_old_v3_v4_are_supported(harness):
    h = harness
    cid, _ = make_conversation(h)
    with h["sessions"].begin() as db:
        row = db.get(Conversation, cid)
        row.prompt_version = "ada-baseline-v3"
    preference(h, "conversation", cid, {"verbosity": "concise"}, dynamic_enabled=True)
    rid = str(uuid4())
    h["provider"].error = ProviderError("model_unavailable")
    assert send(h, cid, request_id=rid).status_code == 502
    before = copy.deepcopy(h["provider"].calls[-1])
    assert preference(h, "conversation", cid, {"verbosity": "detailed"}, 1).status_code == 201
    h["provider"].error = None
    assert send(h, cid, request_id=rid).status_code == 200
    assert h["provider"].calls[-1] == before
    with h["sessions"]() as db:
        assert db.get(Conversation, cid).prompt_version == "ada-baseline-v3"
        assert (
            db.get(Request, (h["a_id"], rid)).expression_snapshot["preferences"]["verbosity"]
            == "concise"
        )


def test_inflight_expression_updates_conflict_and_model_context_never_grants_authority(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Native locking verified with PostgreSQL")
    cid, _ = make_conversation(h)
    preference(h, "conversation", cid, {}, dynamic_enabled=True)
    entered, release = threading.Event(), threading.Event()
    original = h["provider"].complete

    def blocked(messages):
        entered.set()
        assert release.wait(10)
        return original(messages)

    h["provider"].complete = blocked
    result = []
    worker = threading.Thread(target=lambda: result.append(send(h, cid)))
    worker.start()
    assert entered.wait(10)
    try:
        r = preference(h, "conversation", cid, {"initiative": "suggest"}, 1)
        assert r.status_code == 409 and r.json()["detail"] == "conversation_busy"
    finally:
        release.set()
        worker.join(10)
    assert result[0].status_code == 200
    message = h["provider"].calls[-1][0]["content"]
    assert "ada-expression-v1" in message and "permissions" in message


def test_expression_migration_populated_downgrade_refuses_before_ddl(harness):
    h = harness
    cid, _ = make_conversation(h)
    preference(h, "conversation", cid, {"humor": "none"})
    with pytest.raises(RuntimeError, match="Expression history"):
        command.downgrade(h["config"], "0010")
    with h["sessions"]() as db:
        from ada.schema import SCHEMA_HEAD

        assert db.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_HEAD
        assert db.get(Conversation, cid) is not None
    command.check(h["config"])


def test_decay_disable_and_explicit_preferences_keep_evidence_independent(harness, monkeypatch):
    from ada.expression import DECAY_MS, POLICY_BYTES, prompt_expression

    h = harness
    clock = [1_900_000_000_000]
    monkeypatch.setattr("ada.expression.now_ms", lambda: clock[0])
    cid, _ = make_conversation(h)
    preference(
        h, "conversation", cid, {"humor": "none", "verbosity": "concise"}, dynamic_enabled=True
    )
    rid = str(uuid4())
    send(h, cid, request_id=rid)
    before = state(h, cid)
    body = {
        "operation_id": str(uuid4()),
        "session_id": before["session_id"],
        "source_request_id": rid,
        "reviewed": True,
        "reason": "user_selected",
        "vector": {"warmth": 100, "playfulness": 100},
    }
    assert (
        h["client"]
        .post(f"/v1/conversations/{cid}/expression/signals", headers=h["a"], json=body)
        .status_code
        == 201
    )
    assert state(h, cid)["vector"]["warmth"] == 70
    clock[0] += DECAY_MS
    assert state(h, cid)["vector"]["warmth"] == 65
    send(h, cid, request_id=str(uuid4()))
    settled = state(h, cid)
    assert settled["vector"]["warmth"] == 60
    assert settled["preferences"]["humor"] == "none"
    assert (
        len(prompt_expression(before).encode())
        == len(prompt_expression(settled).encode())
        == POLICY_BYTES
    )
    assert (
        preference(
            h, "conversation", cid, {"verbosity": "detailed"}, 1, dynamic_enabled=False
        ).status_code
        == 201
    )
    disabled = state(h, cid)
    assert disabled["vector"] == disabled["defaults"] and not disabled["dynamic_enabled"]
    assert disabled["session_id"] != before["session_id"]


def test_signal_isolation_between_owned_conversations_and_foreign_requests(harness):
    h = harness
    first, _ = make_conversation(h)
    second, _ = make_conversation(h)
    preference(h, "conversation", first, {}, dynamic_enabled=True)
    preference(h, "conversation", second, {}, dynamic_enabled=True)
    rid_a, rid_b = str(uuid4()), str(uuid4())
    send(h, first, request_id=rid_a)
    send(h, second, request_id=rid_b)
    before, other = state(h, first), state(h, second)
    assert before["session_id"] != other["session_id"]
    body = {
        "operation_id": str(uuid4()),
        "session_id": before["session_id"],
        "source_request_id": rid_b,
        "reviewed": True,
        "reason": "user_selected",
        "vector": {"warmth": 100},
    }
    assert (
        h["client"]
        .post(f"/v1/conversations/{first}/expression/signals", headers=h["a"], json=body)
        .status_code
        == 409
    )
    assert h["client"].get(f"/v1/requests/{rid_a}/expression", headers=h["b"]).status_code == 404
    assert state(h, first)["vector"] == before["vector"]
    assert state(h, second)["vector"] == other["vector"]


def test_preference_and_receipt_failure_roll_back_atomically(harness, monkeypatch):
    h = harness
    cid, _ = make_conversation(h)

    def fail(*args, **kwargs):
        raise RuntimeError("synthetic publication failure")

    monkeypatch.setattr(h["app"].state.expression, "publish", fail)
    with pytest.raises(RuntimeError, match="synthetic"):
        preference(h, "conversation", cid, {"verbosity": "concise"})
    assert state(h, cid)["active"] is False
    assert (
        h["client"].get(f"/v1/preferences/conversation/{cid}", headers=h["a"]).json()["revision"]
        == 0
    )


def test_native_owner_target_and_vector_constraints(harness):
    from sqlalchemy.exc import IntegrityError

    from ada.expression_models import ExpressionPreference, ExpressionSession

    h = harness
    cid, _ = make_conversation(h)
    preference(h, "conversation", cid, {}, dynamic_enabled=True)
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(
            ExpressionPreference(
                owner_id=h["b_id"],
                target_kind="conversation",
                target_id=cid,
                conversation_id=cid,
                revision=1,
                values={},
                receipt_id=str(uuid4()),
            )
        )
        db.flush()
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        row = db.get(ExpressionSession, (h["a_id"], cid))
        row.warmth = 101
        db.flush()
    assert state(h, cid)["vector"]["warmth"] == 60


def test_concurrent_preference_compare_and_set_has_one_winner(harness):
    from concurrent.futures import ThreadPoolExecutor

    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Native locking verified with PostgreSQL")
    with ThreadPoolExecutor(2) as executor:
        calls = [
            executor.submit(preference, h, "account", h["a_id"], {"verbosity": value})
            for value in ("concise", "detailed")
        ]
        assert sorted(call.result().status_code for call in calls) == [201, 409]


def test_populated_0010_upgrade_preserves_old_request_and_prompt(harness):
    from ada.personality import build_prompt

    h = harness
    command.downgrade(h["config"], "0010")
    cid, pid, scope, rid = [str(uuid4()) for _ in range(4)]
    snapshot = {"name": "ADA", "style": "conversational", "warmth": "warm", "detail": "balanced"}
    # Use historical SQL columns, not new ORM columns, while at the old revision.
    with h["sessions"].begin() as db:
        db.execute(
            text(
                "INSERT INTO personalities (id,owner_id,name,style,warmth,detail,created_at) VALUES (:pid,:owner,'ADA','conversational','warm','balanced',1)"
            ),
            {"pid": pid, "owner": h["a_id"]},
        )
        db.execute(
            text(
                "INSERT INTO scopes (id,owner_id,kind,name,created_at) VALUES (:sid,:owner,'personal','Synthetic legacy',1)"
            ),
            {"sid": scope, "owner": h["a_id"]},
        )
        import json

        db.execute(
            text(
                "INSERT INTO conversations (id,owner_id,personality_id,scope_id,scope_kind,title,personality_snapshot,system_prompt,prompt_version,revision,created_at) VALUES (:cid,:owner,:pid,:sid,'personal','Synthetic legacy',:snapshot,:prompt,'ada-baseline-v4',1,1)"
            ),
            {
                "cid": cid,
                "owner": h["a_id"],
                "pid": pid,
                "sid": scope,
                "snapshot": json.dumps(snapshot),
                "prompt": build_prompt(snapshot),
            },
        )
        from ada.service import request_fingerprint

        db.execute(
            text(
                "INSERT INTO requests (owner_id,id,conversation_id,content_hash,status,attempt,base_revision,messages,provider,model,response,created_at,started_at,finished_at) VALUES (:owner,:rid,:cid,:hash,'completed',1,0,:messages,'fake','old','Saved answer',1,1,1)"
            ),
            {
                "owner": h["a_id"],
                "rid": rid,
                "cid": cid,
                "hash": request_fingerprint("hello", None, True),
                "messages": json.dumps([{"role": "user", "content": "hello"}]),
            },
        )
    command.upgrade(h["config"], "head")
    assert send(h, cid, request_id=rid).json()["response"] == "Saved answer"
    assert (
        h["client"].get(f"/v1/requests/{rid}/expression", headers=h["a"]).json()["expression"]
        is None
    )
    assert state(h, cid)["active"] is False
    command.check(h["config"])


def test_explicit_prompt_upgrade_keeps_archived_system_and_expression_opt_in(harness):
    from ada.models import PromptChange

    h = harness
    cid, _ = make_conversation(h)
    with h["sessions"].begin() as db:
        row = db.get(Conversation, cid)
        row.prompt_version = "ada-baseline-v1"
        row.system_prompt = "Historical saved prompt"
    assert preference(h, "conversation", cid, {"verbosity": "concise"}).status_code == 409
    r = h["client"].post(f"/v1/conversations/{cid}/prompt-upgrade", headers=h["a"])
    assert r.status_code == 200
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(PromptChange).where(PromptChange.conversation_id == cid)
            ).previous_prompt
            == "Historical saved prompt"
        )
        saved = db.get(Conversation, cid).system_prompt
    assert preference(h, "conversation", cid, {"verbosity": "concise"}).status_code == 201
    with h["sessions"]() as db:
        assert db.get(Conversation, cid).system_prompt == saved


def test_clock_rollback_cannot_reverse_decay_or_escape_native_ranges(harness, monkeypatch):
    h = harness
    instant = [1_900_000_000_000]
    monkeypatch.setattr("ada.expression.now_ms", lambda: instant[0])
    cid, _ = make_conversation(h)
    preference(h, "conversation", cid, {}, dynamic_enabled=True)
    rid = str(uuid4())
    send(h, cid, request_id=rid)
    before = state(h, cid)
    instant[0] -= 60_000
    assert state(h, cid)["vector"] == before["vector"]
    r = send(h, cid, request_id=str(uuid4()))
    assert r.status_code == 200, r.text
    assert state(h, cid)["vector"] == before["vector"]
    assert state(h, cid)["expires_at"] == before["expires_at"]
