import hashlib
import json
import re
import threading

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from ada.errors import ServiceError as ServiceError
from ada.evidence import record_chat_event
from ada.expression import ExpressionService, prompt_expression
from ada.learning import continuity_message, prompt_learning
from ada.memory import time_ms
from ada.models import Conversation, PromptChange, Request, RetrievalTrace, now_ms
from ada.personality import (
    DOCUMENT_PROMPT_VERSIONS,
    PROMPT_VERSION,
    QUALITY_PROMPT_VERSION,
    RETRIEVAL_PROMPT_VERSIONS,
    build_prompt,
)
from ada.providers import ProviderError
from ada.retrieval import (
    iso_time,
    lock_scope_for_retrieval,
    memory_message,
    message_cost,
    plan_query,
    response_citations,
    response_document_citations,
    retrieve,
)
from ada.semantic import SemanticService


def public_request(row: Request, trace=None) -> dict:
    citations, warnings = response_citations(row.response, trace)
    document_citations, document_warnings = response_document_citations(row.response, trace)
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
        "citations": citations,
        "document_citations": document_citations,
        "citation_warnings": warnings + document_warnings,
        "continuity_citations": [
            card
            for card in (row.learning_snapshot or {}).get("continuity", [])
            if re.search(r"\[" + re.escape(card["label"]) + r"\]", row.response or "")
        ],
    }


