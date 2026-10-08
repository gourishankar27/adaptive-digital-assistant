"""Phase 1 scopes, immutable evidence versions, temporal claims and prompt audit.

0001 stays unchanged. Existing scope/event IDs and prompt snapshots are preserved.
"""

import hashlib

import sqlalchemy as sa
from alembic import context, op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "scopes",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.UniqueConstraint("owner_id", "id"),
        sa.UniqueConstraint("owner_id", "id", "kind"),
        sa.CheckConstraint("kind IN ('personal', 'project')", name="scope_kind_allowed"),
    )
    op.create_index("ix_scopes_owner_id", "scopes", ["owner_id"])
    op.execute(
        sa.text(
            "INSERT INTO scopes (id, owner_id, kind, name, created_at) "
            "SELECT scope_id, owner_id, scope_kind, MIN(title), MIN(created_at) "
            "FROM conversations GROUP BY scope_id, owner_id, scope_kind"
        )
    )
    with op.batch_alter_table("conversations") as batch:
        batch.create_unique_constraint(
            "conversation_scope_identity", ["owner_id", "id", "scope_id"]
        )
        batch.create_foreign_key(
            "conversation_scope_owner",
            "scopes",
            ["owner_id", "scope_id", "scope_kind"],
            ["owner_id", "id", "kind"],
        )
    with events_batch() as batch:
        batch.create_unique_constraint(
            "event_source_identity", ["owner_id", "conversation_id", "id"]
        )
    op.create_table(
        "sources",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("conversation_id", sa.String(36)),
        sa.Column("event_id", sa.String(36)),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.UniqueConstraint("event_id"),
        sa.ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id", "event_id"],
            ["events.owner_id", "events.conversation_id", "events.id"],
        ),
        sa.CheckConstraint(
            "(kind = 'chat_event' AND event_id IS NOT NULL AND conversation_id IS NOT NULL) "
            "OR (kind = 'user_note' AND event_id IS NULL AND conversation_id IS NULL)",
            name="source_origin_allowed",
        ),
    )
    op.create_index("ix_sources_owner_id", "sources", ["owner_id"])
    op.create_index("ix_sources_scope_id", "sources", ["scope_id"])
    op.create_table(
        "source_versions",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("trust_class", sa.String(30), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.UniqueConstraint("source_id", "version"),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_id"],
            ["sources.owner_id", "sources.scope_id", "sources.id"],
        ),
        sa.CheckConstraint("version >= 1", name="source_version_positive"),
        sa.CheckConstraint(
            "trust_class IN ('user_explicit', 'model_generated')", name="source_trust_allowed"
        ),
    )
    op.create_index("ix_source_versions_owner_id", "source_versions", ["owner_id"])
    op.create_index("ix_source_versions_scope_id", "source_versions", ["scope_id"])
    backfill_evidence()
    op.create_table(
        "claims",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("subject", sa.String(160), nullable=False),
        sa.Column("predicate", sa.String(160), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("valid_from", sa.BigInteger(), nullable=False),
        sa.Column("valid_to", sa.BigInteger()),
        sa.Column("source_version_id", sa.String(36), nullable=False),
        sa.Column("span_start", sa.Integer(), nullable=False),
        sa.Column("span_end", sa.Integer(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("evidence_hash", sa.String(64), nullable=False),
        sa.Column("write_hash", sa.String(64), nullable=False),
        sa.Column("superseded_by", sa.String(36)),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "scope_id", "id"),
        sa.UniqueConstraint("owner_id", "scope_id", "write_hash", name="claim_write_unique"),
        sa.ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "scope_id", "superseded_by"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
        ),
        sa.CheckConstraint("kind IN ('fact', 'preference', 'decision')", name="claim_kind_allowed"),
        sa.CheckConstraint(
            "valid_to IS NULL OR valid_to > valid_from", name="claim_valid_interval"
        ),
        sa.CheckConstraint("span_start >= 0 AND span_end > span_start", name="claim_valid_span"),
        sa.CheckConstraint(
            "(status = 'active' AND superseded_by IS NULL) OR "
            "(status = 'superseded' AND superseded_by IS NOT NULL AND valid_to IS NOT NULL)",
            name="claim_status_consistent",
        ),
    )
    op.create_index(
        "claim_temporal_lookup", "claims", ["owner_id", "scope_id", "valid_from", "valid_to"]
    )
    op.create_table(
        "conversation_prompt_changes",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("conversation_id", sa.String(36), nullable=False),
        sa.Column("previous_version", sa.String(30), nullable=False),
        sa.Column("new_version", sa.String(30), nullable=False),
        sa.Column("previous_prompt", sa.Text(), nullable=False),
        sa.Column("new_prompt", sa.Text(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["owner_id", "conversation_id"],
            ["conversations.owner_id", "conversations.id"],
        ),
    )
    op.create_index(
        "ix_conversation_prompt_changes_conversation_id",
        "conversation_prompt_changes",
        ["conversation_id"],
    )
    if op.get_bind().dialect.name == "sqlite" and not context.is_offline_mode():
        if op.get_bind().execute(sa.text("PRAGMA foreign_key_check")).fetchone():
            raise RuntimeError("Phase 1 migration left invalid foreign keys")


def backfill_evidence():
    op.execute(
        sa.text(
            "INSERT INTO sources (id, owner_id, scope_id, kind, conversation_id, event_id, created_at) "
            "SELECT e.id, e.owner_id, c.scope_id, 'chat_event', e.conversation_id, e.id, e.created_at "
            "FROM events e JOIN conversations c ON e.owner_id = c.owner_id AND e.conversation_id = c.id"
        )
    )
    connection = op.get_bind()
    if connection.dialect.name == "postgresql":
        # PostgreSQL's built-in SHA-256 accepts bytea; pgcrypto is not required.
        op.execute(
            sa.text(
                "INSERT INTO source_versions "
                "(id, owner_id, scope_id, source_id, version, content, content_hash, trust_class, created_at) "
                "SELECT e.id, e.owner_id, s.scope_id, s.id, 1, e.content, "
                "encode(sha256(convert_to(e.content, 'UTF8')), 'hex'), e.trust_class, e.created_at "
                "FROM events e JOIN sources s ON s.event_id = e.id"
            )
        )
        return
    if context.is_offline_mode():
        raise RuntimeError("SQLite evidence backfill requires an online migration")
    insert = sa.text(
        "INSERT INTO source_versions "
        "(id, owner_id, scope_id, source_id, version, content, content_hash, trust_class, created_at) "
        "VALUES (:id, :owner_id, :scope_id, :source_id, 1, :content, :content_hash, :trust_class, :created_at)"
    )
    # Keep backfill memory bounded, including when old conversations are large.
    last_id = ""
    while True:
        rows = (
            connection.execute(
                sa.text(
                    "SELECT e.id, e.owner_id, s.scope_id, s.id AS source_id, e.content, "
                    "e.trust_class, e.created_at FROM events e JOIN sources s ON s.event_id = e.id "
                    "WHERE e.id > :last_id ORDER BY e.id LIMIT 200"
                ),
                {"last_id": last_id},
            )
            .mappings()
            .all()
        )
        if not rows:
            break
        connection.execute(
            insert,
            [
                dict(row)
                | {"content_hash": hashlib.sha256(row["content"].encode("utf-8")).hexdigest()}
                for row in rows
            ],
        )
        last_id = rows[-1]["id"]


def downgrade():
    # Explicit downgrade discards Phase 1 memory; it is never run by the updater.
    op.drop_table("conversation_prompt_changes")
    op.drop_table("claims")
    op.drop_table("source_versions")
    op.drop_table("sources")
    with events_batch() as batch:
        batch.drop_constraint("event_source_identity", type_="unique")
    with op.batch_alter_table("conversations") as batch:
        batch.drop_constraint("conversation_scope_owner", type_="foreignkey")
        batch.drop_constraint("conversation_scope_identity", type_="unique")
    op.drop_table("scopes")


def events_batch():
    # A supplied snapshot makes Alembic retain unnamed Phase 0 CHECK constraints
    # when SQLite recreates this table. Default reflection would omit role checks.
    table = None
    if op.get_bind().dialect.name == "sqlite" and not context.is_offline_mode():
        table = sa.Table("events", sa.MetaData(), autoload_with=op.get_bind())
    return op.batch_alter_table("events", copy_from=table)
