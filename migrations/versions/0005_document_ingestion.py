"""Private immutable document versions, exact chunks and lexical projection.

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from alembic import context, op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

OLD_ORIGIN = "(kind = 'chat_event' AND event_id IS NOT NULL AND conversation_id IS NOT NULL) OR (kind = 'user_note' AND event_id IS NULL AND conversation_id IS NULL)"
NEW_ORIGIN = "(kind = 'chat_event' AND event_id IS NOT NULL AND conversation_id IS NOT NULL) OR (kind IN ('user_note', 'imported_document') AND event_id IS NULL AND conversation_id IS NULL)"
OLD_TRUST = "trust_class IN ('user_explicit', 'model_generated')"
NEW_TRUST = "trust_class IN ('user_explicit', 'model_generated', 'imported_untrusted')"


def upgrade():
    with op.batch_alter_table("sources") as batch:
        batch.drop_constraint("source_origin_allowed", type_="check")
        batch.create_check_constraint("source_origin_allowed", NEW_ORIGIN)
    with op.batch_alter_table("source_versions") as batch:
        batch.drop_constraint("source_trust_allowed", type_="check")
        batch.create_check_constraint("source_trust_allowed", NEW_TRUST)
    for name in ("document_candidates", "document_selected"):
        op.add_column(
            "retrieval_traces", sa.Column(name, sa.JSON(), nullable=False, server_default="[]")
        )
    op.create_table(
        "document_uploads",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False),
        sa.Column("source_version_id", sa.String(36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(120), nullable=False),
        sa.Column("media_type", sa.String(30), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("raw_hash", sa.String(64), nullable=False),
        sa.Column("raw_bytes", sa.LargeBinary(), nullable=False),
        sa.Column("raw_size", sa.Integer(), nullable=False),
        sa.Column("available_from", sa.BigInteger(), nullable=False),
        sa.Column("available_to", sa.BigInteger()),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("error_code", sa.String(40)),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("published_at", sa.BigInteger()),
        sa.Column("started_at", sa.BigInteger(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "owner_id",
            "scope_id",
            "id",
            "source_version_id",
            "source_id",
            name="document_upload_identity",
        ),
        sa.UniqueConstraint("source_id", "version", name="document_upload_version"),
        sa.UniqueConstraint("source_version_id"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_id"],
            ["sources.owner_id", "sources.scope_id", "sources.id"],
        ),
        sa.CheckConstraint(
            "version >= 1 AND attempt >= 1", name="document_version_attempt_positive"
        ),
        sa.CheckConstraint("raw_size > 0 AND raw_size <= 262144", name="document_raw_size_bounded"),
        sa.CheckConstraint(
            "available_to IS NULL OR available_to > available_from",
            name="document_availability_interval",
        ),
        sa.CheckConstraint(
            "chunk_count >= 0 AND chunk_count <= 512", name="document_chunk_count_bounded"
        ),
        sa.CheckConstraint(
            "(state = 'processing' AND published_at IS NULL AND error_code IS NULL AND chunk_count = 0) OR (state = 'ready' AND published_at IS NOT NULL AND error_code IS NULL AND chunk_count > 0) OR (state = 'failed' AND published_at IS NULL AND error_code IS NOT NULL AND chunk_count = 0)",
            name="document_state_consistent",
        ),
    )
    op.create_index(
        "document_upload_owner_created", "document_uploads", ["owner_id", "created_at", "id"]
    )
    op.create_index(
        "document_upload_source_available",
        "document_uploads",
        ["owner_id", "scope_id", "source_id", "version", "state", "available_from", "published_at"],
    )
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("upload_id", sa.String(36), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False),
        sa.Column("source_version_id", sa.String(36), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("span_start", sa.Integer(), nullable=False),
        sa.Column("span_end", sa.Integer(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("quote_hash", sa.String(64), nullable=False),
        sa.Column("line_start", sa.Integer(), nullable=False),
        sa.Column("line_end", sa.Integer(), nullable=False),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.UniqueConstraint("source_version_id", "ordinal", name="document_chunk_ordinal"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "upload_id", "source_version_id", "source_id"],
            [
                "document_uploads.owner_id",
                "document_uploads.scope_id",
                "document_uploads.id",
                "document_uploads.source_version_id",
                "document_uploads.source_id",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        sa.CheckConstraint(
            "ordinal >= 1 AND ordinal <= 512", name="document_chunk_ordinal_bounded"
        ),
        sa.CheckConstraint(
            "span_start >= 0 AND span_end > span_start AND span_end - span_start <= 1024",
            name="document_chunk_span_bounded",
        ),
        sa.CheckConstraint(
            "line_start >= 1 AND line_end >= line_start", name="document_chunk_lines_valid"
        ),
    )
    op.create_index(
        "document_chunk_version",
        "document_chunks",
        ["owner_id", "scope_id", "source_version_id", "ordinal"],
    )
    op.create_table(
        "document_search",
        sa.Column("chunk_id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("search_text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "chunk_id"],
            ["document_chunks.owner_id", "document_chunks.scope_id", "document_chunks.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("document_search_owner_scope", "document_search", ["owner_id", "scope_id"])
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute(
            "CREATE INDEX document_search_fts ON document_search USING GIN (to_tsvector('simple'::regconfig, search_text))"
        )
    elif dialect == "sqlite":
        op.execute(
            "CREATE VIRTUAL TABLE document_fts USING fts5(search_text, content='document_search', content_rowid='rowid', tokenize='unicode61 remove_diacritics 0')"
        )
        op.execute(
            "CREATE TRIGGER document_search_ai AFTER INSERT ON document_search BEGIN INSERT INTO document_fts(rowid, search_text) VALUES (new.rowid, new.search_text); END"
        )
        op.execute(
            "CREATE TRIGGER document_search_ad AFTER DELETE ON document_search BEGIN INSERT INTO document_fts(document_fts, rowid, search_text) VALUES ('delete', old.rowid, old.search_text); END"
        )
        op.execute(
            "CREATE TRIGGER document_search_au AFTER UPDATE ON document_search BEGIN INSERT INTO document_fts(document_fts, rowid, search_text) VALUES ('delete', old.rowid, old.search_text); INSERT INTO document_fts(rowid, search_text) VALUES (new.rowid, new.search_text); END"
        )
    else:
        raise RuntimeError("Document ingestion requires PostgreSQL or SQLite with FTS5")


def downgrade():
    # Imported evidence cannot fit the previous constraints. Refuse a lossy
    # downgrade until an operator has explicitly removed the imported sources.
    if (
        not context.is_offline_mode()
        and op.get_bind()
        .execute(sa.text("SELECT 1 FROM sources WHERE kind = 'imported_document' LIMIT 1"))
        .first()
    ):
        raise RuntimeError("Document evidence exists; refusing a lossy downgrade")
    if op.get_bind().dialect.name == "sqlite":
        for name in ("document_search_ai", "document_search_ad", "document_search_au"):
            op.execute(f"DROP TRIGGER {name}")
        op.execute("DROP TABLE document_fts")
    op.drop_table("document_search")
    op.drop_table("document_chunks")
    op.drop_table("document_uploads")
    for name in ("document_candidates", "document_selected"):
        op.drop_column("retrieval_traces", name)
    with op.batch_alter_table("source_versions") as batch:
        batch.drop_constraint("source_trust_allowed", type_="check")
        batch.create_check_constraint("source_trust_allowed", OLD_TRUST)
    with op.batch_alter_table("sources") as batch:
        batch.drop_constraint("source_origin_allowed", type_="check")
        batch.create_check_constraint("source_origin_allowed", OLD_ORIGIN)
