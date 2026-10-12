from uuid import UUID

from fastapi import APIRouter, Depends, Response

from ada.expression_contracts import (
    ExpressionOutput,
    ExpressionReceiptOutput,
    PreferenceOutput,
    PreferenceWrite,
    RequestExpressionOutput,
    SessionReset,
    SignalWrite,
    TargetKind,
)


def expression_router(service, current_user, error_responses):
    router = APIRouter(prefix="/v1", tags=["interaction preferences"])
    private = Depends(current_user)
    errors = error_responses(401, 404, 409, 413, 422, 503)

    @router.get(
        "/preferences/{kind}/{target_id}", response_model=PreferenceOutput, responses=errors
    )
    def preference(kind: TargetKind, target_id: UUID, owner: str = private):
        return service.preference(owner, kind, str(target_id))

    @router.post(
        "/preferences/{kind}/{target_id}",
        response_model=ExpressionReceiptOutput,
        responses={201: {"model": ExpressionReceiptOutput}, **errors},
    )
    def write(
        kind: TargetKind,
        target_id: UUID,
        body: PreferenceWrite,
        response: Response,
        owner: str = private,
    ):
        value, created = service.write_preference(owner, kind, str(target_id), body)
        response.status_code = 201 if created else 200
        return value

    @router.get(
        "/conversations/{conversation_id}/expression",
        response_model=ExpressionOutput,
        responses=errors,
    )
    def inspect(conversation_id: UUID, owner: str = private):
        return service.inspect(owner, str(conversation_id))

    @router.post(
        "/conversations/{conversation_id}/expression/signals",
        response_model=ExpressionReceiptOutput,
        responses={201: {"model": ExpressionReceiptOutput}, **errors},
    )
    def signal(conversation_id: UUID, body: SignalWrite, response: Response, owner: str = private):
        value, created = service.signal_or_reset(owner, str(conversation_id), body, "signal")
        response.status_code = 201 if created else 200
        return value

    @router.post(
        "/conversations/{conversation_id}/expression/reset",
        response_model=ExpressionReceiptOutput,
        responses={201: {"model": ExpressionReceiptOutput}, **errors},
    )
    def reset(conversation_id: UUID, body: SessionReset, response: Response, owner: str = private):
        value, created = service.signal_or_reset(owner, str(conversation_id), body, "reset")
        response.status_code = 201 if created else 200
        return value

    @router.get(
        "/expression-receipts/{operation_id}",
        response_model=ExpressionReceiptOutput,
        responses=errors,
    )
    def receipt(operation_id: UUID, owner: str = private):
        return service.receipt(owner, str(operation_id))

    @router.get(
        "/requests/{request_id}/expression",
        response_model=RequestExpressionOutput,
        responses=errors,
    )
    def snapshot(request_id: UUID, owner: str = private):
        return service.request_snapshot(owner, str(request_id))

    return router
