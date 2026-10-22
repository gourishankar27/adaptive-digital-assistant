"""Digest-bound local-only structured streaming. Cancellation is measured, not assumed."""

import ipaddress
import json
import threading
import time
from types import SimpleNamespace
from urllib.parse import urlsplit

import httpx

from ada.agent_provider import _agent_logging, strict_object
from ada.consolidation import MAX_OUTPUT_BYTES
from ada.proposals import fingerprint
from ada.providers import Completion, ProviderError
from ada.stream_provider import bounded_frames


class OllamaReflectionProvider:
    version = "idle-structured-stream-v1"

    def __init__(self, settings, transport=None):
        parsed = urlsplit(settings.ollama_url)
        try:
            local = ipaddress.ip_address(parsed.hostname).is_loopback
        except ValueError:
            local = False
        if (
            not local
            or parsed.scheme not in ("http", "https")
            or parsed.username
            or parsed.password
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
            or not settings.reflection_model_digest
        ):
            raise ValueError("Idle inference requires a digest-bound literal loopback provider")
        self.settings, self.transport, self.model = settings, transport, settings.ollama_model
        self.key = fingerprint(
            {
                "version": self.version,
                "model": self.model,
                "digest": settings.reflection_model_digest,
            }
        )

    def _verify(self, client, cancel, until):
        if cancel.is_set() or time.monotonic() >= until:
            raise ProviderError("reflection_cancelled")
        body = bytearray()
        with client.stream("GET", "/api/tags", headers={"Accept-Encoding": "identity"}) as response:
            response.raise_for_status()
            if response.headers.get("Content-Encoding", "identity") != "identity":
                raise ProviderError("reflection_model_changed")
            for block in response.iter_bytes():
                if cancel.is_set() or time.monotonic() >= until:
                    raise ProviderError("reflection_cancelled")
                body.extend(block)
                if len(body) > 65536:
                    raise ProviderError("reflection_model_changed")
        metadata = json.loads(body)
        models = metadata.get("models")
        if (
            not isinstance(models, list)
            or len(models) > 100
            or not any(
                isinstance(row, dict)
                and (row.get("name") == self.model or row.get("model") == self.model)
                and row.get("digest") == self.settings.reflection_model_digest
                for row in models
            )
        ):
            raise ProviderError("reflection_model_changed")

    def complete(self, messages, schema, cancel, deadline):
        started = time.monotonic()
        done = threading.Event()
        response = None
        previous = getattr(_agent_logging, "active", False)
        _agent_logging.active = True

        def stop():
            while not done.wait(0.025):
                if cancel.is_set() or time.monotonic() - started >= deadline:
                    cancel.set()
                    if response is not None:
                        try:
                            response.close()
                        except Exception:
                            pass
                    return

        watcher = threading.Thread(target=stop, name="ada-idle-provider-stop", daemon=True)
        watcher.start()
        try:
            with httpx.Client(
                base_url=self.settings.ollama_url,
                timeout=httpx.Timeout(min(deadline, 2), connect=1, read=1),
                follow_redirects=False,
                trust_env=False,
                transport=self.transport,
            ) as client:
                self._verify(client, cancel, started + deadline)
                if cancel.is_set():
                    raise ProviderError("reflection_cancelled")
                with client.stream(
                    "POST",
                    "/api/chat",
                    headers={"Accept-Encoding": "identity"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "format": schema,
                        "stream": True,
                        "think": False,
                        "keep_alive": "5m",
                        "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 1024},
                    },
                ) as response:
                    response.raise_for_status()
                    if response.headers.get("Content-Encoding", "identity") != "identity":
                        raise ProviderError("invalid_response")
                    content = ""
                    for frame in bounded_frames(response):
                        if cancel.is_set() or time.monotonic() - started >= deadline:
                            raise ProviderError("reflection_cancelled")
                        value = json.loads(
                            frame,
                            object_pairs_hook=strict_object,
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")),
                        )
                        message = value.get("message")
                        if (
                            value.get("error")
                            or type(value.get("done")) is not bool
                            or value.get("model") != self.model
                            or not isinstance(message, dict)
                            or message.get("role") != "assistant"
                            or message.get("tool_calls")
                            or message.get("thinking")
                            or not isinstance(message.get("content"), str)
                            or "\x00" in message["content"]
                        ):
                            raise ProviderError("invalid_response")
                        content += message["content"]
                        if len(content.encode("utf-8")) > MAX_OUTPUT_BYTES:
                            raise ProviderError("invalid_response")
                        if value["done"]:
                            if not content.strip():
                                raise ProviderError("invalid_response")
                            return Completion(content, self.model)
                    raise ProviderError("invalid_response")
        except httpx.TimeoutException:
            raise ProviderError(
                "reflection_cancelled" if cancel.is_set() else "provider_timeout"
            ) from None
        except (httpx.HTTPError, ValueError, UnicodeError, TypeError, KeyError):
            raise ProviderError(
                "reflection_cancelled" if cancel.is_set() else "provider_unavailable"
            ) from None
        finally:
            done.set()
            watcher.join(1)
            _agent_logging.active = previous

    def generate(self, run, consolidation, cancel, deadline):
        job = SimpleNamespace(
            kind="episode", model=self.model, input={"sources": run.pins}, snapshot=run.snapshot
        )
        summary = consolidation._generate(
            job,
            completion_fn=lambda messages, schema: self.complete(
                messages, schema, cancel, deadline
            ),
        )
        return {"summary": summary}
