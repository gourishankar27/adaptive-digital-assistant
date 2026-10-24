"""Immutable reviewed long-form speech; released one-minute lineage stays unchanged."""

import sqlalchemy as sa
from alembic import context, op
from alembic.script import ScriptDirectory

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "long_voice_inputs",
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("conversation_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("transcript_id", sa.String(36), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("reviewed_text", sa.Text(), nullable=False),
        sa.Column("reviewed_hash", sa.String(64), nullable=False),
        sa.Column("endorsement_id", sa.String(36), nullable=False),
        sa.Column("data_epoch", sa.BigInteger(), nullable=False),
        sa.Column("approved_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("owner_id", "request_id"),
        sa.UniqueConstraint("owner_id", "transcript_id", name="long_voice_transcript_once"),
        sa.CheckConstraint("data_epoch >= 0", name="long_voice_epoch"),
        sa.ForeignKeyConstraint(
            ["owner_id", "request_id", "conversation_id"],
            ["requests.owner_id", "requests.id", "requests.conversation_id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "endorsement_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id", "endorsement_id"],
            ["events.owner_id", "events.conversation_id", "events.id"],
        ),
    )


def downgrade():
    if context.is_offline_mode():
        raise RuntimeError("Voice downgrade requires online history preflight")
    if op.get_bind().execute(sa.text("SELECT 1 FROM long_voice_inputs LIMIT 1")).first():
        raise RuntimeError("Voice narrative history requires a verified backup, not downgrade")
    scripts = ScriptDirectory.from_config(context.config)
    crossed = {
        step.revision.revision
        for step in scripts._downgrade_revs(context.get_context().opts["destination_rev"], revision)
    }
    # SQLite DDL is not transactionally rolled back. Preserve lower released guards
    # before dropping even this empty table on a multi-revision downgrade.
    if "0021" in crossed:
        for table in ("edge_proposals", "edge_devices"):
            if op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first():
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
    if "0020" in crossed:
        scripts.get_revision("0021").module._preflight_previous()
    op.drop_table("long_voice_inputs")
