"""A bounded, human-approved read-only loop with short fenced transactions."""

import json
import time
from uuid import NAMESPACE_URL, uuid5

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from ada.agent_models import AgentApproval, AgentReceipt, AgentRun, AgentStep
from ada.agent_provider import (
    APPROVAL_MS,
    COMPATIBLE_CHAT_PROMPTS,
    CONTEXT_BYTES,
    ELAPSED_MS,
    LEASE_MS,
    MAX_STEPS,
    OUTPUT_TOKENS,
    POLICY,
    PROTOCOL_VERSION,
    validate_message,
)
from ada.errors import ServiceError
from ada.evidence import content_hash
from ada.memory import owned_scope, time_ms
from ada.models import Conversation, now_ms
from ada.providers import ProviderError
from ada.tools import REGISTRY, execute_tool, source_result


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def hashed(domain, value):
    return content_hash(domain + "\0" + canonical(value))


def stable(owner, run, suffix):
    return str(uuid5(NAMESPACE_URL, "ada-agent-v1/" + owner + "/" + run + "/" + suffix))


def protocol():
    return {
        "version": PROTOCOL_VERSION,
        "compatible_chat_prompts": list(COMPATIBLE_CHAT_PROMPTS),
        "max_steps": MAX_STEPS,
        "context_bytes": CONTEXT_BYTES,
        "elapsed_seconds": ELAPSED_MS // 1000,
        "approval_seconds": APPROVAL_MS // 1000,
        "lease_seconds": LEASE_MS // 1000,
        "external_writes": False,
    }


class UnavailableAgentProvider:
    id, model = "unavailable", "unavailable"

    def complete(self, messages, tools):
        raise ProviderError("agent_protocol_unavailable")


