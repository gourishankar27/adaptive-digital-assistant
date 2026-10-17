"""Owner-only, explicit Phase23 read diagnostics and audited prompt upgrade."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ada.contracts import PromptUpgradeOutput
from ada.errors import ServiceError
from ada.models import Request, RetrievalTrace
from ada.personality import QUALITY_PROMPT_VERSION
from ada.retrieval import lock_scope_for_retrieval
from ada.temporal import (
    TimeResolution,
    TimeSelection,
    WindowRetrievalOutput,
    WindowRetrieveInput,
    resolve_time,
    retrieve_window,
)


class QualityContextOutput(BaseModel):
    request_id: UUID
    policy: dict | None = None
    explanation: str = Field(default="Older request snapshots are not reconstructed or upgraded.")


def quality_router(service, sessions, current_user, error_responses):
    router = APIRouter(tags=["answer-quality"])
    principal = Annotated[str, Depends(current_user)]
    errors = error_responses(401, 404, 409, 422)

    @router.post("/v1/temporal/resolve", response_model=TimeResolution, responses=errors)
    def resolve(body: TimeSelection, owner: principal):
        return resolve_time(body)

    @router.post(
        "/v1/scopes/{scope_id}/retrieve-window",
        response_model=WindowRetrievalOutput,
        responses=errors,
    )
    def window(scope_id: UUID, body: WindowRetrieveInput, owner: principal):
        with sessions.begin() as db:
            lock_scope_for_retrieval(db, owner, str(scope_id))
            return retrieve_window(db, owner, str(scope_id), body)

    @router.post(
        "/v1/conversations/{conversation_id}/quality-upgrade",
        response_model=PromptUpgradeOutput,
        responses=errors,
    )
    def upgrade(conversation_id: UUID, owner: principal):
        return service.upgrade_prompt(owner, str(conversation_id), target=QUALITY_PROMPT_VERSION)

    @router.get(
        "/v1/requests/{request_id}/quality-context",
        response_model=QualityContextOutput,
        responses=errors,
    )
    def context(request_id: UUID, owner: principal):
        with sessions() as db:
            row = db.get(Request, (owner, str(request_id)))
            if row is None:
                raise ServiceError(404, "request_not_found")
            trace = db.get(RetrievalTrace, (owner, str(request_id)))
            return {
                "request_id": request_id,
                "policy": trace.plan.get("quality_context") if trace else None,
            }

    return router
