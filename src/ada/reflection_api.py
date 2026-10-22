"""Authenticated owner review; no remote execute/run or factual acceptance API."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from ada.reflection_contracts import (
    ReflectionAction,
    ReflectionArtifactOutput,
    ReflectionPolicyOutput,
    ReflectionPolicyWrite,
    ReflectionReceiptOutput,
    ReflectionRunOutput,
)


def reflection_router(service, current_user, errors):
    router = APIRouter(tags=["idle-reflection"])
    owner_dep = Annotated[str, Depends(current_user)]
    failures = errors(401, 404, 409, 413, 422, 503)

    @router.get("/v1/reflection/policy", response_model=ReflectionPolicyOutput, responses=failures)
    def policy(owner: owner_dep):
        return service.policy(owner)

    @router.post(
        "/v1/reflection/policy", response_model=ReflectionReceiptOutput, responses=failures
    )
    def write_policy(body: ReflectionPolicyWrite, request: Request, owner: owner_dep):
        return service.write_policy(owner, body, request.scope["ada.principal"])

    @router.get(
        "/v1/reflection/receipts/{operation_id}",
        response_model=ReflectionReceiptOutput,
        responses=failures,
    )
    def receipt(operation_id: UUID, owner: owner_dep):
        return service.receipt(owner, str(operation_id))

    @router.get(
        "/v1/reflection/artifacts",
        response_model=list[ReflectionArtifactOutput],
        responses=failures,
    )
    def artifacts(
        owner: owner_dep,
        limit: int = Query(100, ge=1, le=100),
        offset: int = Query(0, ge=0, le=999),
    ):
        return service.artifacts(owner, limit, offset)

    @router.get(
        "/v1/reflection/artifacts/{artifact_id}",
        response_model=ReflectionArtifactOutput,
        responses=failures,
    )
    def artifact(artifact_id: UUID, owner: owner_dep):
        return service.artifact(owner, str(artifact_id))

    @router.post(
        "/v1/reflection/artifacts/{artifact_id}/actions",
        response_model=ReflectionReceiptOutput,
        responses=failures,
    )
    def action(artifact_id: UUID, body: ReflectionAction, request: Request, owner: owner_dep):
        return service.action(owner, str(artifact_id), body, request.scope["ada.principal"])

    @router.get("/v1/reflection/runs", response_model=list[ReflectionRunOutput], responses=failures)
    def runs(
        owner: owner_dep,
        limit: int = Query(100, ge=1, le=100),
        offset: int = Query(0, ge=0, le=999),
    ):
        return service.runs(owner, limit, offset)

    return router
