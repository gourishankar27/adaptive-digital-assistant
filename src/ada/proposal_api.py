"""Owner-only proposal APIs; extraction has no approval capability."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from ada.proposal_contracts import (
    EditInput,
    ExtractionInput,
    ExtractionOutput,
    ProposalOutput,
    ReviewInput,
    ReviewOutput,
)


def proposal_router(service, current_user, error_responses):
    router = APIRouter(tags=["memory-review"])
    principal = Annotated[str, Depends(current_user)]
    errors = error_responses(401, 404, 409, 413, 422, 503)

    @router.post(
        "/v1/scopes/{scope_id}/memory-extractions",
        status_code=201,
        response_model=ExtractionOutput,
        responses={200: {"model": ExtractionOutput}, **errors},
    )
    def extract(scope_id: UUID, body: ExtractionInput, response: Response, owner: principal):
        value, created = service.extract(owner, str(scope_id), body)
        response.status_code = 201 if created else 200
        return value

    @router.get(
        "/v1/memory-extractions/{extraction_id}", response_model=ExtractionOutput, responses=errors
    )
    def extraction(extraction_id: UUID, owner: principal):
        return service.extraction(owner, str(extraction_id))

    @router.get(
        "/v1/scopes/{scope_id}/memory-proposals",
        response_model=list[ProposalOutput],
        responses=errors,
    )
    def inbox(
        scope_id: UUID,
        owner: principal,
        status: Literal["pending", "accepted", "rejected"] | None = "pending",
        limit: int = Query(25, ge=1, le=50),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return service.list(owner, str(scope_id), status, limit, offset)

    @router.get(
        "/v1/memory-proposals/{proposal_id}", response_model=ProposalOutput, responses=errors
    )
    def detail(proposal_id: UUID, owner: principal):
        return service.detail(owner, str(proposal_id))

    @router.post(
        "/v1/memory-proposals/{proposal_id}/edit", response_model=ProposalOutput, responses=errors
    )
    def edit(proposal_id: UUID, body: EditInput, owner: principal):
        return service.edit(owner, str(proposal_id), body)

    @router.post(
        "/v1/memory-proposals/{proposal_id}/review",
        status_code=201,
        response_model=ReviewOutput,
        responses={200: {"model": ReviewOutput}, **errors},
    )
    def review(proposal_id: UUID, body: ReviewInput, response: Response, owner: principal):
        value, created = service.review(owner, str(proposal_id), body)
        response.status_code = 201 if created else 200
        return value

    @router.get("/v1/memory-reviews/{review_id}", response_model=ReviewOutput, responses=errors)
    def receipt(review_id: UUID, owner: principal):
        return service.receipt(owner, str(review_id))

    return router
