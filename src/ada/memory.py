"""Authenticated, explicit user assertions with source spans and valid-time history.

A quote proves where the assertion was recorded. It does not prove the assertion
is true or that subject/predicate/value logically follow from the quote. In this
phase the authenticated user supplies and endorses that structured annotation.
"""

import json
from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from ada.errors import ServiceError
from ada.evidence import content_hash, public_source_version, record_source, validate_text
from ada.models import Claim, Scope, Source, SourceVersion, now_ms
from ada.search import index_claim


def time_ms(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps require a timezone")
    if value.microsecond % 1000:
        raise ValueError("timestamps must have at most millisecond precision")
    delta = value.astimezone(UTC) - datetime(1970, 1, 1, tzinfo=UTC)
    return delta.days * 86_400_000 + delta.seconds * 1000 + delta.microseconds // 1000


class MemoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*")
    @classmethod
    def valid_text(cls, value):
        return validate_text(value)


Timestamp = Annotated[int, Field(json_schema_extra={"format": "int64"})]


class SourceVersionOutput(BaseModel):
    id: UUID
    source_id: UUID
    scope_id: UUID
    version: int
    content: str
    content_hash: str
    trust_class: Literal["user_explicit", "model_generated"]
    created_at: Timestamp


class EvidenceOutput(BaseModel):
    source_version_id: UUID
    span_start: int
    span_end: int
    quote: str
    content_hash: str


class ClaimOutput(BaseModel):
    id: UUID
    scope_id: UUID
    subject: str
    predicate: str
    value: str
    kind: Literal["fact", "preference", "decision"]
    status: Literal["active", "superseded"]
    valid_from: Timestamp
    valid_to: Timestamp | None
    superseded_by: UUID | None
    created_at: Timestamp
    origin: Literal["user_asserted"]
    evidence: EvidenceOutput


class NoteInput(MemoryInput):
    source_id: UUID
    content: str = Field(min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("content must not be blank")
        return value


class EvidenceInput(MemoryInput):
    claim_id: UUID
    source_version_id: UUID
    span_start: int = Field(ge=0, strict=True)
    span_end: int = Field(gt=0, strict=True)
    valid_to: AwareDatetime | None = None

    @field_validator("valid_to")
    @classmethod
    def millisecond_time(cls, value):
        if value is not None:
            time_ms(value)
        return value


class ClaimInput(EvidenceInput):
    subject: str = Field(min_length=1, max_length=160)
    predicate: str = Field(min_length=1, max_length=160)
    value: str = Field(min_length=1, max_length=1000)
    kind: Literal["fact", "preference", "decision"] = "fact"
    valid_from: AwareDatetime | None = None

    @field_validator("subject", "predicate", "value")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("claim fields must not be blank")
        return value.strip()

    @field_validator("valid_from")
    @classmethod
    def millisecond_start(cls, value):
        if value is not None:
            time_ms(value)
        return value


class SupersedeInput(EvidenceInput):
    value: str = Field(min_length=1, max_length=1000)
    effective_at: AwareDatetime | None = None

    @field_validator("value")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("value must not be blank")
        return value.strip()

    @field_validator("effective_at")
    @classmethod
    def millisecond_effective(cls, value):
        if value is not None:
            time_ms(value)
        return value


def public_claim(row):
    return {
        "id": row.id,
        "scope_id": row.scope_id,
        "subject": row.subject,
        "predicate": row.predicate,
        "value": row.value,
        "kind": row.kind,
        "status": row.status,
        "valid_from": row.valid_from,
        "valid_to": row.valid_to,
        "superseded_by": row.superseded_by,
        "created_at": row.created_at,
        "origin": "user_asserted",
        "evidence": {
            "source_version_id": row.source_version_id,
            "span_start": row.span_start,
            "span_end": row.span_end,
            "quote": row.quote,
            "content_hash": row.evidence_hash,
        },
    }


def owned_scope(db, owner, scope_id, *, lock=False):
    query = select(Scope).where(Scope.owner_id == owner, Scope.id == scope_id)
    if lock:
        query = query.with_for_update()
    row = db.scalar(query)
    if row is None:
        raise ServiceError(404, "scope_not_found")
    return row


class MemoryService:
    def __init__(self, sessions):
        self.sessions = sessions

    def note(self, owner, scope_id, body: NoteInput):
        try:
            with self.sessions.begin() as db:
                owned_scope(db, owner, scope_id, lock=True)
                source = db.scalar(
                    select(Source).where(Source.id == str(body.source_id), Source.owner_id == owner)
                )
                if source:
                    version = db.scalar(
                        select(SourceVersion).where(
                            SourceVersion.owner_id == owner,
                            SourceVersion.source_id == source.id,
                            SourceVersion.version == 1,
                        )
                    )
                    if (
                        source.scope_id != scope_id
                        or source.kind != "user_note"
                        or version is None
                        or version.content != body.content
                        or version.content_hash != content_hash(body.content)
                    ):
                        raise ServiceError(409, "source_id_reused")
                    return public_source_version(version), False
                version = record_source(
                    db,
                    owner=owner,
                    scope_id=scope_id,
                    content=body.content,
                    kind="user_note",
                    source_id=str(body.source_id),
                )
                return public_source_version(version), True
        except IntegrityError as exc:
            raise ServiceError(409, "source_conflict") from exc

    @staticmethod
    def _evidence(db, owner, scope_id, body):
        source = db.scalar(
            select(SourceVersion).where(
                SourceVersion.id == str(body.source_version_id),
                SourceVersion.owner_id == owner,
                SourceVersion.scope_id == scope_id,
            )
        )
        if source is None:
            raise ServiceError(404, "source_version_not_found")
        if source.trust_class != "user_explicit":
            raise ServiceError(422, "source_not_user_evidence")
        if content_hash(source.content) != source.content_hash:
            raise ServiceError(409, "evidence_content_changed")
        if not (0 <= body.span_start < body.span_end <= len(source.content)):
            raise ServiceError(422, "invalid_evidence_span")
        quote = source.content[body.span_start : body.span_end]
        if not quote.strip():
            raise ServiceError(422, "empty_evidence_span")
        return source, quote

    @staticmethod
    def _fields(owner, scope_id, body, source, quote, *, subject, predicate, kind, start):
        end = time_ms(body.valid_to) if body.valid_to is not None else None
        if end is not None and end <= start:
            raise ServiceError(422, "invalid_validity_interval")
        return {
            "owner_id": owner,
            "scope_id": scope_id,
            "subject": subject,
            "predicate": predicate,
            "value": body.value,
            "kind": kind,
            "source_version_id": source.id,
            "span_start": body.span_start,
            "span_end": body.span_end,
            "quote": quote,
            "evidence_hash": source.content_hash,
            "valid_from": start,
            "valid_to": end,
        }

    @staticmethod
    def _write_hash(fields, supersedes=None):
        canonical = json.dumps(
            fields | {"supersedes": supersedes},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return content_hash(canonical)

    @staticmethod
    def _existing(db, owner, scope_id, claim_id, fingerprint):
        row = db.scalar(select(Claim).where(Claim.owner_id == owner, Claim.id == claim_id))
        if row is not None:
            if row.scope_id != scope_id or row.write_hash != fingerprint:
                raise ServiceError(409, "claim_id_reused")
            return row
        duplicate = db.scalar(
            select(Claim).where(
                Claim.owner_id == owner, Claim.scope_id == scope_id, Claim.write_hash == fingerprint
            )
        )
        if duplicate is not None:
            raise ServiceError(409, "claim_duplicate")
        return None

    def add(self, owner, scope_id, body: ClaimInput):
        try:
            with self.sessions.begin() as db:
                owned_scope(db, owner, scope_id, lock=True)
                source, quote = self._evidence(db, owner, scope_id, body)
                start = time_ms(body.valid_from) if body.valid_from else source.created_at
                fields = self._fields(
                    owner,
                    scope_id,
                    body,
                    source,
                    quote,
                    subject=body.subject,
                    predicate=body.predicate,
                    kind=body.kind,
                    start=start,
                )
                fingerprint = self._write_hash(fields)
                existing = self._existing(db, owner, scope_id, str(body.claim_id), fingerprint)
                if existing:
                    return public_claim(existing), False
                row = Claim(id=str(body.claim_id), write_hash=fingerprint, **fields)
                db.add(row)
                db.flush()
                index_claim(db, row)
                return public_claim(row), True
        except IntegrityError as exc:
            raise ServiceError(409, "claim_conflict") from exc

    def supersede(self, owner, old_id, body: SupersedeInput):
        try:
            with self.sessions.begin() as db:
                # Get only the scope ID before locking, so the old claim is loaded
                # after concurrent writers have committed. All scope writes lock
                # in this same order. PostgreSQL is the deployment backend.
                scope_id = db.scalar(
                    select(Claim.scope_id).where(Claim.owner_id == owner, Claim.id == old_id)
                )
                if scope_id is None:
                    raise ServiceError(404, "claim_not_found")
                owned_scope(db, owner, scope_id, lock=True)
                old = db.scalar(select(Claim).where(Claim.owner_id == owner, Claim.id == old_id))
                source, quote = self._evidence(db, owner, scope_id, body)
                start = time_ms(body.effective_at) if body.effective_at else source.created_at
                fields = self._fields(
                    owner,
                    scope_id,
                    body,
                    source,
                    quote,
                    subject=old.subject,
                    predicate=old.predicate,
                    kind=old.kind,
                    start=start,
                )
                fingerprint = self._write_hash(fields, old_id)
                existing = self._existing(db, owner, scope_id, str(body.claim_id), fingerprint)
                if existing:
                    return public_claim(existing), False
                if old.status != "active":
                    raise ServiceError(409, "claim_already_superseded")
                if start <= old.valid_from or (old.valid_to is not None and start > old.valid_to):
                    raise ServiceError(422, "correction_outside_validity_interval")
                replacement = Claim(id=str(body.claim_id), write_hash=fingerprint, **fields)
                db.add(replacement)
                db.flush()
                index_claim(db, replacement)
                old.valid_to, old.superseded_by, old.status = start, replacement.id, "superseded"
                db.flush()
                return public_claim(replacement), True
        except IntegrityError as exc:
            raise ServiceError(409, "claim_conflict") from exc

    def list(
        self,
        owner,
        scope_id,
        *,
        as_of=None,
        history=False,
        subject=None,
        predicate=None,
        limit=100,
        offset=0,
    ):
        if history and as_of is not None:
            raise ServiceError(422, "history_and_as_of_conflict")
        with self.sessions() as db:
            owned_scope(db, owner, scope_id)
            query = select(Claim).where(Claim.owner_id == owner, Claim.scope_id == scope_id)
            if not history:
                at = time_ms(as_of) if as_of is not None else now_ms()
                # Status describes the replacement chain, not current validity.
                # A superseded claim can remain valid before a future replacement.
                query = query.where(
                    Claim.valid_from <= at, or_(Claim.valid_to.is_(None), Claim.valid_to > at)
                )
            if subject is not None:
                query = query.where(Claim.subject == subject)
            if predicate is not None:
                query = query.where(Claim.predicate == predicate)
            rows = db.scalars(
                query.order_by(Claim.valid_from, Claim.created_at, Claim.id)
                .limit(limit)
                .offset(offset)
            )
            return [public_claim(row) for row in rows]
