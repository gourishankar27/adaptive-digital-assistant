"""All enabled operations are authenticated, owner-derived, exact-key APIs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from ada.schedule_contracts import (
    ScheduleAction,
    ScheduleConfirm,
    ScheduleInboxAction,
    ScheduleInboxOutput,
    ScheduleOccurrenceOutput,
    ScheduleOpen,
    ScheduleOutput,
    SchedulePolicyOutput,
    SchedulePolicyWrite,
    SchedulePreview,
    ScheduleReceiptOutput,
)


def schedule_router(service, current_user, errors):
    router = APIRouter(tags=["durable-scheduling"])
    owner_dep = Annotated[str, Depends(current_user)]
    failures = errors(401, 404, 409, 410, 413, 422, 503)

    @router.get("/v1/scheduling/policy", response_model=SchedulePolicyOutput, responses=failures)
    def policy(owner: owner_dep):
        return service.policy(owner)

    @router.post("/v1/scheduling/policy", response_model=ScheduleReceiptOutput, responses=failures)
    def write_policy(body: SchedulePolicyWrite, request: Request, owner: owner_dep):
        return service.write_policy(owner, body, request.scope["ada.principal"])

    @router.get(
        "/v1/scheduling/receipts/{operation_id}",
        response_model=ScheduleReceiptOutput,
        responses=failures,
    )
    def receipt(operation_id: UUID, owner: owner_dep):
        return service.receipt(owner, str(operation_id))

    @router.post(
        "/v1/scopes/{scope_id}/schedules/preview",
        response_model=ScheduleReceiptOutput,
        responses=failures,
    )
    def preview(scope_id: UUID, body: SchedulePreview, request: Request, owner: owner_dep):
        return service.preview(owner, str(scope_id), body, request.scope["ada.principal"])

    @router.get(
        "/v1/scopes/{scope_id}/schedules", response_model=list[ScheduleOutput], responses=failures
    )
    def schedules(scope_id: UUID, owner: owner_dep):
        return service.schedules(owner, str(scope_id))

    @router.get("/v1/schedules/{schedule_id}", response_model=ScheduleOutput, responses=failures)
    def detail(schedule_id: UUID, owner: owner_dep):
        return service.detail(owner, str(schedule_id))

    @router.get(
        "/v1/schedules/{schedule_id}/occurrences",
        response_model=list[ScheduleOccurrenceOutput],
        responses=failures,
    )
    def occurrences(
        schedule_id: UUID,
        owner: owner_dep,
        limit: int = Query(100, ge=1, le=100),
        offset: int = Query(0, ge=0, le=999),
    ):
        return service.occurrences(owner, str(schedule_id), limit, offset)

    @router.post(
        "/v1/schedules/{schedule_id}/confirm",
        response_model=ScheduleReceiptOutput,
        responses=failures,
    )
    def confirm(schedule_id: UUID, body: ScheduleConfirm, request: Request, owner: owner_dep):
        return service.confirm(owner, str(schedule_id), body, request.scope["ada.principal"])

    @router.post(
        "/v1/schedules/{schedule_id}/actions",
        response_model=ScheduleReceiptOutput,
        responses=failures,
    )
    def action(schedule_id: UUID, body: ScheduleAction, request: Request, owner: owner_dep):
        return service.action(owner, str(schedule_id), body, request.scope["ada.principal"])

    @router.get(
        "/v1/scheduling/inbox", response_model=list[ScheduleInboxOutput], responses=failures
    )
    def inbox(
        owner: owner_dep,
        limit: int = Query(100, ge=1, le=100),
        offset: int = Query(0, ge=0, le=999),
    ):
        return service.inbox(owner, limit, offset)

    @router.post(
        "/v1/scheduling/inbox/{item_id}/actions",
        response_model=ScheduleReceiptOutput,
        responses=failures,
    )
    def inbox_action(item_id: UUID, body: ScheduleInboxAction, request: Request, owner: owner_dep):
        return service.inbox_action(owner, str(item_id), body, request.scope["ada.principal"])

    @router.post(
        "/v1/scheduling/inbox/{item_id}/open",
        response_model=ScheduleReceiptOutput,
        responses=failures,
    )
    def open_item(item_id: UUID, body: ScheduleOpen, request: Request, owner: owner_dep):
        return service.open(owner, str(item_id), body, request.scope["ada.principal"])

    return router
