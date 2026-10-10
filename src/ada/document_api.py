"""Authenticated, byte-bounded raw uploads; parsing belongs outside transactions."""

import asyncio
import re
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi import Request as HttpRequest
from pydantic import AwareDatetime
from starlette.concurrency import run_in_threadpool
from starlette.requests import ClientDisconnect

from ada.document_contracts import DocumentChunkOutput, DocumentUploadOutput, DocumentVersionOutput
from ada.documents import MAX_UPLOAD_BYTES, DocumentService
from ada.memory import owned_scope, time_ms


def document_router(sessions, current_user, error_responses):
    router = APIRouter(tags=["documents"])
    documents = DocumentService(sessions)
    owner_dependency = Annotated[str, Depends(current_user)]

    def check_scope(owner, scope_id):
        with sessions() as db:
            owned_scope(db, owner, scope_id)

    @router.post(
        "/v1/scopes/{scope_id}/documents/uploads/{upload_id}",
        response_model=DocumentUploadOutput,
        status_code=201,
        responses={
            200: {"model": DocumentUploadOutput, "description": "Same-ID receipt replay"},
            **error_responses(401, 404, 408, 409, 413, 415, 422, 429, 503),
        },
        openapi_extra={
            "requestBody": {
                "required": True,
                "description": "Exact UTF-8 file bytes. No multipart, archives, PDF or remote URLs.",
                "content": {
                    media: {"schema": {"type": "string", "format": "binary"}}
                    for media in ("text/plain", "text/markdown")
                },
            }
        },
    )
    async def upload(
        scope_id: UUID,
        upload_id: UUID,
        request: HttpRequest,
        response: Response,
        owner: owner_dependency,
        source_id: UUID = Query(),
        filename: str = Query(min_length=1, max_length=120),
        available_from: AwareDatetime | None = Query(default=None),
        available_to: AwareDatetime | None = Query(default=None),
    ):
        # Reject foreign scopes before buffering private input, with no transaction
        # held while the client uploads or the parser runs.
        await run_in_threadpool(check_scope, owner, str(scope_id))
        try:
            start = time_ms(available_from) if available_from is not None else None
            end = time_ms(available_to) if available_to is not None else None
        except ValueError:
            raise HTTPException(422, "invalid_document_availability") from None
        media = request.headers.get("content-type", "")
        match = (
            re.fullmatch(
                r'\s*(text/plain|text/markdown)\s*(?:;\s*charset\s*=\s*"?utf-8"?\s*)?',
                media,
                flags=re.I,
            )
            if len(media) <= 128
            else None
        )
        if match is None:
            raise HTTPException(415, "unsupported_document_type")
        raw = bytearray()
        try:
            async with asyncio.timeout(15):
                async for part in request.stream():
                    if len(raw) + len(part) > MAX_UPLOAD_BYTES:
                        raise HTTPException(413, "document_too_large")
                    raw.extend(part)
        except TimeoutError:
            raise HTTPException(408, "document_upload_timed_out") from None
        except ClientDisconnect:
            raise HTTPException(408, "document_upload_interrupted") from None
        result, created = await run_in_threadpool(
            documents.upload,
            owner,
            str(scope_id),
            str(upload_id),
            bytes(raw),
            source_id=str(source_id),
            filename=filename,
            media_type=match.group(1).lower(),
            available_from=start,
            available_to=end,
        )
        response.status_code = 201 if created else 200
        return result

    @router.get(
        "/v1/scopes/{scope_id}/document-uploads",
        response_model=list[DocumentUploadOutput],
        responses=error_responses(401, 404, 422, 503),
    )
    def uploads(
        scope_id: UUID,
        owner: owner_dependency,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return documents.list(owner, str(scope_id), limit=limit, offset=offset)

    @router.get(
        "/v1/document-uploads/{upload_id}",
        response_model=DocumentUploadOutput,
        responses=error_responses(401, 404, 422, 503),
    )
    def upload_status(upload_id: UUID, owner: owner_dependency):
        return documents.get(owner, None, str(upload_id))

    @router.get(
        "/v1/documents/{source_id}/versions",
        response_model=list[DocumentUploadOutput],
        responses=error_responses(401, 404, 422, 503),
    )
    def versions(
        source_id: UUID,
        owner: owner_dependency,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return documents.versions(owner, str(source_id), limit=limit, offset=offset)

    @router.get(
        "/v1/document-versions/{source_version_id}",
        response_model=DocumentVersionOutput,
        responses=error_responses(401, 404, 409, 422, 503),
    )
    def version(source_version_id: UUID, owner: owner_dependency):
        return documents.version(owner, None, str(source_version_id))

    @router.get(
        "/v1/document-versions/{source_version_id}/chunks",
        response_model=list[DocumentChunkOutput],
        responses=error_responses(401, 404, 422, 503),
    )
    def chunks(
        source_version_id: UUID,
        owner: owner_dependency,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0, le=10000),
    ):
        return documents.chunks(owner, None, str(source_version_id), limit=limit, offset=offset)

    @router.get(
        "/v1/document-versions/{source_version_id}/raw",
        responses={
            200: {
                "content": {
                    "application/octet-stream": {"schema": {"type": "string", "format": "binary"}}
                }
            },
            **error_responses(401, 404, 409, 422, 503),
        },
        response_class=Response,
    )
    def raw(source_version_id: UUID, owner: owner_dependency):
        content, _, _ = documents.raw(owner, None, str(source_version_id))
        # Never inline source markup or use the uploaded filename in a header.
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": 'attachment; filename="document.txt"',
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "no-store",
            },
        )

    return router
