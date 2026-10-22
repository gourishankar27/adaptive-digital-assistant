"""Private scheduling authority, finite occurrences, inbox and exact receipts."""

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class ScheduleConsent(Base):
    __tablename__ = "schedule_consents"
    __table_args__ = (CheckConstraint("revision >= 1", name="schedule_consent_revision"),)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean)
    updated_at: Mapped[int] = mapped_column(BigInteger)


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        CheckConstraint(
            "generation >= 1 AND cursor >= 0 AND delivered >= 0 AND missed >= 0",
            name="schedule_counters",
        ),
        CheckConstraint(
            "status IN ('active','paused','deleted','completed','quarantined')",
            name="schedule_status",
        ),
        CheckConstraint("origin_kind IN ('legacy','device','password')", name="schedule_origin"),
        Index("schedule_due", "status", "next_at", "owner_id"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    source_version_id: Mapped[str | None] = mapped_column(String(36))
    source_snapshot: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    generation: Mapped[int] = mapped_column(Integer)
    plan_generation: Mapped[int] = mapped_column(Integer)
    consent_revision: Mapped[int] = mapped_column(Integer)
    question_policy_revision: Mapped[int | None] = mapped_column(Integer)
    epoch: Mapped[int] = mapped_column(BigInteger)
    origin_kind: Mapped[str] = mapped_column(String(12))
    origin_id: Mapped[str] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(String(16))
    reason: Mapped[str | None] = mapped_column(String(64))
    definition: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    plan: Mapped[list] = mapped_column(JSON)
    timezone_data: Mapped[str] = mapped_column(String(40))
    cursor: Mapped[int] = mapped_column(Integer)
    next_at: Mapped[int | None] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
    snoozed_until: Mapped[int | None] = mapped_column(BigInteger)
    delivered: Mapped[int] = mapped_column(Integer)
    missed: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger)
    updated_at: Mapped[int] = mapped_column(BigInteger)


class ScheduleOccurrence(Base):
    __tablename__ = "schedule_occurrences"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "schedule_id"], ["schedules.owner_id", "schedules.id"]),
        UniqueConstraint(
            "owner_id",
            "schedule_id",
            "generation",
            "scheduled_for",
            name="schedule_occurrence_once",
        ),
        CheckConstraint("attempt >= 0 AND generation >= 1", name="schedule_occurrence_counters"),
        CheckConstraint(
            "status IN ('queued','running','delivered','suppressed','failed')",
            name="schedule_occurrence_status",
        ),
        Index("schedule_occurrence_due", "status", "available_at", "lease_until"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schedule_id: Mapped[str] = mapped_column(String(36))
    generation: Mapped[int] = mapped_column(Integer)
    scheduled_for: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(16))
    reason: Mapped[str | None] = mapped_column(String(64))
    attempt: Mapped[int] = mapped_column(Integer)
    lease_until: Mapped[int | None] = mapped_column(BigInteger)
    lease_token: Mapped[str | None] = mapped_column(String(36))
    available_at: Mapped[int] = mapped_column(BigInteger)
    item_id: Mapped[str | None] = mapped_column(String(36))


class ScheduleInboxItem(Base):
    __tablename__ = "schedule_inbox"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(["owner_id", "schedule_id"], ["schedules.owner_id", "schedules.id"]),
        ForeignKeyConstraint(
            ["owner_id", "occurrence_id"],
            ["schedule_occurrences.owner_id", "schedule_occurrences.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "question_id"], ["curiosity_questions.owner_id", "curiosity_questions.id"]
        ),
        ForeignKeyConstraint(
            ["owner_id", "opened_conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        UniqueConstraint("owner_id", "occurrence_id", name="schedule_one_inbox_item"),
        CheckConstraint(
            "status IN ('unread','acknowledged','opened','dismissed')", name="schedule_inbox_status"
        ),
        Index("schedule_inbox_owner", "owner_id", "created_at"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    schedule_id: Mapped[str] = mapped_column(String(36))
    occurrence_id: Mapped[str] = mapped_column(String(36))
    epoch: Mapped[int] = mapped_column(BigInteger)
    kind: Mapped[str] = mapped_column(String(24))
    text: Mapped[str] = mapped_column(String(1000))
    question_id: Mapped[str | None] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(String(16))
    available_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
    acknowledged_at: Mapped[int | None] = mapped_column(BigInteger)
    opened_conversation_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger)


class ScheduleReceipt(Base):
    __tablename__ = "schedule_receipts"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
