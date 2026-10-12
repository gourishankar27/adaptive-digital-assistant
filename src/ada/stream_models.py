"""Owned streaming attempt checkpoints. Legacy request states remain unchanged."""

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class StreamAttempt(Base):
    __tablename__ = "stream_attempts"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "request_id"], ["requests.owner_id", "requests.id"]),
        CheckConstraint("attempt >= 1 AND attempt <= 1000000", name="stream_attempt_range"),
        CheckConstraint(
            "sequence >= 0 AND replay_after >= 0 AND replay_after <= sequence",
            name="stream_sequence_range",
        ),
        CheckConstraint(
            "state IN ('running','cancel_requested','completed','failed','cancelled','interrupted')",
            name="stream_state_allowed",
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    attempt: Mapped[int] = mapped_column(Integer, primary_key=True)
    instance_id: Mapped[str] = mapped_column(String(36))
    state: Mapped[str] = mapped_column(String(20))
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    replay_after: Mapped[int] = mapped_column(Integer, default=0)
    provisional: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[int] = mapped_column(BigInteger)
    deadline_at: Mapped[int] = mapped_column(BigInteger)
    finished_at: Mapped[int | None] = mapped_column(BigInteger)
    cancel_receipt: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))


class StreamEvent(Base):
    __tablename__ = "stream_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "request_id", "attempt"],
            ["stream_attempts.owner_id", "stream_attempts.request_id", "stream_attempts.attempt"],
        ),
        CheckConstraint("sequence >= 1", name="stream_event_sequence_positive"),
        CheckConstraint(
            "kind IN ('started','delta','status','completed','failed','cancel_requested','cancelled','interrupted')",
            name="stream_event_kind_allowed",
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    attempt: Mapped[int] = mapped_column(Integer, primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
