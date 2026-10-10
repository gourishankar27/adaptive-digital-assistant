import json
from contextlib import asynccontextmanager
from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi import Request as HttpRequest
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import case, select, text
from sqlalchemy.exc import SQLAlchemyError

from ada.auth import token_hash
from ada.config import Settings
from ada.contracts import (
    CapabilitiesOutput,
    ConversationOutput,
    ErrorOutput,
    EventOutput,
    LiveOutput,
    PersonalityOutput,
    PromptUpgradeOutput,
    ReadyOutput,
    UserOutput,
    ValidationErrorOutput,
)
from ada.db import connect
from ada.document_api import document_router
from ada.documents import MAX_UPLOAD_BYTES
from ada.entity_api import entity_router
from ada.evidence import public_source_version, validate_text
from ada.memory import (
    ClaimInput,
    ClaimOutput,
    MemoryService,
    NoteInput,
    SourceVersionOutput,
    SupersedeInput,
    Timestamp,
    owned_scope,
    public_claim,
    time_ms,
)
from ada.models import (
    Claim,
    Conversation,
    Event,
    Personality,
    Request,
    RetrievalTrace,
    Scope,
    SourceVersion,
    User,
)
from ada.monitoring import Monitoring, admin_router
from ada.personality import PROMPT_VERSION, build_prompt
from ada.providers import FakeProvider, OllamaProvider
from ada.retrieval import (
    CitationOutput,
    DocumentCitationOutput,
    RetrievalOutput,
    RetrieveInput,
    lock_scope_for_retrieval,
    plan_query,
    public_trace,
    retrieve,
)
from ada.schema import SCHEMA_HEAD
from ada.service import ChatService, ServiceError, public_request


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("*")
    @classmethod
    def valid_text(cls, value):
        return validate_text(value)


class PersonalityInput(StrictInput):
    name: str = Field(default="ADA", min_length=1, max_length=40, pattern=r"^[\w .-]+$")
    style: Literal["direct", "conversational", "formal"] = "conversational"
    warmth: Literal["reserved", "warm"] = "warm"
    detail: Literal["concise", "balanced", "detailed"] = "balanced"


class ConversationInput(StrictInput):
    personality_id: UUID
    title: str = Field(default="New conversation", min_length=1, max_length=120)
    scope_id: UUID | None = None


class ScopeInput(StrictInput):
    name: str = Field(min_length=1, max_length=120)
    kind: Literal["personal", "project"] = "project"


class ScopeOutput(BaseModel):
    id: UUID
    name: str
    kind: Literal["personal", "project"]
    created_at: Timestamp


def public_conversation(row):
    return {
        "id": row.id,
        "title": row.title,
        "scope_id": row.scope_id,
        "scope_kind": row.scope_kind,
        "personality": row.personality_snapshot,
        "prompt_version": row.prompt_version,
        "revision": row.revision,
        "created_at": row.created_at,
    }


def public_scope(row):
    return {"id": row.id, "name": row.name, "kind": row.kind, "created_at": row.created_at}


class ChatInput(StrictInput):
    request_id: UUID
    content: str = Field(min_length=1, max_length=4000)
    as_of: AwareDatetime | None = None
    use_memory: bool = Field(default=True, strict=True)
    use_documents: bool = Field(default=False, strict=True)

    @field_validator("as_of")
    @classmethod
    def millisecond_time(cls, value):
        if value is not None:
            time_ms(value)
        return value

    @field_validator("content")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("content must not be blank")
        return value


class RequestOutput(BaseModel):
    request_id: UUID
    conversation_id: UUID
    status: Literal["running", "completed", "failed"]
    response: str | None
    error_code: str | None
    attempt: int
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    citations: list[CitationOutput]
    document_citations: list[DocumentCitationOutput] = Field(default_factory=list)
    citation_warnings: list[str]


class TraceOutput(RetrievalOutput):
    request_id: UUID
    conversation_id: UUID
    created_at: Timestamp


