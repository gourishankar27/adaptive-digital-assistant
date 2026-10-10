"""Authenticated explicit identity APIs; all authority remains with the owner."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from ada.entities import EntityService
from ada.entity_contracts import (
    AliasInput,
    AliasOutput,
    EntityInput,
    EntityOperationOutput,
    EntityOutput,
    EntityResolutionOutput,
    LinkInput,
    MergeInput,
    MergePreviewOutput,
    OperationInput,
    RenameInput,
    ResolveInput,
    SelfInput,
)


def entity_router(sessions, current_user, error_responses):
    router = APIRouter(tags=["entities"])
    service = EntityService(sessions)
    principal = Annotated[str, Depends(current_user)]
    write_responses = {
        200: {"model": EntityOperationOutput, "description": "Identical operation replay"},
        **error_responses(401, 404, 409, 413, 422, 503),
    }
    reads = error_responses(401, 404, 409, 422, 503)

    def receipt(response, value):
        result, created = value
        response.status_code = 201 if created else 200
        return result

    @router.post(
        "/v1/scopes/{scope_id}/entities",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def create(scope_id: UUID, body: EntityInput, response: Response, owner: principal):
        return receipt(response, service.create(owner, str(scope_id), body))

    @router.get(
        "/v1/scopes/{scope_id}/entities", response_model=list[EntityOutput], responses=reads
    )
    def entities(
        scope_id: UUID,
        owner: principal,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return service.list(owner, str(scope_id), limit, offset)

    @router.post(
        "/v1/scopes/{scope_id}/entities/resolve",
        response_model=EntityResolutionOutput,
        responses=reads,
    )
    def resolve(scope_id: UUID, body: ResolveInput, owner: principal):
        return service.resolve(owner, str(scope_id), body)

    @router.post(
        "/v1/scopes/{scope_id}/entities/self",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def self_link(scope_id: UUID, body: SelfInput, response: Response, owner: principal):
        return receipt(response, service.self_link(owner, str(scope_id), body))

    @router.get(
        "/v1/scopes/{scope_id}/entity-audit",
        response_model=list[EntityOperationOutput],
        responses=reads,
    )
    def audit(
        scope_id: UUID,
        owner: principal,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return service.audit(owner, str(scope_id), limit, offset)

    @router.get(
        "/v1/entity-operations/{operation_id}",
        response_model=EntityOperationOutput,
        responses=reads,
    )
    def operation(operation_id: UUID, owner: principal):
        return service.operation(owner, str(operation_id))

    @router.get("/v1/entities/{entity_id}", response_model=EntityOutput, responses=reads)
    def entity(entity_id: UUID, owner: principal):
        return service.get(owner, str(entity_id))

    @router.get(
        "/v1/entities/{entity_id}/aliases", response_model=list[AliasOutput], responses=reads
    )
    def aliases(
        entity_id: UUID,
        owner: principal,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return service.aliases(owner, str(entity_id), limit, offset)

    @router.post(
        "/v1/entities/{entity_id}/aliases",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def add_alias(entity_id: UUID, body: AliasInput, response: Response, owner: principal):
        return receipt(response, service.mutate(owner, str(entity_id), "alias", body))

    @router.post(
        "/v1/entity-aliases/{alias_id}/retire",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def retire_alias(alias_id: UUID, body: OperationInput, response: Response, owner: principal):
        return receipt(response, service.retire_alias(owner, str(alias_id), body))

    @router.post(
        "/v1/entities/{entity_id}/rename",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def rename(entity_id: UUID, body: RenameInput, response: Response, owner: principal):
        return receipt(response, service.mutate(owner, str(entity_id), "rename", body))

    @router.get(
        "/v1/entities/{entity_id}/merge-preview", response_model=MergePreviewOutput, responses=reads
    )
    def preview(entity_id: UUID, target_id: UUID, owner: principal):
        return service.preview(owner, str(entity_id), str(target_id))

    @router.post(
        "/v1/entities/{entity_id}/merge",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def merge(entity_id: UUID, body: MergeInput, response: Response, owner: principal):
        return receipt(response, service.mutate(owner, str(entity_id), "merge", body))

    @router.post(
        "/v1/entities/{entity_id}/undo-merge",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def undo(entity_id: UUID, body: OperationInput, response: Response, owner: principal):
        return receipt(response, service.mutate(owner, str(entity_id), "undo_merge", body))

    @router.post(
        "/v1/claims/{claim_id}/entity",
        response_model=EntityOperationOutput,
        status_code=201,
        responses=write_responses,
    )
    def link(claim_id: UUID, body: LinkInput, response: Response, owner: principal):
        return receipt(response, service.claim_link(owner, str(claim_id), body))

    return router
