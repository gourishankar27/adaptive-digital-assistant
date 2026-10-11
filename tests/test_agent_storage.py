from concurrent.futures import ThreadPoolExecutor
from threading import Event, local
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation, send
from sqlalchemy import event, func, select, text
from sqlalchemy.exc import IntegrityError
from test_agents import CalculatorAgent, create, prepared

from ada.agent_models import AgentApproval, AgentReceipt, AgentRun, AgentStep


def test_review_downgrade_preflight_preserves_empty_agent_schema_on_sqlite(harness):
    from test_proposals import extract, setup

    h = harness
    scope, _, _, body, _ = setup(h)
    extract(h, scope, body)
    with pytest.raises(RuntimeError, match="review history"):
        command.downgrade(h["config"], "0007")
    with h["sessions"]() as db:
        from ada.schema import SCHEMA_HEAD

        assert db.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_HEAD
        assert db.scalar(select(func.count()).select_from(AgentRun)) == 0
    command.check(h["config"])


def test_populated_upgrade_preserves_plain_chat_and_agent_history_refuses_downgrade(harness):
    h = harness
    conversation, _ = make_conversation(h)
    request = str(uuid4())
    original = send(h, conversation, '{"tool_calls":[{"name":"shell"}]}', request_id=request)
    assert original.status_code == 200
    command.downgrade(h["config"], "0008")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert (
        send(h, conversation, '{"tool_calls":[{"name":"shell"}]}', request_id=request).json()
        == original.json()
    )
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(AgentRun)) == 0
    run, _, _, _ = prepared(h)
    with pytest.raises(RuntimeError, match="Populated agent history"):
        command.downgrade(h["config"], "0008")
    assert h["client"].get(f"/v1/agent-runs/{run['id']}", headers=h["a"]).json() == run


def test_recovery_fences_late_model_result_and_replays_receipt(harness):
    h = harness
    conversation, _ = make_conversation(h)
    service = h["app"].state.agents
    entered, release = Event(), Event()
    clock = [1_800_000_000_000]
    service.clock = lambda: clock[0]
    base = CalculatorAgent(h)

    class SlowModel:
        id, model = base.id, base.model

        def complete(self, messages, tools):
            entered.set()
            assert release.wait(10)
            return base.complete(messages, tools)

    service.provider = SlowModel()
    body = {
        "run_id": str(uuid4()),
        "task": "Calculate 3+4.",
        "protocol_version": "ada-agent-v1",
        "allowed_tools": ["calculator"],
    }
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(create, h, conversation, body)
        try:
            assert entered.wait(5)
            run = service.detail(h["a_id"], body["run_id"])
            recovery = {"operation_id": str(uuid4()), "generation": run["generation"]}
            clock[0] += 91_000
            route = f"/v1/agent-runs/{run['id']}/recover"
            result = h["client"].post(route, headers=h["a"], json=recovery)
            assert result.status_code == 201 and result.json()["outcome"] == "unknown"
            assert h["client"].post(route, headers=h["a"], json=recovery).json() == result.json()
        finally:
            release.set()
        assert future.result(timeout=5).json()["status"] == "unknown"
    assert len(base.calls) == 1
    assert service.detail(h["a_id"], body["run_id"])["steps"][0]["tool"] is None


def test_recovery_of_reserved_tool_keeps_original_approval_receipt_and_never_repeats(harness):
    h = harness
    run, approval, path, provider = prepared(h)
    service = h["app"].state.agents
    entered, release = Event(), Event()
    clock = [run["created_at"]]
    service.clock = lambda: clock[0]

    def slow_tool(*args):
        entered.set()
        assert release.wait(10)
        return {"value": "7"}

    service.dispatch = slow_tool
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(h["client"].post, path + "/approve", headers=h["a"], json=approval)
        try:
            assert entered.wait(5)
            active = service.detail(h["a_id"], run["id"])
            clock[0] += 91_000
            recovery = {"operation_id": str(uuid4()), "generation": active["generation"]}
            recovered = h["client"].post(
                f"/v1/agent-runs/{run['id']}/recover", headers=h["a"], json=recovery
            )
            assert recovered.status_code == 201
            assert recovered.json()["approval_id"] == approval["approval_id"]
        finally:
            release.set()
        assert future.result(timeout=5).json() == recovered.json()
    repeated = h["client"].post(path + "/approve", headers=h["a"], json=approval)
    assert repeated.status_code == 200 and repeated.json() == recovered.json()
    assert len(provider.calls) == 1
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(AgentReceipt)) == 1


def test_concurrent_approvals_and_run_reservations_have_one_execution(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("PostgreSQL row locks serialize actual concurrent agent reservations")
    conversation, _ = make_conversation(h)
    active = local()
    engine = h["sessions"].kw["bind"]

    @event.listens_for(engine, "checkout")
    def checkout(*args):
        active.count = getattr(active, "count", 0) + 1

    @event.listens_for(engine, "checkin")
    def checkin(*args):
        active.count = getattr(active, "count", 0) - 1

    class ConcurrentAgent:
        id, model = "fixture", "synthetic-agent-v1"

        def __init__(self):
            self.calls = []

        def complete(self, messages, tools):
            assert getattr(active, "count", 0) == 0
            self.calls.append(messages)
            if messages[-1]["role"] == "tool":
                return {"role": "assistant", "content": "The recorded calculator result is 7."}
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": "calculator", "arguments": {"expression": "3+4"}}}
                ],
            }

    provider = ConcurrentAgent()
    h["app"].state.agents.provider = provider
    body = {
        "run_id": str(uuid4()),
        "task": "Calculate 3+4.",
        "protocol_version": "ada-agent-v1",
        "allowed_tools": ["calculator"],
    }
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: create(h, conversation, body), range(2)))
    assert sorted(r.status_code for r in responses) == [200, 201]
    assert len(provider.calls) == 1
    run = h["client"].get(f"/v1/agent-runs/{body['run_id']}", headers=h["a"]).json()
    step = run["steps"][0]
    approval = {
        "approval_id": str(uuid4()),
        "preview_hash": step["preview_hash"],
        "argument_hash": step["argument_hash"],
        "tool_version": step["tool_version"],
    }
    route = f"/v1/agent-runs/{run['id']}/steps/{step['id']}/approve"
    executions = []
    original = h["app"].state.agents.dispatch

    def counted(*args):
        executions.append(1)
        return original(*args)

    h["app"].state.agents.dispatch = counted
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(lambda _: h["client"].post(route, headers=h["a"], json=approval), range(2))
        )
    assert all(r.status_code in (200, 201, 409) for r in results)
    assert any(r.status_code == 201 for r in results) and len(executions) == 1
    assert h["client"].post(route, headers=h["a"], json=approval).status_code == 200
    assert len(provider.calls) == 2
    event.remove(engine, "checkout", checkout)
    event.remove(engine, "checkin", checkin)


def test_native_scoped_approval_constraints_reject_forged_actor(harness):
    h = harness
    run, approval, _, _ = prepared(h)
    with pytest.raises(IntegrityError), h["sessions"].begin() as db:
        db.add(
            AgentApproval(
                owner_id=h["a_id"],
                id=str(uuid4()),
                scope_id=run["scope_id"],
                run_id=run["id"],
                step_id=run["steps"][0]["id"],
                actor_id=h["b_id"],
                decision="approve",
                input_hash="0" * 64,
                created_at=run["created_at"],
            )
        )
        db.flush()
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(AgentApproval)) == 0
        assert db.get(AgentStep, (h["a_id"], run["steps"][0]["id"])).status == "pending_approval"
