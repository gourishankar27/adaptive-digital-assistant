"""The opt-in agent protocol does not extend the normal ChatInput domain."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictStr, field_validator

from ada.evidence import validate_text
from ada.memory import Timestamp, time_ms

ToolName = Literal["calculator", "memory_lookup", "source_lookup"]
RunStatus = Literal["running", "pending_approval", "completed", "failed", "unknown"]


class AgentInputBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*")
    @classmethod
    def unicode_text(cls, value):
        return validate_text(value)


class AgentInput(AgentInputBase):
    run_id: UUID
    task: StrictStr = Field(min_length=1, max_length=4000)
    protocol_version: Literal["ada-agent-v1"]
    allowed_tools: list[ToolName] = Field(min_length=1, max_length=3)
    as_of: AwareDatetime | None = None

    @field_validator("task")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("task cannot be blank")
        return value

    @field_validator("allowed_tools")
    @classmethod
    def unique(cls, value):
        if len(set(value)) != len(value):
            raise ValueError("duplicate tools")
        return value

    @field_validator("as_of", mode="before")
    @classmethod
    def typed_time(cls, value):
        if value is not None and not isinstance(value, (str, datetime)):
            raise ValueError("as_of requires an aware ISO timestamp")
        return value

    @field_validator("as_of")
    @classmethod
    def precision(cls, value):
        if value is not None:
            time_ms(value)
        return value


class ApprovalInput(AgentInputBase):
    approval_id: UUID
    preview_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    argument_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    tool_version: StrictStr = Field(min_length=1, max_length=40)


class RecoverInput(AgentInputBase):
    operation_id: UUID
    generation: int = Field(ge=1, strict=True)


class ToolSpecOutput(BaseModel):
    name: ToolName
    version: str
    description: str
    classification: Literal["read_only"]
    permission: Literal["authenticated_owner_scope"]
    allowed_targets: list[Literal["run_scope"]]
    argument_schema: dict
    result_schema: dict
    output_bytes: int
    max_calls: int
    timeout_seconds: int
    approval_required: Literal[True]


class ProtocolOutput(BaseModel):
    version: Literal["ada-agent-v1"]
    compatible_chat_prompts: list[str]
    max_steps: int
    context_bytes: int
    elapsed_seconds: int
    approval_seconds: int
    lease_seconds: int
    external_writes: Literal[False]


class ToolReceiptOutput(BaseModel):
    id: UUID
    approval_id: UUID
    owner_id: UUID
    run_id: UUID
    scope_id: UUID
    step_id: UUID
    tool: ToolName | None
    tool_version: str | None
    argument_hash: str | None
    preview_hash: str | None
    outcome: Literal["completed", "failed", "unknown", "revoked"]
    origin: Literal["tool_result"]
    trust_class: Literal["untrusted_tool_output"]
    result: dict | None
    error_code: str | None
    created_at: Timestamp


class AgentStepOutput(BaseModel):
    id: UUID
    number: int
    attempt: int
    status: Literal[
        "model", "pending_approval", "executing", "completed", "failed", "unknown", "revoked"
    ]
    tool: ToolName | None
    tool_version: str | None
    arguments: dict | None
    argument_hash: str | None
    preview_hash: str | None
    expires_at: Timestamp | None
    receipt: ToolReceiptOutput | None


class AgentRunOutput(BaseModel):
    id: UUID
    owner_id: UUID
    scope_id: UUID
    conversation_id: UUID
    protocol_version: str
    status: RunStatus
    response: str | None
    error_code: str | None
    provider: str
    model: str
    generation: int
    lease_until: Timestamp | None
    created_at: Timestamp
    finished_at: Timestamp | None
    as_of: Timestamp
    steps: list[AgentStepOutput]
