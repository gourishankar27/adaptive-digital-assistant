"""Scoped identity annotations; no record grants user authority."""

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base, now_ms


class Entity(Base):
    __tablename__ = "entities"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "redirect_id"],
            ["entities.owner_id", "entities.scope_id", "entities.id"],
        ),
        CheckConstraint(
            "kind IN ('person', 'project', 'object', 'other')", name="entity_kind_allowed"
        ),
        CheckConstraint(
            "redirect_id IS NULL OR redirect_id != id", name="entity_not_self_redirect"
        ),
        CheckConstraint("revision >= 0", name="entity_revision_positive"),
        Index("entity_scope_created", "owner_id", "scope_id", "created_at", "id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    label: Mapped[str] = mapped_column(String(160))
    normalized_key: Mapped[str] = mapped_column(String(640))
    kind: Mapped[str] = mapped_column(String(20))
    revision: Mapped[int] = mapped_column(default=0)
    redirect_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class EntityAlias(Base):
    __tablename__ = "entity_aliases"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "entity_id"],
            ["entities.owner_id", "entities.scope_id", "entities.id"],
        ),
        CheckConstraint("valid_to IS NULL OR valid_to >= created_at", name="entity_alias_interval"),
        Index(
            "entity_alias_lookup",
            "owner_id",
            "scope_id",
            "normalized_key",
            "created_at",
            "valid_to",
        ),
        Index(
            "entity_alias_current_unique",
            "entity_id",
            "normalized_key",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
            sqlite_where=text("valid_to IS NULL"),
        ),
        Index(
            "entity_canonical_current_unique",
            "entity_id",
            unique=True,
            postgresql_where=text("valid_to IS NULL AND canonical = true"),
            sqlite_where=text("valid_to IS NULL AND canonical = 1"),
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    entity_id: Mapped[str] = mapped_column(String(36))
    label: Mapped[str] = mapped_column(String(160))
    normalized_key: Mapped[str] = mapped_column(String(640))
    canonical: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
    valid_to: Mapped[int | None] = mapped_column(BigInteger)


class EntityMerge(Base):
    __tablename__ = "entity_merges"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_id"],
            ["entities.owner_id", "entities.scope_id", "entities.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "target_id"],
            ["entities.owner_id", "entities.scope_id", "entities.id"],
        ),
        CheckConstraint("source_id != target_id", name="entity_merge_distinct"),
        CheckConstraint("valid_to IS NULL OR valid_to >= created_at", name="entity_merge_interval"),
        Index(
            "entity_merge_current_unique",
            "source_id",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
            sqlite_where=text("valid_to IS NULL"),
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    source_id: Mapped[str] = mapped_column(String(36))
    target_id: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
    valid_to: Mapped[int | None] = mapped_column(BigInteger)


class EntitySelfLink(Base):
    __tablename__ = "entity_self_links"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "entity_id"],
            ["entities.owner_id", "entities.scope_id", "entities.id"],
        ),
        CheckConstraint("valid_to IS NULL OR valid_to >= created_at", name="entity_self_interval"),
        Index(
            "entity_self_current_unique",
            "owner_id",
            "scope_id",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
            sqlite_where=text("valid_to IS NULL"),
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    entity_id: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
    valid_to: Mapped[int | None] = mapped_column(BigInteger)


class ClaimEntityLink(Base):
    __tablename__ = "claim_entity_links"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "entity_id"],
            ["entities.owner_id", "entities.scope_id", "entities.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
        ),
        CheckConstraint("valid_to IS NULL OR valid_to >= created_at", name="claim_entity_interval"),
        Index(
            "claim_entity_current_unique",
            "claim_id",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
            sqlite_where=text("valid_to IS NULL"),
        ),
        Index("claim_entity_lookup", "owner_id", "scope_id", "entity_id", "created_at", "valid_to"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    claim_id: Mapped[str] = mapped_column(String(36))
    entity_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
    valid_to: Mapped[int | None] = mapped_column(BigInteger)


class EntityOperation(Base):
    __tablename__ = "entity_operations"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        Index("entity_operation_scope_created", "owner_id", "scope_id", "created_at", "id"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(20))
    input_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
