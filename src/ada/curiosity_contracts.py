"""Optional owner questions; no factual-memory or scheduled-delivery authority."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ada.evidence import validate_text
from ada.memory import Timestamp

VERSION = "ada-curiosity-v1"
Topic = Literal["interests", "work", "routines", "relationships", "reflection"]


class CuriosityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CuriositySettings(CuriosityInput):
    enabled: bool = Field(default=False, strict=True)
    chat_enabled: bool = Field(default=True, strict=True)
    inbox_enabled: bool = Field(default=True, strict=True)
    notifications_enabled: Literal[False] = False
    frequency: Literal["occasional", "rare", "every_reply"] = "occasional"
    depth: Literal["light", "personal"] = "light"
    topics: dict[Topic, Literal["enabled", "paused", "blocked"]] = Field(
        default_factory=lambda: {
            "interests": "enabled",
            "work": "enabled",
            "routines": "enabled",
            "relationships": "blocked",
            "reflection": "blocked",
        }
    )

    @field_validator("topics")
    @classmethod
    def complete_topics(cls, value):
        if set(value) != {"interests", "work", "routines", "relationships", "reflection"}:
            raise ValueError("All five topic choices are required")
        return value


class CuriosityPolicyWrite(CuriosityInput):
    operation_id: UUID
    expected_revision: int = Field(ge=0, strict=True)
    settings: CuriositySettings


class CuriosityPolicyOutput(BaseModel):
    version: Literal["ada-curiosity-v1"] = VERSION
    revision: int
    settings: CuriositySettings
    day_boundary: Literal["UTC"] = "UTC"
    inbox_daily_limit: Literal[2] = 2
    interview_daily_limit: Literal[10] = 10
    suppression_days: Literal[30] = 30
    permanent_suppressions: int


class CuriosityPinInput(CuriosityInput):
    source_version_id: UUID
    span_start: int = Field(ge=0, strict=True)
    span_end: int = Field(gt=0, strict=True)


class CuriosityCreate(CuriosityInput):
    operation_id: UUID
    policy_revision: int = Field(ge=1, strict=True)
    channel: Literal["chat", "inbox"]
    intent: Literal["normal", "interview"] = "normal"
    topic: Topic | None = None
    request_id: UUID | None = None
    source: CuriosityPinInput | None = None


class CuriosityAction(CuriosityInput):
    operation_id: UUID
    action: Literal[
        "skip", "not_now", "dismiss", "dont_ask_again", "pause_topic", "helpful", "unhelpful"
    ]


class CuriosityOpen(CuriosityInput):
    operation_id: UUID
    conversation_id: UUID
    personality_id: UUID


class CuriosityAnswer(CuriosityInput):
    operation_id: UUID
    request_id: UUID
    text: str = Field(min_length=1, max_length=4000, strict=True)

    @field_validator("text")
    @classmethod
    def valid_text(cls, value):
        validate_text(value)
        if not value.strip():
            raise ValueError("An owner-authored answer is required")
        return value


class CuriositySource(BaseModel):
    source_version_id: UUID
    scope_id: UUID
    content_hash: str
    span_start: int
    span_end: int
    quote: str
    trust_class: Literal["user_explicit"] = "user_explicit"
    created_at: Timestamp


class CuriosityQuestionOutput(BaseModel):
    version: Literal["ada-curiosity-v1"] = VERSION
    id: UUID
    scope_id: UUID
    conversation_id: UUID | None
    request_id: UUID | None
    opened_conversation_id: UUID | None
    answer_request_id: UUID | None
    channel: Literal["chat", "inbox"]
    topic: Topic
    state: str
    text: str | None
    reason: str | None
    policy: dict | None
    source: CuriositySource | None
    created_at: Timestamp
    expires_at: Timestamp
    available_at: Timestamp


class CuriosityReceiptOutput(BaseModel):
    version: Literal["ada-curiosity-v1"] = VERSION
    operation_id: UUID
    action: str
    state: str
    reason: str | None = None
    question_id: UUID | None = None
    conversation_id: UUID | None = None
    request_id: UUID | None = None
    policy_revision: int | None = None
    created_at: Timestamp


class CuriosityMetrics(BaseModel):
    offered: int = 0
    answered: int = 0
    skipped: int = 0
    dismissed: int = 0
    helpful: int = 0
    unhelpful: int = 0
