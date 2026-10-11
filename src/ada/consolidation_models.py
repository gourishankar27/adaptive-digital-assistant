"""Durable owned jobs, exact input references and immutable generated continuity."""

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class ConsolidationJob(Base):
    __tablename__ = "consolidation_jobs"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        UniqueConstraint("owner_id", "scope_id", "kind", "input_hash"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        CheckConstraint(
            "kind IN ('episode','proposals','lexical_rebuild')", name="consolidation_kind"
        ),
        CheckConstraint(
            "status IN ('queued','running','completed','failed','stale')",
            name="consolidation_status",
        ),
        CheckConstraint(
            "checkpoint IN ('reserved','claimed','published','terminal')",
            name="consolidation_checkpoint",
        ),
        CheckConstraint("attempt >= 0 AND attempt <= 3", name="consolidation_attempt"),
        CheckConstraint(
            "(status IN ('completed','failed','stale') AND receipt IS NOT NULL AND finished_at IS NOT NULL AND lease_until IS NULL) OR (status IN ('queued','running') AND receipt IS NULL AND finished_at IS NULL)",
            name="consolidation_receipt",
        ),
        Index("consolidation_queue", "status", "created_at", "owner_id", "id"),
        Index("consolidation_owner", "owner_id", "scope_id", "created_at", "id"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    kind: Mapped[str] = mapped_column(String(20))
    version: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    write_hash: Mapped[str] = mapped_column(String(64))
    input_hash: Mapped[str] = mapped_column(String(64))
    input: Mapped[dict] = mapped_column(JSON)
    snapshot: Mapped[list] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20))
    checkpoint: Mapped[str] = mapped_column(String(20))
    attempt: Mapped[int] = mapped_column(Integer)
    lease_until: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger)
    started_at: Mapped[int | None] = mapped_column(BigInteger)
    finished_at: Mapped[int | None] = mapped_column(BigInteger)
    error_code: Mapped[str | None] = mapped_column(String(40))
    receipt: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))


class ConsolidationSource(Base):
    __tablename__ = "consolidation_sources"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "job_id"],
            ["consolidation_jobs.owner_id", "consolidation_jobs.scope_id", "consolidation_jobs.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "event_id"],
            ["events.owner_id", "events.conversation_id", "events.id"],
        ),
        CheckConstraint(
            "(conversation_id IS NULL AND event_id IS NULL) OR (conversation_id IS NOT NULL AND event_id IS NOT NULL)",
            name="consolidation_event_reference",
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ordinal: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    source_version_id: Mapped[str] = mapped_column(String(36))
    conversation_id: Mapped[str | None] = mapped_column(String(36))
    event_id: Mapped[str | None] = mapped_column(String(36))
    source_hash: Mapped[str] = mapped_column(String(64))


class Episode(Base):
    __tablename__ = "episodes"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        UniqueConstraint("owner_id", "job_id"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "job_id"],
            ["consolidation_jobs.owner_id", "consolidation_jobs.scope_id", "consolidation_jobs.id"],
        ),
        CheckConstraint(
            "range_end > range_start AND trust_class = 'model_generated'",
            name="episode_generated_range",
        ),
        Index("episode_owner", "owner_id", "scope_id", "created_at", "id"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    job_id: Mapped[str] = mapped_column(String(36))
    summary_version: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    trust_class: Mapped[str] = mapped_column(String(30))
    summary: Mapped[dict] = mapped_column(JSON)
    sources: Mapped[list] = mapped_column(JSON)
    range_start: Mapped[int] = mapped_column(BigInteger)
    range_end: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger)


class EpisodeContext(Base):
    __tablename__ = "episode_contexts"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    snapshot: Mapped[dict] = mapped_column(JSON)
