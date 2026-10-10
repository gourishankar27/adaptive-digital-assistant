"""Explicit admin grants, bounded metadata audit, and monitoring indexes.

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_grants",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
    )
    state = op.create_table(
        "admin_audit_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.CheckConstraint("id = 1", name="admin_audit_singleton"),
    )
    op.bulk_insert(state, [{"id": 1}])
    op.create_table(
        "admin_audit",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True),
        sa.Column("actor_id", sa.String(36), nullable=False),
        sa.Column("actor_kind", sa.String(20), nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("target_owner_id", sa.String(36)),
        sa.Column("target_request_id", sa.String(36)),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("actor_kind IN ('user', 'local_operator')", name="admin_audit_actor"),
        sa.CheckConstraint(
            "action IN ('role.grant', 'role.revoke', 'monitor.me', 'monitor.overview', "
            "'monitor.requests', 'monitor.request', 'monitor.providers', 'monitor.audit')",
            name="admin_audit_action",
        ),
        sa.CheckConstraint(
            "outcome IN ('allowed', 'denied', 'not_found', 'invalid', 'failed', "
            "'granted', 'revoked', 'unchanged', 'rate_limited')",
            name="admin_audit_outcome",
        ),
    )
    op.create_index("admin_audit_created", "admin_audit", ["created_at", "id"])
    op.create_index("admin_audit_actor_created", "admin_audit", ["actor_id", "created_at", "id"])
    for name, columns in (
        ("created", ["created_at", "owner_id", "id"]),
        ("status", ["status", "created_at", "owner_id", "id"]),
        ("owner", ["owner_id", "created_at", "id"]),
        ("provider", ["provider", "created_at", "owner_id", "id"]),
    ):
        op.create_index("request_admin_" + name, "requests", columns)


def downgrade():
    for name in ("created", "status", "owner", "provider"):
        op.drop_index("request_admin_" + name, table_name="requests")
    op.drop_table("admin_audit")
    op.drop_table("admin_audit_state")
    op.drop_table("admin_grants")
