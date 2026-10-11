"""Opt-in local real-model probe, using only disposable synthetic owned evidence."""

import os
import time

import pytest
from conftest import make_conversation
from test_agent_tools import approve, start
from test_memory import add, note
from test_proposals import pin

from ada.agent_provider import OllamaAgentProvider
from ada.config import Settings


@pytest.mark.skipif(
    os.environ.get("ADA_AGENT_OLLAMA_PROBE") != "1",
    reason="opt-in real local read-only agent probe",
)
@pytest.mark.parametrize("tool", ["calculator", "memory_lookup", "source_lookup"])
def test_real_native_tool_flow_has_an_owned_durable_receipt(harness, tool):
    h = harness
    if h["sessions"].kw["bind"].dialect.name != "postgresql":
        pytest.skip("real probe runs once with PostgreSQL")
    conversation, _ = make_conversation(h)
    selected = (
        h["client"].get(f"/v1/conversations/{conversation}", headers=h["a"]).json()["scope_id"]
    )
    source = note(h, selected, "Synthetic Mira prefers tea.")
    assert (
        add(h, selected, source, subject="Mira", predicate="drink", value="tea").status_code == 201
    )
    tasks = {
        "calculator": "Use the calculator to compute (19 + 5) / 3, then report its recorded value. Request the native calculator tool before answering.",
        "memory_lookup": 'Look up the stored preference for Mira drink using memory_lookup query "Mira drink" with limit 1. Report the recorded evidence after the tool executes.',
        "source_lookup": "Use source_lookup with these exact arguments, then report its exact recorded quote: "
        + __import__("json").dumps(pin(source)),
    }
    provider = OllamaAgentProvider(Settings(provider="ollama"))
    at = time.monotonic()
    run = start(h, conversation, provider, [tool], task=tasks[tool])
    assert run["status"] == "pending_approval", run["error_code"]
    assert run["steps"][0]["tool"] == tool and run["steps"][0]["receipt"] is None
    receipt, run = approve(h, run)
    assert receipt["outcome"] == "completed" and receipt["tool"] == tool
    assert h["client"].get(f"/v1/tool-receipts/{receipt['id']}", headers=h["a"]).json() == receipt
    assert h["client"].get(f"/v1/tool-receipts/{receipt['id']}", headers=h["b"]).status_code == 404
    if tool == "calculator":
        assert receipt["result"]["value"] == "8"
    elif tool == "memory_lookup":
        assert receipt["result"]["items"][0]["value"] == "tea"
    else:
        assert receipt["result"]["quote"] == source["content"]
    assert run["status"] == "completed" and run["response"]
    print(
        f"real tool={tool} model={provider.model} elapsed_seconds={time.monotonic() - at:.2f} receipt=completed final=completed"
    )
