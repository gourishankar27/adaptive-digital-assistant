from dataclasses import dataclass
from typing import Protocol

import httpx

from ada.config import Settings


class ProviderError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Completion:
    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ChatProvider(Protocol):
    id: str
    model: str

    def complete(self, messages: list[dict]) -> Completion: ...


class FakeProvider:
    id = "fake"
    model = "deterministic-test-v1"

    def complete(self, messages: list[dict]) -> Completion:
        return Completion("[FAKE provider] Received: " + messages[-1]["content"], self.model)

    def stream(self, messages, cancel):
        result = self.complete(messages)
        for index in range(0, len(result.text), 16):
            if cancel.is_set():
                return
            yield result.text[index : index + 16]
        yield result


class OllamaProvider:
    id = "ollama"

    def __init__(self, settings: Settings, transport=None):
        self.settings = settings
        self.model = settings.ollama_model
        self.transport = transport

    def complete(self, messages: list[dict]) -> Completion:
        try:
            with httpx.Client(
                base_url=self.settings.ollama_url,
                timeout=httpx.Timeout(self.settings.timeout_seconds, connect=5),
                transport=self.transport,
                trust_env=False,
            ) as client:
                response = client.post(
                    "/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "think": False,
                        "keep_alive": "5m",
                        "options": {
                            "num_ctx": self.settings.context_tokens,
                            "num_predict": self.settings.output_tokens,
                        },
                    },
                )
                if response.status_code == 404:
                    raise ProviderError("model_not_found")
                response.raise_for_status()
                data = response.json()
                message = data["message"]
                content = message["content"]
                if (
                    data.get("done") is not True
                    or message.get("tool_calls")
                    or not isinstance(content, str)
                    or not content.strip()
                    or "\x00" in content
                ):
                    raise ProviderError("invalid_response")
                try:
                    content.encode("utf-8")
                except UnicodeError:
                    raise ProviderError("invalid_response") from None
                return Completion(
                    content.strip(),
                    str(data.get("model", self.model)),
                    data.get("prompt_eval_count"),
                    data.get("eval_count"),
                )
        except httpx.TimeoutException as exc:
            raise ProviderError("provider_timeout") from exc
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            # Never return raw provider bodies, credentials, or internal URLs to clients.
            raise ProviderError("provider_unavailable") from exc
