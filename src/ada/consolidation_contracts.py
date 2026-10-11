"""Explicit maintenance inputs; generated continuity is never factual evidence."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from ada.evidence import validate_text
from ada.memory import MemoryInput, SupportingEvidence, Timestamp
from ada.proposal_contracts import SourcePin

JobKind = Literal["episode", "proposals", "lexical_rebuild"]
JobStatus = Literal["queued", "running", "completed", "failed", "stale"]


class ConsolidationInput(MemoryInput):
    job_id: UUID
    kind: JobKind
    sources: list[SourcePin] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def selection(self):
        if (self.kind == "lexical_rebuild") != (len(self.sources) == 0):
            raise ValueError(
                "Select exact sources for summaries/proposals, none for scoped rebuild"
            )
        if len({str(p.source_version_id) for p in self.sources}) != len(self.sources):
            raise ValueError("Each source version may be selected once")
        return self


class SummarySection(MemoryInput):
    text: str = Field(min_length=1, max_length=700)
    support: list[SourcePin] = Field(min_length=1, max_length=4)


class SummaryResult(MemoryInput):
    sections: list[SummarySection] = Field(min_length=1, max_length=8)
    tags: list[str] = Field(max_length=8)
    omissions: list[str] = Field(max_length=4)

    @model_validator(mode="after")
    def bounds(self):
        for item in self.tags + self.omissions:
            validate_text(item)
        if any(not x.strip() or len(x) > 40 for x in self.tags):
            raise ValueError("Tags must be compact")
        if any(not x.strip() or len(x) > 240 for x in self.omissions):
            raise ValueError("Omission notes must be compact")
        if any(not x.text.strip() for x in self.sections):
            raise ValueError("Empty summary")
        return self


class EpisodeSource(SupportingEvidence):
    conversation_id: UUID | None
    event_id: UUID | None
    created_at: Timestamp
    source_created_at: Timestamp
    available_from: Timestamp | None = None
    available_to: Timestamp | None = None
    published_at: Timestamp | None = None


class EpisodeOutput(BaseModel):
    id: UUID
    owner_id: UUID
    scope_id: UUID
    job_id: UUID
    summary_version: str
    model: str
    trust_class: Literal["model_generated"]
    sections: list[SummarySection]
    tags: list[str]
    omissions: list[str]
    sources: list[EpisodeSource]
    range_start: Timestamp
    range_end: Timestamp
    created_at: Timestamp


class ConsolidationReceipt(BaseModel):
    id: UUID
    job_id: UUID
    outcome: Literal["completed", "failed", "stale"]
    attempt: int
    episode_id: UUID | None
    extraction_id: UUID | None
    proposal_ids: list[UUID]
    indexed_claims: int | None
    indexed_chunks: int | None
    error_code: str | None
    created_at: Timestamp


class ConsolidationOutput(BaseModel):
    id: UUID
    owner_id: UUID
    scope_id: UUID
    kind: JobKind
    version: str
    status: JobStatus
    checkpoint: Literal["reserved", "claimed", "published", "terminal"]
    attempt: int
    model: str
    lease_until: Timestamp | None
    created_at: Timestamp
    started_at: Timestamp | None
    finished_at: Timestamp | None
    elapsed_ms: int | None
    error_code: str | None
    receipt: ConsolidationReceipt | None


class EpisodeContextInput(MemoryInput):
    request_id: UUID
    episode_ids: list[UUID] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.episode_ids)) != len(self.episode_ids):
            raise ValueError("Duplicate episode selection")
        return self


class EpisodeContextOutput(BaseModel):
    request_id: UUID
    scope_id: UUID
    as_of: Timestamp
    purpose: Literal["navigation_only"]
    episodes: list[EpisodeOutput]
