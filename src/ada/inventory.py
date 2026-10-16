"""Explicit private-content closure for the installed feature inventory."""

from ada import (  # noqa: F401
    agent_models,
    consolidation_models,
    embedding_models,
    entity_models,
    expression_models,
    learning_models,
    proposal_models,
    security_models,
    stream_models,
    voice_models,
)
from ada.errors import ServiceError
from ada.models import Base

CONTENT_TABLES = (
    "agent_approvals",
    "agent_receipts",
    "agent_runs",
    "agent_steps",
    "claim_entity_links",
    "claim_search",
    "claim_support",
    "claims",
    "consolidation_jobs",
    "consolidation_sources",
    "conversation_prompt_changes",
    "conversations",
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
    "voice_inputs",
)

SECURITY_METADATA_TABLES = frozenset(
    {"device_credentials", "deletion_previews", "deletion_jobs", "deleted_requests"}
)


def content_tables():
    actual = {t.name for t in Base.metadata.tables.values() if "owner_id" in t.c}
    if actual != set(CONTENT_TABLES) | SECURITY_METADATA_TABLES:
        raise ServiceError(503, "deletion_inventory_unavailable")
    return [t for t in reversed(Base.metadata.sorted_tables) if t.name in CONTENT_TABLES]
