"""One-worker streaming, durable checkpoints and explicitly owned cancellation."""

import threading
from uuid import uuid4

from sqlalchemy import delete, func, select

from ada.errors import ServiceError
from ada.evidence import record_chat_event
from ada.models import Conversation, Request, RetrievalTrace, User, now_ms
from ada.providers import Completion, ProviderError
from ada.service import public_request, request_fingerprint
from ada.stream_models import StreamAttempt, StreamEvent
from ada.stream_provider import MAX_TEXT_BYTES

ACTIVE = ("running", "cancel_requested")
RETAIN_EVENTS = 256
RETENTION_MS = 86400000
MAX_OWNER_ATTEMPTS = 1000
MAX_REQUEST_ATTEMPTS = 8


class StreamingService:
    def __init__(self, chat):
        self.chat, self.sessions = chat, chat.sessions
        self.instance = str(uuid4())
        self.lock = threading.RLock()
        self.workers = {}
        self.observers = threading.BoundedSemaphore(16)
        self.closing = False

    @property
    def available(self):
        return callable(getattr(self.chat.provider, "stream", None))

    @staticmethod
    def _event(db, row, kind, payload):
        row.sequence += 1
        db.add(
            StreamEvent(
                owner_id=row.owner_id,
                request_id=row.request_id,
                attempt=row.attempt,
                sequence=row.sequence,
                kind=kind,
                payload=payload,
                created_at=now_ms(),
            )
        )
        row.replay_after = max(0, row.sequence - RETAIN_EVENTS)
        if row.replay_after:
            db.execute(
                delete(StreamEvent).where(
                    StreamEvent.owner_id == row.owner_id,
                    StreamEvent.request_id == row.request_id,
                    StreamEvent.attempt == row.attempt,
                    StreamEvent.sequence <= row.replay_after,
                )
            )

    def register(self, db, request):
        # Called in the same transaction as the old request/source/context reservation.
        db.scalar(select(User).where(User.id == request.owner_id).with_for_update())
        owner_count = db.scalar(
            select(func.count())
            .select_from(StreamAttempt)
            .where(StreamAttempt.owner_id == request.owner_id)
        )
        request_count = db.scalar(
            select(func.count())
            .select_from(StreamAttempt)
            .where(
                StreamAttempt.owner_id == request.owner_id, StreamAttempt.request_id == request.id
            )
        )
        if owner_count >= MAX_OWNER_ATTEMPTS or request_count >= MAX_REQUEST_ATTEMPTS:
            raise ServiceError(413, "stream_history_limit")
        row = StreamAttempt(
            owner_id=request.owner_id,
            request_id=request.id,
            attempt=request.attempt,
            instance_id=self.instance,
            state="running",
            sequence=0,
            replay_after=0,
            provisional="",
            created_at=now_ms(),
            deadline_at=now_ms() + (self.chat.settings.timeout_seconds + 30) * 1000,
        )
        db.add(row)
        db.flush()
        self._event(db, row, "started", {"legacy_status": "running"})

    def submit(self, owner, cid, rid, content, *, register=None, **options):
        fingerprint = request_fingerprint(
            content,
            options.get("as_of"),
            options.get("use_memory", True),
            options.get("use_documents", False),
            options.get("input_binding"),
        )
        with self.lock:
            if self.closing or not self.available:
                raise ServiceError(503, "streaming_unavailable")
            with self.sessions() as db:
                old = db.get(Request, (owner, rid))
                if old:
                    self.chat._same(old, cid, fingerprint)
                    if old.status == "completed":
                        return self.status(owner, rid)
                    if old.status == "running":
                        if db.get(StreamAttempt, (owner, rid, old.attempt)) is None:
                            raise ServiceError(409, "request_in_progress")
                        return self.status(owner, rid)
            if not self.chat.capacity.acquire(blocking=False):
                raise ServiceError(503, "generation_capacity_busy")
            transferred = False
            try:

                def registration(db, request):
                    self.register(db, request)
                    if register is not None:
                        register(db, request)

                attempt, messages, completed = self.chat.reserve(
                    owner, cid, rid, content, register=registration, **options
                )
                if completed is not None:
                    return self.status(owner, rid)
                cancel = threading.Event()
                key = (owner, rid, attempt)
                worker = threading.Thread(
                    target=self._run,
                    args=(key, cid, messages, cancel),
                    name="ada-stream-attempt",
                    daemon=True,
                )
                self.workers[key] = (worker, cancel)
                try:
                    worker.start()
                except Exception:
                    self.workers.pop(key, None)
                    self._finish(key, cid, error="interrupted")
                    raise ServiceError(503, "streaming_unavailable") from None
                transferred = True
                return self.status(owner, rid)
            finally:
                if not transferred:
                    self.chat.capacity.release()

    def _run(self, key, cid, messages, cancel):
        completion = None
        error = None
        iterator = None
        try:
            iterator = iter(self.chat.provider.stream(messages, cancel))
            for chunk in iterator:
                if cancel.is_set():
                    break
                if isinstance(chunk, Completion):
                    completion = chunk
                    break
                if not isinstance(chunk, str) or "\x00" in chunk:
                    raise ProviderError("invalid_response")
                # Code-point split, never split UTF-8 bytes or accept unbounded chunks.
                if len(chunk.encode("utf-8")) > MAX_TEXT_BYTES:
                    raise ProviderError("response_too_large")
                for start in range(0, len(chunk), 1024):
                    if not self._delta(key, chunk[start : start + 1024]):
                        cancel.set()
                        break
            if completion is None:
                error = "invalid_response"
        except Exception as exc:
            error = exc.code if isinstance(exc, ProviderError) else "provider_error"
        finally:
            # Provider shutdown is inside the admission lifetime, including delayed finally blocks.
            try:
                if iterator is not None and hasattr(iterator, "close"):
                    iterator.close()
            except Exception:
                error = "provider_error"
            try:
                if self.closing:
                    error = "interrupted"
                self._finish(key, cid, completion, error)
            except Exception:
                # No fake terminal success: restart fences an uncommitted attempt.
                pass
            finally:
                self.chat.capacity.release()
                with self.lock:
                    self.workers.pop(key, None)

    def _delta(self, key, text):
        owner, rid, attempt = key
        with self.sessions.begin() as db:
            request = db.scalar(
                select(Request)
                .where(Request.owner_id == owner, Request.id == rid)
                .with_for_update()
            )
            row = db.scalar(
                select(StreamAttempt)
                .where(
                    StreamAttempt.owner_id == owner,
                    StreamAttempt.request_id == rid,
                    StreamAttempt.attempt == attempt,
                )
                .with_for_update()
            )
            if (
                request is None
                or request.status != "running"
                or request.attempt != attempt
                or row is None
                or row.state != "running"
                or row.instance_id != self.instance
            ):
                return False
            if now_ms() > row.deadline_at:
                raise ProviderError("provider_timeout")
            if len((row.provisional + text).encode("utf-8")) > MAX_TEXT_BYTES:
                raise ProviderError("response_too_large")
            if text:
                row.provisional += text
                self._event(db, row, "delta", {"text": text})
            return True

    def _finish(self, key, cid, completion=None, error=None):
        owner, rid, attempt = key
        with self.sessions.begin() as db:
            conversation = db.scalar(
                select(Conversation)
                .where(Conversation.owner_id == owner, Conversation.id == cid)
                .with_for_update()
            )
            request = db.scalar(
                select(Request)
                .where(Request.owner_id == owner, Request.id == rid)
                .with_for_update()
            )
            row = db.scalar(
                select(StreamAttempt)
                .where(
                    StreamAttempt.owner_id == owner,
                    StreamAttempt.request_id == rid,
                    StreamAttempt.attempt == attempt,
                )
                .with_for_update()
            )
            if (
                request is None
                or row is None
                or row.instance_id != self.instance
                or row.state not in ACTIVE
            ):
                return
            if request.attempt != attempt or request.status != "running":
                row.state, row.finished_at = "interrupted", now_ms()
                self._event(db, row, "interrupted", {"error_code": "request_superseded"})
                return
            if row.state == "cancel_requested":
                row.state, error = "cancelled", "request_cancelled"
            elif error is not None:
                row.state = "interrupted" if error == "interrupted" else "failed"
            elif now_ms() > row.deadline_at:
                row.state, error = "failed", "provider_timeout"
            elif (
                completion is None
                or completion.text != row.provisional.strip()
                or not completion.text.strip()
            ):
                row.state, error = "failed", "invalid_response"
            else:
                row.state = "completed"
            request.finished_at = row.finished_at = now_ms()
            if row.state == "completed":
                request.status, request.response, request.error_code = (
                    "completed",
                    completion.text,
                    None,
                )
                request.model = completion.model
                request.input_tokens, request.output_tokens = (
                    completion.input_tokens,
                    completion.output_tokens,
                )
                conversation.revision += 1
                record_chat_event(db, conversation, rid, "assistant", completion.text)
            else:
                request.status, request.response, request.error_code = "failed", None, error
            self._event(
                db,
                row,
                row.state,
                {"legacy_status": request.status, "error_code": request.error_code},
            )

    def status(self, owner, rid):
        with self.lock, self.sessions.begin() as db:
            if db.bind.dialect.name == "sqlite":
                from sqlalchemy import text

                db.execute(text("BEGIN"))
            request = db.scalar(
                select(Request)
                .where(Request.owner_id == owner, Request.id == rid)
                .with_for_update()
            )
            if request is None:
                raise ServiceError(404, "request_not_found")
            row = db.get(StreamAttempt, (owner, rid, request.attempt))
            orphan = (
                row is not None
                and row.state in ACTIVE
                and (
                    request.status != "running" or (owner, rid, request.attempt) not in self.workers
                )
            )
            orphan_attempt = request.attempt
            own_instance = row is not None and row.instance_id == self.instance
            value = {
                "request_id": rid,
                "conversation_id": request.conversation_id,
                "attempt": request.attempt,
                "available": row is not None,
                "stream_state": row.state if row else request.status,
                "sequence": row.sequence if row else 0,
                "replay_after": row.replay_after if row else 0,
                "provisional": row.provisional if row else "",
                "result": public_request(request, db.get(RetrievalTrace, (owner, rid))),
            }
        if orphan:
            if own_instance:
                self._finish(
                    (owner, rid, orphan_attempt), value["conversation_id"], error="interrupted"
                )
            else:
                self.recover()
            return self.status(owner, rid)
        return value

    def cancel(self, owner, rid, attempt):
        self.status(owner, rid)
        # Same conversation -> request -> attempt lock order as final publication.
        with self.sessions() as db:
            request = db.get(Request, (owner, rid))
            if request is None:
                raise ServiceError(404, "request_not_found")
            cid = request.conversation_id
        with self.sessions.begin() as db:
            db.scalar(
                select(Conversation)
                .where(Conversation.owner_id == owner, Conversation.id == cid)
                .with_for_update()
            )
            request = db.scalar(
                select(Request)
                .where(Request.owner_id == owner, Request.id == rid)
                .with_for_update()
            )
            row = db.scalar(
                select(StreamAttempt)
                .where(
                    StreamAttempt.owner_id == owner,
                    StreamAttempt.request_id == rid,
                    StreamAttempt.attempt == attempt,
                )
                .with_for_update()
            )
            if request.attempt != attempt:
                raise ServiceError(409, "attempt_superseded")
            if row is None:
                raise ServiceError(409, "streaming_unavailable")
            if row.cancel_receipt:
                result = row.cancel_receipt
            else:
                terminal = row.state not in ACTIVE or request.status != "running"
                result = {
                    "request_id": rid,
                    "attempt": attempt,
                    "outcome": "already_terminal" if terminal else "requested",
                    "observed_state": row.state,
                    "created_at": now_ms(),
                }
                row.cancel_receipt = result
                if not terminal:
                    row.state = "cancel_requested"
                    self._event(db, row, "cancel_requested", {"legacy_status": "running"})
        if result["outcome"] == "requested":
            with self.lock:
                worker = self.workers.get((owner, rid, attempt))
                if worker:
                    worker[1].set()
        return result

    def events(self, owner, rid, attempt, after):
        # Reconcile an operator-recovered request even if its provider is still shutting down.
        self.status(owner, rid)
        with self.sessions() as db:
            request = db.get(Request, (owner, rid))
            if request is None:
                raise ServiceError(404, "request_not_found")
            if request.attempt != attempt:
                raise ServiceError(409, "attempt_superseded")
            row = db.get(StreamAttempt, (owner, rid, attempt))
            if row is None:
                raise ServiceError(404, "stream_unavailable")
            if after > row.sequence:
                raise ServiceError(409, "invalid_stream_cursor")
            if after < row.replay_after or (
                row.finished_at is not None and now_ms() > row.finished_at + RETENTION_MS
            ):
                raise ServiceError(409, "stream_cursor_expired")
            rows = db.scalars(
                select(StreamEvent)
                .where(
                    StreamEvent.owner_id == owner,
                    StreamEvent.request_id == rid,
                    StreamEvent.attempt == attempt,
                    StreamEvent.sequence > after,
                )
                .order_by(StreamEvent.sequence)
                .limit(16)
            ).all()
            return (
                [
                    {
                        "request_id": rid,
                        "attempt": attempt,
                        "sequence": event.sequence,
                        "type": event.kind,
                        "payload": event.payload,
                        "created_at": event.created_at,
                    }
                    for event in rows
                ],
                row.state not in ACTIVE,
            )

    def recover(self):
        # Lifespan startup only; one worker/process is a required operating boundary.
        with self.sessions() as db:
            pending = [
                (row.owner_id, row.request_id, row.attempt)
                for row in db.scalars(
                    select(StreamAttempt).where(
                        StreamAttempt.state.in_(ACTIVE), StreamAttempt.instance_id != self.instance
                    )
                ).all()
            ]
        for key in pending:
            with self.sessions.begin() as db:
                owner, rid, attempt = key
                request = db.scalar(
                    select(Request)
                    .where(Request.owner_id == owner, Request.id == rid)
                    .with_for_update()
                )
                row = db.scalar(
                    select(StreamAttempt)
                    .where(
                        StreamAttempt.owner_id == owner,
                        StreamAttempt.request_id == rid,
                        StreamAttempt.attempt == attempt,
                    )
                    .with_for_update()
                )
                if row.state not in ACTIVE or row.instance_id == self.instance:
                    continue
                row.state, row.finished_at = "interrupted", now_ms()
                if request.status == "running" and request.attempt == attempt:
                    request.status, request.error_code, request.finished_at = (
                        "failed",
                        "interrupted",
                        row.finished_at,
                    )
                self._event(db, row, "interrupted", {"error_code": "interrupted"})

    def stop(self):
        with self.lock:
            self.closing = True
            workers = list(self.workers.values())
            for _, signal in workers:
                signal.set()
        for worker, _ in workers:
            worker.join(2)
