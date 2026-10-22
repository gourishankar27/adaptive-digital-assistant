"""Explicit owner commitments; task status and generated suggestions are not facts."""

from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ada.evidence import validate_text
from ada.memory import SupportingEvidence, Timestamp
from ada.proposal_contracts import SourcePin
from ada.schedule_contracts import ScheduleDefinition, ScheduleReceiptOutput
from ada.schedule_time import zone

VERSION = "ada-work-v1"


class WorkInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class WorkFields(WorkInput):
    kind: Literal["goal", "task"]
    description: str = Field(min_length=1, max_length=1000, strict=True)
    status: Literal["planned", "done", "deferred", "unknown", "dismissed"] = "planned"
    goal_id: UUID | None = None
    origin_request_id: UUID | None = None
    due_local: str | None = Field(default=None, pattern=r"^\d{4}-\d\d-\d\dT\d\d:\d\d$")
    timezone: str | None = Field(default=None, max_length=80)
    fold: Literal["reject", "first", "second"] = "reject"
    pins: list[SourcePin] = Field(default_factory=list, max_length=4)

    @field_validator("description")
    @classmethod
    def nonblank(cls, value):
        validate_text(value)
        if not value.strip():
            raise ValueError("A description is required")
        return value

    @model_validator(mode="after")
    def valid_due(self):
        self.due_ms()
        if self.kind == "goal" and self.goal_id:
            raise ValueError("Goals do not nest")
        return self

    def due_ms(self):
        if self.due_local is None and self.timezone is None:
            return None
        if not self.due_local or not self.timezone:
            raise ValueError("A due time needs both a local date/time and IANA timezone")
        try:
            local = datetime.strptime(self.due_local, "%Y-%m-%dT%H:%M")
            tz = zone(self.timezone)
            choices = set()
            for fold in (0, 1):
                utc = local.replace(tzinfo=tz, fold=fold).astimezone(timezone.utc)
                if utc.astimezone(tz).replace(tzinfo=None) == local:
                    delta = utc - datetime(1970, 1, 1, tzinfo=timezone.utc)
                    choices.add(delta.days * 86400000 + delta.seconds * 1000)
            if not choices or (len(choices) > 1 and self.fold == "reject"):
                raise ValueError("The local time is missing or ambiguous; choose an occurrence")
            return (max if self.fold == "second" else min)(choices)
        except (OverflowError, OSError):
            raise ValueError("Due time is out of range") from None


class WorkWrite(WorkInput):
    operation_id: UUID
    expected_revision: int = Field(ge=0, strict=True)
    review: Literal["confirm"]
    reminder_choice: Literal["none", "review_after_save"] = "none"
    fields: WorkFields
    preview_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class WorkProjectCreate(WorkInput):
    operation_id: UUID
    name: str = Field(min_length=1, max_length=120, strict=True)

    @field_validator("name")
    @classmethod
    def nonblank(cls, value):
        validate_text(value)
        if not value.strip():
            raise ValueError("A name is required")
        return value


class WorkPreviewOutput(BaseModel):
    version: Literal["ada-work-v1"] = VERSION
    preview_hash: str
    due_at: Timestamp | None
    sources: list[SupportingEvidence]
    provenance: str
    reminder: Literal["not_scheduled"] = "not_scheduled"
    reminder_choice: Literal["none", "review_after_save"] = "none"


class WorkOutput(BaseModel):
    version: Literal["ada-work-v1"] = VERSION
    id: UUID
    scope_id: UUID
    revision: int
    fields: WorkFields
    due_at: Timestamp | None
    overdue: bool
    origin_conversation_id: UUID | None = None
    provenance: Literal["owner_created", "owner_reviewed_suggestion"]
    sources: list[SupportingEvidence]
    source_unavailable: str | None
    schedule_id: UUID | None
    question_id: UUID | None
    created_at: Timestamp
    updated_at: Timestamp


class WorkRevisionOutput(BaseModel):
    revision: int
    fields: WorkFields
    created_at: Timestamp


class WorkBriefInput(WorkInput):
    operation_id: UUID
    scope_ids: list[UUID] = Field(min_length=1, max_length=4)
    item_ids: list[UUID] = Field(min_length=1, max_length=30)
    day: date
    timezone: str = Field(min_length=1, max_length=80)

    @model_validator(mode="after")
    def bounded_selection(self):
        zone(self.timezone)
        if len(set(self.scope_ids)) != len(self.scope_ids) or len(set(self.item_ids)) != len(
            self.item_ids
        ):
            raise ValueError("Selections must be unique")
        return self


class WorkBriefItem(BaseModel):
    label: str
    task: WorkOutput
    overdue: bool
    due_on_day: bool
    changes: list[str]


class WorkBriefOutput(BaseModel):
    version: Literal["ada-work-v1"] = VERSION
    id: UUID
    scope_ids: list[UUID]
    day: date
    timezone: str
    items: list[WorkBriefItem]
    needs_decision: int
    timezone_data: str
    generated_by: Literal["deterministic_task_projection"] = "deterministic_task_projection"
    factual_evidence: Literal[False] = False
    created_at: Timestamp


class WorkFollowup(WorkInput):
    operation_id: UUID
    expected_revision: int = Field(ge=1, strict=True)
    policy_revision: int = Field(ge=1, strict=True)
    topic: Literal["work", "routines"]
    review: Literal["confirm"]


class WorkReminderPreview(WorkInput):
    operation_id: UUID
    expected_revision: int = Field(ge=1, strict=True)
    definition: ScheduleDefinition


class WorkReminderConfirm(WorkInput):
    operation_id: UUID
    expected_revision: int = Field(ge=1, strict=True)
    preview_id: UUID
    consent_revision: int = Field(ge=1, strict=True)
    schedule_id: UUID
    expected_generation: int = Field(ge=0, strict=True)
    review: Literal["confirm"]


class WorkReceiptOutput(BaseModel):
    version: Literal["ada-work-v1"] = VERSION
    operation_id: UUID
    action: str
    state: Literal["completed"] = "completed"
    item_id: UUID | None = None
    scope_id: UUID | None = None
    revision: int | None = None
    question_id: UUID | None = None
    schedule_id: UUID | None = None
    brief_id: UUID | None = None
    schedule_preview: ScheduleReceiptOutput | None = None
    created_at: Timestamp
