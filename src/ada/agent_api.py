"""Opt-in owned agent routes. Ordinary chat never invokes this router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from ada.agent_contracts import (
    AgentInput,
    AgentRunOutput,
    ApprovalInput,
    ProtocolOutput,
    RecoverInput,
    ToolReceiptOutput,
    ToolSpecOutput,
)
from ada.agents import protocol
from ada.tools import REGISTRY


def agent_router(service, current_user, error_responses):
    router = APIRouter(tags=["read-only-agents"])
    principal = Annotated[str, Depends(current_user)]
    errors = error_responses(401, 403, 404, 409, 413, 422, 503)

    @router.get("/v1/tools", response_model=list[ToolSpecOutput], responses=errors)
    def tools(owner: principal):
        return [spec.public() for spec in REGISTRY.values()]

    @router.get("/v1/agent-protocols", response_model=list[ProtocolOutput], responses=errors)
    def protocols(owner: principal):
        return [protocol()]

    @router.post(
        "/v1/conversations/{conversation_id}/agent-runs",
        status_code=201,
        response_model=AgentRunOutput,
        responses={200: {"model": AgentRunOutput}, **errors},
    )
    def create(conversation_id: UUID, body: AgentInput, response: Response, owner: principal):
        value, created = service.create(owner, str(conversation_id), body)
        response.status_code = 201 if created else 200
        return value

    @router.get(
        "/v1/conversations/{conversation_id}/agent-runs",
        response_model=list[AgentRunOutput],
        responses=errors,
    )
    def runs(
        conversation_id: UUID,
        owner: principal,
        limit: int = Query(25, ge=1, le=50),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return service.list(owner, str(conversation_id), limit, offset)

    @router.get("/v1/agent-runs/{run_id}", response_model=AgentRunOutput, responses=errors)
    def detail(run_id: UUID, owner: principal):
        return service.detail(owner, str(run_id))

    @router.post(
        "/v1/agent-runs/{run_id}/steps/{step_id}/approve",
        status_code=201,
        response_model=ToolReceiptOutput,
        responses={200: {"model": ToolReceiptOutput}, **errors},
    )
    def approve(
        run_id: UUID, step_id: UUID, body: ApprovalInput, response: Response, owner: principal
    ):
        value, created = service.approve(owner, str(run_id), str(step_id), body)
        response.status_code = 201 if created else 200
        return value

    @router.post(
        "/v1/agent-runs/{run_id}/steps/{step_id}/revoke",
        status_code=201,
        response_model=ToolReceiptOutput,
        responses={200: {"model": ToolReceiptOutput}, **errors},
    )
    def revoke(
        run_id: UUID, step_id: UUID, body: ApprovalInput, response: Response, owner: principal
    ):
        value, created = service.approve(owner, str(run_id), str(step_id), body, decision="revoke")
        response.status_code = 201 if created else 200
        return value

    @router.post(
        "/v1/agent-runs/{run_id}/recover",
        status_code=201,
        response_model=ToolReceiptOutput,
        responses={200: {"model": ToolReceiptOutput}, **errors},
    )
    def recover(run_id: UUID, body: RecoverInput, response: Response, owner: principal):
        value, created = service.recover(owner, str(run_id), body)
        response.status_code = 201 if created else 200
        return value

    @router.get(
        "/v1/tool-receipts/{receipt_id}", response_model=ToolReceiptOutput, responses=errors
    )
    def receipt(receipt_id: UUID, owner: principal):
        return service.receipt(owner, str(receipt_id))

    return router
