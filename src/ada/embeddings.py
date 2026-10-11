"""Bounded server-only embeddings. A vector never establishes factual authority."""

import json
import math
import time
from typing import Protocol

import httpx

MAX_BATCH = 8
MAX_INPUT_BYTES = 6000
MAX_RESPONSE_BYTES = 512 * 1024
INDEX_VERSION = "embeddinggemma-search-v1"
RANKING_VERSION = "lexical-first-rrf60-v1"


class EmbeddingError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str], *, query: bool = False) -> list[list[float]]: ...


def unit_vector(value, dimensions):
    if not isinstance(value, list) or len(value) != dimensions:
        raise EmbeddingError("embedding_dimension_changed")
    if any(type(x) not in (float, int) or abs(x) > 1e20 or not math.isfinite(x) for x in value):
        raise EmbeddingError("embedding_invalid_vector")
    norm = math.sqrt(math.fsum(x * x for x in value))
    if not math.isfinite(norm) or norm < 1e-12:
        raise EmbeddingError("embedding_invalid_vector")
    return [x / norm for x in value]


class OllamaEmbeddingProvider:
    def __init__(self, settings, transport=None):
        self.settings, self.transport = settings, transport

    def _json(self, client, method, path, **kwargs):
        started = time.monotonic()
        with client.stream(method, path, **kwargs) as response:
            response.raise_for_status()
            body = bytearray()
            for part in response.iter_bytes():
                body.extend(part)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise EmbeddingError("embedding_response_bound")
                if time.monotonic() - started > self.settings.embedding_timeout_seconds:
                    raise EmbeddingError("embedding_timeout")
            return json.loads(body)

    def _check_digest(self, client):
        models = self._json(client, "GET", "/api/tags")["models"]
        if not any(
            m.get("name") == self.settings.embedding_model
            and m.get("digest") == self.settings.embedding_digest
            for m in models
        ):
            raise EmbeddingError("embedding_model_changed")

    def embed(self, texts, *, query=False):
        prefix = "task: search result | query: " if query else "title: none | text: "
        if not 1 <= len(texts) <= MAX_BATCH or any(
            not t.strip() or len((prefix + t).encode("utf-8")) > MAX_INPUT_BYTES for t in texts
        ):
            raise EmbeddingError("embedding_input_bound")
        try:
            with httpx.Client(
                base_url=self.settings.ollama_url,
                timeout=httpx.Timeout(self.settings.embedding_timeout_seconds, connect=2),
                transport=self.transport,
                trust_env=False,
                follow_redirects=False,
            ) as client:
                # Tags are mutable; validate immediately before AND after inference.
                self._check_digest(client)
                data = self._json(
                    client,
                    "POST",
                    "/api/embed",
                    json={
                        "model": self.settings.embedding_model,
                        "input": [prefix + t for t in texts],
                        "truncate": False,
                        "keep_alive": "0",
                        "dimensions": self.settings.embedding_dimensions,
                    },
                )
                self._check_digest(client)
                if data.get("model") != self.settings.embedding_model:
                    raise EmbeddingError("embedding_model_changed")
                vectors = data["embeddings"]
                if not isinstance(vectors, list) or len(vectors) != len(texts):
                    raise EmbeddingError("embedding_invalid_response")
                return [unit_vector(v, self.settings.embedding_dimensions) for v in vectors]
        except httpx.TimeoutException:
            raise EmbeddingError("embedding_timeout") from None
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError, OverflowError):
            raise EmbeddingError("embedding_unavailable") from None
