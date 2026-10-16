"""Owner-bound device credentials and explicit saved-content deletion metadata."""

import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("data_revision", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column(
        "users",
        sa.Column("data_epoch", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("users", sa.Column("deletion_job_id", sa.String(36), nullable=True))
    op.create_table(
        "device_credentials",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("label", sa.String(80), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
        sa.Column("last_used_at", sa.BigInteger()),
        sa.Column("revoked_at", sa.BigInteger()),
        sa.Column("rotated_from_id", sa.String(36)),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.UniqueConstraint("owner_id", "id"),
        sa.UniqueConstraint("token_hash"),
        sa.CheckConstraint("expires_at > created_at", name="device_credential_expiry"),
    )
    op.create_index(
        "device_credential_owner", "device_credentials", ["owner_id", "created_at", "id"]
    )
    op.create_table(
        "deletion_previews",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
        sa.Column("counts", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
    )
    op.create_table(
        "deletion_jobs",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("preview_id", sa.String(36), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("counts", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempt", sa.BigInteger(), nullable=False),
        sa.Column("lease_until", sa.BigInteger()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("finished_at", sa.BigInteger()),
        sa.Column("error_code", sa.String(40)),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.CheckConstraint(
            "status IN ('queued','running','completed','failed')", name="deletion_status"
        ),
        sa.CheckConstraint("attempt BETWEEN 0 AND 3", name="deletion_attempt"),
    )
    op.create_index("deletion_queue", "deletion_jobs", ["status", "created_at"])
    op.create_table(
        "deleted_requests",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("request_id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), nullable=False),
        sa.Column("deleted_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
    )


def downgrade():
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
    for table in ("deleted_requests", "deletion_jobs", "deletion_previews", "device_credentials"):
        op.drop_table(table)
    for column in ("deletion_job_id", "data_epoch", "data_revision"):
        op.drop_column("users", column)
