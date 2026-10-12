"""Closed, output-only monitoring allowlists. Never serialize domain ORM rows."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ada.consolidation_contracts import JobKind, JobStatus
from ada.memory import Timestamp

Outcome = Literal[
    "allowed",
    "denied",
    "not_found",
    "invalid",
    "failed",
    "granted",
    "revoked",
    "unchanged",
    "rate_limited",
]
Action = Literal[
    "role.grant",
    "role.revoke",
    "monitor.me",
    "monitor.overview",
    "monitor.requests",
    "monitor.request",
    "monitor.providers",
    "monitor.audit",
]


class Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AdminMeOutput(Metadata):
    id: UUID
    permissions: list[Literal["monitoring:read"]]


class RetrievalSummary(Metadata):
    available: bool
    candidate_count: int | None = None
    selected_count: int | None = None
    retrieval_ms: int | None = None
    memory_limit_bytes: int | None = None
    memory_used_bytes: int | None = None
    prompt_limit_bytes: int | None = None
    prompt_used_bytes: int | None = None
    history_pairs_omitted: int | None = None
    candidate_pool_truncated: bool | None = None


class AdminRequestOutput(Metadata):
    owner_id: UUID
    request_id: UUID
    conversation_id: UUID
    scope_id: UUID
    status: Literal["running", "completed", "failed"]
    attempt: int
    provider: str
    model: str
    created_at: Timestamp
    started_at: Timestamp
    finished_at: Timestamp | None
    observed_at: Timestamp
    elapsed_ms: Timestamp | None = Field(
        description="Finished/observed minus current attempt start, including context and DB overhead; not provider latency."
    )
    error_code: str | None
    input_tokens: int | None
    output_tokens: int | None


class AdminRequestDetailOutput(AdminRequestOutput):
    retrieval: RetrievalSummary
    stream: "StreamMetadata | None" = None


class StreamMetadata(Metadata):
    state: Literal["running", "cancel_requested", "completed", "failed", "cancelled", "interrupted"]
    sequence: int
    replay_after: int
    created_at: Timestamp
    finished_at: Timestamp | None


class AdminRequestsOutput(Metadata):
    items: list[AdminRequestOutput]
    limit: int
    offset: int
    has_more: bool
    created_from: Timestamp
    created_to: Timestamp
    updated_at: Timestamp


class ProviderHealth(Metadata):
    reachability: Literal["reachable", "unreachable", "unknown"]
    model_available: bool | None
    checked_at: Timestamp | None
    error_code: Literal["provider_unavailable", "invalid_health_response"] | None
    cache_seconds: Literal[30] = 30


class AdmissionOutput(Metadata):
    max_parallel: int
    process_available_slots: int
    process_active_slots: int
    workers: Literal[1] = 1


class AdminProvidersOutput(Metadata):
    provider: str
    model: str
    health: ProviderHealth
    generation_admission: AdmissionOutput
    context_tokens: int
    output_tokens: int
    timeout_seconds: int
    gpu_utilization: float | None = None
    tokens_per_second: float | None = None


class RequestCounts(Metadata):
    running: int = 0
    completed: int = 0
    failed: int = 0


class AgentCounts(Metadata):
    running: int = Field(ge=0)
    pending_approval: int = Field(ge=0)
    completed: int = Field(ge=0)
    failed: int = Field(ge=0)
    unknown: int = Field(ge=0)


class AdminOverviewOutput(Metadata):
    consolidation_job_counts: dict[JobStatus, int] | None = None
    consolidation_jobs: list["AdminJobMetadata"] | None = None
    agent_run_counts: AgentCounts | None = None
    memory_proposal_counts: dict[Literal["pending", "accepted", "rejected"], int] | None = None
    interaction_learning_counts: (
        dict[Literal["config", "observe", "review", "reset"], int] | None
    ) = None
    window_hours: int
    created_from: Timestamp
    updated_at: Timestamp
    requests: RequestCounts
    input_tokens: int | None
    output_tokens: int | None
    input_tokens_known_requests: int
    output_tokens_known_requests: int
    database_ready: bool
    schema_version: str | None
    provider_health: ProviderHealth
    generation_admission: AdmissionOutput
    gpu_utilization: float | None = None
    tokens_per_second: float | None = None


class AdminJobMetadata(Metadata):
    id: UUID
    owner_id: UUID
    scope_id: UUID
    kind: JobKind
    status: JobStatus
    checkpoint: str
    version: str
    attempt: int
    created_at: Timestamp
    started_at: Timestamp | None
    finished_at: Timestamp | None
    elapsed_ms: int | None


class AdminAuditOutput(Metadata):
    id: Timestamp
    actor_id: UUID
    actor_kind: Literal["user", "local_operator"]
    action: Action
    target_owner_id: UUID | None
    target_request_id: UUID | None
    outcome: Outcome
    created_at: Timestamp


class AdminAuditsOutput(Metadata):
    items: list[AdminAuditOutput]
    limit: int
    offset: int
    has_more: bool
    retention_days: Literal[30] = 30
    max_rows: Literal[10000] = 10000
    updated_at: Timestamp
