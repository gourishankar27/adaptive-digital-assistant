from uuid import uuid4

import pytest
from conftest import make_conversation


class CalculatorAgent:
    id, model = "fixture", "synthetic-agent-v1"

    def __init__(self, h):
        self.h, self.calls = h, []

    def complete(self, messages, tools):
        assert self.h["sessions"].kw["bind"].pool.checkedout() == 0
        self.calls.append(messages)
        if messages[-1]["role"] == "tool":
            return {"role": "assistant", "content": "The recorded calculator result is 7."}
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": "calculator", "arguments": {"expression": "3 + 4"}}}
            ],
        }


def create(h, conversation, body, who="a"):
    return h["client"].post(
        f"/v1/conversations/{conversation}/agent-runs", headers=h[who], json=body
    )


def test_tool_is_only_executed_after_exact_owned_approval_and_receipt_replays(harness):
    h = harness
    conversation, _ = make_conversation(h)
    provider = CalculatorAgent(h)
    h["app"].state.agents.provider = provider
    body = {
        "run_id": str(uuid4()),
        "task": "Use the calculator for 3 + 4.",
        "protocol_version": "ada-agent-v1",
        "allowed_tools": ["calculator"],
    }
    result = create(h, conversation, body)
    assert result.status_code == 201, result.text
    run = result.json()
    assert run["status"] == "pending_approval" and run["response"] is None
    step = run["steps"][0]
    assert step["tool"] == "calculator" and step["receipt"] is None
    assert create(h, conversation, body).json() == run and len(provider.calls) == 1
    path = f"/v1/agent-runs/{run['id']}/steps/{step['id']}/approve"
    approval = {
        "approval_id": str(uuid4()),
        "preview_hash": step["preview_hash"],
        "argument_hash": step["argument_hash"],
        "tool_version": step["tool_version"],
    }
    assert h["client"].post(path, headers=h["b"], json=approval).status_code == 404
    assert (
        h["client"]
        .post(path, headers=h["a"], json=approval | {"preview_hash": "0" * 64})
        .status_code
        == 409
    )
    approved = h["client"].post(path, headers=h["a"], json=approval)
    assert approved.status_code == 201, approved.text
    receipt = approved.json()
    assert receipt["outcome"] == "completed" and receipt["result"]["value"] == "7"
    assert receipt["origin"] == "tool_result" and receipt["trust_class"] == "untrusted_tool_output"
    repeated = h["client"].post(path, headers=h["a"], json=approval)
    assert repeated.status_code == 200 and repeated.json() == receipt
    assert len(provider.calls) == 2
    finished = h["client"].get(f"/v1/agent-runs/{run['id']}", headers=h["a"]).json()
    assert finished["status"] == "completed" and finished["steps"][0]["receipt"] == receipt
    assert create(h, conversation, body | {"task": "Changed task"}).status_code == 409
    assert h["client"].get(f"/v1/agent-runs/{run['id']}", headers=h["b"]).status_code == 404
    assert h["client"].get(f"/v1/scopes/{run['scope_id']}/claims", headers=h["a"]).json() == []


def test_expired_model_lease_cannot_publish_a_late_tool_proposal(harness):
    h = harness
    conversation, _ = make_conversation(h)
    service = h["app"].state.agents
    at = [1_800_000_000_000]
    service.clock = lambda: at[0]
    original = CalculatorAgent(h)

    class LateAgent:
        id, model = original.id, original.model

        def complete(self, messages, tools):
            at[0] += 91_000
            return original.complete(messages, tools)

    service.provider = LateAgent()
    result = create(
        h,
        conversation,
        {
            "run_id": str(uuid4()),
            "task": "Calculate 3+4.",
            "protocol_version": "ada-agent-v1",
            "allowed_tools": ["calculator"],
        },
    )
    assert result.status_code == 201
    assert result.json()["status"] == "unknown"
    assert result.json()["error_code"] == "agent_interrupted"
    assert result.json()["steps"][0]["tool"] is None


@pytest.mark.parametrize(
    "name,args",
    [
        ("shell", {"command": "read a secret"}),
        ("calculator", {"expression": "3+4", "owner": "foreign"}),
        ("memory_lookup", {"query": "private", "scope_id": str(uuid4())}),
        ("calculator", {"expression": True}),
    ],
)
def test_injected_or_malformed_commands_are_terminal_without_execution(harness, name, args):
    h = harness
    conversation, _ = make_conversation(h)
    service = h["app"].state.agents

    class InjectedAgent:
        id, model = "fixture", "synthetic-agent-v1"

        def complete(self, messages, tools):
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": name, "arguments": args}}],
            }

    service.provider = InjectedAgent()
    dispatched = []
    service.dispatch = lambda *args: dispatched.append(args)
    response = create(
        h,
        conversation,
        {
            "run_id": str(uuid4()),
            "task": "Synthetic instruction injection.",
            "protocol_version": "ada-agent-v1",
            "allowed_tools": ["calculator", "memory_lookup"],
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "failed" and response.json()["response"] is None
    assert not dispatched


def prepared(h):
    conversation, _ = make_conversation(h)
    provider = CalculatorAgent(h)
    h["app"].state.agents.provider = provider
    body = {
        "run_id": str(uuid4()),
        "task": "Calculate 3+4.",
        "protocol_version": "ada-agent-v1",
        "allowed_tools": ["calculator"],
    }
    run = create(h, conversation, body).json()
    step = run["steps"][0]
    approval = {
        "approval_id": str(uuid4()),
        "preview_hash": step["preview_hash"],
        "argument_hash": step["argument_hash"],
        "tool_version": step["tool_version"],
    }
    path = f"/v1/agent-runs/{run['id']}/steps/{step['id']}"
    return run, approval, path, provider


def test_expired_approval_stops_run_without_executing(harness):
    h = harness
    run, approval, path, provider = prepared(h)
    h["app"].state.agents.clock = lambda: run["steps"][0]["expires_at"] + 1
    response = h["client"].post(path + "/approve", headers=h["a"], json=approval)
    assert response.status_code == 409
    finished = h["client"].get(f"/v1/agent-runs/{run['id']}", headers=h["a"]).json()
    assert finished["status"] == "failed" and finished["error_code"] == "agent_approval_expired"
    assert finished["steps"][0]["receipt"] is None and len(provider.calls) == 1


def test_deny_does_not_need_model_capacity_and_cannot_be_reapproved(harness):
    h = harness
    run, approval, path, provider = prepared(h)
    capacity = h["app"].state.chat.capacity
    assert capacity.acquire(False) and capacity.acquire(False)
    try:
        response = h["client"].post(path + "/revoke", headers=h["a"], json=approval)
        assert response.status_code == 201 and response.json()["outcome"] == "revoked"
        assert (
            h["client"].post(path + "/revoke", headers=h["a"], json=approval).json()
            == response.json()
        )
    finally:
        capacity.release()
        capacity.release()
    assert h["client"].post(path + "/approve", headers=h["a"], json=approval).status_code == 409
    assert len(provider.calls) == 1
