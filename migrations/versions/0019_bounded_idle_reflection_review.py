"""bounded idle reflection review"""

import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "reflection_provider_state",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("ready", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=False),
        sa.Column("observed_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "reflection_policies",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("epoch", sa.BigInteger(), nullable=False),
        sa.Column("consent_revision", sa.Integer(), nullable=False),
        sa.Column("origin_kind", sa.String(length=12), nullable=False),
        sa.Column("origin_id", sa.String(length=36), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("last_decision", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "origin_kind IN ('legacy','device','password')", name="reflection_origin"
        ),
        sa.CheckConstraint("revision >= 1 AND epoch >= 0", name="reflection_policy_counters"),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("owner_id"),
    )
    op.create_table(
        "reflection_receipts",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("owner_id", "id"),
    )
    op.create_table(
        "reflection_runs",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_id", sa.String(length=36), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("epoch", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("policy_hash", sa.String(length=64), nullable=False),
        sa.Column("question_revision", sa.Integer(), nullable=True),
        sa.Column("provider_key", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=True),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("lease_token", sa.String(length=36), nullable=True),
        sa.Column("lease_until", sa.BigInteger(), nullable=True),
        sa.Column("budget_day", sa.String(length=10), nullable=False),
        sa.Column("charged_ms", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
        sa.Column("snapshot", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("pins", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("omissions", sa.JSON(), nullable=False),
        sa.Column("artifact_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("started_at", sa.BigInteger(), nullable=True),
        sa.Column("finished_at", sa.BigInteger(), nullable=True),
        sa.Column("elapsed_ms", sa.BigInteger(), nullable=True),
        sa.Column("model_elapsed_ms", sa.BigInteger(), nullable=True),
        sa.CheckConstraint(
            "(status = 'running' AND lease_until IS NOT NULL AND lease_token IS NOT NULL) OR (status != 'running' AND lease_until IS NULL AND lease_token IS NULL)",
            name="reflection_run_lease",
        ),
        sa.CheckConstraint("kind IN ('report','question','summary')", name="reflection_kind"),
        sa.CheckConstraint(
            "status IN ('queued','running','completed','suppressed','failed','quarantined')",
            name="reflection_run_status",
        ),
        sa.CheckConstraint(
            "attempt >= 0 AND attempt <= 3 AND charged_ms >= 0 AND revision >= 1 AND epoch >= 0",
            name="reflection_run_counters",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id"],
            ["scopes.owner_id", "scopes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["reflection_policies.owner_id"],
        ),
        sa.PrimaryKeyConstraint("owner_id", "id"),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
    )
    op.create_index(
        "reflection_budget", "reflection_runs", ["owner_id", "budget_day"], unique=False
    )
    op.create_index(
        "reflection_queue",
        "reflection_runs",
        ["status", "created_at", "owner_id", "id"],
        unique=False,
    )
    op.create_table(
        "reflection_artifacts",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("epoch", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("rationale", sa.String(length=64), nullable=False),
        sa.Column("question_template", sa.String(length=50), nullable=True),
        sa.Column("content", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("omissions", sa.JSON(), nullable=False),
        sa.Column("episode_id", sa.String(length=36), nullable=True),
        sa.Column("question_id", sa.String(length=36), nullable=True),
        sa.Column("conversation_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("elapsed_ms", sa.BigInteger(), nullable=False),
        sa.Column("model_elapsed_ms", sa.BigInteger(), nullable=True),
        sa.CheckConstraint(
            "kind IN ('report','question','summary')", name="reflection_artifact_kind"
        ),
        sa.CheckConstraint(
            "status IN ('pending','kept','dismissed')", name="reflection_artifact_status"
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "run_id"],
            ["reflection_runs.owner_id", "reflection_runs.scope_id", "reflection_runs.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id"],
            ["scopes.owner_id", "scopes.id"],
        ),
        sa.PrimaryKeyConstraint("owner_id", "id"),
        sa.UniqueConstraint("owner_id", "run_id"),
        sa.UniqueConstraint("owner_id", "question_template", name="reflection_owner_template"),
    )
    op.create_index(
        "reflection_review", "reflection_artifacts", ["owner_id", "created_at", "id"], unique=False
    )
    with op.batch_alter_table("admin_audit") as batch:
        batch.drop_constraint("admin_audit_action", type_="check")
        batch.create_check_constraint(
            "admin_audit_action",
            "action IN ('role.grant', 'role.revoke', 'monitor.me', 'monitor.overview', 'monitor.requests', 'monitor.request', 'monitor.providers', 'monitor.audit', 'monitor.scheduling', 'monitor.reflection')",
        )


def downgrade():
    if context.is_offline_mode():
        raise RuntimeError("Reflection downgrade requires online history preflight")
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
            .execute(sa.text("SELECT 1 FROM admin_audit WHERE action='monitor.scheduling' LIMIT 1"))
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
                # Preserve every lower history guard before any SQLite/nontransactional DDL.
                for step, (tables, message) in guards.items():
                    if step in crossed:
                        for table in tables:
                            if db.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                                raise RuntimeError(message + "; restore a verified backup")
    with op.batch_alter_table("admin_audit") as batch:
        batch.drop_constraint("admin_audit_action", type_="check")
        batch.create_check_constraint(
            "admin_audit_action",
            "action IN ('role.grant', 'role.revoke', 'monitor.me', 'monitor.overview', 'monitor.requests', 'monitor.request', 'monitor.providers', 'monitor.audit', 'monitor.scheduling')",
        )
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("reflection_review", table_name="reflection_artifacts")
    op.drop_table("reflection_artifacts")
    op.drop_index("reflection_queue", table_name="reflection_runs")
    op.drop_index("reflection_budget", table_name="reflection_runs")
    op.drop_table("reflection_runs")
    op.drop_table("reflection_receipts")
    op.drop_table("reflection_policies")
    op.drop_table("reflection_provider_state")
    # ### end Alembic commands ###
