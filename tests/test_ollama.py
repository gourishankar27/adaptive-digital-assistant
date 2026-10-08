import json

import httpx
import pytest

from ada.config import Settings
from ada.providers import OllamaProvider, ProviderError


def test_ollama_payload_and_usage():
    def handle(request):
        body = json.loads(request.content)
        assert body["stream"] is False and body["think"] is False
        assert body["model"] == "qwen3.8:27b"
        assert body["options"] == {"num_ctx": 8192, "num_predict": 512}
        assert body["messages"][-1] == {"role": "user", "content": "hello"}
        return httpx.Response(
            200,
            json={
                "message": {"content": "reply"},
                "done": True,
                "prompt_eval_count": 5,
                "eval_count": 2,
            },
        )

    out = OllamaProvider(Settings(), httpx.MockTransport(handle)).complete(
        [{"role": "user", "content": "hello"}]
    )
    assert out.text == "reply" and out.input_tokens == 5


@pytest.mark.parametrize(
    "response,code",
    [
        (httpx.Response(404, json={"error": "secret internals"}), "model_not_found"),
        (httpx.Response(500, text="secret internals"), "provider_unavailable"),
        (httpx.Response(200, json={"message": {"content": ""}, "done": True}), "invalid_response"),
        (
            httpx.Response(200, json={"message": {"content": "partial"}, "done": False}),
            "invalid_response",
        ),
        (
            httpx.Response(
                200, json={"message": {"content": "x", "tool_calls": [{}]}, "done": True}
            ),
            "invalid_response",
        ),
        (httpx.Response(200, text="not JSON"), "provider_unavailable"),
    ],
)
def test_ollama_errors_are_sanitized(response, code):
    provider = OllamaProvider(Settings(), httpx.MockTransport(lambda _: response))
    with pytest.raises(ProviderError) as error:
        provider.complete([])
    assert str(error.value) == code


def test_ollama_timeout():
    def timeout(_):
        raise httpx.ReadTimeout("private internal address")

    with pytest.raises(ProviderError, match="provider_timeout"):
        OllamaProvider(Settings(), httpx.MockTransport(timeout)).complete([])
