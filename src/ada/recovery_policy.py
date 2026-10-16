"""Reviewed recovery inventories. A new migration does not implicitly extend them."""

from ada.inventory import CONTENT_TABLES, SECURITY_METADATA_TABLES, content_tables
from ada.operations import RecoveryError

LEGACY_0005_TABLES = frozenset(
    {
        "alembic_version",
        "users",
        "personalities",
        "conversations",
        "requests",
        "events",
        "scopes",
        "sources",
        "source_versions",
        "claims",
        "conversation_prompt_changes",
        "claim_search",
        "retrieval_traces",
        "admin_grants",
        "admin_audit_state",
        "admin_audit",
        "document_uploads",
        "document_chunks",
        "document_search",
    }
)
CURRENT_0015_TABLES = (
    frozenset(CONTENT_TABLES)
    | SECURITY_METADATA_TABLES
    | {
        "alembic_version",
        "users",
        "admin_grants",
        "admin_audit_state",
        "admin_audit",
    }
)
SUPPORTED_TABLES = {"0005": LEGACY_0005_TABLES, "0015": CURRENT_0015_TABLES}


def validate_inventory(head, names):
    if head not in SUPPORTED_TABLES or set(names) != SUPPORTED_TABLES[head]:
        raise RecoveryError("Schema inventory is not covered by a reviewed recovery policy")
    if head == "0015":
        content_tables()  # An unclassified new owner model must also fail closed.
