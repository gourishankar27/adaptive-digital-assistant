"""Expression is a typed style policy, never evidence or authorization."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ada.memory import Timestamp

POLICY_VERSION = "ada-expression-v1"
TargetKind = Literal["account", "scope", "profile", "conversation"]


class ExpressionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PreferenceValues(ExpressionInput):
    verbosity: Literal["concise", "balanced", "detailed"] | None = None
    initiative: Literal["respond", "suggest"] | None = None
    formality: Literal["casual", "neutral", "formal"] | None = None
    humor: Literal["none", "light"] | None = None
    cadence: Literal["direct", "stepwise"] | None = None


class EffectivePreferences(ExpressionInput):
    verbosity: Literal["concise", "balanced", "detailed"]
    initiative: Literal["respond", "suggest"]
    formality: Literal["casual", "neutral", "formal"]
    humor: Literal["none", "light"]
    cadence: Literal["direct", "stepwise"]


class PreferenceWrite(ExpressionInput):
    operation_id: UUID
    expected_revision: int = Field(ge=0, strict=True)
    values: PreferenceValues
    dynamic_enabled: bool | None = Field(default=None, strict=True)


class ExpressionVector(ExpressionInput):
    warmth: int = Field(ge=0, le=100, strict=True)
    focus: int = Field(ge=0, le=100, strict=True)
    energy: int = Field(ge=0, le=100, strict=True)
    playfulness: int = Field(ge=0, le=100, strict=True)
    concern: int = Field(ge=0, le=100, strict=True)


class SignalVector(ExpressionInput):
    warmth: int | None = Field(default=None, ge=-1000, le=1000, strict=True)
    focus: int | None = Field(default=None, ge=-1000, le=1000, strict=True)
    energy: int | None = Field(default=None, ge=-1000, le=1000, strict=True)
    playfulness: int | None = Field(default=None, ge=-1000, le=1000, strict=True)
    concern: int | None = Field(default=None, ge=-1000, le=1000, strict=True)


class SignalWrite(ExpressionInput):
    operation_id: UUID
    session_id: UUID
    source_request_id: UUID
    reviewed: Literal[True]
    reason: Literal["user_selected", "reviewed_model_signal"]
    vector: SignalVector

    @field_validator("reviewed", mode="before")
    @classmethod
    def explicit_review(cls, value):
        if value is not True:
            raise ValueError("explicit review is required")
        return value


class SessionReset(ExpressionInput):
    operation_id: UUID
    session_id: UUID


class PreferenceOutput(BaseModel):
    target_kind: TargetKind
    target_id: UUID
    revision: int
    values: PreferenceValues
    receipt_id: UUID | None


class ExpressionOutput(BaseModel):
    policy_version: Literal["ada-expression-v1"] = POLICY_VERSION
    conversation_id: UUID
    profile_id: UUID
    scope_id: UUID
    active: bool
    binding_revision: int
    preferences: EffectivePreferences
    origins: dict[str, Literal["personality", "account", "scope", "profile", "conversation"]]
    source_receipts: dict[str, UUID | None]
    dynamic_enabled: bool
    session_id: UUID | None
    turn: int
    vector: ExpressionVector
    defaults: ExpressionVector
    expires_at: Timestamp | None
    expired: bool
    last_request_id: UUID | None


class ExpressionReceiptOutput(BaseModel):
    operation_id: UUID
    action: Literal["preferences", "signal", "reset"]
    target_kind: TargetKind
    target_id: UUID
    created_at: Timestamp
    reason: Literal["explicit_settings", "user_reset", "user_selected", "reviewed_model_signal"]
    source_request_id: UUID | None = None
    preference: PreferenceOutput | None = None
    expression: ExpressionOutput | None = None


class RequestExpressionOutput(BaseModel):
    request_id: UUID
    expression: ExpressionOutput | None
