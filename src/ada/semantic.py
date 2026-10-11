"""Bounded exact semantic channel; no global vector pool or background inference."""

import hashlib
import json
import math
import time
from dataclasses import dataclass

from pydantic import BaseModel
from sqlalchemy import delete, func, select

from ada.embedding_models import EmbeddingEntry
from ada.embeddings import (
    INDEX_VERSION,
    MAX_BATCH,
    RANKING_VERSION,
    EmbeddingError,
    OllamaEmbeddingProvider,
    unit_vector,
)
from ada.errors import ServiceError
from ada.evidence import content_hash
from ada.memory import Timestamp, owned_scope
from ada.models import Claim, DocumentChunk, Scope, SourceVersion

CORPUS_LIMIT = 256
CORPUS_BYTES = 1024 * 1024


class SemanticDiagnostic(BaseModel):
    state: str = "disabled"
    reason: str = "provider_disabled"
    namespace: str | None = None
    model: str | None = None
    model_digest: str | None = None
    dimensions: int | None = None
    index_version: str = INDEX_VERSION
    ranking_version: str = RANKING_VERSION
    eligible: int = 0
    indexed: int = 0
    query_ms: int = 0
    ranking_ms: int = 0
    index_built_at: Timestamp | None = None
    min_similarity: float | None = None


class RebuildOutput(BaseModel):
    namespace: str
    indexed: int
    reused: int
    corpus_limit: int = CORPUS_LIMIT
    elapsed_ms: int


@dataclass
class PreparedQuery:
    diagnostic: dict
    vector: list | None = None


def claim_text(claim):
    # Canonical identity is deliberately excluded: explicit links can change
    # without rewriting original annotations, evidence or the semantic namespace.
    return f"{claim.subject}\n{claim.predicate}\n{claim.value}\n{claim.quote}"


def _bounded_rows(db, query, remaining=None):
    # Read only sizes first. Four bytes per code point is a conservative UTF-8
    # bound; at most 257 metadata rows are scanned by this work gate.
    remaining = CORPUS_LIMIT if remaining is None else remaining
    sizes = (
        db.execute(query.with_only_columns(func.length(SourceVersion.content)).limit(remaining + 1))
        .scalars()
        .all()
    )
    if len(sizes) > remaining or sum(n * 4 for n in sizes) > CORPUS_BYTES:
        raise EmbeddingError("scope_work_bound")
    return db.execute(query.limit(remaining)).all(), sum(n * 4 for n in sizes)


def _metadata(kind, row):
    item, source = row[:2]
    text = claim_text(item) if kind == "claim" else item.quote
    return {
        "kind": kind,
        "item_id": item.id,
        "claim_id": item.id if kind == "claim" else None,
        "chunk_id": item.id if kind == "document" else None,
        "source_version_id": source.id,
        "source_hash": source.content_hash,
        "text_hash": content_hash(text),
    }, text