def request_fingerprint(content, as_of, use_memory, use_documents=False, input_binding=None):
    if input_binding is not None:
        legacy = request_fingerprint(content, as_of, use_memory, use_documents)
        return hashlib.sha256(
            b"\0ada-reviewed-voice-v1\0" + legacy.encode() + input_binding.encode()
        ).hexdigest()
    if use_documents:
        canonical = json.dumps(
            {
                "content": content,
                "as_of": time_ms(as_of) if as_of else None,
                "use_memory": use_memory,
                "use_documents": True,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(b"\0ada-chat-options-v2\0" + canonical.encode()).hexdigest()
    # Preserve old request IDs for default options across Phase 0/1 upgrades.
    if as_of is None and use_memory:
        return hashlib.sha256(content.encode()).hexdigest()
    canonical = json.dumps(
        {"content": content, "as_of": time_ms(as_of) if as_of else None, "use_memory": use_memory},
        sort_keys=True,
        separators=(",", ":"),
    )
    # Valid user text cannot contain NUL. Domain separation prevents a default
    # content string containing this JSON from colliding with an option payload.
    return hashlib.sha256(b"\0ada-chat-options-v1\0" + canonical.encode()).hexdigest()


class ChatService:
    def __init__(self, sessions, provider, settings):
        self.sessions, self.provider, self.settings = sessions, provider, settings
        self.capacity = threading.BoundedSemaphore(settings.max_parallel)
        self.semantic = SemanticService(sessions, settings, self.capacity)
        self.expression = ExpressionService(sessions)
        self.learning = None  # Wired to the same proposal/consolidation services by create_app.
        self.curiosity = None  # Optional versioned navigation, never a factual evidence channel.
        self.reflection = None

    def acquire_foreground(self, owner):
        background = self.reflection.activity(owner) if self.reflection is not None else False
        if self.capacity.acquire(blocking=False):
            return True
        # Preserve ordinary busy behavior; only a preempted idle unit gets a bounded handoff.
        return bool(background and self.capacity.acquire(timeout=2))

    def _context(
        self,
        db,
        conversation,
        content,
        as_of,
        use_memory,
        use_documents=False,
        prepared=None,
        expression=None,
        learning=None,
        voice_style=None,
    ):
        system = {"role": "system", "content": conversation.system_prompt}
        system["content"] += prompt_expression(expression)
        system["content"] += prompt_learning(learning)
        if voice_style is not None:
            from ada.voice_style import voice_style_prompt

            system["content"] += voice_style_prompt(voice_style)
        newest = {"role": "user", "content": content}
        compatible = conversation.prompt_version in RETRIEVAL_PROMPT_VERSIONS
        document_compatible = conversation.prompt_version in DOCUMENT_PROMPT_VERSIONS
        plan = plan_query(
            content,
            as_of,
            enabled=compatible and use_memory,
            reason="prompt_upgrade_required"
            if not compatible
            else ("disabled" if not use_memory else None),
        )
        plan["prompt_version"] = conversation.prompt_version
        document_enabled = document_compatible and use_memory and use_documents
        plan["documents_enabled"] = document_enabled and plan["time_mode"] != "needs_date"
        plan["document_reason"] = (
            "prompt_upgrade_required"
            if use_documents and use_memory and not document_compatible
            else (
                "disabled"
                if not document_enabled
                else ("date_required" if plan["time_mode"] == "needs_date" else "ready")
            )
        )
        if compatible:
            at = iso_time(plan["as_of"]) if plan["as_of"] is not None else "date required"
            policy = (
                f"\nServer memory context: mode={plan['time_mode']}, as_of={at}, "
                f"retrieval={'enabled' if plan['enabled'] else 'disabled'}. "
                "Only labels in the evidence block of this request can be cited. "
                "Earlier assistant answers and old labels are not retrieved evidence for this request."
            )
            if document_compatible:
                policy += (
                    f" Imported document retrieval={'enabled' if plan['documents_enabled'] else 'disabled'}."
                    " D labels identify imported_untrusted excerpts, never user-endorsed assertions."
                )
            system["content"] += policy
        remaining = self.settings.prompt_bytes - message_cost(system) - message_cost(newest)
        if remaining < 0:
            raise ServiceError(413, "message_exceeds_context_budget")
        lock_scope_for_retrieval(db, conversation.owner_id, conversation.scope_id)
        result = retrieve(
            db,
            conversation.owner_id,
            conversation.scope_id,
            plan,
            limit=self.settings.retrieval_limit,
            budget_bytes=min(remaining, self.settings.memory_bytes),
            use_documents=document_enabled,
            semantic=self.semantic,
            prepared=prepared,
        )
        evidence = memory_message(result["selected"], result["plan"], result["document_selected"])
        remaining -= result["budget"]["memory_used_bytes"]
        continuity = continuity_message(learning)
        if continuity:
            needed = message_cost(continuity)
            if needed > remaining:
                learning["continuity"] = []
                learning["continuity_reason"] = "context_budget"
                continuity = None
            else:
                remaining -= needed
        # Complete pairs only. Failed/in-flight turns remain evidence, not model history.
        quality = conversation.prompt_version == QUALITY_PROMPT_VERSION
        rows = db.scalars(
            select(Request)
            .where(
                Request.owner_id == conversation.owner_id,
                Request.conversation_id == conversation.id,
                Request.status == "completed",
            )
            .order_by(Request.base_revision.desc())
            .limit(51 if quality else 50)
        ).all()
        truncated = len(rows) > 50
        rows = rows[:50]
        if quality:
            from ada.quality_context import rank_history

            rows = rank_history(rows, content)
        pairs = []
        for row in rows:
            pair = [row.messages[-1], {"role": "assistant", "content": row.response}]
            needed = sum(message_cost(m) for m in pair)
            if needed > remaining:
                continue
            pairs.append((row.base_revision, pair))
            remaining -= needed
        messages = [system] + [m for _, pair in sorted(pairs) for m in pair]
        if evidence:
            messages.append(evidence)
        if continuity:
            messages.append(continuity)
        messages.append(newest)
        if self.curiosity is not None:
            question = self.curiosity.context(db, conversation)
            if question is not None:
                # Keep exact existing evidence and the whole prompt budget. Optional context
                # cannot prevent ordinary text chat when it does not fit.
                if (
                    sum(message_cost(m) for m in messages) + message_cost(question)
                    <= self.settings.prompt_bytes
                ):
                    messages.insert(-1, question)
                    result["budget"]["curiosity_context"] = "ada-curiosity-v1"
                else:
                    result["budget"]["curiosity_context"] = "omitted_budget"
        result["budget"].update(
            prompt_limit_bytes=self.settings.prompt_bytes,
            prompt_used_bytes=sum(message_cost(m) for m in messages),
            history_pairs=len(pairs),
            history_pairs_omitted=len(rows) - len(pairs),
        )
        if quality:
            result["plan"]["quality_context"] = {
                "version": "ada-quality-context-v1",
                "history_considered": len(rows),
                "history_selected": len(pairs),
                "history_search_truncated": truncated,
                "evidence_selected": len(result["selected"]) + len(result["document_selected"]),
                "candidate_pool_truncated": result["budget"]["candidate_pool_truncated"],
                "continuity_reason": (learning or {}).get("continuity_reason", "not_enrolled"),
                "continuity_search_truncated": (learning or {}).get(
                    "continuity_search_truncated", False
                ),
                "omission_reasons": sorted(
                    {
                        c["decision"]
                        for c in result["candidates"] + result["document_candidates"]
                        if c["decision"] != "selected"
                    }
                ),
            }
        return messages, result

    def chat(
        self,
        owner,
        conversation_id,
        request_id,
        content,
        *,
        as_of=None,
        use_memory=True,
        use_documents=False,
    ):
        fingerprint = request_fingerprint(content, as_of, use_memory, use_documents)
        # Return completed retries even when GPU capacity is busy.
        with self.sessions() as db:
            old = db.get(Request, (owner, request_id))
            if old:
                self._same(old, conversation_id, fingerprint)
                if old.status == "completed":
                    return public_request(old, db.get(RetrievalTrace, (owner, request_id)))
        if not self.acquire_foreground(owner):
            raise ServiceError(503, "generation_capacity_busy")
        try:
            attempt, messages, completed = self.reserve(
                owner,
                conversation_id,
                request_id,
                content,
                as_of=as_of,
                use_memory=use_memory,
                use_documents=use_documents,
            )
            if completed is not None:
                return completed
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
                return public_request(row, db.get(RetrievalTrace, (owner, request_id)))
        finally:
            self.capacity.release()

    def reserve(
        self,
        owner,
        conversation_id,
        request_id,
        content,
        *,
        as_of=None,
        use_memory=True,
        use_documents=False,
        register=None,
        input_binding=None,
        voice_style=None,
    ):
        """Reserve a frozen attempt under already-acquired process admission."""
        fingerprint = request_fingerprint(content, as_of, use_memory, use_documents, input_binding)
        # Validate private identity before embedding, outside the reservation
        # transaction. Failed/running retries never refresh their evidence.
        prepared = None
        with self.sessions() as db:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.id == conversation_id, Conversation.owner_id == owner
                )
            )
            if conversation is None:
                raise ServiceError(404, "conversation_not_found")
            retry = db.get(Request, (owner, request_id))
            plan = plan_query(
                content,
                as_of,
                enabled=use_memory and conversation.prompt_version in RETRIEVAL_PROMPT_VERSIONS,
            )
        if retry is None:
            prepared = self.semantic.prepare(
                content,
                admitted=True,
                enabled=plan["enabled"] and plan["time_mode"] != "needs_date",
            )
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
                        return (
                            None,
                            None,
                            public_request(old, db.get(RetrievalTrace, (owner, request_id))),
                        )
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
                    expression = self.expression.reserve_snapshot(db, conversation, request_id)
                    learning = (
                        self.learning.reserve_snapshot(
                            db,
                            conversation,
                            content,
                            expression,
                            as_of,
                            use_memory,
                        )
                        if self.learning
                        else None
                    )
                    context, retrieval = self._context(
                        db,
                        conversation,
                        content,
                        as_of,
                        use_memory,
                        use_documents,
                        prepared,
                        expression,
                        learning,
                        voice_style,
                    )
                    old = Request(
                        owner_id=owner,
                        id=request_id,
                        conversation_id=conversation_id,
                        content_hash=fingerprint,
                        status="running",
                        base_revision=conversation.revision,
                        messages=context,
                        expression_snapshot=expression,
                        learning_snapshot=learning,
                        provider=self.provider.id,
                        model=self.provider.model,
                    )
                    db.add(old)
                    db.flush()
                    db.add(
                        RetrievalTrace(
                            owner_id=owner,
                            request_id=request_id,
                            conversation_id=conversation_id,
                            **{key: value for key, value in retrieval.items()},
                        )
                    )
                    record_chat_event(db, conversation, request_id, "user", content)
                else:
                    old.status, old.error_code = "running", None
                    old.attempt += 1
                    old.started_at, old.finished_at = now_ms(), None
                    old.provider, old.model = self.provider.id, self.provider.model
                db.flush()
                attempt, messages = old.attempt, old.messages
                if register is not None:
                    register(db, old)
        except IntegrityError as exc:
            raise ServiceError(409, "request_conflict") from exc
        return attempt, messages, None

    def upgrade_prompt(self, owner, conversation_id, *, target=PROMPT_VERSION):
        if target not in (PROMPT_VERSION, QUALITY_PROMPT_VERSION):
            raise ServiceError(409, "unsupported_prompt_upgrade")
        with self.sessions.begin() as db:
            conversation = db.scalar(
                select(Conversation)
                .where(Conversation.id == conversation_id, Conversation.owner_id == owner)
                .with_for_update()
            )
            if conversation is None:
                raise ServiceError(404, "conversation_not_found")
            if conversation.prompt_version == target:
                return {
                    "id": conversation.id,
                    "prompt_version": target,
                    "revision": conversation.revision,
                }
            supported = (
                "ada-baseline-v1",
                "ada-baseline-v2",
                "ada-baseline-v3",
            ) + ((PROMPT_VERSION,) if target == QUALITY_PROMPT_VERSION else ())
            if conversation.prompt_version not in supported:
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
            new_prompt = build_prompt(conversation.personality_snapshot, version=target)
            db.add(
                PromptChange(
                    owner_id=owner,
                    conversation_id=conversation_id,
                    previous_version=conversation.prompt_version,
                    new_version=target,
                    previous_prompt=conversation.system_prompt,
                    new_prompt=new_prompt,
                )
            )
            conversation.system_prompt, conversation.prompt_version = new_prompt, target
            # Failed attempts keep their original prompt snapshot. They must not
            # resume across an explicit change to the conversation's context.
            conversation.revision += 1
            return {
                "id": conversation.id,
                "prompt_version": target,
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
