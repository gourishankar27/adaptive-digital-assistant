import json

import httpx
import pytest

from ada.config import Settings
from ada.embeddings import EmbeddingError, OllamaEmbeddingProvider, unit_vector


def settings():
    return Settings(embedding_digest="a" * 64)


def test_embedding_transport_pins_digest_and_never_truncates():
    calls = []

    def respond(request):
        calls.append(request)
        if request.url.path == "/api/tags":
            return httpx.Response(
                200, json={"models": [{"name": "embeddinggemma:300m", "digest": "a" * 64}]}
            )
        body = json.loads(request.content)
        assert body["truncate"] is False and body["keep_alive"] == "0"
        assert body["input"] == ["task: search result | query: synthetic question"]
        return httpx.Response(
            200, json={"model": body["model"], "embeddings": [[1.0] + [0.0] * 767]}
        )

    p = OllamaEmbeddingProvider(settings(), httpx.MockTransport(respond))
    assert p.embed(["synthetic question"], query=True)[0][0] == 1
    assert [r.url.path for r in calls] == ["/api/tags", "/api/embed", "/api/tags"]


@pytest.mark.parametrize("vector", [[0.0] * 768, [1.0], [float("nan")] * 768, [True] * 768])
def test_invalid_vectors_fail_closed(vector):
    with pytest.raises(EmbeddingError):
        unit_vector(vector, 768)


def test_digest_change_and_timeout_are_sanitized():
    p = OllamaEmbeddingProvider(
        settings(), httpx.MockTransport(lambda _: httpx.Response(200, json={"models": []}))
    )
    with pytest.raises(EmbeddingError, match="embedding_model_changed"):
        p.embed(["synthetic"])

    def timeout(request):
        raise httpx.ReadTimeout("private body", request=request)

    p = OllamaEmbeddingProvider(settings(), httpx.MockTransport(timeout))
    with pytest.raises(EmbeddingError, match="embedding_timeout"):
        p.embed(["synthetic"])


def test_work_bounds_reject_before_network():
    def unexpected(_):
        pytest.fail("network must not run for oversized input")

    p = OllamaEmbeddingProvider(settings(), httpx.MockTransport(unexpected))
    for texts in (["x"] * 9, ["x" * 8000], []):
        with pytest.raises(EmbeddingError, match="embedding_input_bound"):
            p.embed(texts)


def test_model_changes_during_call_and_oversized_response_fail_closed():
    tags = 0

    def respond(request):
        nonlocal tags
        if request.url.path == "/api/tags":
            tags += 1
            return httpx.Response(
                200,
                json={
                    "models": [
                        {"name": "embeddinggemma:300m", "digest": ("a" if tags == 1 else "b") * 64}
                    ]
                },
            )
        return httpx.Response(
            200, json={"model": "embeddinggemma:300m", "embeddings": [[1.0] + [0.0] * 767]}
        )

    with pytest.raises(EmbeddingError, match="embedding_model_changed"):
        OllamaEmbeddingProvider(settings(), httpx.MockTransport(respond)).embed(["synthetic"])
    with pytest.raises(EmbeddingError, match="embedding_response_bound"):
        OllamaEmbeddingProvider(
            settings(), httpx.MockTransport(lambda _: httpx.Response(200, content=b"x" * 524289))
        ).embed(["synthetic"])
