"""Scoped read-only agent runs, fenced steps, exact approvals and receipts."""

import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def string(name, width=36, nullable=False, primary_key=False):
    return sa.Column(name, sa.String(width), nullable=nullable, primary_key=primary_key)


def upgrade():
    op.create_table(
        "agent_runs",
        string("owner_id", primary_key=True),
        string("id", primary_key=True),
        string("scope_id"),
        string("conversation_id"),
        string("input_hash", 64),
        sa.Column("input", sa.JSON(), nullable=False),
        string("protocol_version", 40),
        sa.Column("protocol_snapshot", sa.JSON(), nullable=False),
        sa.Column("messages", sa.JSON(), nullable=False),
        string("provider", 40),
        string("model", 120),
        string("status", 24),
        sa.Column("response", sa.Text(), nullable=True),
        string("error_code", 40, nullable=True),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("lease_until", sa.BigInteger(), nullable=True),
        sa.Column("as_of", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("finished_at", sa.BigInteger(), nullable=True),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        sa.CheckConstraint(
            "status IN ('running','pending_approval','completed','failed','unknown')",
            name="agent_run_status",
        ),
        sa.CheckConstraint("generation >= 1", name="agent_generation"),
        sa.CheckConstraint(
            "(status = 'completed' AND response IS NOT NULL AND error_code IS NULL) OR (status <> 'completed' AND response IS NULL)",
            name="agent_run_response",
        ),
    )
    op.create_index(
        "agent_owner_created", "agent_runs", ["owner_id", "scope_id", "created_at", "id"]
    )
    op.create_index("agent_monitor_created", "agent_runs", ["created_at", "status"])
    op.create_table(
        "agent_steps",
        string("owner_id", primary_key=True),
        string("id", primary_key=True),
        string("run_id"),
        string("scope_id"),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        string("status", 24),
        string("tool", 40, nullable=True),
        string("tool_version", 40, nullable=True),
        sa.Column("arguments", sa.JSON(), nullable=True),
        string("argument_hash", 64, nullable=True),
        string("preview_hash", 64, nullable=True),
        sa.Column("model_message", sa.JSON(), nullable=True),
        sa.Column("expires_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("finished_at", sa.BigInteger(), nullable=True),
        sa.UniqueConstraint("owner_id", "scope_id", "run_id", "id"),
        sa.UniqueConstraint("owner_id", "run_id", "number"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id"],
            ["agent_runs.owner_id", "agent_runs.scope_id", "agent_runs.id"],
        ),
        sa.CheckConstraint("number >= 1 AND number <= 5 AND attempt >= 1", name="agent_step_bound"),
        sa.CheckConstraint(
            "status IN ('model','pending_approval','executing','completed','failed','unknown','revoked')",
            name="agent_step_status",
        ),
    )
    op.create_table(
        "agent_approvals",
        string("owner_id", primary_key=True),
        string("id", primary_key=True),
        string("scope_id"),
        string("run_id"),
        string("step_id"),
        string("actor_id"),
        string("decision", 16),
        string("input_hash", 64),
        string("argument_hash", 64, nullable=True),
        string("preview_hash", 64, nullable=True),
        string("tool_version", 40, nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint("owner_id", "scope_id", "run_id", "step_id", "id"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id", "step_id"],
            [
                "agent_steps.owner_id",
                "agent_steps.scope_id",
                "agent_steps.run_id",
                "agent_steps.id",
            ],
        ),
        sa.CheckConstraint("actor_id = owner_id", name="agent_approval_actor"),
        sa.CheckConstraint(
            "decision IN ('approve','revoke','recover')", name="agent_approval_decision"
        ),
    )
    op.create_table(
        "agent_receipts",
        string("owner_id", primary_key=True),
        string("id", primary_key=True),
        string("scope_id"),
        string("run_id"),
        string("step_id"),
        string("approval_id"),
        string("outcome", 16),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint("owner_id", "step_id"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id", "step_id", "approval_id"],
            [
                "agent_approvals.owner_id",
                "agent_approvals.scope_id",
                "agent_approvals.run_id",
                "agent_approvals.step_id",
                "agent_approvals.id",
            ],
        ),
        sa.CheckConstraint(
            "outcome IN ('completed','failed','unknown','revoked')", name="agent_receipt_outcome"
        ),
    )


def downgrade():
    if context.is_offline_mode():
        raise RuntimeError("Agent downgrade requires an online history preflight.")
    # SQLite DDL is not transactionally rolled back when a lower revision refuses.
    # Preflight the already-existing 0008 guard before removing any 0009 table.
    steps = ScriptDirectory.from_config(context.config)._downgrade_revs(
        context.get_context().opts["destination_rev"], revision
    )
    if any(step.revision.revision == "0008" for step in steps) and any(
        op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first()
        for table in ("memory_extractions", "memory_proposals", "memory_reviews", "claim_support")
    ):
        raise RuntimeError("0008 contains review history; restore a verified backup instead")
    if op.get_bind().execute(sa.text("SELECT 1 FROM agent_runs LIMIT 1")).first():
        raise RuntimeError(
            "Populated agent history cannot be downgraded; restore a verified backup."
        )
    for table in ("agent_receipts", "agent_approvals", "agent_steps", "agent_runs"):
        op.drop_table(table)
