"""Explicit password enrollment and revocable digest-only session families."""

import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory

revision = "0016"
down_revision = "0015"
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "password_credentials",
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("login", sa.String(160), nullable=False, unique=True),
        sa.Column("verifier", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "login_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("label", sa.String(80), nullable=False),
        sa.Column("access_hash", sa.String(64), nullable=False, unique=True),
        *[
            sa.Column(name, sa.BigInteger(), nullable=False)
            for name in (
                "created_at",
                "access_expires_at",
                "expires_at",
                "idle_expires_at",
                "generation",
            )
        ],
        sa.Column("revoked_at", sa.BigInteger(), nullable=True),
    )
    op.create_index("ix_login_sessions_owner_id", "login_sessions", ["owner_id"])
    op.create_table(
        "refresh_verifiers",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column("family_id", sa.String(36), sa.ForeignKey("login_sessions.id"), nullable=False),
        sa.Column("used_at", sa.BigInteger(), nullable=True),
    )
    op.create_index("ix_refresh_verifiers_family_id", "refresh_verifiers", ["family_id"])


def downgrade():
    if context.is_offline_mode():
        raise RuntimeError("Password downgrade requires online preflight")
    for table in ("password_credentials", "login_sessions", "refresh_verifiers"):
        if op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
            raise RuntimeError("Credential history cannot be downgraded automatically")
    if context.is_offline_mode():
        raise RuntimeError("Security downgrade requires online history preflight")
    connection = op.get_bind()
    for table in ("device_credentials", "deletion_jobs", "deletion_previews", "deleted_requests"):
        if connection.scalar(sa.text(f"SELECT COUNT(*) FROM {table}")):
            raise RuntimeError("Cannot downgrade populated security or deletion history.")
    if connection.scalar(
        sa.text("SELECT COUNT(*) FROM users WHERE data_epoch <> 0 OR deletion_job_id IS NOT NULL")
    ):
        raise RuntimeError("Cannot downgrade retained deletion state.")
    db = connection
    steps = ScriptDirectory.from_config(context.config)._downgrade_revs(
        context.get_context().opts["destination_rev"], revision
    )
    crossed = {step.revision.revision for step in steps}
    if "0014" in crossed and db.execute(sa.text("SELECT 1 FROM voice_inputs LIMIT 1")).first():
        raise RuntimeError("Reviewed voice history cannot be downgraded; restore a verified backup")
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
    for table in ("refresh_verifiers", "login_sessions", "password_credentials"):
        op.drop_table(table)
