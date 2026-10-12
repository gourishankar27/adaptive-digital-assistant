from typing import TYPE_CHECKING, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ada.memory import Timestamp

if TYPE_CHECKING:
    from ada.api import RequestOutput

StreamState = Literal[
    "running", "cancel_requested", "completed", "failed", "cancelled", "interrupted"
]


class CancelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attempt: int = Field(ge=1, le=1000000, strict=True)


class CancelReceipt(BaseModel):
    request_id: UUID
    attempt: int
    outcome: Literal["requested", "already_terminal"]
    observed_state: StreamState
    created_at: Timestamp


class StreamStatus(BaseModel):
    request_id: UUID
    conversation_id: UUID
    attempt: int
    available: bool
    stream_state: StreamState
    sequence: int
    replay_after: int
    provisional: str
    # Bound in the route factory to the unchanged legacy output model.
    result: "RequestOutput"


class StreamEventOutput(BaseModel):
    request_id: UUID
    attempt: int
    sequence: int
    type: Literal[
        "started",
        "delta",
        "status",
        "completed",
        "failed",
        "cancel_requested",
        "cancelled",
        "interrupted",
    ]
    payload: dict
    created_at: Timestamp