class AgentService:
    def __init__(self, sessions, provider, capacity, clock=now_ms):
        self.sessions, self.provider, self.capacity, self.clock = (
            sessions,
            provider,
            capacity,
            clock,
        )
        self.dispatch = execute_tool

    def _owned(self, db, owner, key, lock=False):
        row = db.get(AgentRun, (owner, key))
        if row is None or row.protocol_version != PROTOCOL_VERSION:
            raise ServiceError(404, "agent_run_not_found")
        if lock:
            owned_scope(db, owner, row.scope_id, lock=True)
            row = db.scalar(
                select(AgentRun)
                .where(AgentRun.owner_id == owner, AgentRun.id == key)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
        return row

    def _steps(self, db, run):
        return list(
            db.scalars(
                select(AgentStep)
                .where(AgentStep.owner_id == run.owner_id, AgentStep.run_id == run.id)
                .order_by(AgentStep.number)
            )
        )

    def _output(self, db, run):
        steps = []
        for step in self._steps(db, run):
            receipt = db.scalar(
                select(AgentReceipt).where(
                    AgentReceipt.owner_id == run.owner_id, AgentReceipt.step_id == step.id
                )
            )
            steps.append(
                {
                    "id": step.id,
                    "number": step.number,
                    "attempt": step.attempt,
                    "status": step.status,
                    "tool": step.tool,
                    "tool_version": step.tool_version,
                    "arguments": step.arguments,
                    "argument_hash": step.argument_hash,
                    "preview_hash": step.preview_hash,
                    "expires_at": step.expires_at,
                    "receipt": receipt.snapshot if receipt else None,
                }
            )
        return {
            "id": run.id,
            "owner_id": run.owner_id,
            "scope_id": run.scope_id,
            "conversation_id": run.conversation_id,
            "protocol_version": run.protocol_version,
            "status": run.status,
            "response": run.response,
            "error_code": run.error_code,
            "provider": run.provider,
            "model": run.model,
            "generation": run.generation,
            "lease_until": run.lease_until,
            "created_at": run.created_at,
            "finished_at": run.finished_at,
            "as_of": run.as_of,
            "steps": steps,
        }

    def detail(self, owner, key):
        with self.sessions() as db:
            return self._output(db, self._owned(db, owner, key))

    def list(self, owner, conversation, limit, offset):
        with self.sessions() as db:
            if (
                db.scalar(
                    select(Conversation.id).where(
                        Conversation.owner_id == owner, Conversation.id == conversation
                    )
                )
                is None
            ):
                raise ServiceError(404, "conversation_not_found")
            rows = db.scalars(
                select(AgentRun)
                .where(
                    AgentRun.owner_id == owner,
                    AgentRun.conversation_id == conversation,
                    AgentRun.protocol_version == PROTOCOL_VERSION,
                )
                .order_by(AgentRun.created_at.desc(), AgentRun.id)
                .limit(limit)
                .offset(offset)
            )
            return [self._output(db, run) for run in rows]

    def receipt(self, owner, key):
        with self.sessions() as db:
            receipt = db.get(AgentReceipt, (owner, key))
            if (
                receipt is None
                or self._owned(db, owner, receipt.run_id).protocol_version != PROTOCOL_VERSION
            ):
                raise ServiceError(404, "agent_receipt_not_found")
            return receipt.snapshot

    def _terminal(self, run, step, status, code=None):
        run.status, run.error_code, run.lease_until = status, code, None
        run.finished_at = self.clock()
        step.status = "completed" if status == "completed" else status
        step.finished_at = run.finished_at

    def _bound(self, run):
        if self.clock() - run.created_at >= ELAPSED_MS:
            raise ServiceError(409, "agent_elapsed_bound")
        for name, spec in run.protocol_snapshot["tools"].items():
            if name not in REGISTRY or spec != REGISTRY[name].public():
                raise ServiceError(409, "agent_registry_changed")

    def _model_step(self, db, run):
        self._bound(run)
        number = len(self._steps(db, run)) + 1
        if number > MAX_STEPS:
            raise ServiceError(409, "agent_step_bound")
        if number > 1:
            run.generation += 1
        run.status, run.lease_until = "running", self.clock() + LEASE_MS
        step = AgentStep(
            owner_id=run.owner_id,
            id=stable(run.owner_id, run.id, f"step/{number}"),
            run_id=run.id,
            scope_id=run.scope_id,
            number=number,
            attempt=run.generation,
            status="model",
            created_at=self.clock(),
        )
        db.add(step)
        db.flush()
        return step.id, run.generation

    def create(self, owner, conversation, body):
        key = str(body.run_id)
        payload = body.model_dump(mode="json")
        payload["as_of"] = time_ms(body.as_of) if body.as_of else None
        fingerprint = hashed("ada-agent-input-v1", {"conversation": conversation, "input": payload})
        with self.sessions() as db:
            old = db.get(AgentRun, (owner, key))
            if old:
                if old.input_hash != fingerprint:
                    raise ServiceError(409, "agent_run_id_reused")
                return self._output(db, old), False
            conv = db.scalar(
                select(Conversation).where(
                    Conversation.owner_id == owner, Conversation.id == conversation
                )
            )
            if conv is None:
                raise ServiceError(404, "conversation_not_found")
            if conv.prompt_version not in COMPATIBLE_CHAT_PROMPTS:
                raise ServiceError(409, "agent_prompt_upgrade_required")
        if not self.capacity.acquire(blocking=False):
            raise ServiceError(503, "generation_capacity_busy")
        try:
            with self.sessions.begin() as db:
                conv = db.scalar(
                    select(Conversation)
                    .where(Conversation.owner_id == owner, Conversation.id == conversation)
                    .with_for_update()
                )
                if conv is None:
                    raise ServiceError(404, "conversation_not_found")
                owned_scope(db, owner, conv.scope_id, lock=True)
                old = db.get(AgentRun, (owner, key))
                if old:
                    if old.input_hash != fingerprint:
                        raise ServiceError(409, "agent_run_id_reused")
                    return self._output(db, old), False
                if conv.prompt_version not in COMPATIBLE_CHAT_PROMPTS:
                    raise ServiceError(409, "agent_prompt_upgrade_required")
                if (
                    db.scalar(
                        select(func.count())
                        .select_from(AgentRun)
                        .where(AgentRun.owner_id == owner, AgentRun.scope_id == conv.scope_id)
                    )
                    >= 100
                ):
                    raise ServiceError(413, "agent_retained_limit")
                at = self.clock()
                run = AgentRun(
                    owner_id=owner,
                    id=key,
                    scope_id=conv.scope_id,
                    conversation_id=conversation,
                    input_hash=fingerprint,
                    input=payload,
                    protocol_version=body.protocol_version,
                    protocol_snapshot={
                        "protocol": protocol(),
                        "chat_prompt": conv.prompt_version,
                        "tools": {name: REGISTRY[name].public() for name in body.allowed_tools},
                    },
                    messages=[
                        {
                            "role": "system",
                            "content": POLICY + canonical(conv.personality_snapshot),
                        },
                        {"role": "user", "content": body.task},
                    ],
                    provider=self.provider.id,
                    model=self.provider.model,
                    status="running",
                    generation=1,
                    as_of=payload["as_of"] if payload["as_of"] is not None else at,
                    created_at=at,
                )
                db.add(run)
                db.flush()
                step_id, generation = self._model_step(db, run)
            self._drive_model(owner, key, step_id, generation)
            return self.detail(owner, key), True
        except IntegrityError:
            raise ServiceError(409, "agent_reservation_conflict") from None
        finally:
            self.capacity.release()

    def _fail_model(self, owner, key, step_id, generation, code):
        with self.sessions.begin() as db:
            run = self._owned(db, owner, key, lock=True)
            if run.generation == generation and run.status == "running":
                self._terminal(run, db.get(AgentStep, (owner, step_id)), "failed", code)

    def _drive_model(self, owner, key, step_id, generation):
        try:
            with self.sessions() as db:
                run = self._owned(db, owner, key)
                if run.generation != generation or run.status != "running":
                    return
                self._bound(run)
                messages = run.messages
                tools = [REGISTRY[name].native() for name in run.input["allowed_tools"]]
                if self.provider.id != run.provider or self.provider.model != run.model:
                    raise ServiceError(409, "agent_provider_changed")
                if (
                    len(canonical({"messages": messages, "tools": tools}).encode("utf-8"))
                    + 512
                    + OUTPUT_TOKENS
                    > CONTEXT_BYTES
                ):
                    raise ServiceError(413, "agent_context_bound")
            # No database connection or transaction is retained during inference.
            message = validate_message(self.provider.complete(messages, tools))
            with self.sessions.begin() as db:
                run = self._owned(db, owner, key, lock=True)
                step = db.get(AgentStep, (owner, step_id))
                if (
                    run.generation != generation
                    or run.status != "running"
                    or step.status != "model"
                ):
                    return  # A recovered lease fences every late provider result.
                if self.clock() >= run.lease_until:
                    self._terminal(run, step, "unknown", "agent_interrupted")
                    return
                self._bound(run)
                if not message.get("tool_calls"):
                    run.response = message["content"]
                    step.model_message = message
                    self._terminal(run, step, "completed")
                    return
                function = message["tool_calls"][0]["function"]
                name = function["name"]
                if name not in run.input["allowed_tools"] or name not in REGISTRY:
                    raise ServiceError(403, "agent_tool_not_allowed")
                spec = REGISTRY[name]
                arguments = spec.arguments.model_validate(function["arguments"]).model_dump(
                    mode="json"
                )
                if sum(s.tool == name for s in self._steps(db, run)) >= spec.max_calls:
                    raise ServiceError(409, "agent_tool_call_bound")
                if name == "source_lookup":
                    source_result(db, owner, run.scope_id, run.as_of, arguments)
                step.tool, step.tool_version, step.arguments = name, spec.version, arguments
                step.argument_hash = hashed(
                    "ada-agent-arguments-v1",
                    {"tool": name, "version": spec.version, "arguments": arguments},
                )
                step.expires_at = self.clock() + APPROVAL_MS
                step.preview_hash = hashed(
                    "ada-agent-preview-v1",
                    {
                        "owner": owner,
                        "run": key,
                        "scope": run.scope_id,
                        "step": step.id,
                        "argument_hash": step.argument_hash,
                        "expires_at": step.expires_at,
                        "as_of": run.as_of,
                        "protocol": run.protocol_version,
                    },
                )
                step.model_message = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{"function": {"name": name, "arguments": arguments}}],
                }
                step.status, run.status, run.lease_until = (
                    "pending_approval",
                    "pending_approval",
                    None,
                )
        except ProviderError as error:
            code = (
                error.code
                if error.code
                in {
                    "provider_timeout",
                    "provider_unavailable",
                    "model_not_found",
                    "invalid_agent_response",
                    "agent_response_bound",
                    "agent_protocol_unavailable",
                }
                else "agent_provider_error"
            )
            self._fail_model(owner, key, step_id, generation, code)
        except ServiceError as error:
            self._fail_model(owner, key, step_id, generation, error.code)
        except (ValidationError, ValueError, TypeError, UnicodeError):
            self._fail_model(owner, key, step_id, generation, "agent_invalid_command")
        except Exception:
            self._fail_model(owner, key, step_id, generation, "agent_provider_error")

    def _same_approval(self, old, key, step_id, fingerprint):
        if old.run_id != key or old.step_id != step_id or old.input_hash != fingerprint:
            raise ServiceError(409, "agent_approval_id_reused")
        if old.result is None:
            raise ServiceError(409, "agent_execution_in_progress")
        return old.result

    def _preview(self, db, run, step_id, body):
        self._bound(run)
        step = db.get(AgentStep, (run.owner_id, step_id))
        if step is None or step.run_id != run.id:
            raise ServiceError(404, "agent_step_not_found")
        if run.status != "pending_approval" or step.status != "pending_approval":
            raise ServiceError(409, "agent_step_not_pending")
        if step.expires_at <= self.clock():
            raise ServiceError(409, "agent_approval_expired")
        if (
            step.preview_hash != body.preview_hash
            or step.argument_hash != body.argument_hash
            or step.tool_version != body.tool_version
        ):
            raise ServiceError(409, "agent_preview_changed")
        if step.argument_hash != hashed(
            "ada-agent-arguments-v1",
            {"tool": step.tool, "version": step.tool_version, "arguments": step.arguments},
        ):
            raise ServiceError(409, "agent_preview_changed")
        if step.tool == "source_lookup":
            source_result(db, run.owner_id, run.scope_id, run.as_of, step.arguments)
        return step

    def _receipt(self, db, run, step, approval, outcome, result=None, code=None):
        at = self.clock()
        snapshot = {
            "id": stable(run.owner_id, run.id, "receipt/" + approval.id),
            "approval_id": approval.id,
            "owner_id": run.owner_id,
            "run_id": run.id,
            "scope_id": run.scope_id,
            "step_id": step.id,
            "tool": step.tool,
            "tool_version": step.tool_version,
            "argument_hash": step.argument_hash,
            "preview_hash": step.preview_hash,
            "outcome": outcome,
            "origin": "tool_result",
            "trust_class": "untrusted_tool_output",
            "result": result,
            "error_code": code,
            "created_at": at,
        }
        db.add(
            AgentReceipt(
                owner_id=run.owner_id,
                id=snapshot["id"],
                scope_id=run.scope_id,
                run_id=run.id,
                step_id=step.id,
                approval_id=approval.id,
                outcome=outcome,
                snapshot=snapshot,
                created_at=at,
            )
        )
        approval.result = snapshot
        return snapshot

    def approve(self, owner, key, step_id, body, decision="approve"):
        approval_id = str(body.approval_id)
        fingerprint = hashed(
            "ada-agent-approval-v1",
            {
                "run": key,
                "step": step_id,
                "decision": decision,
                "input": body.model_dump(mode="json"),
            },
        )
        with self.sessions() as db:
            self._owned(db, owner, key)
            old = db.get(AgentApproval, (owner, approval_id))
            if old:
                return self._same_approval(old, key, step_id, fingerprint), False
        acquired = decision == "approve" and self.capacity.acquire(blocking=False)
        if decision == "approve" and not acquired:
            raise ServiceError(503, "generation_capacity_busy")
        try:
            with self.sessions.begin() as db:
                run = self._owned(db, owner, key, lock=True)
                old = db.get(AgentApproval, (owner, approval_id))
                if old:
                    return self._same_approval(old, key, step_id, fingerprint), False
                step = self._preview(db, run, step_id, body)
                approval = AgentApproval(
                    owner_id=owner,
                    id=approval_id,
                    scope_id=run.scope_id,
                    run_id=key,
                    step_id=step_id,
                    actor_id=owner,
                    decision=decision,
                    input_hash=fingerprint,
                    argument_hash=body.argument_hash,
                    preview_hash=body.preview_hash,
                    tool_version=body.tool_version,
                    created_at=self.clock(),
                )
                db.add(approval)
                db.flush()
                if decision == "revoke":
                    step.status = "revoked"
                    run.status, run.error_code, run.finished_at = (
                        "failed",
                        "agent_approval_revoked",
                        self.clock(),
                    )
                    receipt = self._receipt(
                        db, run, step, approval, "revoked", code="agent_approval_revoked"
                    )
                    return receipt, True
                run.generation += 1
                generation = run.generation
                run.status, run.lease_until, step.status = (
                    "running",
                    self.clock() + LEASE_MS,
                    "executing",
                )
                scope, at, tool, arguments = run.scope_id, run.as_of, step.tool, step.arguments
            started = time.monotonic()
            result, error = None, None
            try:
                result = self.dispatch(self.sessions, owner, scope, at, tool, arguments)
                result = REGISTRY[tool].result.model_validate(result).model_dump(mode="json")
                if time.monotonic() - started > REGISTRY[tool].timeout_seconds:
                    raise ServiceError(503, "agent_tool_timeout")
                if len(canonical(result).encode("utf-8")) > REGISTRY[tool].output_bytes:
                    raise ServiceError(413, "agent_tool_output_bound")
            except ServiceError as failure:
                error = failure.code
            except (ValueError, ValidationError, TypeError, UnicodeError):
                error = "agent_tool_invalid_result"
            except Exception:
                error = "agent_tool_failed"
            with self.sessions.begin() as db:
                run = self._owned(db, owner, key, lock=True)
                approval = db.get(AgentApproval, (owner, approval_id))
                step = db.get(AgentStep, (owner, step_id))
                if run.generation != generation or step.status != "executing":
                    if approval.result is not None:
                        return approval.result, True
                    raise ServiceError(409, "agent_attempt_fenced")
                if self.clock() >= run.lease_until:
                    receipt = self._receipt(
                        db, run, step, approval, "unknown", code="agent_interrupted"
                    )
                    self._terminal(run, step, "unknown", "agent_interrupted")
                    return receipt, True
                try:
                    self._bound(run)
                except ServiceError as failure:
                    error = failure.code
                if error:
                    receipt = self._receipt(db, run, step, approval, "failed", code=error)
                    self._terminal(run, step, "failed", error)
                    return receipt, True
                receipt = self._receipt(db, run, step, approval, "completed", result=result)
                step.status, step.finished_at = "completed", self.clock()
                run.messages = run.messages + [
                    step.model_message,
                    {
                        "role": "tool",
                        "tool_name": tool,
                        "content": canonical(
                            {
                                "receipt_id": receipt["id"],
                                "origin": "tool_result",
                                "trust_class": "untrusted_tool_output",
                                "result": result,
                            }
                        ),
                    },
                ]
                try:
                    next_step, generation = self._model_step(db, run)
                except ServiceError as failure:
                    run.status, run.error_code, run.lease_until, run.finished_at = (
                        "failed",
                        failure.code,
                        None,
                        self.clock(),
                    )
                    next_step = None
            if next_step is not None:
                self._drive_model(owner, key, next_step, generation)
            return receipt, True
        except ServiceError as failure:
            if failure.code in {
                "agent_approval_expired",
                "agent_elapsed_bound",
                "agent_registry_changed",
                "tool_source_unavailable",
                "tool_source_changed",
                "tool_source_span_invalid",
                "tool_source_bound",
            }:
                # The rejected approval never grants authority. Commit a terminal
                # state separately after the failed reservation has rolled back.
                with self.sessions.begin() as db:
                    run = self._owned(db, owner, key, lock=True)
                    step = db.get(AgentStep, (owner, step_id))
                    if (
                        run.status == "pending_approval"
                        and step
                        and step.run_id == key
                        and step.status == "pending_approval"
                    ):
                        self._terminal(run, step, "failed", failure.code)
            raise
        except IntegrityError:
            raise ServiceError(409, "agent_receipt_conflict") from None
        finally:
            if acquired:
                self.capacity.release()

    def recover(self, owner, key, body):
        nonce = str(body.operation_id)
        fingerprint = hashed(
            "ada-agent-recovery-v1", {"run": key, "input": body.model_dump(mode="json")}
        )
        with self.sessions.begin() as db:
            run = self._owned(db, owner, key, lock=True)
            old = db.get(AgentApproval, (owner, nonce))
            if old:
                if old.run_id != key or old.input_hash != fingerprint or old.decision != "recover":
                    raise ServiceError(409, "agent_recovery_id_reused")
                return old.result, False
            if (
                run.status != "running"
                or run.generation != body.generation
                or self.clock() < run.lease_until
            ):
                raise ServiceError(409, "agent_lease_not_expired")
            step = self._steps(db, run)[-1]
            operation = AgentApproval(
                owner_id=owner,
                id=nonce,
                scope_id=run.scope_id,
                run_id=key,
                step_id=step.id,
                actor_id=owner,
                decision="recover",
                input_hash=fingerprint,
                created_at=self.clock(),
            )
            db.add(operation)
            db.flush()
            approval = (
                db.scalar(
                    select(AgentApproval).where(
                        AgentApproval.owner_id == owner,
                        AgentApproval.step_id == step.id,
                        AgentApproval.decision == "approve",
                    )
                )
                or operation
            )
            receipt = self._receipt(db, run, step, approval, "unknown", code="agent_interrupted")
            operation.result = receipt
            run.generation += 1
            self._terminal(run, step, "unknown", "agent_interrupted")
            return receipt, True
