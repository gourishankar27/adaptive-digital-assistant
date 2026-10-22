"""Explicit selected PDF bytes only; never filesystem or remote URL ingestion."""

import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from pydantic import AwareDatetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from starlette.requests import ClientDisconnect

from ada.document_contracts import DocumentUploadOutput
from ada.documents import MAX_UPLOAD_BYTES
from ada.errors import ServiceError
from ada.memory import owned_scope, time_ms


def pdf_router(service, sessions, current_user, scheduling, error_responses):
    router = APIRouter(tags=["text-pdf"])
    owner_dep = Annotated[str, Depends(current_user)]

    @router.get(
        "/v1/document-uploads/{upload_id}/raw",
        response_class=Response,
        responses=error_responses(401, 404, 409, 503),
    )
    def original(upload_id: UUID, owner: owner_dep):
        try:
            content, media = service.raw_upload(owner, str(upload_id))
        except SQLAlchemyError:
            raise ServiceError(503, "pdf_storage_unavailable") from None
        filename = "document.pdf" if media == "application/pdf" else "document.txt"
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "no-store",
            },
        )

    async def safe_upload(*args, **kwargs):
        try:
            return await run_in_threadpool(*args, **kwargs)
        except IntegrityError:
            raise ServiceError(409, "pdf_upload_conflict") from None
        except SQLAlchemyError:
            raise ServiceError(503, "pdf_storage_unavailable") from None

    @router.post(
        "/v1/scopes/{scope_id}/documents/pdf-uploads/{upload_id}",
        response_model=DocumentUploadOutput,
        status_code=201,
        responses={
            200: {"model": DocumentUploadOutput},
            **error_responses(401, 404, 408, 409, 413, 415, 422, 429, 503),
        },
        openapi_extra={
            "requestBody": {
                "required": True,
                "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
            }
        },
    )
    async def upload(
        scope_id: UUID,
        upload_id: UUID,
        request: Request,
        response: Response,
        owner: owner_dep,
        source_id: UUID = Query(),
        filename: str = Query(min_length=1, max_length=120),
        available_from: AwareDatetime | None = Query(default=None),
        available_to: AwareDatetime | None = Query(default=None),
    ):
        def check():
            with sessions() as db:
                owned_scope(db, owner, str(scope_id))

        await run_in_threadpool(check)
        if not service.parser.available:
            raise ServiceError(503, "pdf_parser_unavailable")
        if request.headers.get("content-type", "").lower().strip() != "application/pdf":
            raise ServiceError(415, "pdf_type_invalid")
        raw = bytearray()
        try:
            async with asyncio.timeout(15):
                async for part in request.stream():
                    if len(raw) + len(part) > MAX_UPLOAD_BYTES:
                        raise ServiceError(413, "document_size_limit")
                    raw.extend(part)
        except (TimeoutError, ClientDisconnect):
            raise ServiceError(408, "pdf_upload_interrupted") from None
        try:
            start = time_ms(available_from) if available_from is not None else None
            end = time_ms(available_to) if available_to is not None else None
        except (ValueError, OverflowError):
            raise ServiceError(422, "document_time_invalid") from None
        result, created = await safe_upload(
            service.upload,
            owner,
            str(scope_id),
            str(upload_id),
            bytes(raw),
            source_id=str(source_id),
            filename=filename,
            media_type="application/pdf",
            available_from=start,
            available_to=end,
            authorize=lambda db: scheduling._owner(db, owner, request.scope["ada.principal"]),
        )
        response.status_code = 201 if created else 200
        return result

    return router
