"""Private idle-work grants, leased units and generated review artifacts."""

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


class ReflectionPolicy(Base):
    __tablename__ = "reflection_policies"
    __table_args__ = (
        CheckConstraint("revision >= 1 AND epoch >= 0", name="reflection_policy_counters"),
        CheckConstraint("origin_kind IN ('legacy','device','password')", name="reflection_origin"),
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer)
    version: Mapped[str] = mapped_column(String(40))
    enabled: Mapped[bool] = mapped_column(Boolean)
    epoch: Mapped[int] = mapped_column(BigInteger)
    consent_revision: Mapped[int] = mapped_column(Integer)
    origin_kind: Mapped[str] = mapped_column(String(12))
    origin_id: Mapped[str] = mapped_column(String(36))
    settings: Mapped[dict] = mapped_column(JSON)
    last_decision: Mapped[str | None] = mapped_column(String(64))
    updated_at: Mapped[int] = mapped_column(BigInteger)


class ReflectionRun(Base):
    __tablename__ = "reflection_runs"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        CheckConstraint("kind IN ('report','question','summary')", name="reflection_kind"),
        CheckConstraint(
            "status IN ('queued','running','completed','suppressed','failed','quarantined')",
            name="reflection_run_status",
        ),
        CheckConstraint(
            "attempt >= 0 AND attempt <= 3 AND charged_ms >= 0 AND revision >= 1 AND epoch >= 0",
            name="reflection_run_counters",
        ),
        CheckConstraint(
            "(status = 'running' AND lease_until IS NOT NULL AND lease_token IS NOT NULL) OR (status != 'running' AND lease_until IS NULL AND lease_token IS NULL)",
            name="reflection_run_lease",
        ),
        Index("reflection_queue", "status", "created_at", "owner_id", "id"),
        Index("reflection_budget", "owner_id", "budget_day"),
    )
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("reflection_policies.owner_id"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    revision: Mapped[int] = mapped_column(Integer)
    epoch: Mapped[int] = mapped_column(BigInteger)
    kind: Mapped[str] = mapped_column(String(12))
    policy_hash: Mapped[str] = mapped_column(String(64))
    question_revision: Mapped[int | None] = mapped_column(Integer)
    provider_key: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16))
    reason: Mapped[str | None] = mapped_column(String(64))
    attempt: Mapped[int] = mapped_column(Integer)
    lease_token: Mapped[str | None] = mapped_column(String(36))
    lease_until: Mapped[int | None] = mapped_column(BigInteger)
    budget_day: Mapped[str] = mapped_column(String(10))
    charged_ms: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
    snapshot: Mapped[list | None] = mapped_column(JSON(none_as_null=True))
    pins: Mapped[list | None] = mapped_column(JSON(none_as_null=True))
    omissions: Mapped[dict] = mapped_column(JSON)
    artifact_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger)
    started_at: Mapped[int | None] = mapped_column(BigInteger)
    finished_at: Mapped[int | None] = mapped_column(BigInteger)
    elapsed_ms: Mapped[int | None] = mapped_column(BigInteger)
    model_elapsed_ms: Mapped[int | None] = mapped_column(BigInteger)


class ReflectionArtifact(Base):
    __tablename__ = "reflection_artifacts"
    __table_args__ = (
        UniqueConstraint("owner_id", "run_id"),
        UniqueConstraint("owner_id", "question_template", name="reflection_owner_template"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id"],
            ["reflection_runs.owner_id", "reflection_runs.scope_id", "reflection_runs.id"],
        ),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        CheckConstraint("kind IN ('report','question','summary')", name="reflection_artifact_kind"),
        CheckConstraint(
            "status IN ('pending','kept','dismissed')", name="reflection_artifact_status"
        ),
        Index("reflection_review", "owner_id", "created_at", "id"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    run_id: Mapped[str] = mapped_column(String(36))
    epoch: Mapped[int] = mapped_column(BigInteger)
    kind: Mapped[str] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(12))
    rationale: Mapped[str] = mapped_column(String(64))
    question_template: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    sources: Mapped[list] = mapped_column(JSON)
    omissions: Mapped[dict] = mapped_column(JSON)
    episode_id: Mapped[str | None] = mapped_column(String(36))
    question_id: Mapped[str | None] = mapped_column(String(36))
    conversation_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger)
    elapsed_ms: Mapped[int] = mapped_column(BigInteger)
    model_elapsed_ms: Mapped[int | None] = mapped_column(BigInteger)


class ReflectionReceipt(Base):
    __tablename__ = "reflection_receipts"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)


class ReflectionProviderState(Base):
    """Non-content safety attestation; an owner erasure cannot reset a model ban."""

    __tablename__ = "reflection_provider_state"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ready: Mapped[bool] = mapped_column(Boolean)
    reason: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[int] = mapped_column(BigInteger)
