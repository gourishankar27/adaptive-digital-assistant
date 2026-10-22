"""Explicit bounded calendar intent and owner-only durable delivery contracts."""

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

from ada.curiosity_contracts import CuriosityPinInput, CuriositySource, Topic
from ada.evidence import validate_text
from ada.memory import Timestamp, time_ms

VERSION = "ada-scheduling-v1"


class ScheduleInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    @field_validator("expires_at", "until", check_fields=False)
    @classmethod
    def millisecond_precision(cls, value):
        if value is not None:
            time_ms(value)
        return value


class ScheduleDefinition(ScheduleInput):
    kind: Literal["reminder", "curiosity_question"] = "reminder"
    text: str = Field(default="", max_length=1000, strict=True)
    topic: Topic | None = None
    source: CuriosityPinInput | None = None
    timezone: str = Field(min_length=1, max_length=80, strict=True)
    start_local: str = Field(pattern=r"^\d{4}-\d\d-\d\dT\d\d:\d\d$", strict=True)
    frequency: Literal["once", "daily", "weekly"] = "once"
    count: int = Field(default=1, ge=1, le=100, strict=True)
    fold: Literal["reject", "first", "second"] = "reject"
    gap: Literal["reject", "skip"] = "skip"
    allowed_start: int = Field(default=480, ge=0, le=1439, strict=True)
    allowed_end: int = Field(default=1320, ge=1, le=1440, strict=True)
    expires_at: AwareDatetime
    channel: Literal["inbox"] = "inbox"

    @field_validator("text")
    @classmethod
    def valid_text(cls, value):
        validate_text(value)
        return value

    @model_validator(mode="after")
    def bounded_intent(self):
        if self.allowed_start >= self.allowed_end:
            raise ValueError("Allowed hours must be an increasing same-day interval")
        if self.frequency == "once" and self.count != 1:
            raise ValueError("A one-time schedule has exactly one occurrence")
        if self.kind == "reminder" and (not self.text.strip() or self.topic or self.source):
            raise ValueError("A reminder requires owner text and has no generated source context")
        if self.kind == "curiosity_question" and (self.text or self.topic is None):
            raise ValueError("A scheduled question selects an allowed topic, not generated input")
        return self


class SchedulePreview(ScheduleInput):
    operation_id: UUID
    definition: ScheduleDefinition


class ScheduleConfirm(ScheduleInput):
    operation_id: UUID
    preview_id: UUID
    expected_generation: int = Field(ge=0, strict=True)
    consent_revision: int = Field(ge=1, strict=True)


class SchedulePolicyWrite(ScheduleInput):
    operation_id: UUID
    expected_revision: int = Field(ge=0, strict=True)
    enabled: bool = Field(strict=True)


class ScheduleAction(ScheduleInput):
    operation_id: UUID
    expected_generation: int = Field(ge=1, strict=True)
    action: Literal["pause", "reauthorize", "delete", "snooze"]
    until: AwareDatetime | None = None


class ScheduleInboxAction(ScheduleInput):
    operation_id: UUID
    action: Literal["acknowledge", "dismiss", "snooze"]
    until: AwareDatetime | None = None


class ScheduleOpen(ScheduleInput):
    operation_id: UUID
    conversation_id: UUID
    personality_id: UUID


class SchedulePolicyOutput(BaseModel):
    version: Literal["ada-scheduling-v1"] = VERSION
    revision: int
    enabled: bool
    globally_enabled: bool
    notice_channel: Literal["foreground_in_app"] = "foreground_in_app"
    background_push: Literal[False] = False


class ScheduleReceiptOutput(BaseModel):
    version: Literal["ada-scheduling-v1"] = VERSION
    operation_id: UUID
    action: str
    state: str
    schedule_id: UUID | None = None
    item_id: UUID | None = None
    conversation_id: UUID | None = None
    generation: int | None = None
    consent_revision: int | None = None
    definition: ScheduleDefinition | None = None
    source: CuriositySource | None = None
    occurrences: list[dict] | None = None
    timezone_data: str | None = None
    preview_expires_at: Timestamp | None = None
    created_at: Timestamp


class ScheduleOutput(BaseModel):
    version: Literal["ada-scheduling-v1"] = VERSION
    id: UUID
    scope_id: UUID
    generation: int
    state: str
    reason: str | None
    definition: ScheduleDefinition | None
    next_at: Timestamp | None
    snoozed_until: Timestamp | None
    delivered: int
    missed: int
    consent_revision: int
    origin_kind: Literal["legacy", "device", "password"]
    created_at: Timestamp
    updated_at: Timestamp


class ScheduleOccurrenceOutput(BaseModel):
    id: UUID
    schedule_id: UUID
    generation: int
    scheduled_for: Timestamp
    state: str
    reason: str | None
    attempt: int
    lease_until: Timestamp | None
    item_id: UUID | None


class ScheduleInboxOutput(BaseModel):
    version: Literal["ada-scheduling-v1"] = VERSION
    id: UUID
    scope_id: UUID
    schedule_id: UUID
    occurrence_id: UUID
    kind: Literal["reminder", "curiosity_question"]
    text: str | None
    question_id: UUID | None
    state: str
    available_at: Timestamp
    expires_at: Timestamp
    acknowledged_at: Timestamp | None
    opened_conversation_id: UUID | None
    created_at: Timestamp


class ScheduleAdminOutput(BaseModel):
    globally_enabled: bool
    worker_running: bool = False
    process_error_count: int = 0
    last_error_code: (
        Literal["dispatcher_storage_unavailable", "dispatcher_iteration_failed"] | None
    ) = None
    schedules: dict[str, int]
    occurrences: dict[str, int]
    inbox: dict[str, int]
    updated_at: Timestamp
