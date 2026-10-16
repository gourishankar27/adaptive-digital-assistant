"""Owner-only credential and explicit saved-content privacy contracts."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select

from ada.evidence import validate_text
from ada.memory import Timestamp
from ada.models import User


class CredentialInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    operation_id: UUID
    label: str = Field(min_length=1, max_length=80)
    lifetime_days: int = Field(default=30, ge=1, le=90, strict=True)

    @field_validator("label")
    @classmethod
    def label_text(cls, value):
        return validate_text(value)


class CredentialOutput(BaseModel):
    id: UUID
    label: str
    created_at: Timestamp
    expires_at: Timestamp
    last_used_at: Timestamp | None
    revoked_at: Timestamp | None
    rotated_from_id: UUID | None


class CredentialIssueOutput(BaseModel):
    credential: CredentialOutput
    token: str | None = Field(repr=False)


class SecurityStatusOutput(BaseModel):
    owner_id: UUID
    current_credential_id: UUID | None
    legacy_credential: bool
    enrollment_enabled: bool
    deletion_worker_enabled: bool
    data_epoch: int = Field(ge=0)
    retention: Literal["until_explicit_owner_deletion"]
    telemetry: dict[str, int | str]


class DeletionPreviewOutput(BaseModel):
    id: UUID
    revision: int = Field(ge=0)
    created_at: Timestamp
    expires_at: Timestamp
    counts: dict[str, int]
    retained: list[str]
    backups_may_retain_content: bool
    offline_clients_may_retain_content: bool


class DeletionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: UUID
    preview_id: UUID
    confirmation: Literal["erase_saved_content"]


class DeletionOutput(BaseModel):
    id: UUID
    status: Literal["queued", "running", "completed", "failed"]
    attempt: int = Field(ge=0, le=3)
    created_at: Timestamp
    finished_at: Timestamp | None
    error_code: str | None
    counts: dict[str, int]
    backups_may_retain_content: bool
    offline_clients_may_retain_content: bool


def security_router(credentials, deletion, gate, current_user, error_responses):
    router = APIRouter(prefix="/v1/security", tags=["security and privacy"])
    private = Depends(current_user)
    errors = error_responses(401, 404, 409, 413, 422, 429, 503)

    @router.get("/status", response_model=SecurityStatusOutput, responses=errors)
    def status(request: Request, owner: str = private):
        principal = request.scope["ada.principal"]
        with credentials.sessions() as db:
            epoch = db.scalar(select(User.data_epoch).where(User.id == owner))
        return {
            "owner_id": owner,
            "current_credential_id": principal.credential_id,
            "legacy_credential": principal.credential_id is None,
            "enrollment_enabled": credentials.settings.device_enrollment_enabled,
            "deletion_worker_enabled": credentials.settings.deletion_worker_enabled,
            "data_epoch": epoch,
            "retention": "until_explicit_owner_deletion",
            "telemetry": gate.snapshot(owner),
        }

    @router.get("/credentials", response_model=list[CredentialOutput], responses=errors)
    def list_credentials(owner: str = private):
        return credentials.list(owner)

    @router.post(
        "/credentials",
        response_model=CredentialIssueOutput,
        status_code=201,
        responses={200: {"model": CredentialIssueOutput}, **errors},
    )
    def enroll(body: CredentialInput, response: Response, owner: str = private):
        result, created = credentials.enroll(
            owner, str(body.operation_id), body.label, body.lifetime_days
        )
        response.status_code = 201 if created else 200
        return result

    @router.post(
        "/credentials/{credential_id}/rotate",
        response_model=CredentialIssueOutput,
        status_code=201,
        responses={200: {"model": CredentialIssueOutput}, **errors},
    )
    def rotate(
        credential_id: UUID,
        body: CredentialInput,
        request: Request,
        response: Response,
        owner: str = private,
    ):
        result, created = credentials.enroll(
            owner, str(body.operation_id), body.label, body.lifetime_days, str(credential_id)
        )
        response.status_code = 201 if created else 200
        if result["token"] is not None and request.scope["ada.principal"].credential_id == str(
            credential_id
        ):
            # Only this admitted self-rotation response uses the freshly issued replacement.
            request.scope["ada.replacement_principal"] = credentials.authenticate(
                result["token"], touch=False
            )
        return result

    @router.post(
        "/credentials/{credential_id}/revoke", response_model=CredentialOutput, responses=errors
    )
    def revoke(credential_id: UUID, request: Request, owner: str = private):
        result = credentials.revoke(owner, str(credential_id))
        # Self-revocation may return its fixed acknowledgement; later access is denied.
        request.scope["ada.self_revoked"] = request.scope["ada.principal"].credential_id == str(
            credential_id
        )
        return result

    @router.post(
        "/deletion-previews",
        response_model=DeletionPreviewOutput,
        status_code=201,
        responses=errors,
    )
    def preview(owner: str = private):
        return deletion.preview(owner)

    @router.post(
        "/deletions",
        response_model=DeletionOutput,
        status_code=202,
        responses={200: {"model": DeletionOutput}, **errors},
    )
    def confirm(body: DeletionInput, response: Response, owner: str = private):
        result = deletion.confirm(owner, str(body.job_id), str(body.preview_id))
        response.status_code = 202 if result["status"] in ("queued", "running") else 200
        return result

    @router.get("/deletions", response_model=list[DeletionOutput], responses=errors)
    def list_deletions(owner: str = private):
        return deletion.list(owner)

    @router.get("/deletions/{job_id}", response_model=DeletionOutput, responses=errors)
    def get_deletion(job_id: UUID, owner: str = private):
        return deletion.get(owner, str(job_id))

    return router
