"""Versioned, reviewed long narratives; audio never crosses this boundary."""

import hashlib
import json
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.errors import ServiceError
from ada.evidence import content_hash, validate_text
from ada.memory import Timestamp
from ada.models import Base, Conversation, Event, SourceVersion, User, now_ms

PROTOCOL = "ada-long-reviewed-voice-v1"
MAX_TEXT = 32768
MAX_DURATION = 7200000


class SegmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    sequence: int = Field(ge=0, le=511, strict=True)
    end_ms: int = Field(ge=1, le=MAX_DURATION, strict=True)
    text: str = Field(min_length=1, max_length=MAX_TEXT)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def exact(self):
        validate_text(self.text)
        if not self.text.strip() or content_hash(self.text) != self.sha256:
            raise ValueError("invalid segment")
        return self


class LongTranscriptInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transcript_id: UUID
    engine_id: Literal["sherpa_zipformer_en_v1"]
    engine_version: Literal["sherpa-onnx-1.13.8"]
    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    language: Literal["en-US"]
    duration_ms: int = Field(ge=1, le=MAX_DURATION, strict=True)
    segments: list[SegmentInput] = Field(min_length=1, max_length=512)

    @model_validator(mode="after")
    def ordered(self):
        if (
            len({s.id for s in self.segments}) != len(self.segments)
            or [s.sequence for s in self.segments] != list(range(len(self.segments)))
            or any(s.end_ms > self.duration_ms for s in self.segments)
            or any(a.end_ms > b.end_ms for a, b in zip(self.segments, self.segments[1:]))
            or len(" ".join(s.text for s in self.segments)) > MAX_TEXT
        ):
            raise ValueError("invalid ordered transcript")
        return self


class LongVoiceFields(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)
    conversation_style: Literal["listen", "questions", "suggestions"] = "listen"
    transcript: LongTranscriptInput
    reviewed_text: str = Field(min_length=1, max_length=MAX_TEXT)
    data_epoch: int = Field(ge=0, strict=True)
    context_start: int = Field(ge=0, strict=True)
    context_end: int = Field(ge=1, strict=True)
    review: Literal["approve"]

    @field_validator("reviewed_text")
    @classmethod
    def text_valid(cls, value):
        validate_text(value)
        if not value.strip():
            raise ValueError("reviewed wording cannot be blank")
        return value


