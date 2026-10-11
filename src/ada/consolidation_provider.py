"""Bounded structured summarization; no new provider dependencies or chat prompt."""

import json
import time

import httpx

from ada.agent_provider import _agent_logging, strict_object
from ada.consolidation import MAX_OUTPUT_BYTES
from ada.providers import Completion, ProviderError


class OllamaConsolidator:
    id = "ollama"

    def __init__(self, settings, transport=None):
        self.settings, self.transport, self.model = settings, transport, settings.ollama_model

    def complete(self, messages, schema):
        previous = getattr(_agent_logging, "active", False)
        _agent_logging.active = True
        try:
            return self._complete(messages, schema)
        finally:
            _agent_logging.active = previous

    def _complete(self, messages, schema):
        started = time.monotonic()
        timeout = min(60, self.settings.timeout_seconds)
        try:
            with httpx.Client(
                base_url=self.settings.ollama_url,
                timeout=httpx.Timeout(timeout, connect=min(timeout, 5)),
                transport=self.transport,
                trust_env=False,
                follow_redirects=False,
            ) as client:
                with client.stream(
                    "POST",
                    "/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "format": schema,
                        "stream": False,
                        "think": False,
                        "keep_alive": "0",
                        "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 2048},
                    },
                ) as response:
                    if response.status_code == 404:
                        raise ProviderError("model_not_found")
                    response.raise_for_status()
                    body = bytearray()
                    for chunk in response.iter_bytes(chunk_size=4096):
                        body.extend(chunk)
                        if len(body) > 65536 or time.monotonic() - started > timeout:
                            raise ProviderError("provider_timeout")
                data = json.loads(
                    body,
                    object_pairs_hook=strict_object,
                    parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")),
                )
            message = data["message"]
            value = message["content"]
            if (
                data.get("done") is not True
                or data.get("model") != self.model
                or message.get("tool_calls")
                or message.get("thinking")
                or message.get("role") != "assistant"
                or not isinstance(value, str)
                or not value.strip()
                or len(value.encode("utf-8")) > MAX_OUTPUT_BYTES
            ):
                raise ProviderError("provider_unavailable")
            return Completion(value, self.model)
        except httpx.TimeoutException:
            raise ProviderError("provider_timeout") from None
        except (httpx.HTTPError, ValueError, TypeError, KeyError, UnicodeError):
            raise ProviderError("provider_unavailable") from None
