"""Bounded native NDJSON streaming; disconnect observers never close this adapter."""

import json
import threading
import time

import httpx

from ada.providers import Completion, OllamaProvider, ProviderError

MAX_TEXT_BYTES = 65536
MAX_FRAME_BYTES = 16384


class StreamingOllamaProvider(OllamaProvider):
    def stream(self, messages, cancel):
        end = threading.Event()
        response = None
        started = time.monotonic()

        def shutdown():
            while not end.wait(0.05):
                if cancel.is_set() or time.monotonic() - started > self.settings.timeout_seconds:
                    if response is not None:
                        try:
                            response.close()
                        except Exception:
                            pass
                    return

        watcher = threading.Thread(target=shutdown, name="ada-provider-stop", daemon=True)
        watcher.start()
        try:
            with httpx.Client(
                base_url=self.settings.ollama_url,
                timeout=httpx.Timeout(self.settings.timeout_seconds, connect=5),
                transport=self.transport,
                trust_env=False,
            ) as client:
                with client.stream(
                    "POST",
                    "/api/chat",
                    headers={"Accept-Encoding": "identity"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                        "think": False,
                        "keep_alive": "5m",
                        "options": {
                            "num_ctx": self.settings.context_tokens,
                            "num_predict": self.settings.output_tokens,
                        },
                    },
                ) as response:
                    if response.status_code == 404:
                        raise ProviderError("model_not_found")
                    response.raise_for_status()
                    if response.headers.get("Content-Encoding", "identity") != "identity":
                        raise ProviderError("invalid_response")
                    text = ""
                    size = 0
                    for line in bounded_frames(response):
                        if cancel.is_set():
                            return
                        if time.monotonic() - started > self.settings.timeout_seconds:
                            raise ProviderError("provider_timeout")
                        data = json.loads(line.decode("utf-8"))
                        if (
                            not isinstance(data, dict)
                            or data.get("error")
                            or type(data.get("done")) is not bool
                        ):
                            raise ProviderError("invalid_response")
                        message = data.get("message")
                        if not isinstance(message, dict) or message.get("tool_calls"):
                            raise ProviderError("invalid_response")
                        delta = message.get("content")
                        if not isinstance(delta, str) or "\x00" in delta:
                            raise ProviderError("invalid_response")
                        size += len(delta.encode("utf-8"))
                        if size > MAX_TEXT_BYTES:
                            raise ProviderError("response_too_large")
                        text += delta
                        if delta:
                            yield delta
                        if data["done"]:
                            if not text.strip():
                                raise ProviderError("invalid_response")
                            counts = [data.get(key) for key in ("prompt_eval_count", "eval_count")]
                            if any(
                                value is not None
                                and (type(value) is not int or not 0 <= value <= 2**63 - 1)
                                for value in counts
                            ):
                                raise ProviderError("invalid_response")
                            model = data.get("model", self.model)
                            if not isinstance(model, str) or not 1 <= len(model) <= 120:
                                raise ProviderError("invalid_response")
                            yield Completion(text.strip(), model, *counts)
                            return
                    # A terminal frame is mandatory, even if a peer closed after text.
                    raise ProviderError("invalid_response")
        except httpx.TimeoutException:
            if not cancel.is_set():
                raise ProviderError("provider_timeout") from None
        except (httpx.HTTPError, ValueError, KeyError, TypeError, UnicodeError):
            if not cancel.is_set():
                raise ProviderError("provider_unavailable") from None
        finally:
            end.set()
            watcher.join(1)


def bounded_frames(response):
    pending = b""
    for block in response.iter_bytes():
        if len(block) > 65536:
            raise ProviderError("invalid_response")
        pending += block
        while b"\n" in pending:
            line, pending = pending.split(b"\n", 1)
            if len(line) > MAX_FRAME_BYTES:
                raise ProviderError("invalid_response")
            if line.strip():
                yield line
        if len(pending) > MAX_FRAME_BYTES:
            raise ProviderError("invalid_response")
    if pending.strip():
        yield pending
