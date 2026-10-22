"""Strict device enrollment and generated draft synchronization, no promotion API."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ada.evidence import validate_text
from ada.memory import Timestamp
from ada.proposal_contracts import SourcePin


class EdgeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class EdgeEnroll(EdgeInput):
    operation_id: UUID
    label: str = Field(min_length=1, max_length=80)
    public_key: str = Field(min_length=80, max_length=256)
    review: Literal["confirm"]


class EdgeRevoke(EdgeInput):
    operation_id: UUID
    expected_revision: int = Field(ge=1, strict=True)
    review: Literal["confirm"]


class EdgeSync(EdgeInput):
    proposal_id: UUID
    device_id: UUID
    device_revision: int = Field(ge=1, strict=True)
    sequence: int = Field(ge=1, le=10000, strict=True)
    task: Literal["offline_reply"]
    model_id: Literal["Qwen/Qwen3-0.6B-GGUF"]
    model_digest: Literal["9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031"]
    runtime: Literal["llama.cpp-620d2225cc436ab0b001e3200e590e3b286ef9ab"]
    prompt: str = Field(min_length=1, max_length=2000)
    prompt_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    output: str = Field(min_length=1, max_length=4000)
    sources: list[SourcePin] = Field(default_factory=list, max_length=4)
    signature: str = Field(min_length=80, max_length=192)

    @field_validator("prompt", "output")
    @classmethod
    def valid_text(cls, value):
        validate_text(value)
        if not value.strip():
            raise ValueError("Text required")
        return value


class EdgeDeviceOutput(BaseModel):
    version: Literal["ada-device-drafts-v1"] = "ada-device-drafts-v1"
    id: UUID
    revision: int
    last_sequence: int
    label: str
    public_key: str
    enrollment_id: UUID
    revocation_id: UUID | None
    revoked_at: Timestamp | None
    created_at: Timestamp


class EdgeProposalOutput(BaseModel):
    version: Literal["ada-device-drafts-v1"] = "ada-device-drafts-v1"
    id: UUID
    scope_id: UUID
    device_id: UUID
    sequence: int
    task: Literal["offline_reply"] = "offline_reply"
    model_id: str
    model_digest: str
    runtime: str
    output: str
    prompt_hash: str
    sources: list[SourcePin]
    trust_class: Literal["model_generated"] = "model_generated"
    state: Literal["draft"] = "draft"
    created_at: Timestamp
