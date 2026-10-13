from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ada.evidence import validate_text
from ada.memory import Timestamp


class TranscriptInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transcript_id: UUID
    engine_id: Literal["android_on_device"]
    # Reported platform version, not a claim of attested engine package/version.
    engine_version: str = Field(min_length=1, max_length=120, pattern=r"^[\x20-\x7e]+$")
    language: str = Field(
        min_length=2, max_length=35, pattern=r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8}){0,4}$"
    )
    duration_ms: int = Field(ge=1, le=60000, strict=True)
    original_text: str = Field(min_length=1, max_length=4000)

    @field_validator("original_text")
    @classmethod
    def valid_original(cls, value):
        validate_text(value)
        if not value.strip():
            raise ValueError("transcript cannot be blank")
        return value


class VoiceLineageOutput(BaseModel):
    request_id: UUID
    conversation_id: UUID
    scope_id: UUID
    transcript_id: UUID
    engine_id: str
    engine_version: str
    engine_metadata: Literal["client_reported"] = "client_reported"
    language: str
    duration_ms: int
    original_text: str
    original_hash: str
    original_origin: Literal["asr_generated"] = "asr_generated"
    original_trust: Literal["generated_interpretation"] = "generated_interpretation"
    reviewed_text: str
    reviewed_hash: str
    reviewed_origin: Literal["user_reviewed"] = "user_reviewed"
    endorsement_source_version_id: UUID
    approved_at: Timestamp
    audio_storage: Literal["not_received_by_server"] = "not_received_by_server"
    audio_sha256: None = None
