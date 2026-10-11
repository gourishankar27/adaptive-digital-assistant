import json
import logging

import httpx
import pytest

from ada.config import Settings
from ada.consolidation_provider import OllamaConsolidator
from ada.providers import ProviderError


def test_structured_native_adapter_bounds_no_tools_thinking_and_private_logs(caplog):
    caplog.set_level(logging.DEBUG)
    observed = []

    def transport(request):
        value = json.loads(request.content)
        observed.append(value)
        return httpx.Response(
            200,
            json={
                "model": "synthetic",
                "done": True,
                "message": {"role": "assistant", "content": '{"sections":[]}'},
            },
        )

    p = OllamaConsolidator(
        Settings(
            ollama_url="http://synthetic-name:synthetic-password@localhost",
            ollama_model="synthetic",
        ),
        httpx.MockTransport(transport),
    )
    result = p.complete(
        [{"role": "user", "content": "synthetic-private-excerpt"}], {"type": "object"}
    )
    assert result.model == "synthetic" and observed[0]["format"] == {"type": "object"}
    assert (
        observed[0]["think"] is False
        and observed[0]["stream"] is False
        and "tools" not in observed[0]
    )
    assert observed[0]["options"] == {"temperature": 0, "num_ctx": 8192, "num_predict": 2048}
    assert not any(
        x in caplog.text
        for x in ("synthetic-name", "synthetic-password", "synthetic-private-excerpt")
    )


@pytest.mark.parametrize(
    "kind",
    [
        "redirect",
        "timeout",
        "missing_model",
        "model_change",
        "thinking",
        "tool",
        "oversize",
        "duplicate",
        "nonfinite",
        "not_done",
    ],
)
def test_native_adapter_fails_closed_sanitized(kind):
    def transport(request):
        if kind == "timeout":
            raise httpx.ReadTimeout("synthetic-private-timeout")
        if kind == "redirect":
            return httpx.Response(307, headers={"Location": "http://foreign.invalid"})
        if kind == "missing_model":
            return httpx.Response(404)
        if kind == "oversize":
            return httpx.Response(200, content=b"x" * 65537)
        if kind == "duplicate":
            return httpx.Response(200, content=b'{"model":"synthetic","model":"synthetic"}')
        if kind == "nonfinite":
            return httpx.Response(200, content=b'{"model":NaN}')
        message = {"role": "assistant", "content": "{}"}
        if kind == "thinking":
            message["thinking"] = "synthetic-private-reasoning"
        if kind == "tool":
            message["tool_calls"] = [{}]
        return httpx.Response(
            200,
            json={
                "done": kind != "not_done",
                "model": "different" if kind == "model_change" else "synthetic",
                "message": message,
            },
        )

    p = OllamaConsolidator(Settings(ollama_model="synthetic"), httpx.MockTransport(transport))
    with pytest.raises(ProviderError) as error:
        p.complete([], {})
    assert str(error.value) in ("provider_timeout", "model_not_found", "provider_unavailable")
