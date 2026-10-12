from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class ExpressionPreference(Base):
    __tablename__ = "expression_preferences"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "profile_id"], ["personalities.owner_id", "personalities.id"]
        ),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id"], ["conversations.owner_id", "conversations.id"]
        ),
        CheckConstraint(
            "(target_kind='account' AND target_id=owner_id AND profile_id IS NULL AND scope_id IS NULL AND conversation_id IS NULL) OR (target_kind='profile' AND target_id=profile_id AND profile_id IS NOT NULL AND scope_id IS NULL AND conversation_id IS NULL) OR (target_kind='scope' AND target_id=scope_id AND scope_id IS NOT NULL AND profile_id IS NULL AND conversation_id IS NULL) OR (target_kind='conversation' AND target_id=conversation_id AND conversation_id IS NOT NULL AND profile_id IS NULL AND scope_id IS NULL)",
            name="expression_target",
        ),
        CheckConstraint("revision >= 1", name="expression_preference_revision"),
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    target_kind: Mapped[str] = mapped_column(String(20), primary_key=True)
    target_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    profile_id: Mapped[str | None] = mapped_column(String(36))
    scope_id: Mapped[str | None] = mapped_column(String(36))
    conversation_id: Mapped[str | None] = mapped_column(String(36))
    revision: Mapped[int] = mapped_column(Integer)
    values: Mapped[dict] = mapped_column(JSON)
    receipt_id: Mapped[str] = mapped_column(String(36))


class ExpressionBinding(Base):
    __tablename__ = "expression_bindings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "profile_id"], ["personalities.owner_id", "personalities.id"]
        ),
        UniqueConstraint("owner_id", "conversation_id", "profile_id"),
        CheckConstraint("revision >= 0", name="expression_binding_revision"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    profile_id: Mapped[str] = mapped_column(String(36))
    revision: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean)
    dynamic_enabled: Mapped[bool] = mapped_column(Boolean)
    preferences: Mapped[dict] = mapped_column(JSON)
    origins: Mapped[dict] = mapped_column(JSON)
    source_receipts: Mapped[dict] = mapped_column(JSON)


class ExpressionSession(Base):
    __tablename__ = "expression_sessions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "profile_id"],
            [
                "expression_bindings.owner_id",
                "expression_bindings.conversation_id",
                "expression_bindings.profile_id",
            ],
        ),
        CheckConstraint(
            "warmth BETWEEN 0 AND 100 AND focus BETWEEN 0 AND 100 AND energy BETWEEN 0 AND 100 AND playfulness BETWEEN 0 AND 100 AND concern BETWEEN 0 AND 100",
            name="expression_vector_ranges",
        ),
        CheckConstraint(
            "turn >= 0 AND last_signal_turn >= -1 AND last_signal_turn <= turn",
            name="expression_turn",
        ),
        CheckConstraint(
            "expires_at >= started_at AND touched_at >= started_at", name="expression_expiry"
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    profile_id: Mapped[str] = mapped_column(String(36))
    session_id: Mapped[str] = mapped_column(String(36))
    turn: Mapped[int] = mapped_column(Integer)
    last_signal_turn: Mapped[int] = mapped_column(Integer)
    last_request_id: Mapped[str | None] = mapped_column(String(36))
    warmth: Mapped[int] = mapped_column(Integer)
    focus: Mapped[int] = mapped_column(Integer)
    energy: Mapped[int] = mapped_column(Integer)
    playfulness: Mapped[int] = mapped_column(Integer)
    concern: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[int] = mapped_column(BigInteger)
    touched_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)


class ExpressionReceipt(Base):
    __tablename__ = "expression_receipts"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
