"""Read-only cross-owner metadata, current grants, and generation-free health."""

import json
import logging
import re
import threading
import time
from typing import Annotated, Literal
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import Request as HttpRequest
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError

from ada.admin import AUDIT_RETENTION_MS, PollLimiter, audit, audit_lock
from ada.admin_contracts import (
    Action,
    AdminAuditsOutput,
    AdminMeOutput,
    AdminOverviewOutput,
    AdminProvidersOutput,
    AdminRequestDetailOutput,
    AdminRequestsOutput,
    Outcome,
)
from ada.contracts import ErrorOutput, ValidationErrorOutput
from ada.memory import Timestamp
from ada.models import AdminAudit, AdminGrant, Conversation, Request, RetrievalTrace, now_ms
from ada.proposal_models import MemoryProposal
from ada.providers import OllamaProvider
from ada.schema import SCHEMA_HEAD

DAY_MS = 24 * 60 * 60 * 1000
_probe_logging = threading.local()


class _ProbeLogFilter(logging.Filter):
    def filter(self, record):
        return not getattr(_probe_logging, "active", False)


# httpx logs full URLs at INFO, which may contain configured credentials or paths.
for _logger in (
    "httpx",
    "httpcore.connection",
    "httpcore.http11",
    "httpcore.http2",
    "httpcore.proxy",
    "httpcore.socks",
):
    logging.getLogger(_logger).addFilter(_ProbeLogFilter())
ERROR_CODES = frozenset(
    {
        "provider_timeout",
        "provider_unavailable",
        "model_not_found",
        "invalid_response",
        "interrupted",
        "conversation_changed",
        "provider_error",
    }
)


def safe_tag(value):
    # Tags only: never return URLs, credentials, free-form errors or provider bodies.
    if (
        isinstance(value, str)
        and re.fullmatch(r"[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)*(?::[a-zA-Z0-9_.-]+)?", value)
        and len(value) <= 120
    ):
        return value
    return "unknown"


def model_key(value):
    # Ollama resolves a bare final name to the latest tag, including namespaces.
    return value if ":" in value.rsplit("/", 1)[-1] else value + ":latest"


class ProviderProbe:
    def __init__(self, provider, clock=time.monotonic):
        self.provider, self.clock = provider, clock
        self.lock = threading.Lock()
        self.expires = 0.0
        self.result = None

    def get(self):
        with self.lock:
            if self.result is not None and self.clock() < self.expires:
                return dict(self.result)
            result = {
                "reachability": "unknown",
                "model_available": None,
                "checked_at": None,
                "error_code": None,
            }
            if isinstance(self.provider, OllamaProvider):
                # Streaming bounds the metadata response; no chat/inference call.
                _probe_logging.active = True
                try:
                    deadline = time.monotonic() + 3
                    with httpx.Client(
                        base_url=self.provider.settings.ollama_url,
                        timeout=3,
                        transport=self.provider.transport,
                        trust_env=False,
                        headers={"Accept-Encoding": "identity"},
                    ) as client:
                        with client.stream("GET", "/api/tags") as response:
                            response.raise_for_status()
                            payload = bytearray()
                            for chunk in response.iter_raw():
                                if time.monotonic() > deadline:
                                    raise httpx.ReadTimeout("health_probe_deadline")
                                if len(payload) + len(chunk) > 256_000:
                                    raise ValueError("health_response_too_large")
                                payload.extend(chunk)
                    data = json.loads(payload)
                    models = data["models"]
                    if not isinstance(models, list) or any(
                        not isinstance(m, dict) or not isinstance(m.get("name"), str)
                        for m in models
                    ):
                        raise ValueError("invalid_health_response")
                    result.update(
                        reachability="reachable",
                        model_available=any(
                            model_key(m["name"]) == model_key(self.provider.model) for m in models
                        ),
                    )
                except (httpx.HTTPError, httpx.InvalidURL):
                    result.update(reachability="unreachable", error_code="provider_unavailable")
                except (ValueError, TypeError, KeyError):
                    result.update(reachability="reachable", error_code="invalid_health_response")
                finally:
                    _probe_logging.active = False
                result["checked_at"] = now_ms()
            self.result, self.expires = result, self.clock() + 30
            return dict(result)


class BoundedQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0, le=10_000)


class RequestQuery(BoundedQuery):
    owner_id: UUID | None = None
    request_id: UUID | None = None
    status: Literal["running", "completed", "failed"] | None = None
    provider: str | None = Field(None, max_length=40, pattern=r"^[a-zA-Z0-9_.-]+$")
    created_from: Timestamp | None = Field(None, ge=0)
    created_to: Timestamp | None = Field(None, ge=0)


class AuditQuery(BoundedQuery):
    actor_id: UUID | None = None
    action: Action | None = None
    outcome: Outcome | None = None


def request_columns():
    return select(
        Request.owner_id,
        Request.id.label("request_id"),
        Request.conversation_id,
        Conversation.scope_id,
        Request.status,
        Request.attempt,
        Request.provider,
        Request.model,
        Request.created_at,
        Request.started_at,
        Request.finished_at,
        Request.error_code,
        Request.input_tokens,
        Request.output_tokens,
    ).join(
        Conversation,
        (Conversation.owner_id == Request.owner_id) & (Conversation.id == Request.conversation_id),
    )


def request_metadata(row, timestamp):
    item = dict(row)
    item["observed_at"] = timestamp
    finish = (
        item["finished_at"]
        if item["finished_at"] is not None
        else timestamp
        if item["status"] == "running"
        else None
    )
    item["elapsed_ms"] = max(0, finish - item["started_at"]) if finish is not None else None
    item["provider"], item["model"] = safe_tag(item["provider"]), safe_tag(item["model"])
    if item["error_code"] is not None and item["error_code"] not in ERROR_CODES:
        item["error_code"] = "unknown_error"
    return item


def retrieval_summary(db, owner, request_id):
    array_length = func.json_array_length
    budget_fields = (
        "memory_limit_bytes",
        "memory_used_bytes",
        "prompt_limit_bytes",
        "prompt_used_bytes",
        "history_pairs_omitted",
    )
    query = select(
        array_length(RetrievalTrace.candidates).label("candidate_count"),
        array_length(RetrievalTrace.selected).label("selected_count"),
        RetrievalTrace.retrieval_ms,
        *(RetrievalTrace.budget[k].as_integer().label(k) for k in budget_fields),
        RetrievalTrace.budget["candidate_pool_truncated"]
        .as_boolean()
        .label("candidate_pool_truncated"),
    ).where(RetrievalTrace.owner_id == owner, RetrievalTrace.request_id == request_id)
    row = db.execute(query).mappings().first()
    return {"available": False} if row is None else {"available": True, **dict(row)}


class Monitoring:
    def __init__(self, sessions, settings, provider, service):
        self.sessions, self.settings, self.provider, self.service = (
            sessions,
            settings,
            provider,
            service,
        )
        self.limiter, self.probe = PollLimiter(), ProviderProbe(provider)

    def admission(self):
        # Snapshot the real semaphore under its own lock; never acquire a slot to probe.
        with self.service.capacity._cond:
            available = self.service.capacity._value
        return {
            "max_parallel": self.settings.max_parallel,
            "process_available_slots": available,
            "process_active_slots": self.settings.max_parallel - available,
        }

    def authorize(self, owner):
        with self.sessions() as db:
            return db.scalar(select(AdminGrant.enabled).where(AdminGrant.user_id == owner)) is True

    def record(self, owner, action, outcome, target_owner=None, target_request=None, recheck=False):
        with self.sessions.begin() as db:
            audit_lock(db)
            if (
                recheck
                and db.scalar(select(AdminGrant.enabled).where(AdminGrant.user_id == owner))
                is not True
            ):
                outcome = "denied"
            audit(
                db,
                actor_id=owner,
                action=action,
                outcome=outcome,
                owner_id=target_owner,
                request_id=target_request,
            )
        return outcome


