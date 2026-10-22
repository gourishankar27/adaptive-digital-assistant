"""Owner-only installation registration and untrusted draft receipts."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ada.edge_contracts import (
    EdgeDeviceOutput,
    EdgeEnroll,
    EdgeProposalOutput,
    EdgeRevoke,
    EdgeSync,
)
from ada.errors import ServiceError


def invoke(action, *args):
    try:
        return action(*args)
    except IntegrityError:
        raise ServiceError(409, "edge_storage_conflict") from None
    except SQLAlchemyError:
        raise ServiceError(503, "edge_storage_unavailable") from None


def edge_router(service, current_user, errors):
    router = APIRouter(tags=["device-drafts"])
    owner_dep = Annotated[str, Depends(current_user)]
    responses = errors(401, 404, 409, 410, 413, 422, 503)

    @router.get("/v1/edge/devices", response_model=list[EdgeDeviceOutput], responses=responses)
    def devices(owner: owner_dep):
        return invoke(service.devices, owner)

    @router.post(
        "/v1/edge/devices/{device_id}", response_model=EdgeDeviceOutput, responses=responses
    )
    def enroll(device_id: UUID, body: EdgeEnroll, request: Request, owner: owner_dep):
        return invoke(service.enroll, owner, str(device_id), body, request.scope["ada.principal"])

    @router.post(
        "/v1/edge/devices/{device_id}/revoke", response_model=EdgeDeviceOutput, responses=responses
    )
    def revoke(device_id: UUID, body: EdgeRevoke, request: Request, owner: owner_dep):
        return invoke(service.revoke, owner, str(device_id), body, request.scope["ada.principal"])

    @router.post(
        "/v1/scopes/{scope_id}/edge/proposals/{proposal_id}",
        response_model=EdgeProposalOutput,
        responses=responses,
    )
    def sync(scope_id: UUID, proposal_id: UUID, body: EdgeSync, request: Request, owner: owner_dep):
        return invoke(
            service.sync,
            owner,
            str(scope_id),
            str(proposal_id),
            body,
            request.scope["ada.principal"],
        )

    @router.get(
        "/v1/edge/proposals/{proposal_id}", response_model=EdgeProposalOutput, responses=responses
    )
    def get(proposal_id: UUID, owner: owner_dep):
        return invoke(service.get, owner, str(proposal_id))

    return router
