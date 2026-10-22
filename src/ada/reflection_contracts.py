"""Explicit bounded idle-work consent and generated owner-review artifacts."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ada.consolidation_contracts import EpisodeSource, SummaryResult
from ada.curiosity_contracts import CuriositySource, Topic
from ada.memory import Timestamp
from ada.proposal_contracts import SourcePin
from ada.schedule_time import zone

VERSION = "ada-reflection-v1"
Kind = Literal["report", "question", "summary"]


class ReflectionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class ReflectionSettings(ReflectionInput):
    enabled: bool = Field(default=False, strict=True)
    scope_ids: list[UUID] = Field(default_factory=list, max_length=4)
    source_types: list[
        Literal["user_notes", "imported_documents", "completed_user_turns", "completed_model_turns"]
    ] = Field(default_factory=lambda: ["user_notes"], min_length=1, max_length=4)
    automatic_completed_turns: bool = Field(default=False, strict=True)
    lookback_days: int = Field(default=7, ge=1, le=30, strict=True)
    timezone: str = Field(default="UTC", min_length=1, max_length=80)
    allowed_start: int = Field(default=0, ge=0, le=1439, strict=True)
    allowed_end: int = Field(default=60, ge=1, le=1440, strict=True)
    job_kinds: list[Kind] = Field(
        default_factory=lambda: ["report", "question"], min_length=1, max_length=3
    )
    question_topic: Topic = "work"
    allow_empty: bool = Field(default=True, strict=True)
    idle_seconds: int = Field(default=900, ge=900, le=86400, strict=True)
    nightly_seconds: int = Field(default=600, ge=1, le=600, strict=True)
    max_jobs: int = Field(default=3, ge=1, le=3, strict=True)
    unit_seconds: int = Field(default=20, ge=1, le=30, strict=True)
    minimum_memory_percent: int = Field(default=10, ge=10, le=90, strict=True)
    minimum_disk_mib: int = Field(default=1024, ge=1024, le=102400, strict=True)
    maximum_thermal_c: int = Field(default=80, ge=40, le=80, strict=True)

    @model_validator(mode="after")
    def bounded_selection(self):
        zone(self.timezone)
        if self.allowed_start >= self.allowed_end:
            raise ValueError("Allowed hours must be an increasing same-day interval")
        if self.unit_seconds > self.nightly_seconds:
            raise ValueError("A unit must fit inside the nightly budget")
        if self.enabled and not self.scope_ids:
            raise ValueError("Choose owned scopes before enabling idle work")
        for items in (self.scope_ids, self.source_types, self.job_kinds):
            if len(items) != len(set(items)):
                raise ValueError("Selections must be unique")
        if (
            any(x.startswith("completed_") for x in self.source_types)
            and not self.automatic_completed_turns
        ):
            raise ValueError("Automatic selection of completed turns requires separate consent")
        return self


class ReflectionPolicyWrite(ReflectionInput):
    operation_id: UUID
    expected_revision: int = Field(ge=0, strict=True)
    settings: ReflectionSettings


class ReflectionPolicyOutput(BaseModel):
    version: Literal["ada-reflection-v1"] = VERSION
    revision: int
    settings: ReflectionSettings
    globally_enabled: bool
    scheduling_consent: bool
    summary_generation: bool = False
    last_decision: str | None
    foreground_idle_seconds: int


class ReflectionFinding(ReflectionInput):
    category: Literal["owner_marked_open_item", "possible_change_or_conflict"]
    text: str = Field(min_length=1, max_length=1000)
    support: list[SourcePin] = Field(min_length=1, max_length=4)
    claim_ids: list[UUID] = Field(default_factory=list, max_length=2)


class ReflectionQuestion(ReflectionInput):
    topic: Topic
    template_key: str
    text: str
    source: CuriositySource | None = None


class ReflectionContent(ReflectionInput):
    findings: list[ReflectionFinding] | None = Field(default=None, max_length=8)
    question: ReflectionQuestion | None = None
    summary: SummaryResult | None = None


class ReflectionArtifactOutput(BaseModel):
    version: Literal["ada-reflection-v1"] = VERSION
    id: UUID
    scope_id: UUID
    run_id: UUID
    kind: Kind
    state: str
    provenance: Literal["rule_generated", "model_generated"]
    rationale: str
    content: ReflectionContent | None
    sources: list[EpisodeSource]
    omissions: dict[str, int]
    created_at: Timestamp
    elapsed_ms: int
    model_elapsed_ms: int | None
    episode_id: UUID | None = None
    question_id: UUID | None = None
    conversation_id: UUID | None = None
    unavailable_reason: str | None = None


class ReflectionRunOutput(BaseModel):
    id: UUID
    scope_id: UUID
    kind: Kind
    state: str
    attempt: int
    reason: str | None
    artifact_id: UUID | None
    created_at: Timestamp
    finished_at: Timestamp | None
    elapsed_ms: int | None
    charged_ms: int


class ReflectionAction(ReflectionInput):
    operation_id: UUID
    action: Literal["keep", "dismiss", "open_question"]
    conversation_id: UUID | None = None
    personality_id: UUID | None = None


class ReflectionReceiptOutput(BaseModel):
    version: Literal["ada-reflection-v1"] = VERSION
    operation_id: UUID
    action: str
    state: Literal["completed"] = "completed"
    revision: int | None = None
    artifact_id: UUID | None = None
    episode_id: UUID | None = None
    question_id: UUID | None = None
    conversation_id: UUID | None = None
    created_at: Timestamp


class ReflectionAdminOutput(BaseModel):
    globally_enabled: bool
    summary_generation: bool
    suspended_model_class: bool
    policies_enabled: int
    runs: dict[str, int]
    artifacts: dict[str, int]
    maximum_nightly_seconds: Literal[600] = 600
    maximum_jobs: Literal[3] = 3
    minimum_idle_seconds: Literal[900] = 900
    updated_at: Timestamp