def admin_router(monitor, current_user):
    router = APIRouter(prefix="/v1/admin", tags=["admin monitoring"])
    failures = {code: {"model": ErrorOutput} for code in (401, 403, 404, 429, 503)}
    failures[422] = {"model": ValidationErrorOutput}
    actions = {
        "/v1/admin/" + route: "monitor." + action
        for route, action in (
            ("me", "me"),
            ("overview", "overview"),
            ("requests", "requests"),
            ("requests/{owner_id}/{request_id}", "request"),
            ("providers", "providers"),
            ("audit", "audit"),
        )
    }

    def current_admin(request: HttpRequest, owner: str = Depends(current_user)):
        action = actions[request.scope["route"].path]

        def target(key):
            try:
                return str(UUID(str(request.path_params.get(key, request.query_params.get(key)))))
            except ValueError:
                return None

        target_owner = target("owner_id")
        targets = (target_owner, target("request_id") if target_owner is not None else None)
        try:
            allowed, record = monitor.limiter.admit(owner)
            if not allowed:
                if record:
                    monitor.record(owner, action, "rate_limited", *targets)
                raise HTTPException(429, "monitoring_rate_limited", headers={"Retry-After": "60"})
            if not monitor.authorize(owner):
                monitor.record(owner, action, "denied", *targets)
                raise HTTPException(403, "admin_required")
            try:
                yield owner
            except Exception as exc:
                outcome = (
                    "invalid"
                    if isinstance(exc, RequestValidationError)
                    or (isinstance(exc, HTTPException) and exc.status_code == 422)
                    else "not_found"
                    if isinstance(exc, HTTPException) and exc.status_code == 404
                    else "failed"
                )
                monitor.record(owner, action, outcome, *targets)
                raise
            else:
                if monitor.record(owner, action, "allowed", *targets, recheck=True) == "denied":
                    raise HTTPException(403, "admin_required")
        except (SQLAlchemyError, RuntimeError):
            raise HTTPException(503, "monitoring_unavailable") from None

    admin = Depends(current_admin, scope="function")

    @router.get("/me", response_model=AdminMeOutput, responses=failures)
    def me(owner: str = admin):
        return {"id": owner, "permissions": ["monitoring:read"]}

    @router.get("/requests", response_model=AdminRequestsOutput, responses=failures)
    def requests(filters: Annotated[RequestQuery, Query()], owner: str = admin):
        timestamp = now_ms()
        end = filters.created_to if filters.created_to is not None else timestamp + 1
        start = filters.created_from if filters.created_from is not None else max(0, end - DAY_MS)
        if (
            end <= start
            or end - start > 7 * DAY_MS
            or (filters.request_id is not None and filters.owner_id is None)
        ):
            raise HTTPException(422, "invalid_monitoring_filter")
        query = request_columns().where(Request.created_at >= start, Request.created_at < end)
        for key in ("owner_id", "status", "provider"):
            value = getattr(filters, key)
            if value is not None:
                query = query.where(getattr(Request, key) == str(value))
        if filters.request_id is not None:
            query = query.where(Request.id == str(filters.request_id))
        with monitor.sessions() as db:
            rows = (
                db.execute(
                    query.order_by(
                        Request.created_at.desc(), Request.owner_id.desc(), Request.id.desc()
                    )
                    .offset(filters.offset)
                    .limit(filters.limit + 1)
                )
                .mappings()
                .all()
            )
        return {
            "items": [request_metadata(r, timestamp) for r in rows[: filters.limit]],
            "limit": filters.limit,
            "offset": filters.offset,
            "has_more": len(rows) > filters.limit,
            "created_from": start,
            "created_to": end,
            "updated_at": timestamp,
        }

    @router.get(
        "/requests/{owner_id}/{request_id}",
        response_model=AdminRequestDetailOutput,
        responses=failures,
    )
    def request_detail(owner_id: UUID, request_id: UUID, owner: str = admin):
        with monitor.sessions() as db:
            row = (
                db.execute(
                    request_columns().where(
                        Request.owner_id == str(owner_id), Request.id == str(request_id)
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                raise HTTPException(404, "request_not_found")
            return request_metadata(row, now_ms()) | {
                "retrieval": retrieval_summary(db, str(owner_id), str(request_id))
            }

    @router.get("/providers", response_model=AdminProvidersOutput, responses=failures)
    def providers(owner: str = admin):
        return {
            "provider": safe_tag(monitor.provider.id),
            "model": safe_tag(monitor.provider.model),
            "health": monitor.probe.get(),
            "generation_admission": monitor.admission(),
            "context_tokens": monitor.settings.context_tokens,
            "output_tokens": monitor.settings.output_tokens,
            "timeout_seconds": monitor.settings.timeout_seconds,
        }

    @router.get("/overview", response_model=AdminOverviewOutput, responses=failures)
    def overview(window_hours: int = Query(24, ge=1, le=168), owner: str = admin):
        timestamp = now_ms()
        start = max(0, timestamp - window_hours * 60 * 60 * 1000)
        health = monitor.probe.get()  # No database transaction is open during network I/O.
        with monitor.sessions() as db:
            rows = (
                db.execute(
                    select(
                        Request.status,
                        func.count().label("count"),
                        func.sum(Request.input_tokens).label("input_tokens"),
                        func.sum(Request.output_tokens).label("output_tokens"),
                        func.count(Request.input_tokens).label("input_known"),
                        func.count(Request.output_tokens).label("output_known"),
                    )
                    .where(Request.created_at >= start, Request.created_at <= timestamp)
                    .group_by(Request.status)
                )
                .mappings()
                .all()
            )
            version = db.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one_or_none()
            proposal_counts = None
            if version == SCHEMA_HEAD:
                counts = dict(
                    db.execute(
                        select(MemoryProposal.status, func.count())
                        .where(
                            MemoryProposal.created_at >= start,
                            MemoryProposal.created_at <= timestamp,
                        )
                        .group_by(MemoryProposal.status)
                    ).all()
                )
                proposal_counts = {
                    state: counts.get(state, 0) for state in ("pending", "accepted", "rejected")
                }
        return {
            "window_hours": window_hours,
            "created_from": start,
            "updated_at": timestamp,
            "requests": {r["status"]: r["count"] for r in rows},
            "memory_proposal_counts": proposal_counts,
            **{
                key: sum(r[key] or 0 for r in rows) if any(r[known] for r in rows) else None
                for key, known in (
                    ("input_tokens", "input_known"),
                    ("output_tokens", "output_known"),
                )
            },
            "input_tokens_known_requests": sum(r["input_known"] for r in rows),
            "output_tokens_known_requests": sum(r["output_known"] for r in rows),
            "database_ready": version == SCHEMA_HEAD,
            "schema_version": SCHEMA_HEAD if version == SCHEMA_HEAD else None,
            "provider_health": health,
            "generation_admission": monitor.admission(),
        }

    @router.get("/audit", response_model=AdminAuditsOutput, responses=failures)
    def audits(filters: Annotated[AuditQuery, Query()], owner: str = admin):
        # Read only the retention window, even when this is the first request after downtime.
        timestamp = now_ms()
        query = select(
            *(
                getattr(AdminAudit, k)
                for k in (
                    "id",
                    "actor_id",
                    "actor_kind",
                    "action",
                    "target_owner_id",
                    "target_request_id",
                    "outcome",
                    "created_at",
                )
            )
        ).where(AdminAudit.created_at >= timestamp - AUDIT_RETENTION_MS)
        for key in ("actor_id", "action", "outcome"):
            value = getattr(filters, key)
            if value is not None:
                query = query.where(getattr(AdminAudit, key) == str(value))
        with monitor.sessions() as db:
            rows = (
                db.execute(
                    query.order_by(AdminAudit.id.desc())
                    .offset(filters.offset)
                    .limit(filters.limit + 1)
                )
                .mappings()
                .all()
            )
        return {
            "items": [dict(r) for r in rows[: filters.limit]],
            "limit": filters.limit,
            "offset": filters.offset,
            "has_more": len(rows) > filters.limit,
            "updated_at": timestamp,
        }

    return router
