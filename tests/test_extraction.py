import json

import httpx
import pytest
from pydantic import ValidationError

from ada.config import Settings
from ada.extraction import MAX_HTTP_BYTES, OllamaExtractor
from ada.proposal_contracts import Candidate
from ada.providers import ProviderError


@pytest.mark.parametrize("mutation", [{"confidence": True}, {"valid_from": 1790812800}])
def test_candidate_rejects_coerced_model_types(mutation):
    candidate = {
        "subject": "Synthetic",
        "predicate": "drink",
        "value": "tea",
        "kind": "preference",
        "support": [
            {
                "source_version_id": "00000000-0000-4000-8000-000000000001",
                "version": 1,
                "content_hash": "a" * 64,
                "span_start": 0,
                "span_end": 3,
            }
        ],
    }
    with pytest.raises(ValidationError):
        Candidate.model_validate(candidate | mutation)


def test_bounded_structured_extractor_does_not_follow_or_supply_tools():
    def handler(request):
        body = json.loads(request.content)
        assert body["format"]["additionalProperties"] is False
        assert body["stream"] is False and body["think"] is False
        assert "tools" not in body and body["options"]["num_predict"] == 2048
        return httpx.Response(
            200,
            json={"done": True, "model": "test-model", "message": {"content": '{"candidates":[]}'}},
        )

    provider = OllamaExtractor(Settings(ollama_model="test-model"), httpx.MockTransport(handler))
    assert provider.complete([{"role": "user", "content": "Synthetic"}]).text == '{"candidates":[]}'


@pytest.mark.parametrize(
    "variant", ["huge", "changed_model", "tools", "unfinished", "missing", "redirect", "timeout"]
)
def test_extractor_failure_is_bounded_and_sanitized(variant):
    def handler(request):
        if variant == "huge":
            return httpx.Response(200, content=b"x" * (MAX_HTTP_BYTES + 1))
        if variant == "redirect":
            return httpx.Response(307, headers={"Location": "https://example.com/private"})
        if variant == "timeout":
            raise httpx.ReadTimeout("private URL/token text")
        data = {"done": True, "model": "test-model", "message": {"content": '{"candidates":[]}'}}
        if variant == "changed_model":
            data["model"] = "different"
        elif variant == "tools":
            data["message"]["tool_calls"] = [{"function": "approve"}]
        elif variant == "unfinished":
            data["done"] = False
        else:
            return httpx.Response(404, text="private source")
        return httpx.Response(200, json=data)

    provider = OllamaExtractor(Settings(ollama_model="test-model"), httpx.MockTransport(handler))
    with pytest.raises(ProviderError) as exc:
        provider.complete([])
    assert exc.value.code in {
        "extraction_response_bound",
        "invalid_extraction_response",
        "model_not_found",
        "provider_unavailable",
        "provider_timeout",
    }
    assert "private" not in str(exc.value)
