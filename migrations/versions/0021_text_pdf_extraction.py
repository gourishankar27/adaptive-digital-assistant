"""Versioned text-PDF extraction on existing immutable upload records."""
import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory
revision="0021"
down_revision="0020"
branch_labels=None
depends_on=None

def upgrade():
    op.add_column("document_uploads",sa.Column("extraction",sa.JSON(),nullable=True))

def downgrade():
    if op.get_bind().execute(sa.text("SELECT 1 FROM document_uploads WHERE media_type='application/pdf' OR extraction IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("PDF history cannot be downgraded; restore a verified backup")
    _preflight_previous()
    op.drop_column("document_uploads","extraction")

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
                    # Preserve every lower history guard before any SQLite/nontransactional DDL.
                    for step, (tables, message) in guards.items():
                        if step in crossed:
                            for table in tables:
                                if db.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
                                    raise RuntimeError(message + "; restore a verified backup")
