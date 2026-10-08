"""Scoped lexical projection, native full-text indexes, and durable retrieval traces.

Revision ID: 0003
Revises: 0002
"""

import re

import sqlalchemy as sa
from alembic import context, op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def _normalize(value):
    # Frozen projection v1. Do not import mutable application normalization.
    value = value.lower().replace("c++", "cpp").replace("c#", "csharp").replace("_", " ")
    return " ".join(re.sub(r"[^\w]+", " ", value).split())


def upgrade():
    search = op.create_table(
        "claim_search",
        sa.Column("claim_id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("subject_key", sa.String(640), nullable=False),
        sa.Column("predicate_key", sa.String(640), nullable=False),
        sa.Column("search_text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "claim_search_subject",
        "claim_search",
        ["owner_id", "scope_id", "subject_key", "predicate_key"],
    )
    op.create_table(
        "retrieval_traces",
        sa.Column("owner_id", sa.String(36), primary_key=True),
        sa.Column("request_id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("version", sa.String(40), nullable=False),
        sa.Column("plan", sa.JSON(), nullable=False),
        sa.Column("candidates", sa.JSON(), nullable=False),
        sa.Column("selected", sa.JSON(), nullable=False),
        sa.Column("budget", sa.JSON(), nullable=False),
        sa.Column("retrieval_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id", "request_id", "conversation_id"],
            ["requests.owner_id", "requests.id", "requests.conversation_id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
    )
    dialect = op.get_bind().dialect.name
    if context.is_offline_mode():
        # Offline PostgreSQL SQL is inspectable. Normal upgrades use the frozen
        # Python projection below, independent of database locale.
        def sql_normalize(expr):
            return (
                "btrim(regexp_replace(replace(replace(replace(lower("
                + expr
                + "), 'c++', 'cpp'), 'c#', 'csharp'), '_', ' '), '[^[:alnum:]]+', ' ', 'g'))"
            )

        op.execute(
            "INSERT INTO claim_search (claim_id, owner_id, scope_id, subject_key, "
            "predicate_key, search_text) SELECT id, owner_id, scope_id, "
            + sql_normalize("subject")
            + ", "
            + sql_normalize("predicate")
            + ", "
            + sql_normalize("subject || ' ' || predicate || ' ' || value || ' ' || quote")
            + " FROM claims"
        )
    else:
        conn = op.get_bind()
        rows = conn.execute(
            sa.text("SELECT id, owner_id, scope_id, subject, predicate, value, quote FROM claims")
        ).mappings()
        batch = []
        for row in rows:
            batch.append(
                {
                    "claim_id": row["id"],
                    "owner_id": row["owner_id"],
                    "scope_id": row["scope_id"],
                    "subject_key": _normalize(row["subject"]),
                    "predicate_key": _normalize(row["predicate"]),
                    "search_text": _normalize(
                        " ".join(row[k] for k in ("subject", "predicate", "value", "quote"))
                    ),
                }
            )
            if len(batch) == 500:
                conn.execute(search.insert(), batch)
                batch.clear()
        if batch:
            conn.execute(search.insert(), batch)
    if dialect == "postgresql":
        op.execute(
            "CREATE INDEX claim_search_fts ON claim_search "
            "USING GIN (to_tsvector('simple'::regconfig, search_text))"
        )
    elif dialect == "sqlite":
        op.execute(
            "CREATE VIRTUAL TABLE claim_fts USING fts5(search_text, "
            "content='claim_search', content_rowid='rowid', tokenize='unicode61 remove_diacritics 0')"
        )
        op.execute("INSERT INTO claim_fts(claim_fts) VALUES ('rebuild')")
        op.execute(
            "CREATE TRIGGER claim_search_ai AFTER INSERT ON claim_search BEGIN "
            "INSERT INTO claim_fts(rowid, search_text) VALUES (new.rowid, new.search_text); END"
        )
        op.execute(
            "CREATE TRIGGER claim_search_ad AFTER DELETE ON claim_search BEGIN "
            "INSERT INTO claim_fts(claim_fts, rowid, search_text) "
            "VALUES ('delete', old.rowid, old.search_text); END"
        )
        op.execute(
            "CREATE TRIGGER claim_search_au AFTER UPDATE ON claim_search BEGIN "
            "INSERT INTO claim_fts(claim_fts, rowid, search_text) "
            "VALUES ('delete', old.rowid, old.search_text); "
            "INSERT INTO claim_fts(rowid, search_text) VALUES (new.rowid, new.search_text); END"
        )
    else:
        raise RuntimeError("Phase 2 requires PostgreSQL or SQLite with FTS5")


def downgrade():
    if op.get_bind().dialect.name == "sqlite":
        for name in ("claim_search_ai", "claim_search_ad", "claim_search_au"):
            op.execute(f"DROP TRIGGER {name}")
        op.execute("DROP TABLE claim_fts")
    op.drop_table("retrieval_traces")
    op.drop_table("claim_search")