class LongVoiceInput(Base):
    __tablename__ = "long_voice_inputs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "request_id", "conversation_id"],
            ["requests.owner_id", "requests.id", "requests.conversation_id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "endorsement_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "endorsement_id"],
            ["events.owner_id", "events.conversation_id", "events.id"],
        ),
        UniqueConstraint("owner_id", "transcript_id", name="long_voice_transcript_once"),
        CheckConstraint("data_epoch >= 0", name="long_voice_epoch"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    transcript_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    reviewed_text: Mapped[str] = mapped_column(Text)
    reviewed_hash: Mapped[str] = mapped_column(String(64))
    endorsement_id: Mapped[str] = mapped_column(String(36))
    data_epoch: Mapped[int] = mapped_column(BigInteger)
    approved_at: Mapped[int] = mapped_column(BigInteger)


class LongVoiceOutput(BaseModel):
    protocol: Literal["ada-long-reviewed-voice-v1"] = PROTOCOL
    request_id: UUID
    conversation_id: UUID
    scope_id: UUID
    transcript: LongTranscriptInput
    reviewed_text: str
    reviewed_hash: str
    context_start: int
    context_end: int
    endorsement_source_version_id: UUID
    original_trust: Literal["generated_interpretation"] = "generated_interpretation"
    reviewed_origin: Literal["user_reviewed"] = "user_reviewed"
    engine_metadata: Literal["client_reported"] = "client_reported"
    audio_storage: Literal["not_received_by_server"] = "not_received_by_server"
    approved_at: Timestamp


class LongVoiceService:
    def __init__(self, streaming):
        self.streaming, self.sessions = streaming, streaming.sessions

    def submit(self, owner, cid, body):
        with self.sessions() as db:
            account = db.get(User, owner)
            if account is None or account.data_epoch != body.data_epoch:
                raise ServiceError(409, "content_epoch_changed")
        if (
            not (0 <= body.context_start < body.context_end <= len(body.reviewed_text))
            or body.reviewed_text[body.context_start : body.context_end] != body.content
        ):
            raise ServiceError(422, "long_voice_context_mismatch")
        payload = {
            "transcript": body.transcript.model_dump(mode="json"),
            "context_start": body.context_start,
            "context_end": body.context_end,
            "conversation_style": body.conversation_style,
        }
        binding = hashlib.sha256(
            (
                PROTOCOL
                + json.dumps(
                    {**payload, "reviewed_text": body.reviewed_text, "data_epoch": body.data_epoch},
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                )
            ).encode()
        ).hexdigest()

        def register(db, request):
            account = db.scalar(select(User).where(User.id == owner).with_for_update())
            if account.data_epoch != body.data_epoch:
                raise ServiceError(409, "content_epoch_changed")
            previous = db.get(LongVoiceInput, (owner, str(body.request_id)))
            if previous:
                if previous.input_hash != binding:
                    raise ServiceError(409, "idempotency_key_reused")
                return
            count = db.scalar(
                select(func.count())
                .select_from(LongVoiceInput)
                .where(LongVoiceInput.owner_id == owner)
            )
            if count >= 1000:
                raise ServiceError(413, "long_voice_history_limit")
            conversation = db.get(Conversation, cid)
            event = db.scalar(
                select(Event).where(
                    Event.owner_id == owner, Event.request_id == request.id, Event.role == "user"
                )
            )
            db.add(
                LongVoiceInput(
                    owner_id=owner,
                    request_id=request.id,
                    conversation_id=cid,
                    scope_id=conversation.scope_id,
                    transcript_id=str(body.transcript.transcript_id),
                    input_hash=binding,
                    payload=payload,
                    reviewed_text=body.reviewed_text,
                    reviewed_hash=content_hash(body.reviewed_text),
                    endorsement_id=event.id,
                    data_epoch=body.data_epoch,
                    approved_at=now_ms(),
                )
            )
            db.flush()

        return self.streaming.submit(
            owner,
            cid,
            str(body.request_id),
            body.content,
            as_of=body.as_of,
            use_memory=body.use_memory,
            use_documents=body.use_documents,
            input_binding=binding,
            register=register,
            voice_style=body.conversation_style,
        )

    def get(self, owner, rid):
        with self.sessions() as db:
            row = db.get(LongVoiceInput, (owner, rid))
            if row is None:
                raise ServiceError(404, "long_voice_input_not_found")
            source = db.get(SourceVersion, row.endorsement_id)
            try:
                original = LongTranscriptInput.model_validate(row.payload["transcript"])
                start, end = row.payload["context_start"], row.payload["context_end"]
                if (
                    type(start) is not int
                    or type(end) is not int
                    or not 0 <= start < end <= len(row.reviewed_text)
                    or end - start > 4000
                ):
                    raise ValueError("invalid retained context")
            except (ValueError, TypeError, KeyError):
                raise ServiceError(409, "long_voice_lineage_unavailable") from None
            if (
                source is None
                or source.owner_id != owner
                or source.scope_id != row.scope_id
                or source.trust_class != "user_explicit"
                or source.content != row.reviewed_text[start:end]
                or source.content_hash != content_hash(source.content)
                or content_hash(row.reviewed_text) != row.reviewed_hash
            ):
                raise ServiceError(409, "long_voice_lineage_unavailable")
            return LongVoiceOutput(
                request_id=rid,
                conversation_id=row.conversation_id,
                scope_id=row.scope_id,
                transcript=original,
                reviewed_text=row.reviewed_text,
                reviewed_hash=row.reviewed_hash,
                context_start=start,
                context_end=end,
                endorsement_source_version_id=row.endorsement_id,
                approved_at=row.approved_at,
            )