def error_responses(*statuses):
    """Describe implemented failures without changing exception handlers."""
    return {
        status: {
            "model": ValidationErrorOutput if status == 422 else ErrorOutput,
            "description": "Sanitized validation issues or error code; input is omitted"
            if status == 422
            else "Sanitized error code",
        }
        for status in statuses
    }


def create_app(settings=None, provider=None, sessions=None):
    settings = settings or Settings()
    engine = None
    if sessions is None:
        engine, sessions = connect(settings.database_url)
    provider = provider or (
        FakeProvider() if settings.provider == "fake" else OllamaProvider(settings)
    )
    service = ChatService(sessions, provider, settings)
    memory = MemoryService(sessions)

    @asynccontextmanager
    async def lifespan(_):
        yield
        if engine is not None:
            engine.dispose()

    app = FastAPI(
        title="ADA",
        version="0.2.0",
        lifespan=lifespan,
        description="Scoped memory retrieval, cited chat, durable evidence traces and explicitly granted admin monitoring.",
    )
    app.state.sessions, app.state.chat, app.state.memory = sessions, service, memory

    @app.middleware("http")
    async def monitoring_cache(request: HttpRequest, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/v1/admin/") or (
            request.url.path.startswith("/v1/")
            and ("/document-" in request.url.path or "/documents" in request.url.path)
        ):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(SQLAlchemyError)
    def database_error(request: HttpRequest, exc: SQLAlchemyError):
        # Do not echo SQL parameters, credential hashes or connection strings.
        return JSONResponse(status_code=503, content={"detail": "database_not_ready"})

    @app.exception_handler(ServiceError)
    async def service_error(_: HttpRequest, exc: ServiceError):
        headers = {"Retry-After": "3"} if exc.status == 503 else None
        return JSONResponse(status_code=exc.status, content={"detail": exc.code}, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: HttpRequest, exc: RequestValidationError):
        # Avoid echoing private input. ASCII JSON also handles deliberately
        # malformed Unicode keys/values without turning validation into a 500.
        errors = [{key: error[key] for key in ("type", "loc", "msg")} for error in exc.errors()]
        return Response(
            status_code=422,
            media_type="application/json",
            content=json.dumps({"detail": errors}, ensure_ascii=True),
        )

    bearer = HTTPBearer(auto_error=False)

    def current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                401, "authentication_required", headers={"WWW-Authenticate": "Bearer"}
            )
        if len(credentials.credentials) > 200:
            raise HTTPException(401, "invalid_token")
        with sessions() as db:
            user_id = db.scalar(
                select(User.id).where(User.token_hash == token_hash(credentials.credentials))
            )
            if user_id is None:
                raise HTTPException(401, "invalid_token", headers={"WWW-Authenticate": "Bearer"})
            return user_id

    app.state.admin = Monitoring(sessions, settings, provider, service)
    app.include_router(admin_router(app.state.admin, current_user))
    app.include_router(document_router(sessions, current_user, error_responses))
    app.include_router(entity_router(sessions, current_user, error_responses))

    def owned_conversation(db, owner, conversation_id):
        row = db.scalar(
            select(Conversation).where(
                Conversation.id == str(conversation_id), Conversation.owner_id == owner
            )
        )
        if row is None:
            raise HTTPException(404, "conversation_not_found")
        return row

    @app.get("/health/live", response_model=LiveOutput)
    def live():
        return {"status": "ok"}

    @app.get("/health/ready", response_model=ReadyOutput, responses={503: {"model": ErrorOutput}})
    def ready():
        try:
            with sessions() as db:
                version = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                if version != SCHEMA_HEAD:
                    raise RuntimeError("schema mismatch")
        except Exception:
            raise HTTPException(503, "database_not_ready") from None
        return {"status": "ready", "schema": version}

    @app.get("/v1/me", response_model=UserOutput, responses=error_responses(401))
    def me(owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.get(User, owner)
            return {"id": row.id, "name": row.name}

    @app.get("/v1/capabilities", response_model=CapabilitiesOutput, responses=error_responses(401))
    def capabilities(owner: str = Depends(current_user)):
        return {
            "api_version": "v1",
            "admin_monitoring": True,
            "document_ingestion": "text_markdown_v1",
            "document_uploads": True,
            "document_retrieval": True,
            "document_citations": True,
            "document_max_bytes": MAX_UPLOAD_BYTES,
            "scoped_entities": True,
            "entity_resolution": "explicit_aliases_v1",
            "entity_writes": True,
            "chat": True,
            "streaming": False,
            "tools": False,
            "structured_memory": True,
            "memory_writes": "explicit_user_assertions",
            "memory_in_chat": True,
            "memory_retrieval": "full_text_and_subject",
            "memory_citations": True,
            "retrieval_traces": True,
            "chat_prompt_version": PROMPT_VERSION,
            "automatic_memory_extraction": False,
            "historical_memory_queries": True,
            "private_project_scopes": True,
            "shared_scopes": False,
            "edge_inference": False,
            "personality_isolation": True,
            "authority": "server",
            "provider": provider.id,
            "model": provider.model,
        }

    @app.post(
        "/v1/personalities",
        status_code=201,
        response_model=PersonalityOutput,
        responses=error_responses(401, 422),
    )
    def create_personality(body: PersonalityInput, owner: str = Depends(current_user)):
        with sessions.begin() as db:
            row = Personality(owner_id=owner, **body.model_dump())
            db.add(row)
            db.flush()
            return {"id": row.id, **body.model_dump()}

    @app.get(
        "/v1/personalities",
        response_model=list[PersonalityOutput],
        responses=error_responses(401, 422),
    )
    def personalities(
        owner: str = Depends(current_user),
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        with sessions() as db:
            rows = db.scalars(
                select(Personality)
                .where(Personality.owner_id == owner)
                .order_by(Personality.created_at, Personality.id)
                .limit(limit)
                .offset(offset)
            )
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "style": p.style,
                    "warmth": p.warmth,
                    "detail": p.detail,
                }
                for p in rows
            ]

    @app.post(
        "/v1/conversations",
        status_code=201,
        response_model=ConversationOutput,
        responses=error_responses(401, 404, 422),
    )
    def create_conversation(body: ConversationInput, owner: str = Depends(current_user)):
        with sessions.begin() as db:
            personality = db.scalar(
                select(Personality).where(
                    Personality.id == str(body.personality_id), Personality.owner_id == owner
                )
            )
            if personality is None:
                raise HTTPException(404, "personality_not_found")
            snapshot = {k: getattr(personality, k) for k in ("name", "style", "warmth", "detail")}
            if body.scope_id:
                scope = owned_scope(db, owner, str(body.scope_id))
            else:
                scope = Scope(owner_id=owner, kind="personal", name=body.title)
                db.add(scope)
                db.flush()
            row = Conversation(
                owner_id=owner,
                personality_id=personality.id,
                scope_id=scope.id,
                scope_kind=scope.kind,
                title=body.title,
                personality_snapshot=snapshot,
                system_prompt=build_prompt(snapshot),
                prompt_version=PROMPT_VERSION,
            )
            db.add(row)
            db.flush()
            return public_conversation(row)

    @app.get(
        "/v1/conversations",
        response_model=list[ConversationOutput],
        responses=error_responses(401, 422),
    )
    def conversations(
        owner: str = Depends(current_user),
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        with sessions() as db:
            rows = db.scalars(
                select(Conversation)
                .where(Conversation.owner_id == owner)
                .order_by(Conversation.created_at, Conversation.id)
                .limit(limit)
                .offset(offset)
            )
            return [public_conversation(c) for c in rows]

    @app.get(
        "/v1/conversations/{conversation_id}",
        response_model=ConversationOutput,
        responses=error_responses(401, 404, 422),
    )
    def conversation(conversation_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            return public_conversation(owned_conversation(db, owner, conversation_id))

    @app.post(
        "/v1/conversations/{conversation_id}/prompt-upgrade",
        response_model=PromptUpgradeOutput,
        responses=error_responses(401, 404, 409, 422),
    )
    def upgrade_prompt(conversation_id: UUID, owner: str = Depends(current_user)):
        return service.upgrade_prompt(owner, str(conversation_id))

    @app.get(
        "/v1/conversations/{conversation_id}/events",
        response_model=list[EventOutput],
        responses=error_responses(401, 404, 422),
    )
    def events(
        conversation_id: UUID,
        owner: str = Depends(current_user),
        limit: int = Query(100, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ):
        with sessions() as db:
            owned_conversation(db, owner, conversation_id)
            rows = db.execute(
                select(Event, Request.status)
                .join(
                    Request, (Request.owner_id == Event.owner_id) & (Request.id == Event.request_id)
                )
                .where(Event.owner_id == owner, Event.conversation_id == str(conversation_id))
                .order_by(Request.created_at, Request.id, case((Event.role == "user", 0), else_=1))
                .limit(limit)
                .offset(offset)
            )
            return [
                {
                    "id": e.id,
                    "role": e.role,
                    "content": e.content,
                    "trust_class": e.trust_class,
                    "request_id": e.request_id,
                    "request_status": status,
                    "created_at": e.created_at,
                    "source_version_id": e.id,
                }
                for e, status in rows
            ]

    @app.post(
        "/v1/conversations/{conversation_id}/messages",
        response_model=RequestOutput,
        responses=error_responses(401, 404, 409, 413, 422, 502, 503),
    )
    def chat(conversation_id: UUID, body: ChatInput, owner: str = Depends(current_user)):
        return service.chat(
            owner,
            str(conversation_id),
            str(body.request_id),
            body.content,
            as_of=body.as_of,
            use_memory=body.use_memory,
            use_documents=body.use_documents,
        )

    @app.get(
        "/v1/requests/{request_id}",
        response_model=RequestOutput,
        responses=error_responses(401, 404, 422),
    )
    def request_status(request_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.get(Request, (owner, str(request_id)))
            if row is None:
                raise HTTPException(404, "request_not_found")
            return public_request(row, db.get(RetrievalTrace, (owner, str(request_id))))

    @app.get(
        "/v1/requests/{request_id}/retrieval",
        response_model=TraceOutput,
        responses=error_responses(401, 404, 422),
    )
    def request_retrieval(request_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.get(Request, (owner, str(request_id)))
            if row is None:
                raise HTTPException(404, "request_not_found")
            trace = db.get(RetrievalTrace, (owner, str(request_id)))
            if trace is None:
                raise HTTPException(404, "retrieval_trace_unavailable")
            return public_trace(trace)

    @app.post(
        "/v1/scopes",
        status_code=201,
        response_model=ScopeOutput,
        responses=error_responses(401, 422),
    )
    def create_scope(body: ScopeInput, owner: str = Depends(current_user)):
        with sessions.begin() as db:
            row = Scope(owner_id=owner, **body.model_dump())
            db.add(row)
            db.flush()
            return public_scope(row)

    @app.get("/v1/scopes", response_model=list[ScopeOutput], responses=error_responses(401, 422))
    def scopes(
        owner: str = Depends(current_user),
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        with sessions() as db:
            rows = db.scalars(
                select(Scope)
                .where(Scope.owner_id == owner)
                .order_by(Scope.created_at, Scope.id)
                .limit(limit)
                .offset(offset)
            )
            return [public_scope(row) for row in rows]

    @app.get(
        "/v1/scopes/{scope_id}",
        response_model=ScopeOutput,
        responses=error_responses(401, 404, 422),
    )
    def scope(scope_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            return public_scope(owned_scope(db, owner, str(scope_id)))

    @app.post(
        "/v1/scopes/{scope_id}/retrieve",
        response_model=RetrievalOutput,
        responses=error_responses(401, 404, 422),
    )
    def retrieve_memory(scope_id: UUID, body: RetrieveInput, owner: str = Depends(current_user)):
        with sessions.begin() as db:
            lock_scope_for_retrieval(db, owner, str(scope_id))
            return retrieve(
                db,
                owner,
                str(scope_id),
                plan_query(body.query, body.as_of),
                limit=body.limit,
                budget_bytes=body.budget_bytes,
                use_documents=body.use_documents,
            )

    @app.post(
        "/v1/scopes/{scope_id}/notes",
        status_code=201,
        response_model=SourceVersionOutput,
        responses={
            200: {"model": SourceVersionOutput, "description": "Same-ID replay"},
            **error_responses(401, 404, 409, 422),
        },
    )
    def create_note(
        scope_id: UUID, body: NoteInput, response: Response, owner: str = Depends(current_user)
    ):
        result, created = memory.note(owner, str(scope_id), body)
        response.status_code = 201 if created else 200
        return result

    @app.get(
        "/v1/scopes/{scope_id}/source-versions",
        response_model=list[SourceVersionOutput],
        responses=error_responses(401, 404, 422),
    )
    def source_versions(
        scope_id: UUID,
        owner: str = Depends(current_user),
        limit: int = Query(100, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ):
        with sessions() as db:
            owned_scope(db, owner, str(scope_id))
            rows = db.scalars(
                select(SourceVersion)
                .where(
                    SourceVersion.owner_id == owner,
                    SourceVersion.scope_id == str(scope_id),
                    SourceVersion.trust_class.in_(("user_explicit", "model_generated")),
                )
                .order_by(SourceVersion.created_at, SourceVersion.id)
                .limit(limit)
                .offset(offset)
            )
            return [public_source_version(row) for row in rows]

    @app.get(
        "/v1/source-versions/{source_version_id}",
        response_model=SourceVersionOutput,
        responses=error_responses(401, 404, 422),
    )
    def source_version(source_version_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.scalar(
                select(SourceVersion).where(
                    SourceVersion.owner_id == owner,
                    SourceVersion.id == str(source_version_id),
                    SourceVersion.trust_class.in_(("user_explicit", "model_generated")),
                )
            )
            if row is None:
                raise HTTPException(404, "source_version_not_found")
            return public_source_version(row)

    @app.post(
        "/v1/scopes/{scope_id}/claims",
        status_code=201,
        response_model=ClaimOutput,
        responses={
            200: {"model": ClaimOutput, "description": "Same-ID replay"},
            **error_responses(401, 404, 409, 422),
        },
    )
    def create_claim(
        scope_id: UUID, body: ClaimInput, response: Response, owner: str = Depends(current_user)
    ):
        result, created = memory.add(owner, str(scope_id), body)
        response.status_code = 201 if created else 200
        return result

    @app.get(
        "/v1/scopes/{scope_id}/claims",
        response_model=list[ClaimOutput],
        responses=error_responses(401, 404, 422),
    )
    def claims(
        scope_id: UUID,
        owner: str = Depends(current_user),
        as_of: AwareDatetime | None = None,
        history: bool = False,
        subject: str | None = Query(None, min_length=1, max_length=160),
        predicate: str | None = Query(None, min_length=1, max_length=160),
        limit: int = Query(100, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ):
        try:
            if as_of is not None:
                time_ms(as_of)
            validate_text(subject)
            validate_text(predicate)
        except ValueError:
            raise HTTPException(422, "invalid_query_value") from None
        return memory.list(
            owner,
            str(scope_id),
            as_of=as_of,
            history=history,
            subject=subject,
            predicate=predicate,
            limit=limit,
            offset=offset,
        )

    @app.get(
        "/v1/claims/{claim_id}",
        response_model=ClaimOutput,
        responses=error_responses(401, 404, 422),
    )
    def claim(claim_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.scalar(select(Claim).where(Claim.owner_id == owner, Claim.id == str(claim_id)))
            if row is None:
                raise HTTPException(404, "claim_not_found")
            return public_claim(row)

    @app.post(
        "/v1/claims/{claim_id}/supersede",
        status_code=201,
        response_model=ClaimOutput,
        responses={
            200: {"model": ClaimOutput, "description": "Same-ID replay"},
            **error_responses(401, 404, 409, 422),
        },
    )
    def supersede_claim(
        claim_id: UUID, body: SupersedeInput, response: Response, owner: str = Depends(current_user)
    ):
        result, created = memory.supersede(owner, str(claim_id), body)
        response.status_code = 201 if created else 200
        return result

    return app
