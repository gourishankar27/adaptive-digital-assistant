"""Versioned text-PDF extraction on existing immutable upload records."""

import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "edge_devices",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("epoch", sa.BigInteger(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("last_sequence", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("public_key", sa.String(length=256), nullable=False),
        sa.Column("enrollment_id", sa.String(length=36), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("revoked_at", sa.BigInteger(), nullable=True),
        sa.Column("revocation_id", sa.String(length=36), nullable=True),
        sa.Column("revocation_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "revision>=1 AND last_sequence>=0 AND epoch>=0", name="edge_device_counters"
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("owner_id", "id"),
    )
    op.create_table(
        "edge_proposals",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_id", sa.String(length=36), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("epoch", sa.BigInteger(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("output", sa.Text(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("sequence>=1 AND epoch>=0", name="edge_proposal_counters"),
        sa.ForeignKeyConstraint(
            ["owner_id", "device_id"], ["edge_devices.owner_id", "edge_devices.id"]
        ),
        sa.ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        sa.PrimaryKeyConstraint("owner_id", "id"),
        sa.UniqueConstraint("owner_id", "device_id", "sequence", name="edge_proposal_sequence"),
    )
    op.add_column("document_uploads", sa.Column("extraction", sa.JSON(), nullable=True))


def downgrade():
    for table in ("edge_proposals", "edge_devices"):
        if op.get_bind().execute(sa.text("SELECT 1 FROM " + table + " LIMIT 1")).first():
            raise RuntimeError(
                "Device draft history cannot be downgraded; restore a verified backup"
            )
    if (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT 1 FROM document_uploads WHERE media_type='application/pdf' OR extraction IS NOT NULL LIMIT 1"
            )
        )
        .first()
    ):
        raise RuntimeError("PDF history cannot be downgraded; restore a verified backup")
    crossed = {
        step.revision.revision
        for step in ScriptDirectory.from_config(context.config)._downgrade_revs(
            context.get_context().opts["destination_rev"], revision
        )
    }
    if "0020" in crossed:
        _preflight_previous()
    op.drop_column("document_uploads", "extraction")
    op.drop_table("edge_proposals")
    op.drop_table("edge_devices")


def _preflight_previous():
    if context.is_offline_mode():
        raise RuntimeError("Work history downgrade requires online inspection")
    for table in ("work_items", "work_revisions", "work_receipts", "work_briefs"):
        if op.get_bind().execute(sa.text("SELECT COUNT(*) FROM " + table)).scalar():
            raise RuntimeError("Work history cannot be discarded by downgrade")
    crossed = {
        step.revision.revision
        for step in ScriptDirectory.from_config(context.config)._downgrade_revs(
            context.get_context().opts["destination_rev"], revision
        )
    }
    if "0019" in crossed:
        for table in (
            "reflection_artifacts",
            "reflection_runs",
            "reflection_receipts",
            "reflection_policies",
            "reflection_provider_state",
        ):
            if op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                raise RuntimeError(
                    "Reflection consent/artifact/safety history cannot be downgraded automatically"
                )
        if (
            op.get_bind()
            .execute(sa.text("SELECT 1 FROM admin_audit WHERE action='monitor.reflection' LIMIT 1"))
            .first()
        ):
            raise RuntimeError("Reflection audit history cannot be downgraded automatically")
        crossed = {
            step.revision.revision
            for step in ScriptDirectory.from_config(context.config)._downgrade_revs(
                context.get_context().opts["destination_rev"], revision
            )
        }
        if "0018" in crossed:
            if context.is_offline_mode():
                raise RuntimeError("Schedule downgrade requires online history preflight")
            if (
                op.get_bind()
                .execute(
                    sa.text("SELECT 1 FROM admin_audit WHERE action='monitor.scheduling' LIMIT 1")
                )
                .first()
            ):
                raise RuntimeError("Schedule audit history cannot be downgraded automatically")
            for table in (
                "schedule_inbox",
                "schedule_occurrences",
                "schedules",
                "schedule_receipts",
                "schedule_consents",
            ):
                if op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                    raise RuntimeError("Schedule history cannot be downgraded automatically")
            crossed = {
                step.revision.revision
                for step in ScriptDirectory.from_config(context.config)._downgrade_revs(
                    context.get_context().opts["destination_rev"], revision
                )
            }
            if "0017" in crossed:
                if context.is_offline_mode():
                    raise RuntimeError("Curiosity downgrade requires online history preflight")
                for table in ("curiosity_questions", "curiosity_receipts", "curiosity_policies"):
                    if op.get_bind().scalar(sa.text(f"SELECT COUNT(*) FROM {table}")):
                        raise RuntimeError("Curiosity history cannot be downgraded automatically")
                crossed = {
                    step.revision.revision
                    for step in ScriptDirectory.from_config(context.config)._downgrade_revs(
                        context.get_context().opts["destination_rev"], revision
                    )
                }
                if "0016" in crossed:
                    for table in ("password_credentials", "login_sessions", "refresh_verifiers"):
                        if op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                            raise RuntimeError(
                                "Credential history cannot be downgraded automatically"
                            )
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
                            raise RuntimeError(
                                "Cannot downgrade populated security or deletion history."
                            )
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
                    if (
                        "0014" in crossed
                        and db.execute(sa.text("SELECT 1 FROM voice_inputs LIMIT 1")).first()
                    ):
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
                            sa.text(
                                "SELECT 1 FROM requests WHERE learning_snapshot IS NOT NULL LIMIT 1"
                            )
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
                            (
                                "memory_extractions",
                                "memory_proposals",
                                "memory_reviews",
                                "claim_support",
                            ),
                            "0008 contains review history",
                        ),
                        "0006": (
                            ("entities", "entity_operations", "claim_entity_links"),
                            "Entity history exists; refusing a lossy downgrade",
                        ),
                        "0005": (
                            ("document_uploads",),
                            "Document evidence exists; refusing a lossy downgrade",
                        ),
                    }
                    for step, (tables, message) in guards.items():
                        if step in crossed:
                            for table in tables:
                                if db.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                                    raise RuntimeError(message + "; restore a verified backup")
