"""Private structured work, immutable revisions, exact receipts and brief snapshots."""

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class WorkItem(Base):
    __tablename__ = "work_items"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "goal_id"],
            ["work_items.owner_id", "work_items.scope_id", "work_items.id"],
        ),
        CheckConstraint("revision >= 1 AND epoch >= 0", name="work_item_counters"),
        CheckConstraint("kind IN ('goal','task')", name="work_item_kind"),
        CheckConstraint(
            "status IN ('planned','done','deferred','unknown','dismissed')", name="work_item_status"
        ),
        CheckConstraint(
            "goal_id IS NULL OR (kind='task' AND goal_id<>id)", name="work_item_parent"
        ),
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    goal_id: Mapped[str | None] = mapped_column(String(36))
    kind: Mapped[str] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(12))
    revision: Mapped[int] = mapped_column(Integer)
    epoch: Mapped[int] = mapped_column(BigInteger)
    fields: Mapped[dict] = mapped_column(JSON)
    due_at: Mapped[int | None] = mapped_column(BigInteger)
    provenance: Mapped[str] = mapped_column(String(40))
    schedule_id: Mapped[str | None] = mapped_column(String(36))
    question_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger)
    updated_at: Mapped[int] = mapped_column(BigInteger)


class WorkRevision(Base):
    __tablename__ = "work_revisions"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "item_id"], ["work_items.owner_id", "work_items.id"]),
        CheckConstraint("revision >= 1", name="work_revision_positive"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    fields: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)


class WorkReceipt(Base):
    __tablename__ = "work_receipts"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)


class WorkBrief(Base):
    __tablename__ = "work_briefs"
    __table_args__ = (
        UniqueConstraint("owner_id", "cache_key"),
        CheckConstraint("epoch >= 0", name="work_brief_epoch"),
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    epoch: Mapped[int] = mapped_column(BigInteger)
    cache_key: Mapped[str] = mapped_column(String(64))
    input_hash: Mapped[str] = mapped_column(String(64))
    snapshot: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
