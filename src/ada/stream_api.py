import asyncio
import json
import re
import threading
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.background import BackgroundTask

from ada.errors import ServiceError
from ada.stream_contracts import CancelInput, CancelReceipt, StreamEventOutput, StreamStatus


def stream_router(service, current_user, error_responses, chat_input, request_output):
    StreamStatus.model_rebuild(_types_namespace={"RequestOutput": request_output})
    router = APIRouter(prefix="/v1", tags=["streaming"])
    private = Depends(current_user)
    errors = error_responses(401, 404, 409, 413, 422, 503)

    # Annotation is assigned explicitly to reuse the exact existing input schema.
    def submit(conversation_id: UUID, body, owner: str = private):
        return service.submit(
            owner,
            str(conversation_id),
            str(body.request_id),
            body.content,
            as_of=body.as_of,
            use_memory=body.use_memory,
            use_documents=body.use_documents,
        )

    submit.__annotations__["body"] = chat_input
    router.post(
        "/conversations/{conversation_id}/stream-requests",
        status_code=202,
        response_model=StreamStatus,
        responses=errors,
    )(submit)

    @router.get(
        "/requests/{request_id}/stream-status", response_model=StreamStatus, responses=errors
    )
    def status(request_id: UUID, owner: str = private):
        return service.status(owner, str(request_id))

    @router.post("/requests/{request_id}/cancel", response_model=CancelReceipt, responses=errors)
    def cancel(request_id: UUID, body: CancelInput, owner: str = private):
        return service.cancel(owner, str(request_id), body.attempt)

    @router.get(
        "/requests/{request_id}/stream",
        response_class=StreamingResponse,
        openapi_extra={"x-ada-event-schema": StreamEventOutput.model_json_schema()},
        responses={
            200: {"content": {"text/event-stream": {"schema": {"type": "string"}}}},
            **errors,
        },
    )
    def stream(
        request_id: UUID,
        request: Request,
        attempt: int = Query(ge=1, le=1000000),
        after: int = Query(default=0, ge=0, le=2147483647),
        last_event_id: str | None = Header(default=None, max_length=40),
        owner: str = private,
    ):
        rid = str(request_id)
        if last_event_id is not None:
            if not re.fullmatch(r"[1-9][0-9]{0,6}:[0-9]{1,10}", last_event_id):
                raise ServiceError(409, "invalid_stream_cursor")
            cursor_attempt, cursor = map(int, last_event_id.split(":"))
            if cursor_attempt != attempt or (after and after != cursor):
                raise ServiceError(409, "invalid_stream_cursor")
            after = cursor
        service.events(owner, rid, attempt, after)  # Validate before headers.
        if not service.observers.acquire(blocking=False):
            raise ServiceError(503, "stream_observer_capacity_busy")
        released = False
        release_lock = threading.Lock()

        def release_observer():
            nonlocal released
            with release_lock:
                if not released:
                    released = True
                    service.observers.release()

        principal = request.scope["ada.principal"]

        async def observe():
            cursor = after
            try:
                while not await request.is_disconnected():
                    # Fresh principal check at each bounded batch/heartbeat, including token rotation.
                    try:
                        valid = request.app.state.security.current(principal)
                    except ServiceError:
                        valid = False
                    if not valid:
                        yield 'event: access_lost\ndata: {"detail":"invalid_token"}\n\n'
                        return
                    try:
                        batch, terminal = service.events(owner, rid, attempt, cursor)
                    except ServiceError as exc:
                        yield (
                            "event: reset_required\ndata: "
                            + json.dumps({"detail": exc.code})
                            + "\n\n"
                        )
                        return
                    for event in batch:
                        cursor = event["sequence"]
                        yield f"id: {attempt}:{cursor}\nevent: {event['type']}\ndata: {json.dumps(event, ensure_ascii=True, separators=(',', ':'))}\n\n"
                    if terminal and not batch:
                        return
                    if not batch:
                        yield ": keepalive\n\n"
                        await asyncio.sleep(0.25)
            except SQLAlchemyError:
                yield 'event: reset_required\ndata: {"detail":"database_not_ready"}\n\n'
            finally:
                release_observer()

        return StreamingResponse(
            observe(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
            background=BackgroundTask(release_observer),
        )

    return router
