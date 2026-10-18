"""Owned curiosity controls, optional companion replies and later inbox."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from ada.curiosity_contracts import (
    CuriosityAction,
    CuriosityAnswer,
    CuriosityCreate,
    CuriosityMetrics,
    CuriosityOpen,
    CuriosityPolicyOutput,
    CuriosityPolicyWrite,
    CuriosityQuestionOutput,
    CuriosityReceiptOutput,
)


def curiosity_router(service, credentials, current_user, error_responses):
    router = APIRouter(tags=["conversational-curiosity"])
    owner_dep = Annotated[str, Depends(current_user)]
    errors = error_responses(401, 404, 409, 410, 413, 422, 429, 502, 503)

    @router.get("/v1/curiosity/policy", response_model=CuriosityPolicyOutput, responses=errors)
    def policy(owner: owner_dep):
        return service.policy(owner)

    @router.post("/v1/curiosity/policy", response_model=CuriosityReceiptOutput, responses=errors)
    def write_policy(body: CuriosityPolicyWrite, owner: owner_dep):
        return service.write_policy(owner, body)

    @router.get(
        "/v1/curiosity/receipts/{operation_id}",
        response_model=CuriosityReceiptOutput,
        responses=errors,
    )
    def receipt(operation_id: UUID, owner: owner_dep):
        return service.receipt(owner, str(operation_id))

    @router.get(
        "/v1/scopes/{scope_id}/curiosity/questions",
        response_model=list[CuriosityQuestionOutput],
        responses=errors,
    )
    def questions(scope_id: UUID, owner: owner_dep):
        return service.questions(owner, scope=str(scope_id))

    @router.post(
        "/v1/scopes/{scope_id}/curiosity/questions",
        response_model=CuriosityReceiptOutput,
        responses=errors,
    )
    def create(scope_id: UUID, body: CuriosityCreate, owner: owner_dep):
        return service.create(owner, str(scope_id), body)

    @router.get(
        "/v1/curiosity/questions/{question_id}",
        response_model=CuriosityQuestionOutput,
        responses=errors,
    )
    def detail(question_id: UUID, owner: owner_dep):
        return service.detail(owner, str(question_id))

    @router.post(
        "/v1/curiosity/questions/{question_id}/actions",
        response_model=CuriosityReceiptOutput,
        responses=errors,
    )
    def action(question_id: UUID, body: CuriosityAction, owner: owner_dep):
        return service.action(owner, str(question_id), body)

    @router.post(
        "/v1/curiosity/questions/{question_id}/open",
        response_model=CuriosityReceiptOutput,
        responses=errors,
    )
    def open_question(question_id: UUID, body: CuriosityOpen, owner: owner_dep):
        return service.open(owner, str(question_id), body)

    @router.post(
        "/v1/curiosity/questions/{question_id}/answer",
        response_model=CuriosityReceiptOutput,
        responses=errors,
    )
    def answer(question_id: UUID, body: CuriosityAnswer, request: Request, owner: owner_dep):
        principal = request.scope.get("ada.principal")
        return service.answer(
            owner,
            str(question_id),
            body,
            lambda: principal is not None and credentials.current(principal),
        )

    @router.get(
        "/v1/conversations/{conversation_id}/curiosity/questions",
        response_model=list[CuriosityQuestionOutput],
        responses=errors,
    )
    def conversation_questions(conversation_id: UUID, owner: owner_dep):
        return service.questions(owner, conversation=str(conversation_id))

    @router.get("/v1/curiosity/metrics", response_model=CuriosityMetrics, responses=errors)
    def metrics(owner: owner_dep):
        return service.metrics(owner)

    return router
