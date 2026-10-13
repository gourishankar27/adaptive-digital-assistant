"""Immutable generated ASR input linked to a separate, explicit user endorsement."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class VoiceInput(Base):
    __tablename__ = "voice_inputs"
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
            ["owner_id", "scope_id", "endorsement_source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "endorsement_source_version_id"],
            ["events.owner_id", "events.conversation_id", "events.id"],
        ),
        UniqueConstraint("owner_id", "transcript_id", name="voice_transcript_once"),
        CheckConstraint("duration_ms BETWEEN 1 AND 60000", name="voice_duration_bounded"),
        CheckConstraint("engine_id = 'android_on_device'", name="voice_engine_supported"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    transcript_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    engine_id: Mapped[str] = mapped_column(String(40))
    engine_version: Mapped[str] = mapped_column(String(120))
    language: Mapped[str] = mapped_column(String(35))
    duration_ms: Mapped[int] = mapped_column(BigInteger)
    original_text: Mapped[str] = mapped_column(Text)
    original_hash: Mapped[str] = mapped_column(String(64))
    endorsement_source_version_id: Mapped[str] = mapped_column(String(36))
    reviewed_hash: Mapped[str] = mapped_column(String(64))
    approved_at: Mapped[int] = mapped_column(BigInteger)
