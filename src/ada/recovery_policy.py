"""Reviewed recovery inventories. A new migration does not implicitly extend them."""

from ada.inventory import content_tables
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
CURRENT_0015_TABLES = frozenset(
    {
        "admin_audit",
        "admin_audit_state",
        "admin_grants",
        "agent_approvals",
        "agent_receipts",
        "agent_runs",
        "agent_steps",
        "alembic_version",
        "claim_entity_links",
        "claim_search",
        "claim_support",
        "claims",
        "consolidation_jobs",
        "consolidation_sources",
        "conversation_prompt_changes",
        "conversations",
        "deleted_requests",
        "deletion_jobs",
        "deletion_previews",
        "device_credentials",
        "document_chunks",
        "document_search",
        "document_uploads",
        "embedding_entries",
        "entities",
        "entity_aliases",
        "entity_merges",
        "entity_operations",
        "entity_self_links",
        "episode_contexts",
        "episodes",
        "events",
        "expression_bindings",
        "expression_preferences",
        "expression_receipts",
        "expression_sessions",
        "interaction_observations",
        "interaction_proposals",
        "learned_preferences",
        "learning_enrollments",
        "learning_receipts",
        "memory_extractions",
        "memory_proposals",
        "memory_reviews",
        "personalities",
        "requests",
        "retrieval_traces",
        "scopes",
        "source_versions",
        "sources",
        "stream_attempts",
        "stream_events",
        "users",
        "voice_inputs",
    }
)
CURRENT_0016_TABLES = CURRENT_0015_TABLES | {
    "password_credentials",
    "login_sessions",
    "refresh_verifiers",
}
CURRENT_0017_TABLES = CURRENT_0016_TABLES | {
    "curiosity_policies",
    "curiosity_questions",
    "curiosity_receipts",
}
CURRENT_0018_TABLES = CURRENT_0017_TABLES | {
    "schedule_consents",
    "schedules",
    "schedule_occurrences",
    "schedule_inbox",
    "schedule_receipts",
}
CURRENT_0019_TABLES = CURRENT_0018_TABLES | {
    "reflection_policies",
    "reflection_runs",
    "reflection_artifacts",
    "reflection_receipts",
    "reflection_provider_state",
}
CURRENT_0020_TABLES = CURRENT_0019_TABLES | {
    "work_items",
    "work_revisions",
    "work_receipts",
    "work_briefs",
}
SUPPORTED_TABLES = {
    "0005": LEGACY_0005_TABLES,
    "0015": CURRENT_0015_TABLES,
    "0016": CURRENT_0016_TABLES,
    "0017": CURRENT_0017_TABLES,
    "0018": CURRENT_0018_TABLES,
    "0019": CURRENT_0019_TABLES,
    "0020": CURRENT_0020_TABLES,
    "0021": CURRENT_0020_TABLES | {"edge_devices", "edge_proposals"},
}


def validate_inventory(head, names):
    if head not in SUPPORTED_TABLES or set(names) != SUPPORTED_TABLES[head]:
        raise RecoveryError("Schema inventory is not covered by a reviewed recovery policy")
    if head in ("0015", "0016", "0017", "0018", "0019", "0020", "0021"):
        content_tables()  # An unclassified new owner model must also fail closed.
