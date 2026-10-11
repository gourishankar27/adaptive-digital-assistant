from uuid import uuid4

import httpx
import pytest
from conftest import make_conversation
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from test_agent_tools import Commands, approve, start
from test_agents import create, prepared
from test_memory import note
from test_proposals import pin

from ada.agent_models import AgentApproval, AgentReceipt
from ada.agent_provider import OllamaAgentProvider
from ada.config import Settings
from ada.providers import ProviderError


def slots_released(service):
    assert service.capacity.acquire(blocking=False)
    assert service.capacity.acquire(blocking=False)
    assert not service.capacity.acquire(blocking=False)
    service.capacity.release()
    service.capacity.release()


@pytest.mark.parametrize(
    "failure",
    [
        RuntimeError("synthetic-private-crash"),
        ProviderError("synthetic-private-code"),
        ProviderError("provider_timeout"),
    ],
)
def test_provider_failure_is_terminal_sanitized_and_releases_admission(harness, failure):
    h = harness
    conversation, _ = make_conversation(h)
    service = h["app"].state.agents

    class Broken:
        id, model = "fixture", "synthetic-broken"

        def complete(self, *_):
            assert h["sessions"].kw["bind"].pool.checkedout() == 0
            raise failure

    service.provider = Broken()
    body = {
        "run_id": str(uuid4()),
        "task": "Synthetic failure test.",
        "protocol_version": "ada-agent-v1",
        "allowed_tools": ["calculator"],
    }
    response = create(h, conversation, body)
    assert response.status_code == 201
    assert response.json()["status"] == "failed" and response.json()["response"] is None
    assert "synthetic-private" not in response.text and not response.json()["steps"][0]["receipt"]
    assert create(h, conversation, body).json() == response.json()
    slots_released(service)


def test_http_provider_timeout_and_oversized_response_are_sanitized():
    settings = Settings(provider="ollama")

    def timeout(request):
        raise httpx.ReadTimeout("synthetic-private-url", request=request)

    for handler, code in (
        (timeout, "provider_timeout"),
        (lambda _: httpx.Response(200, content=b"x" * 65537), "agent_response_bound"),
    ):
        with pytest.raises(ProviderError) as failure:
            OllamaAgentProvider(settings, httpx.MockTransport(handler)).complete([], [])
        assert failure.value.code == code


def test_capacity_refusal_does_not_reserve_a_run_or_leak_slots(harness):
    h = harness
    service = h["app"].state.agents
    conversation, _ = make_conversation(h)
    service.capacity.acquire()
    service.capacity.acquire()
    body = {
        "run_id": str(uuid4()),
        "task": "Synthetic bound.",
        "protocol_version": "ada-agent-v1",
        "allowed_tools": ["calculator"],
    }
    try:
        assert create(h, conversation, body).status_code == 503
        assert (
            h["client"].get("/v1/agent-runs/" + body["run_id"], headers=h["a"]).status_code == 404
        )
    finally:
        service.capacity.release()
        service.capacity.release()
    slots_released(service)


def test_failed_receipt_transaction_stays_unconfirmed_and_recovery_never_reexecutes(
    harness, monkeypatch
):
    h = harness
    service = h["app"].state.agents
    at = [1_800_000_000_000]
    service.clock = lambda: at[0]
    run, approval, route, provider = prepared(h)
    dispatched = []
    original_dispatch = service.dispatch
    original_receipt = service._receipt

    def counted(*args):
        dispatched.append(1)
        return original_dispatch(*args)

    def broken(*args, **kwargs):
        original_receipt(*args, **kwargs)
        raise SQLAlchemyError("synthetic-private-db")

    service.dispatch = counted
    monkeypatch.setattr(service, "_receipt", broken)
    assert h["client"].post(route + "/approve", headers=h["a"], json=approval).status_code == 503
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(AgentReceipt)) == 0
        assert db.get(AgentApproval, (h["a_id"], approval["approval_id"])).result is None
    assert len(dispatched) == 1 and len(provider.calls) == 1
    slots_released(service)
    monkeypatch.setattr(service, "_receipt", original_receipt)
    at[0] += 91_000
    recovery = h["client"].post(
        f"/v1/agent-runs/{run['id']}/recover",
        headers=h["a"],
        json={"operation_id": str(uuid4()), "generation": run["generation"] + 1},
    )
    assert recovery.status_code == 201 and recovery.json()["outcome"] == "unknown"
    assert (
        h["client"].post(route + "/approve", headers=h["a"], json=approval).json()
        == recovery.json()
    )
    assert len(dispatched) == 1 and len(provider.calls) == 1


