import hashlib
import threading

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from ada.evidence import record_chat_event
from ada.models import Conversation, PromptChange, Request, now_ms
from ada.personality import PROMPT_VERSION, build_prompt
from ada.providers import ProviderError


class ServiceError(Exception):
    def __init__(self, status: int, code: str):
        self.status, self.code = status, code
        super().__init__(code)


def public_request(row: Request) -> dict:
    return {
        "request_id": row.id,
        "conversation_id": row.conversation_id,
        "status": row.status,
        "response": row.response,
        "error_code": row.error_code,
        "attempt": row.attempt,
        "provider": row.provider,
        "model": row.model,
        "input_tokens": row.input_tokens,
        "output_tokens": row.output_tokens,
    }


class ChatService:
    def __init__(self, sessions, provider, settings):
        self.sessions, self.provider, self.settings = sessions, provider, settings
        self.capacity = threading.BoundedSemaphore(settings.max_parallel)

    def _context(self, db, conversation, content):
        system = {"role": "system", "content": conversation.system_prompt}
        newest = {"role": "user", "content": content}

        def cost(m):
            return len(m["content"].encode("utf-8")) + 64

        remaining = self.settings.prompt_bytes - cost(system) - cost(newest)
        if remaining < 0:
            raise ServiceError(413, "message_exceeds_context_budget")
        # Complete pairs only. Failed/in-flight turns remain evidence, not model history.
        rows = db.scalars(
            select(Request)
            .where(
                Request.owner_id == conversation.owner_id,
                Request.conversation_id == conversation.id,
                Request.status == "completed",
            )
            .order_by(Request.base_revision.desc())
            .limit(50)
        ).all()
        pairs = []
        for row in rows:
            pair = [row.messages[-1], {"role": "assistant", "content": row.response}]
            needed = sum(cost(m) for m in pair)
            if needed > remaining:
                break
            pairs.append(pair)
            remaining -= needed
        return [system] + [m for pair in reversed(pairs) for m in pair] + [newest]

    def chat(self, owner, conversation_id, request_id, content):
        fingerprint = hashlib.sha256(content.encode()).hexdigest()
        # Return completed retries even when GPU capacity is busy.
        with self.sessions() as db:
            old = db.get(Request, (owner, request_id))
            if old:
                self._same(old, conversation_id, fingerprint)
                if old.status == "completed":
                    return public_request(old)
        if not self.capacity.acquire(blocking=False):
            raise ServiceError(503, "generation_capacity_busy")
        try:
            try:
                with self.sessions.begin() as db:
                    conversation = db.scalar(
                        select(Conversation)
                        .where(Conversation.id == conversation_id, Conversation.owner_id == owner)
                        .with_for_update()
                    )
                    if conversation is None:
                        raise ServiceError(404, "conversation_not_found")
                    old = db.get(Request, (owner, request_id))
                    if old:
                        self._same(old, conversation_id, fingerprint)
                        if old.status == "completed":
                            return public_request(old)
                        if old.status == "running":
                            raise ServiceError(409, "request_in_progress")
                        if old.base_revision != conversation.revision:
                            raise ServiceError(409, "retry_history_changed")
                    active = db.scalar(
                        select(Request.id).where(
                            Request.owner_id == owner,
                            Request.conversation_id == conversation_id,
                            Request.status == "running",
                        )
                    )
                    if active:
                        raise ServiceError(409, "conversation_busy")
                    if old is None:
                        old = Request(
                            owner_id=owner,
                            id=request_id,
                            conversation_id=conversation_id,
                            content_hash=fingerprint,
                            status="running",
                            base_revision=conversation.revision,
                            messages=self._context(db, conversation, content),
                            provider=self.provider.id,
                            model=self.provider.model,
                        )
                        db.add(old)
                        db.flush()
                        record_chat_event(db, conversation, request_id, "user", content)
                    else:
                        old.status, old.error_code = "running", None
                        old.attempt += 1
                        old.started_at, old.finished_at = now_ms(), None
                        old.provider, old.model = self.provider.id, self.provider.model
                    db.flush()
                    attempt, messages = old.attempt, old.messages
            except IntegrityError as exc:
                raise ServiceError(409, "request_conflict") from exc
            try:
                completion = self.provider.complete(messages)
            except Exception as exc:
                code = exc.code if isinstance(exc, ProviderError) else "provider_error"
                self._fail(owner, request_id, attempt, code)
                raise ServiceError(502, code) from exc
            # Fence stale responses after recovery/retry. Persist response and event atomically.
            with self.sessions.begin() as db:
                conversation = db.scalar(
                    select(Conversation)
                    .where(Conversation.id == conversation_id, Conversation.owner_id == owner)
                    .with_for_update()
                )
                row = db.scalar(
                    select(Request)
                    .where(Request.owner_id == owner, Request.id == request_id)
                    .with_for_update()
                )
                if row.status != "running" or row.attempt != attempt:
                    raise ServiceError(409, "request_superseded")
                row.status, row.response, row.finished_at = "completed", completion.text, now_ms()
                row.model = completion.model
                row.input_tokens, row.output_tokens = (
                    completion.input_tokens,
                    completion.output_tokens,
                )
                conversation.revision += 1
                record_chat_event(db, conversation, request_id, "assistant", completion.text)
                return public_request(row)
        finally:
            self.capacity.release()

    def upgrade_prompt(self, owner, conversation_id):
        with self.sessions.begin() as db:
            conversation = db.scalar(
                select(Conversation)
                .where(Conversation.id == conversation_id, Conversation.owner_id == owner)
                .with_for_update()
            )
            if conversation is None:
                raise ServiceError(404, "conversation_not_found")
            if conversation.prompt_version == PROMPT_VERSION:
                return {
                    "id": conversation.id,
                    "prompt_version": PROMPT_VERSION,
                    "revision": conversation.revision,
                }
            if conversation.prompt_version != "ada-baseline-v1":
                raise ServiceError(409, "unsupported_prompt_upgrade")
            active = db.scalar(
                select(Request.id).where(
                    Request.owner_id == owner,
                    Request.conversation_id == conversation_id,
                    Request.status == "running",
                )
            )
            if active:
                raise ServiceError(409, "conversation_busy")
            new_prompt = build_prompt(conversation.personality_snapshot)
            db.add(
                PromptChange(
                    owner_id=owner,
                    conversation_id=conversation_id,
                    previous_version=conversation.prompt_version,
                    new_version=PROMPT_VERSION,
                    previous_prompt=conversation.system_prompt,
                    new_prompt=new_prompt,
                )
            )
            conversation.system_prompt, conversation.prompt_version = new_prompt, PROMPT_VERSION
            # Failed attempts keep their original prompt snapshot. They must not
            # resume across an explicit change to the conversation's context.
            conversation.revision += 1
            return {
                "id": conversation.id,
                "prompt_version": PROMPT_VERSION,
                "revision": conversation.revision,
            }

    @staticmethod
    def _same(row, conversation_id, fingerprint):
        if row.conversation_id != conversation_id or row.content_hash != fingerprint:
            raise ServiceError(409, "idempotency_key_reused")

    def _fail(self, owner, request_id, attempt, code):
        with self.sessions.begin() as db:
            db.execute(
                update(Request)
                .where(
                    Request.owner_id == owner,
                    Request.id == request_id,
                    Request.attempt == attempt,
                    Request.status == "running",
                )
                .values(status="failed", error_code=code, finished_at=now_ms())
            )


def recover_stale(sessions, cutoff_ms):
    """Operator action: mark abandoned requests retryable. Late completions are fenced."""
    with sessions.begin() as db:
        result = db.execute(
            update(Request)
            .where(Request.status == "running", Request.started_at < cutoff_ms)
            .values(status="failed", error_code="interrupted", finished_at=now_ms())
        )
        return result.rowcount
