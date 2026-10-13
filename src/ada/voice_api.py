from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import create_model

from ada.stream_contracts import StreamStatus
from ada.voice_contracts import TranscriptInput, VoiceLineageOutput


def voice_router(service, current_user, error_responses, chat_input):
    reviewed_input = create_model(
        "ReviewedVoiceInput",
        __base__=chat_input,
        transcript=(TranscriptInput, ...),
        review=(Literal["approve"], ...),
    )
    router = APIRouter(prefix="/v1", tags=["voice"])
    private = Depends(current_user)
    errors = error_responses(401, 404, 409, 413, 422, 503)

    def submit(conversation_id: UUID, body, owner: str = private):
        return service.submit(owner, str(conversation_id), body)

    submit.__annotations__["body"] = reviewed_input
    router.post(
        "/conversations/{conversation_id}/voice-requests",
        status_code=202,
        response_model=StreamStatus,
        responses=errors,
    )(submit)

    @router.get(
        "/requests/{request_id}/voice-input", response_model=VoiceLineageOutput, responses=errors
    )
    def get(request_id: UUID, owner: str = private):
        return service.get(owner, str(request_id))

    @router.get(
        "/conversations/{conversation_id}/voice-inputs",
        response_model=list[VoiceLineageOutput],
        responses=errors,
    )
    def list_inputs(
        conversation_id: UUID,
        limit: int = Query(default=25, ge=1, le=50),
        offset: int = Query(default=0, ge=0, le=100000),
        owner: str = private,
    ):
        return service.list(owner, str(conversation_id), limit, offset)

    return router
