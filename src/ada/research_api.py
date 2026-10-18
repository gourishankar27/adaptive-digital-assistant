"""Owner-controlled research; no endpoint implicitly approves a follow-on call."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from ada.document_contracts import DocumentUploadOutput
from ada.research_contracts import (
    ResearchAction,
    ResearchApproval,
    ResearchCreate,
    ResearchNoteInput,
    ResearchOutput,
    WebSnapshotOutput,
)


def research_router(service, credentials, current_user, error_responses):
    router = APIRouter(tags=["public-web-research"])
    owner_dep = Annotated[str, Depends(current_user)]
    errors = error_responses(401, 404, 409, 410, 413, 422, 429, 503)

    def current(request):
        principal = request.scope.get("ada.principal")
        return lambda: principal is not None and credentials.current(principal)

    @router.post(
        "/v1/conversations/{conversation_id}/research-runs",
        response_model=ResearchOutput,
        responses=errors,
    )
    def create(conversation_id: UUID, body: ResearchCreate, owner: owner_dep):
        return service.create(owner, str(conversation_id), body)

    @router.get(
        "/v1/conversations/{conversation_id}/research-runs",
        response_model=list[ResearchOutput],
        responses=errors,
    )
    def runs(conversation_id: UUID, owner: owner_dep):
        return service.list(owner, str(conversation_id))

    @router.get("/v1/research-runs/{run_id}", response_model=ResearchOutput, responses=errors)
    def detail(run_id: UUID, owner: owner_dep):
        return service.detail(owner, str(run_id))

    @router.post(
        "/v1/research-runs/{run_id}/calls", response_model=ResearchOutput, responses=errors
    )
    def next_call(run_id: UUID, body: ResearchAction, owner: owner_dep):
        return service.next(owner, str(run_id), body)

    @router.post(
        "/v1/research-runs/{run_id}/approve", response_model=ResearchOutput, responses=errors
    )
    def approve(run_id: UUID, body: ResearchApproval, request: Request, owner: owner_dep):
        return service.approve(owner, str(run_id), body, current(request))

    @router.post(
        "/v1/research-runs/{run_id}/cancel", response_model=ResearchOutput, responses=errors
    )
    def cancel(run_id: UUID, owner: owner_dep):
        return service.cancel(owner, str(run_id))

    @router.post(
        "/v1/research-runs/{run_id}/answer", response_model=ResearchOutput, responses=errors
    )
    def answer(run_id: UUID, request: Request, owner: owner_dep):
        return service.answer(owner, str(run_id), current(request))

    @router.get(
        "/v1/research-runs/{run_id}/sources/{receipt_id}",
        response_model=WebSnapshotOutput,
        responses=errors,
    )
    def source(run_id: UUID, receipt_id: UUID, owner: owner_dep):
        return service.source(owner, str(run_id), str(receipt_id))

    @router.post(
        "/v1/research-runs/{run_id}/save-note",
        response_model=DocumentUploadOutput,
        responses=errors,
    )
    def save_note(run_id: UUID, body: ResearchNoteInput, owner: owner_dep):
        return service.save_note(owner, str(run_id), body)

    return router
