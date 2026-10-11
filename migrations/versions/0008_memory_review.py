"""Private proposed memory and explicit endorsement provenance.

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from alembic import context, op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("claims", sa.Column("provenance", sa.JSON(), nullable=True))
    op.create_table(
        "memory_extractions",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("extractor_version", sa.String(40), nullable=False),
        sa.Column("validation", sa.JSON(), nullable=False),
        sa.Column("error_code", sa.String(40)),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        sa.CheckConstraint(
            "state IN ('processing', 'completed', 'failed')", name="extraction_state"
        ),
    )
    op.create_index(
        "extraction_owner_created",
        "memory_extractions",
        ["owner_id", "scope_id", "created_at", "id"],
    )
    op.create_table(
        "memory_proposals",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("extraction_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("original_candidate", sa.JSON(), nullable=False),
        sa.Column("candidate", sa.JSON(), nullable=False),
        sa.Column("edits", sa.JSON(), nullable=False),
        sa.Column("support", sa.JSON(), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("extractor_version", sa.String(40), nullable=False),
        sa.Column("validation", sa.JSON(), nullable=False),
        sa.Column("rejection_reason", sa.Text()),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "extraction_id"],
            ["memory_extractions.owner_id", "memory_extractions.scope_id", "memory_extractions.id"],
        ),
        sa.CheckConstraint("status IN ('pending', 'accepted', 'rejected')", name="proposal_status"),
        sa.CheckConstraint("revision >= 1", name="proposal_revision"),
    )
    op.create_index(
        "proposal_inbox", "memory_proposals", ["owner_id", "scope_id", "status", "created_at", "id"]
    )
    op.create_table(
        "memory_reviews",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("proposal_id", sa.String(36), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("review_hash", sa.String(64), nullable=False),
        sa.Column("annotation", sa.Text(), nullable=False),
        sa.Column("claim_id", sa.String(36)),
        sa.Column("endorsement_source_version_id", sa.String(36)),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.UniqueConstraint("owner_id", "proposal_id"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "proposal_id"],
            ["memory_proposals.owner_id", "memory_proposals.scope_id", "memory_proposals.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "endorsement_source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        sa.CheckConstraint(
            "(decision = 'accept' AND claim_id IS NOT NULL AND endorsement_source_version_id IS NOT NULL) OR (decision = 'reject' AND claim_id IS NULL AND endorsement_source_version_id IS NULL)",
            name="review_decision_consistent",
        ),
    )
    op.create_table(
        "claim_support",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("claim_id", sa.String(36), primary_key=True),
        sa.Column("ordinal", sa.Integer(), primary_key=True),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("review_id", sa.String(36), nullable=False),
        sa.Column("source_version_id", sa.String(36), nullable=False),
        sa.Column("evidence_hash", sa.String(64), nullable=False),
        sa.Column("span_start", sa.Integer(), nullable=False),
        sa.Column("span_end", sa.Integer(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "review_id"],
            ["memory_reviews.owner_id", "memory_reviews.scope_id", "memory_reviews.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        sa.CheckConstraint("span_start >= 0 AND span_end > span_start", name="support_valid_span"),
    )


def downgrade():
    if not context.is_offline_mode():
        db = op.get_bind()
        if any(
            db.scalar(sa.text(f"SELECT count(*) FROM {table}"))
            for table in (
                "memory_extractions",
                "memory_proposals",
                "memory_reviews",
                "claim_support",
            )
        ):
            raise RuntimeError("0008 contains review history; restore a verified backup instead")
    for table in ("claim_support", "memory_reviews", "memory_proposals", "memory_extractions"):
        op.drop_table(table)
    op.drop_column("claims", "provenance")
