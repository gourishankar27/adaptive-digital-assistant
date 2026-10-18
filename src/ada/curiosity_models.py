"""Owned policy, question snapshots and minimal exact-operation receipts."""

from sqlalchemy import (
    JSON,
    BigInteger,
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


class CuriosityPolicy(Base):
    __tablename__ = "curiosity_policies"
    __table_args__ = (CheckConstraint("revision >= 1", name="curiosity_policy_revision"),)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer)
    settings: Mapped[dict] = mapped_column(JSON)
    suppressed: Mapped[list] = mapped_column(JSON)
    daily: Mapped[dict] = mapped_column(JSON)
    metrics: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[int] = mapped_column(BigInteger)


class CuriosityQuestion(Base):
    __tablename__ = "curiosity_questions"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "opened_conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        ForeignKeyConstraint(["owner_id", "request_id"], ["requests.owner_id", "requests.id"]),
        ForeignKeyConstraint(
            ["owner_id", "answer_request_id"],
            ["requests.owner_id", "requests.id"],
            use_alter=True,
            name="curiosity_answer_request",
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        UniqueConstraint("owner_id", "request_id", name="curiosity_one_per_reply"),
        CheckConstraint(
            "channel IN ('chat','inbox') AND topic IN ('interests','work','routines','relationships','reflection')",
            name="curiosity_channel_topic",
        ),
        CheckConstraint(
            "status IN ('pending','offered','opened','answering','answered','skipped','dismissed','revoked','expired','deferred')",
            name="curiosity_question_state",
        ),
        CheckConstraint(
            "expires_at > created_at AND policy_revision >= 1", name="curiosity_expiry"
        ),
        Index("curiosity_owner_inbox", "owner_id", "channel", "status", "created_at"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    conversation_id: Mapped[str | None] = mapped_column(String(36))
    opened_conversation_id: Mapped[str | None] = mapped_column(String(36))
    request_id: Mapped[str | None] = mapped_column(String(36))
    answer_request_id: Mapped[str | None] = mapped_column(String(36))
    source_version_id: Mapped[str | None] = mapped_column(String(36))
    channel: Mapped[str] = mapped_column(String(12))
    topic: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    template_key: Mapped[str] = mapped_column(String(50))
    policy_revision: Mapped[int] = mapped_column(Integer)
    epoch: Mapped[int] = mapped_column(BigInteger)
    payload: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    feedback: Mapped[str | None] = mapped_column(String(12))
    created_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
    available_at: Mapped[int] = mapped_column(BigInteger)
    closed_at: Mapped[int | None] = mapped_column(BigInteger)


class CuriosityReceipt(Base):
    __tablename__ = "curiosity_receipts"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
