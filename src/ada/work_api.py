"""Owned work review and resume APIs; no admin reader or tool registry entry."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ada.errors import ServiceError
from ada.work_contracts import (
    WorkBriefInput,
    WorkBriefOutput,
    WorkFollowup,
    WorkOutput,
    WorkPreviewOutput,
    WorkProjectCreate,
    WorkReceiptOutput,
    WorkReminderConfirm,
    WorkReminderPreview,
    WorkRevisionOutput,
    WorkWrite,
)


def invoke(action, *args):
    try:
        return action(*args)
    except IntegrityError:
        raise ServiceError(409, "work_storage_conflict") from None
    except SQLAlchemyError:
        raise ServiceError(503, "work_storage_unavailable") from None


def work_router(service, current_user, errors):
    router = APIRouter(tags=["projects-and-follow-through"])
    owner_dep = Annotated[str, Depends(current_user)]
    failures = errors(401, 404, 409, 410, 413, 422, 503)

    @router.get("/v1/scopes/{scope_id}/work", response_model=list[WorkOutput], responses=failures)
    def items(scope_id: UUID, owner: owner_dep, offset: int = Query(0, ge=0, le=150)):
        return invoke(service.items, owner, str(scope_id), offset)

    @router.post(
        "/v1/work/projects/{scope_id}", response_model=WorkReceiptOutput, responses=failures
    )
    def project(scope_id: UUID, body: WorkProjectCreate, request: Request, owner: owner_dep):
        try:
            return invoke(
                service.project, owner, str(scope_id), body, request.scope["ada.principal"]
            )
        except IntegrityError:
            raise ServiceError(409, "work_project_id_reused") from None

    @router.get("/v1/work/{item_id}", response_model=WorkOutput, responses=failures)
    def detail(item_id: UUID, owner: owner_dep):
        return invoke(service.detail, owner, str(item_id))

    @router.get(
        "/v1/work/{item_id}/history", response_model=list[WorkRevisionOutput], responses=failures
    )
    def history(item_id: UUID, owner: owner_dep, offset: int = Query(0, ge=0, le=1900)):
        return invoke(service.history, owner, str(item_id), offset)

    @router.post(
        "/v1/scopes/{scope_id}/work/{item_id}/preview",
        response_model=WorkPreviewOutput,
        responses=failures,
    )
    def preview(scope_id: UUID, item_id: UUID, body: WorkWrite, request: Request, owner: owner_dep):
        return invoke(
            service.preview,
            owner,
            str(scope_id),
            str(item_id),
            body,
            request.scope["ada.principal"],
        )

    @router.post(
        "/v1/scopes/{scope_id}/work/{item_id}", response_model=WorkReceiptOutput, responses=failures
    )
    def write(scope_id: UUID, item_id: UUID, body: WorkWrite, request: Request, owner: owner_dep):
        return invoke(
            service.write, owner, str(scope_id), str(item_id), body, request.scope["ada.principal"]
        )

    @router.get(
        "/v1/work/receipts/{operation_id}", response_model=WorkReceiptOutput, responses=failures
    )
    def receipt(operation_id: UUID, owner: owner_dep):
        return invoke(service.receipt, owner, str(operation_id))

    @router.post("/v1/work/briefs", response_model=WorkBriefOutput, responses=failures)
    def brief(body: WorkBriefInput, request: Request, owner: owner_dep):
        return invoke(service.brief, owner, body, request.scope["ada.principal"])

    @router.get("/v1/work/briefs/{brief_id}", response_model=WorkBriefOutput, responses=failures)
    def brief_detail(brief_id: UUID, owner: owner_dep):
        return invoke(service.brief_detail, owner, str(brief_id))

    @router.post(
        "/v1/work/{item_id}/followup", response_model=WorkReceiptOutput, responses=failures
    )
    def followup(item_id: UUID, body: WorkFollowup, request: Request, owner: owner_dep):
        return invoke(service.followup, owner, str(item_id), body, request.scope["ada.principal"])

    @router.post(
        "/v1/work/{item_id}/reminder-preview", response_model=WorkReceiptOutput, responses=failures
    )
    def reminder_preview(
        item_id: UUID, body: WorkReminderPreview, request: Request, owner: owner_dep
    ):
        return invoke(
            service.reminder_preview, owner, str(item_id), body, request.scope["ada.principal"]
        )

    @router.post(
        "/v1/work/{item_id}/reminder-confirm", response_model=WorkReceiptOutput, responses=failures
    )
    def reminder_confirm(
        item_id: UUID, body: WorkReminderConfirm, request: Request, owner: owner_dep
    ):
        return invoke(
            service.reminder_confirm, owner, str(item_id), body, request.scope["ada.principal"]
        )

    return router
