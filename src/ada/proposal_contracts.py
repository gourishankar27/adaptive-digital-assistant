"""Strict proposal/review contracts. Confidence and source text grant no authority."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field, field_validator, model_validator

from ada.memory import MemoryInput, SupportingEvidence, Timestamp, time_ms


class SourcePin(MemoryInput):
    source_version_id: UUID
    version: int = Field(ge=1, strict=True)
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    span_start: int = Field(ge=0, strict=True)
    span_end: int = Field(gt=0, strict=True)


class Candidate(MemoryInput):
    subject: str = Field(min_length=1, max_length=160)
    predicate: str = Field(min_length=1, max_length=160)
    value: str = Field(min_length=1, max_length=1000)
    kind: Literal["fact", "preference", "decision"]
    valid_from: AwareDatetime | None = None
    valid_to: AwareDatetime | None = None
    subject_entity_id: UUID | None = None
    support: list[SourcePin] = Field(min_length=1, max_length=4)
    confidence: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False, strict=True)

    @field_validator("valid_from", "valid_to", mode="before")
    @classmethod
    def typed_date(cls, value):
        if value is not None and not isinstance(value, (str, datetime)):
            raise ValueError("effective dates require a timezone-aware ISO timestamp")
        return value

    @field_validator("subject", "predicate", "value")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("annotation must not be blank")
        return value.strip()

    @field_validator("valid_from", "valid_to")
    @classmethod
    def precision(cls, value):
        if value is not None:
            time_ms(value)
        return value

    @model_validator(mode="after")
    def interval(self):
        if self.valid_from and self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError("invalid interval")
        return self


class ExtractionInput(MemoryInput):
    extraction_id: UUID
    sources: list[SourcePin] = Field(min_length=1, max_length=4)


class ExtractionResult(MemoryInput):
    candidates: list[Candidate] = Field(max_length=8)


class EditInput(MemoryInput):
    revision: int = Field(ge=1, strict=True)
    review_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    candidate: Candidate


class ReviewInput(EditInput):
    review_id: UUID
    decision: Literal["accept", "reject"]
    annotation: str = Field(min_length=1, max_length=1000)
    replace_claim_id: UUID | None = None

    @field_validator("annotation")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("decision annotation required")
        return value.strip()


class ExtractionOutput(BaseModel):
    id: UUID
    scope_id: UUID
    state: Literal["processing", "completed", "failed"]
    model: str
    extractor_version: str
    validation: dict
    error_code: str | None
    proposal_ids: list[UUID]
    created_at: Timestamp


class ConflictOutput(BaseModel):
    id: UUID
    value: str
    valid_from: Timestamp
    valid_to: Timestamp | None
    status: str
    write_hash: str
    subject_entity_id: UUID | None


class ProposalOutput(BaseModel):
    id: UUID
    scope_id: UUID
    extraction_id: UUID
    status: Literal["pending", "accepted", "rejected"]
    revision: int
    candidate: Candidate
    original_candidate: Candidate
    model: str
    extractor_version: str
    validation: dict
    support: list[SupportingEvidence]
    conflicts: list[ConflictOutput]
    review_hash: str
    rejection_reason: str | None
    review_id: UUID | None
    created_at: Timestamp


class ReviewOutput(BaseModel):
    id: UUID
    proposal_id: UUID
    scope_id: UUID
    principal_id: UUID
    decision: Literal["accept", "reject"]
    revision: int
    review_hash: str
    claim_id: UUID | None
    endorsement_source_version_id: UUID | None
    created_at: Timestamp
