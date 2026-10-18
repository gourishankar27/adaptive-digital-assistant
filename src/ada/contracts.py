"""Output-only HTTP contracts. These models do not grant access or alter requests."""

from typing import Literal, NotRequired, TypedDict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, with_config

from ada.memory import Timestamp


class LiveOutput(BaseModel):
    status: Literal["ok"]


class ReadyOutput(BaseModel):
    status: Literal["ready"]
    schema_version: str = Field(alias="schema")


class UserOutput(BaseModel):
    id: UUID
    name: str
    data_epoch: int = Field(default=0, ge=0)


class CapabilitiesOutput(BaseModel):
    curiosity_protocol: str = "disabled"
    curiosity_notifications: bool = False
    web_research: str = "disabled"
    web_search: str = "disabled"
    answer_quality: str = "unsupported"
    calendar_windows: str = "unsupported"
    quality_prompt_version: str | None = None
    device_credentials: str = "unsupported"
    private_deletion: str = "unsupported"
    voice_input: str = "unsupported"
    voice_audio_uploads: bool = False
    stream_protocol: str = "unsupported"
    generation_cancellation: bool = False
    interaction_learning: str = "unsupported"
    interaction_preferences: str = "unsupported"
    session_expression: str = "unsupported"
    automatic_affect_inference: bool = False
    episodes: str = "unsupported"
    consolidation_jobs: str = "unsupported"
    consolidation_generation: bool = False
    consolidation_worker: bool = False
    agent_tools: str = "unsupported"
    agent_protocol: str = "unsupported"
    agent_registry: list[str] = Field(default_factory=list)
    memory_proposals: str = "unsupported"
    memory_review: bool = False
    memory_provenance: str = "legacy"
    semantic_retrieval: bool = False
    semantic_state: str = "disabled"
    scoped_entities: bool = False
    entity_resolution: str = "unsupported"
    entity_writes: bool = False
    admin_monitoring: bool = False
    document_ingestion: str = "unsupported"
    document_uploads: bool = False
    document_retrieval: bool = False
    document_citations: bool = False
    document_max_bytes: int = 0
    api_version: str
    chat: bool
    streaming: bool
    tools: bool
    structured_memory: bool
    memory_writes: str
    memory_in_chat: bool
    memory_retrieval: str
    memory_citations: bool
    retrieval_traces: bool
    chat_prompt_version: str
    automatic_memory_extraction: bool
    historical_memory_queries: bool
    private_project_scopes: bool
    shared_scopes: bool
    edge_inference: bool
    personality_isolation: bool
    authority: str
    provider: str
    model: str


class PersonalitySnapshotOutput(BaseModel):
    # Saved expression snapshots retain their historical/future values and keys.
    model_config = ConfigDict(extra="allow")

    name: str
    style: str
    warmth: str
    detail: str


class PersonalityOutput(PersonalitySnapshotOutput):
    id: UUID


class ConversationOutput(BaseModel):
    id: UUID
    title: str
    scope_id: UUID
    scope_kind: Literal["personal", "project"]
    personality: PersonalitySnapshotOutput
    prompt_version: str
    revision: int
    created_at: Timestamp


class PromptUpgradeOutput(BaseModel):
    id: UUID
    prompt_version: str
    revision: int


class EventOutput(BaseModel):
    id: UUID
    role: Literal["user", "assistant"]
    content: str
    trust_class: Literal["user_explicit", "model_generated"]
    request_id: UUID
    request_status: Literal["running", "completed", "failed"]
    created_at: Timestamp
    source_version_id: UUID


class ValidationIssueOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    loc: list[str | int]
    msg: str


class ErrorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detail: str


class ValidationErrorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # 422 also covers sanitized service/query codes, not just field validation.
    detail: str | list[ValidationIssueOutput]


@with_config(ConfigDict(extra="allow"))
class RetrievalCandidateOutput(TypedDict):
    claim_id: UUID
    channels: list[str]
    decision: str
    # Slot siblings were not ranked. Preserve absent keys instead of adding nulls.
    score: NotRequired[float]
    term_coverage: NotRequired[int]
    semantic_similarity: NotRequired[float]


@with_config(ConfigDict(extra="allow"))
class RetrievalBudgetOutput(TypedDict):
    memory_limit_bytes: int
    memory_used_bytes: int
    selected_limit: int
    candidate_limit_per_channel: int
    candidate_pool_truncated: bool
    # Direct retrieval has no whole-chat prompt/history budget.
    prompt_limit_bytes: NotRequired[int]
    prompt_used_bytes: NotRequired[int]
    history_pairs: NotRequired[int]
    history_pairs_omitted: NotRequired[int]
