import json

import httpx
import pytest

from ada.config import Settings
from ada.providers import ProviderError


def test_native_tool_protocol_is_separate_and_bounded():
    from ada.agent_provider import OllamaAgentProvider
    from ada.tools import REGISTRY

    settings = Settings(provider="ollama")
    captured = []

    def handler(request):
        captured.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "done": True,
                "model": settings.ollama_model,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {"function": {"name": "calculator", "arguments": {"expression": "2+3"}}}
                    ],
                },
            },
        )

    adapter = OllamaAgentProvider(settings, httpx.MockTransport(handler))
    answer = adapter.complete(
        [{"role": "user", "content": "Calculate 2+3."}], [REGISTRY["calculator"].native()]
    )
    assert answer["tool_calls"][0]["function"]["name"] == "calculator"
    assert captured[0]["stream"] is False and captured[0]["think"] is False
    assert captured[0]["tools"][0]["type"] == "function"
    bad = OllamaAgentProvider(
        settings,
        httpx.MockTransport(
            lambda _: httpx.Response(
                200, content=b'{"done":true,"done":false,"message":{"content":"private"}}'
            )
        ),
    )
    with pytest.raises(ProviderError):
        bad.complete([], [])


def test_agent_provider_does_not_log_private_endpoint_or_body(caplog):
    from ada.agent_provider import OllamaAgentProvider

    settings = Settings(
        provider="ollama", ollama_url="http://synthetic-user:synthetic-password@localhost:11434"
    )
    with caplog.at_level("DEBUG"):
        provider = OllamaAgentProvider(
            settings,
            httpx.MockTransport(
                lambda _: httpx.Response(
                    200,
                    json={
                        "done": True,
                        "model": settings.ollama_model,
                        "message": {"role": "assistant", "content": "synthetic-private-answer"},
                    },
                )
            ),
        )
        provider.complete([{"role": "user", "content": "synthetic-private-task"}], [])
    assert "synthetic-" not in caplog.text


@pytest.mark.parametrize(
    "message",
    [
        {"role": "tool", "content": "wrong role"},
        {"role": "assistant", "content": "answer", "thinking": "hidden"},
        {"role": "assistant", "content": ""},
        {"role": "assistant", "content": "😀" * 2000},
        {
            "role": "assistant",
            "content": "answer",
            "tool_calls": [{"function": {"name": "calculator", "arguments": {}}}],
        },
        {
            "role": "assistant",
            "tool_calls": [{"function": {"name": "calculator", "arguments": "{}"}}],
        },
    ],
)
def test_native_adapter_rejects_ambiguous_unbounded_replies(message):
    from ada.agent_provider import validate_message

    with pytest.raises((ProviderError, ValueError)):
        validate_message(message)