def test_fifth_step_and_elapsed_limits_stop_without_manufactured_answer(harness):
    h = harness
    conversation, _ = make_conversation(h)
    selected = (
        h["client"].get(f"/v1/conversations/{conversation}", headers=h["a"]).json()["scope_id"]
    )
    source = note(h, selected, "Synthetic bounded lookup.")
    commands = [
        ("calculator", {"expression": "1+1"}),
        ("memory_lookup", {"query": "synthetic"}),
        ("calculator", {"expression": "2+2"}),
        ("memory_lookup", {"query": "bounded"}),
        ("source_lookup", pin(source)),
    ]
    provider = Commands(h, commands)
    run = start(h, conversation, provider, ["calculator", "memory_lookup", "source_lookup"])
    for _ in range(5):
        assert run["status"] == "pending_approval", run["error_code"]
        receipt, run = approve(h, run)
        assert receipt["outcome"] == "completed"
    assert (
        run["status"] == "failed"
        and run["error_code"] == "agent_step_bound"
        and run["response"] is None
    )
    assert len(provider.calls) == 5
    slots_released(h["app"].state.agents)


def test_tool_output_size_fails_honestly(harness):
    h = harness
    service = h["app"].state.agents
    run, approval, route, provider = prepared(h)
    service.dispatch = lambda *_: {"value": "x" * 5000}
    response = h["client"].post(route + "/approve", headers=h["a"], json=approval)
    assert (
        response.status_code == 201
        and response.json()["outcome"] == "failed"
        and response.json()["result"] is None
    )
    assert len(provider.calls) == 1
    slots_released(service)


def test_tool_elapsed_timeout_fails_honestly_without_next_inference(harness, monkeypatch):
    from types import SimpleNamespace

    import ada.agents as module

    h = harness
    service = h["app"].state.agents
    _, approval, route, provider = prepared(h)
    ticks = iter([0, 6])
    monkeypatch.setattr(module, "time", SimpleNamespace(monotonic=lambda: next(ticks)))
    response = h["client"].post(route + "/approve", headers=h["a"], json=approval)
    assert response.status_code == 201
    assert (
        response.json()["outcome"] == "failed"
        and response.json()["error_code"] == "agent_tool_timeout"
    )
    assert len(provider.calls) == 1
    slots_released(service)


def test_elapsed_run_and_changed_registry_cannot_authorize_execution(harness, monkeypatch):
    from dataclasses import replace

    from ada.tools import REGISTRY

    h = harness
    service = h["app"].state.agents
    at = [1_800_000_000_000]
    service.clock = lambda: at[0]
    run, approval, route, provider = prepared(h)
    at[0] += 300_001
    result = h["client"].post(route + "/approve", headers=h["a"], json=approval)
    assert result.status_code == 409 and result.json()["detail"] == "agent_elapsed_bound"
    assert (
        h["client"].get(f"/v1/agent-runs/{run['id']}", headers=h["a"]).json()["status"] == "failed"
    )
    assert len(provider.calls) == 1
    run, approval, route, provider = prepared(h)
    monkeypatch.setitem(
        REGISTRY,
        "calculator",
        replace(REGISTRY["calculator"], version="changed-unreleased-version"),
    )
    result = h["client"].post(route + "/approve", headers=h["a"], json=approval)
    assert result.status_code == 409 and result.json()["detail"] == "agent_registry_changed"
    assert len(provider.calls) == 1
    slots_released(service)
