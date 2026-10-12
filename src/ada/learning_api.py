from uuid import UUID

from fastapi import APIRouter, Depends, Response

from ada.learning_contracts import (
    LearningConfigWrite,
    LearningReceiptOutput,
    LearningResetWrite,
    LearningReviewWrite,
    LearningStateOutput,
    ObservationWrite,
    RequestLearningOutput,
)


def learning_router(service, current_user, error_responses):
    router = APIRouter(prefix="/v1", tags=["interaction learning"])
    private = Depends(current_user)
    errors = error_responses(401, 404, 409, 413, 422, 503)

    @router.get("/scopes/{scope_id}/learning", response_model=LearningStateOutput, responses=errors)
    def state(scope_id: UUID, owner: str = private):
        return service.state(owner, str(scope_id))

    def status(response, result):
        value, created = result
        response.status_code = 201 if created else 200
        return value

    writes = {201: {"model": LearningReceiptOutput}, **errors}

    @router.post(
        "/scopes/{scope_id}/learning/config", response_model=LearningReceiptOutput, responses=writes
    )
    def configure(
        scope_id: UUID, body: LearningConfigWrite, response: Response, owner: str = private
    ):
        return status(response, service.configure(owner, str(scope_id), body))

    @router.post(
        "/scopes/{scope_id}/learning/observations",
        response_model=LearningReceiptOutput,
        responses=writes,
    )
    def observe(scope_id: UUID, body: ObservationWrite, response: Response, owner: str = private):
        return status(response, service.observe(owner, str(scope_id), body))

    @router.post(
        "/scopes/{scope_id}/learning/reviews",
        response_model=LearningReceiptOutput,
        responses=writes,
    )
    def review(scope_id: UUID, body: LearningReviewWrite, response: Response, owner: str = private):
        return status(response, service.review(owner, str(scope_id), body))

    @router.post(
        "/scopes/{scope_id}/learning/reset", response_model=LearningReceiptOutput, responses=writes
    )
    def reset(scope_id: UUID, body: LearningResetWrite, response: Response, owner: str = private):
        return status(response, service.configure(owner, str(scope_id), body, reset=True))

    @router.get(
        "/learning-receipts/{operation_id}", response_model=LearningReceiptOutput, responses=errors
    )
    def receipt(operation_id: UUID, owner: str = private):
        return service.receipt(owner, str(operation_id))

    @router.get(
        "/requests/{request_id}/learning", response_model=RequestLearningOutput, responses=errors
    )
    def snapshot(request_id: UUID, owner: str = private):
        return service.request_snapshot(owner, str(request_id))

    return router
