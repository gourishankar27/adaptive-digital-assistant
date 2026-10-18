"""Owned opt-in curiosity, immutable question context and exact operation receipts."""

import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory

revision = "0017"
down_revision = "0016"
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "curiosity_policies",
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        *[
            sa.Column(k, sa.JSON(), nullable=False)
            for k in ("settings", "suppressed", "daily", "metrics")
        ],
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("revision >= 1", name="curiosity_policy_revision"),
    )
    op.create_table(
        "curiosity_questions",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_id", sa.String(36), nullable=False),
        *[
            sa.Column(k, sa.String(36), nullable=True)
            for k in (
                "conversation_id",
                "opened_conversation_id",
                "request_id",
                "answer_request_id",
                "source_version_id",
            )
        ],
        sa.Column("channel", sa.String(12), nullable=False),
        sa.Column("topic", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("template_key", sa.String(50), nullable=False),
        sa.Column("policy_revision", sa.Integer(), nullable=False),
        sa.Column("epoch", sa.BigInteger(), nullable=False),
        sa.Column("payload", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("feedback", sa.String(12), nullable=True),
        *[
            sa.Column(k, sa.BigInteger(), nullable=False)
            for k in ("created_at", "expires_at", "available_at")
        ],
        sa.Column("closed_at", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "opened_conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        sa.ForeignKeyConstraint(["owner_id", "request_id"], ["requests.owner_id", "requests.id"]),
        sa.ForeignKeyConstraint(
            ["owner_id", "answer_request_id"],
            ["requests.owner_id", "requests.id"],
            name="curiosity_answer_request",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        sa.UniqueConstraint("owner_id", "request_id", name="curiosity_one_per_reply"),
        sa.CheckConstraint(
            "channel IN ('chat','inbox') AND topic IN ('interests','work','routines','relationships','reflection')",
            name="curiosity_channel_topic",
        ),
        sa.CheckConstraint(
            "status IN ('pending','offered','opened','answering','answered','skipped','dismissed','revoked','expired','deferred')",
            name="curiosity_question_state",
        ),
        sa.CheckConstraint(
            "expires_at > created_at AND policy_revision >= 1", name="curiosity_expiry"
        ),
    )
    op.create_index(
        "curiosity_owner_inbox",
        "curiosity_questions",
        ["owner_id", "channel", "status", "created_at"],
    )
    op.create_table(
        "curiosity_receipts",
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
    )


def downgrade():
    if context.is_offline_mode():
        raise RuntimeError("Curiosity downgrade requires online history preflight")
    for table in ("curiosity_questions", "curiosity_receipts", "curiosity_policies"):
        if op.get_bind().scalar(sa.text(f"SELECT COUNT(*) FROM {table}")):
            raise RuntimeError("Curiosity history cannot be downgraded automatically")
    # Preserve released lower guards before SQLite can commit any destructive DDL.
    crossed = {
        step.revision.revision
        for step in ScriptDirectory.from_config(context.config)._downgrade_revs(
            context.get_context().opts["destination_rev"], revision
        )
    }
    if "0016" in crossed:
        for table in ("password_credentials", "login_sessions", "refresh_verifiers"):
            if op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                raise RuntimeError("Credential history cannot be downgraded automatically")
        if context.is_offline_mode():
            raise RuntimeError("Security downgrade requires online history preflight")
        connection = op.get_bind()
        for table in (
            "device_credentials",
            "deletion_jobs",
            "deletion_previews",
            "deleted_requests",
        ):
            if connection.scalar(sa.text(f"SELECT COUNT(*) FROM {table}")):
                raise RuntimeError("Cannot downgrade populated security or deletion history.")
        if connection.scalar(
            sa.text(
                "SELECT COUNT(*) FROM users WHERE data_epoch <> 0 OR deletion_job_id IS NOT NULL"
            )
        ):
            raise RuntimeError("Cannot downgrade retained deletion state.")
        db = connection
        steps = ScriptDirectory.from_config(context.config)._downgrade_revs(
            context.get_context().opts["destination_rev"], revision
        )
        crossed = {step.revision.revision for step in steps}
        if "0014" in crossed and db.execute(sa.text("SELECT 1 FROM voice_inputs LIMIT 1")).first():
            raise RuntimeError(
                "Reviewed voice history cannot be downgraded; restore a verified backup"
            )
        if "0013" in crossed:
            for table in ("stream_attempts", "stream_events"):
                if db.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                    raise RuntimeError(
                        "Streaming history cannot be downgraded; restore a verified backup"
                    )
        if "0012" in crossed:
            for table in (
                "learning_enrollments",
                "learning_receipts",
                "interaction_observations",
                "interaction_proposals",
                "learned_preferences",
            ):
                if db.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                    raise RuntimeError(
                        "Learning history cannot be downgraded; restore a verified backup"
                    )
            if db.execute(
                sa.text("SELECT 1 FROM requests WHERE learning_snapshot IS NOT NULL LIMIT 1")
            ).first():
                raise RuntimeError(
                    "Learning request history cannot be downgraded; restore a verified backup"
                )
        if "0011" in crossed:
            for query in (
                "SELECT 1 FROM expression_preferences LIMIT 1",
                "SELECT 1 FROM expression_receipts LIMIT 1",
                "SELECT 1 FROM expression_sessions LIMIT 1",
                "SELECT 1 FROM expression_bindings WHERE active LIMIT 1",
                "SELECT 1 FROM requests WHERE expression_snapshot IS NOT NULL LIMIT 1",
            ):
                if db.execute(sa.text(query)).first():
                    raise RuntimeError(
                        "Expression history cannot be downgraded; restore a verified backup"
                    )
        if (
            "0005" in crossed
            and db.execute(
                sa.text("SELECT 1 FROM sources WHERE kind='imported_document' LIMIT 1")
            ).first()
        ):
            raise RuntimeError(
                "Document evidence exists; refusing a lossy downgrade; restore a verified backup"
            )
        guards = {
            "0010": (
                ("consolidation_jobs", "episode_contexts"),
                "Populated consolidation history cannot be downgraded",
            ),
            "0009": (("agent_runs",), "Populated agent history cannot be downgraded"),
            "0008": (
                ("memory_extractions", "memory_proposals", "memory_reviews", "claim_support"),
                "0008 contains review history",
            ),
            "0006": (
                ("entities", "entity_operations", "claim_entity_links"),
                "Entity history exists; refusing a lossy downgrade",
            ),
            "0005": (("document_uploads",), "Document evidence exists; refusing a lossy downgrade"),
        }
        # Preserve every lower history guard before any SQLite/nontransactional DDL.
        for step, (tables, message) in guards.items():
            if step in crossed:
                for table in tables:
                    if db.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                        raise RuntimeError(message + "; restore a verified backup")
    op.drop_table("curiosity_receipts")
    op.drop_index("curiosity_owner_inbox", table_name="curiosity_questions")
    op.drop_table("curiosity_questions")
    op.drop_table("curiosity_policies")
