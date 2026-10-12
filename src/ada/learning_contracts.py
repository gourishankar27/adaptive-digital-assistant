"""Bounded interaction proposals, never factual claims or authorization."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from ada.expression_contracts import PreferenceValues
from ada.memory import MemoryInput, SupportingEvidence, Timestamp
from ada.proposal_contracts import SourcePin

VERSION = "ada-learning-v1"
Confidence = Literal["explicit_statement", "repeated_observation", "weak_inference"]


class LearningConfigWrite(MemoryInput):
    operation_id: UUID
    expected_revision: int = Field(ge=0, strict=True)
    status: Literal["off", "enrolled", "paused"]
    continuity_enabled: bool = Field(default=False, strict=True)


class ObservationWrite(MemoryInput):
    operation_id: UUID
    source: SourcePin
    values: PreferenceValues
    confidence_class: Confidence

    @model_validator(mode="after")
    def one_preference(self):
        if len(self.values.model_dump(exclude_none=True)) != 1:
            raise ValueError("Select exactly one interaction preference")
        return self


class LearningReviewWrite(MemoryInput):
    operation_id: UUID
    proposal_id: UUID
    expected_revision: int = Field(ge=1, strict=True)
    decision: Literal["approve", "reject"]
    account_wide: bool = Field(default=False, strict=True)
    reviewed: Literal[True]
    values: PreferenceValues | None = None

    @field_validator("reviewed", mode="before")
    @classmethod
    def explicit_review(cls, value):
        if value is not True:
            raise ValueError("Explicit user review is required")
        return value


class LearningResetWrite(MemoryInput):
    operation_id: UUID
    expected_revision: int = Field(ge=0, strict=True)


class LearningConfigOutput(BaseModel):
    scope_id: UUID
    revision: int
    epoch: int
    status: Literal["off", "enrolled", "paused"]
    continuity_enabled: bool
    policy_version: str
    threshold: int


class InteractionObservationOutput(BaseModel):
    id: UUID
    owner_id: UUID
    scope_id: UUID
    source_request_id: UUID
    source: SourcePin
    evidence: SupportingEvidence
    values: PreferenceValues
    confidence_class: Confidence
    interpretation_trust: Literal["unreviewed_interpretation"]
    extraction_version: str
    purpose: Literal["interaction_preference"]
    created_at: Timestamp
    expires_at: Timestamp


class InteractionProposalOutput(BaseModel):
    id: UUID
    revision: int
    values: PreferenceValues
    status: Literal["pending", "approved", "rejected"]
    independent_count: int
    eligible: bool
    observations: list[UUID]
    expires_at: Timestamp
    trust_class: Literal["unreviewed_interpretation"]


class LearnedPreferenceOutput(BaseModel):
    id: UUID
    values: PreferenceValues
    account_wide: bool
    receipt_id: UUID
    proposal_id: UUID
    created_at: Timestamp
    observation_ids: list[UUID] = Field(default_factory=list, max_length=200)
    reviewed_revision: int | None = None


class LearningStateOutput(BaseModel):
    config: LearningConfigOutput
    observations: list[InteractionObservationOutput]
    proposals: list[InteractionProposalOutput]
    learned: list[LearnedPreferenceOutput]


class LearningReceiptOutput(BaseModel):
    operation_id: UUID
    scope_id: UUID
    action: Literal["config", "observe", "review", "reset"]
    revision: int
    epoch: int
    observation_id: UUID | None = None
    proposal_id: UUID | None = None
    decision: Literal["approve", "reject"] | None = None
    created_at: Timestamp
    observation_ids: list[UUID] = Field(default_factory=list, max_length=200)
    proposal_revision: int | None = None


class ContinuityCard(SupportingEvidence):
    label: str
    episode_id: UUID
    summary_trust: Literal["model_generated"]
    uncertainty: Literal["source_reference_not_verified_recollection"]
    omitted_source_count: int = Field(default=0, ge=0)


class LearningSnapshot(BaseModel):
    policy_version: str
    scope_id: UUID
    epoch: int
    revision: int
    preferences: PreferenceValues
    receipts: dict[str, UUID]
    continuity: list[ContinuityCard]
    continuity_reason: str


class RequestLearningOutput(BaseModel):
    request_id: UUID
    learning: LearningSnapshot | None
