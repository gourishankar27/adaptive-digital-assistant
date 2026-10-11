from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from ada.consolidation_contracts import (
    ConsolidationInput,
    ConsolidationOutput,
    EpisodeContextInput,
    EpisodeContextOutput,
    EpisodeOutput,
)


def consolidation_router(service, current_user, error_responses):
    router = APIRouter(prefix="/v1", tags=["episodes and consolidation"])
    private = Depends(current_user)
    failures = error_responses(401, 404, 409, 413, 422, 503)

    @router.post(
        "/scopes/{scope_id}/consolidation-jobs",
        response_model=ConsolidationOutput,
        responses={201: {"model": ConsolidationOutput}, **failures},
    )
    def enqueue(scope_id: UUID, body: ConsolidationInput, response: Response, owner: str = private):
        result, created = service.enqueue(owner, str(scope_id), body)
        response.status_code = 201 if created else 200
        return result

    @router.get(
        "/scopes/{scope_id}/consolidation-jobs",
        response_model=list[ConsolidationOutput],
        responses=failures,
    )
    def jobs(
        scope_id: UUID,
        owner: str = private,
        limit: int = Query(25, ge=1, le=50),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return service.jobs(owner, str(scope_id), limit, offset)

    @router.get(
        "/consolidation-jobs/{job_id}", response_model=ConsolidationOutput, responses=failures
    )
    def job(job_id: UUID, owner: str = private):
        return service.get(owner, str(job_id))

    @router.get(
        "/scopes/{scope_id}/episodes", response_model=list[EpisodeOutput], responses=failures
    )
    def episodes(
        scope_id: UUID,
        owner: str = private,
        limit: int = Query(25, ge=1, le=50),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return service.episodes(owner, str(scope_id), limit, offset)

    @router.get("/episodes/{episode_id}", response_model=EpisodeOutput, responses=failures)
    def episode(episode_id: UUID, owner: str = private):
        return service.episode(owner, str(episode_id))

    @router.post(
        "/scopes/{scope_id}/episode-contexts",
        response_model=EpisodeContextOutput,
        responses={201: {"model": EpisodeContextOutput}, **failures},
    )
    def context(
        scope_id: UUID, body: EpisodeContextInput, response: Response, owner: str = private
    ):
        result, created = service.context(owner, str(scope_id), body)
        response.status_code = 201 if created else 200
        return result

    @router.get(
        "/episode-contexts/{request_id}", response_model=EpisodeContextOutput, responses=failures
    )
    def frozen_context(request_id: UUID, owner: str = private):
        return service.get_context(owner, str(request_id))

    return router