class SemanticService:
    def __init__(self, sessions, settings, capacity, provider=None):
        self.sessions, self.settings, self.capacity = sessions, settings, capacity
        self.provider = provider or OllamaEmbeddingProvider(settings)
        self.namespace = hashlib.sha256(
            json.dumps(
                [
                    settings.embedding_model,
                    settings.embedding_digest,
                    settings.embedding_dimensions,
                    INDEX_VERSION,
                ],
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        self.last_state = "configured" if self.enabled else "disabled"

    @property
    def enabled(self):
        return self.settings.embedding_enabled and bool(self.settings.embedding_digest)

    def diagnostic(self, state="disabled", reason="provider_disabled"):
        return SemanticDiagnostic(
            state=state,
            reason=reason,
            namespace=self.namespace if self.enabled else None,
            model=self.settings.embedding_model if self.enabled else None,
            model_digest=self.settings.embedding_digest if self.enabled else None,
            dimensions=self.settings.embedding_dimensions if self.enabled else None,
            min_similarity=self.settings.embedding_min_similarity if self.enabled else None,
        ).model_dump()

    def prepare(self, query, *, admitted=False, enabled=True):
        if not self.enabled or not enabled:
            return PreparedQuery(self.diagnostic())
        acquired = False
        if not admitted:
            acquired = self.capacity.acquire(blocking=False)
            if not acquired:
                self.last_state = "degraded"
                return PreparedQuery(self.diagnostic("degraded", "generation_capacity_busy"))
        started = time.perf_counter_ns()
        try:
            vector = self.provider.embed([query], query=True)
            if len(vector) != 1:
                raise EmbeddingError("embedding_invalid_response")
            result = PreparedQuery(
                self.diagnostic("available", "ready"),
                unit_vector(vector[0], self.settings.embedding_dimensions),
            )
            self.last_state = "available"
        except EmbeddingError as exc:
            result = PreparedQuery(self.diagnostic("degraded", exc.code))
            self.last_state = "degraded"
        finally:
            if acquired:
                self.capacity.release()
        result.diagnostic["query_ms"] = (time.perf_counter_ns() - started) // 1_000_000
        return result

    def _entries(self, db, owner, scope):
        entries = list(
            db.scalars(
                select(EmbeddingEntry)
                .where(
                    EmbeddingEntry.owner_id == owner,
                    EmbeddingEntry.scope_id == scope,
                    EmbeddingEntry.namespace == self.namespace,
                )
                .limit(CORPUS_LIMIT + 1)
            )
        )
        if len(entries) > CORPUS_LIMIT:
            raise EmbeddingError("scope_work_bound")
        return {(r.kind, r.item_id): r for r in entries}

    def _matches(self, entry, metadata):
        return (
            entry is not None
            and all(getattr(entry, key) == value for key, value in metadata.items())
            and (
                entry.model == self.settings.embedding_model
                and entry.model_digest == self.settings.embedding_digest
                and entry.dimensions == self.settings.embedding_dimensions
                and entry.index_version == INDEX_VERSION
            )
        )

    def _snapshot(self, db, owner, scope):
        from ada.retrieval import (
            _base_query,
            _document_base_query,
            _valid_document,
            _valid_evidence,
        )

        claims, size = _bounded_rows(db, _base_query(owner, scope, None).order_by(Claim.id))
        documents, doc_size = _bounded_rows(
            db,
            _document_base_query(owner, scope, None).order_by(DocumentChunk.id),
            CORPUS_LIMIT - len(claims),
        )
        if size + doc_size > CORPUS_BYTES:
            raise EmbeddingError("scope_work_bound")
        items = []
        for kind, rows, valid in (
            ("claim", claims, lambda *row: _valid_evidence(*row, db=db)),
            ("document", documents, _valid_document),
        ):
            for row in rows:
                if valid(*row):
                    metadata, text = _metadata(kind, row)
                    items.append((metadata, text))
        return items

    def rebuild(self, owner, scope):
        started = time.perf_counter_ns()
        with self.sessions() as db:
            owned_scope(db, owner, scope)
        if not self.enabled:
            raise ServiceError(503, "embeddings_disabled")
        if not self.capacity.acquire(blocking=False):
            raise ServiceError(503, "generation_capacity_busy")
        try:
            with self.sessions() as db:
                items = self._snapshot(db, owner, scope)
                entries = self._entries(db, owner, scope)
                old = {}
                for metadata, _ in items:
                    key = (metadata["kind"], metadata["item_id"])
                    if self._matches(entries.get(key), metadata):
                        try:
                            old[key] = unit_vector(
                                entries[key].vector, self.settings.embedding_dimensions
                            )
                        except EmbeddingError:
                            pass
            # No Session/transaction remains open during provider calls.
            pending = [(m, t) for m, t in items if (m["kind"], m["item_id"]) not in old]
            vectors = dict(old)
            for start in range(0, len(pending), MAX_BATCH):
                if (time.perf_counter_ns() - started) / 1_000_000_000 > 120:
                    raise EmbeddingError("embedding_rebuild_timeout")
                batch = pending[start : start + MAX_BATCH]
                output = self.provider.embed([t for _, t in batch])
                if len(output) != len(batch):
                    raise EmbeddingError("embedding_invalid_response")
                for (metadata, _), vector in zip(batch, output):
                    vectors[metadata["kind"], metadata["item_id"]] = unit_vector(
                        vector, self.settings.embedding_dimensions
                    )
            with self.sessions.begin() as db:
                # Correction/upload/another rebuild serializes here. Immutable
                # history stays intact; newly changed corpus aborts publication.
                locked = db.scalar(
                    select(Scope)
                    .where(Scope.owner_id == owner, Scope.id == scope)
                    .with_for_update()
                )
                if locked is None:
                    raise ServiceError(404, "scope_not_found")
                current = self._snapshot(db, owner, scope)
                if current != items:
                    raise ServiceError(409, "embedding_corpus_changed")
                # Replace only discardable derived data. One namespace per scope
                # bounds storage across model changes; frozen traces survive.
                db.execute(
                    delete(EmbeddingEntry).where(
                        EmbeddingEntry.owner_id == owner, EmbeddingEntry.scope_id == scope
                    )
                )
                for metadata, _ in items:
                    db.add(
                        EmbeddingEntry(
                            owner_id=owner,
                            scope_id=scope,
                            namespace=self.namespace,
                            **metadata,
                            model=self.settings.embedding_model,
                            model_digest=self.settings.embedding_digest,
                            dimensions=self.settings.embedding_dimensions,
                            index_version=INDEX_VERSION,
                            vector=vectors[metadata["kind"], metadata["item_id"]],
                        )
                    )
            return RebuildOutput(
                namespace=self.namespace,
                indexed=len(items),
                reused=len(old),
                elapsed_ms=(time.perf_counter_ns() - started) // 1_000_000,
            ).model_dump()
        except EmbeddingError as exc:
            self.last_state = "degraded"
            raise ServiceError(503, exc.code) from None
        finally:
            self.capacity.release()

    def rank(self, db, owner, scope, prepared, claim_query, document_query=None):
        from ada.retrieval import _valid_document, _valid_evidence

        diagnostic = dict(prepared.diagnostic)
        empty = {"claim": [], "document": [], "diagnostic": diagnostic}
        if prepared.vector is None:
            return empty
        started = time.perf_counter_ns()
        try:
            claims, size = _bounded_rows(db, claim_query.order_by(Claim.id))
            docs, doc_size = (
                _bounded_rows(
                    db, document_query.order_by(DocumentChunk.id), CORPUS_LIMIT - len(claims)
                )
                if document_query is not None
                else ([], 0)
            )
            if size + doc_size > CORPUS_BYTES:
                raise EmbeddingError("scope_work_bound")
            entries = self._entries(db, owner, scope)
            diagnostic["eligible"] = len(claims) + len(docs)
            ranked = {"claim": [], "document": []}
            used = []
            for kind, rows, valid in (
                ("claim", claims, lambda *row: _valid_evidence(*row, db=db)),
                ("document", docs, _valid_document),
            ):
                for row in rows:
                    if not valid(*row):
                        continue
                    metadata, _ = _metadata(kind, row)
                    entry = entries.get((kind, metadata["item_id"]))
                    if not self._matches(entry, metadata):
                        # Fail the semantic channel as a whole for partial/stale
                        # namespaces; lexical results remain exactly available.
                        raise EmbeddingError("index_incomplete_or_stale")
                    vector = unit_vector(entry.vector, self.settings.embedding_dimensions)
                    score = math.fsum(x * y for x, y in zip(prepared.vector, vector))
                    used.append(entry.built_at)
                    if score >= self.settings.embedding_min_similarity:
                        ranked[kind].append((row, round(score, 8)))
            diagnostic.update(indexed=len(used), index_built_at=max(used) if used else None)
            for hits in ranked.values():
                hits.sort(key=lambda item: (-item[1], item[0][0].id))
                del hits[64:]
            return ranked | {"diagnostic": diagnostic}
        except EmbeddingError as exc:
            diagnostic.update(state="degraded", reason=exc.code)
            self.last_state = "degraded"
            return empty
        finally:
            diagnostic["ranking_ms"] = (time.perf_counter_ns() - started) // 1_000_000
