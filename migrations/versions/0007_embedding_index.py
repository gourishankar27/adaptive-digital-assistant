"""Discardable scoped exact embedding index. No source or trace history changes.

Revision ID: 0007
Revises: 0006
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "embedding_entries",
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("namespace", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("item_id", sa.String(36), nullable=False),
        sa.Column("claim_id", sa.String(36)),
        sa.Column("chunk_id", sa.String(36)),
        sa.Column("source_version_id", sa.String(36), nullable=False),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("text_hash", sa.String(64), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("model_digest", sa.String(64), nullable=False),
        sa.Column("index_version", sa.String(40), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("vector", sa.JSON(), nullable=False),
        sa.Column("built_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("owner_id", "scope_id", "namespace", "kind", "item_id"),
        sa.ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "chunk_id"],
            ["document_chunks.owner_id", "document_chunks.scope_id", "document_chunks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        sa.CheckConstraint(
            "(kind = 'claim' AND claim_id IS NOT NULL AND chunk_id IS NULL AND item_id = claim_id) OR (kind = 'document' AND chunk_id IS NOT NULL AND claim_id IS NULL AND item_id = chunk_id)",
            name="embedding_item_reference",
        ),
        sa.CheckConstraint(
            "dimensions >= 1 AND dimensions <= 768", name="embedding_dimensions_bounded"
        ),
    )


def downgrade():
    # Vectors are derived and disposable; old requests keep their own snapshots.
    op.drop_table("embedding_entries")
