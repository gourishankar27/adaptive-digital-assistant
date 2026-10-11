"""Private agent history, exact approvals and immutable tool receipts."""

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        CheckConstraint(
            "status IN ('running','pending_approval','completed','failed','unknown')",
            name="agent_run_status",
        ),
        CheckConstraint("generation >= 1", name="agent_generation"),
        CheckConstraint(
            "(status = 'completed' AND response IS NOT NULL AND error_code IS NULL) OR (status <> 'completed' AND response IS NULL)",
            name="agent_run_response",
        ),
        Index("agent_owner_created", "owner_id", "scope_id", "created_at", "id"),
        Index("agent_monitor_created", "created_at", "status"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    conversation_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    input: Mapped[dict] = mapped_column(JSON)
    protocol_version: Mapped[str] = mapped_column(String(40))
    protocol_snapshot: Mapped[dict] = mapped_column(JSON)
    messages: Mapped[list] = mapped_column(JSON)
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(24))
    response: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(40))
    generation: Mapped[int] = mapped_column(Integer)
    lease_until: Mapped[int | None] = mapped_column(BigInteger)
    as_of: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger)
    finished_at: Mapped[int | None] = mapped_column(BigInteger)


class AgentStep(Base):
    __tablename__ = "agent_steps"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "run_id", "id"),
        UniqueConstraint("owner_id", "run_id", "number"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id"],
            ["agent_runs.owner_id", "agent_runs.scope_id", "agent_runs.id"],
        ),
        CheckConstraint("number >= 1 AND number <= 5 AND attempt >= 1", name="agent_step_bound"),
        CheckConstraint(
            "status IN ('model','pending_approval','executing','completed','failed','unknown','revoked')",
            name="agent_step_status",
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    number: Mapped[int] = mapped_column(Integer)
    attempt: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24))
    tool: Mapped[str | None] = mapped_column(String(40))
    tool_version: Mapped[str | None] = mapped_column(String(40))
    arguments: Mapped[dict | None] = mapped_column(JSON)
    argument_hash: Mapped[str | None] = mapped_column(String(64))
    preview_hash: Mapped[str | None] = mapped_column(String(64))
    model_message: Mapped[dict | None] = mapped_column(JSON)
    expires_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger)
    finished_at: Mapped[int | None] = mapped_column(BigInteger)


class AgentApproval(Base):
    __tablename__ = "agent_approvals"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "run_id", "step_id", "id"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id", "step_id"],
            [
                "agent_steps.owner_id",
                "agent_steps.scope_id",
                "agent_steps.run_id",
                "agent_steps.id",
            ],
        ),
        CheckConstraint("actor_id = owner_id", name="agent_approval_actor"),
        CheckConstraint(
            "decision IN ('approve','revoke','recover')", name="agent_approval_decision"
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    run_id: Mapped[str] = mapped_column(String(36))
    step_id: Mapped[str] = mapped_column(String(36))
    actor_id: Mapped[str] = mapped_column(String(36))
    decision: Mapped[str] = mapped_column(String(16))
    input_hash: Mapped[str] = mapped_column(String(64))
    argument_hash: Mapped[str | None] = mapped_column(String(64))
    preview_hash: Mapped[str | None] = mapped_column(String(64))
    tool_version: Mapped[str | None] = mapped_column(String(40))
    result: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)


class AgentReceipt(Base):
    __tablename__ = "agent_receipts"
    __table_args__ = (
        UniqueConstraint("owner_id", "step_id"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id", "step_id", "approval_id"],
            [
                "agent_approvals.owner_id",
                "agent_approvals.scope_id",
                "agent_approvals.run_id",
                "agent_approvals.step_id",
                "agent_approvals.id",
            ],
        ),
        CheckConstraint(
            "outcome IN ('completed','failed','unknown','revoked')", name="agent_receipt_outcome"
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    run_id: Mapped[str] = mapped_column(String(36))
    step_id: Mapped[str] = mapped_column(String(36))
    approval_id: Mapped[str] = mapped_column(String(36))
    outcome: Mapped[str] = mapped_column(String(16))
    snapshot: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
