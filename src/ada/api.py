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

from ada.auth import token_hash
from ada.config import Settings
from ada.db import connect
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
from ada.models import Claim, Conversation, Event, Personality, Request, Scope, SourceVersion, User
from ada.personality import PROMPT_VERSION, build_prompt
from ada.providers import FakeProvider, OllamaProvider
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

    @field_validator("content")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("content must not be blank")
        return value


class RequestOutput(BaseModel):
    request_id: str
    conversation_id: str
    status: Literal["running", "completed", "failed"]
    response: str | None
    error_code: str | None
    attempt: int
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None


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
        version="0.1.0",
        lifespan=lifespan,
        description="Phase 1. Explicit source-backed memory; local administrator-issued tokens.",
    )
    app.state.sessions, app.state.chat, app.state.memory = sessions, service, memory

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
            user = db.scalar(
                select(User).where(User.token_hash == token_hash(credentials.credentials))
            )
            if user is None:
                raise HTTPException(401, "invalid_token", headers={"WWW-Authenticate": "Bearer"})
            return user.id

    def owned_conversation(db, owner, conversation_id):
        row = db.scalar(
            select(Conversation).where(
                Conversation.id == str(conversation_id), Conversation.owner_id == owner
            )
        )
        if row is None:
            raise HTTPException(404, "conversation_not_found")
        return row

    @app.get("/health/live")
    def live():
        return {"status": "ok"}

    @app.get("/health/ready")
    def ready():
        try:
            with sessions() as db:
                version = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                if version != "0002":
                    raise RuntimeError("schema mismatch")
        except Exception:
            raise HTTPException(503, "database_not_ready") from None
        return {"status": "ready", "schema": version}

    @app.get("/v1/me")
    def me(owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.get(User, owner)
            return {"id": row.id, "name": row.name}

    @app.get("/v1/capabilities")
    def capabilities(owner: str = Depends(current_user)):
        return {
            "api_version": "v1",
            "chat": True,
            "streaming": False,
            "tools": False,
            "structured_memory": True,
            "memory_writes": "explicit_user_assertions",
            "memory_in_chat": False,
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

    @app.post("/v1/personalities", status_code=201)
    def create_personality(body: PersonalityInput, owner: str = Depends(current_user)):
        with sessions.begin() as db:
            row = Personality(owner_id=owner, **body.model_dump())
            db.add(row)
            db.flush()
            return {"id": row.id, **body.model_dump()}

    @app.get("/v1/personalities")
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

    @app.post("/v1/conversations", status_code=201)
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

    @app.get("/v1/conversations")
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

    @app.get("/v1/conversations/{conversation_id}")
    def conversation(conversation_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            return public_conversation(owned_conversation(db, owner, conversation_id))

    @app.post("/v1/conversations/{conversation_id}/prompt-upgrade")
    def upgrade_prompt(conversation_id: UUID, owner: str = Depends(current_user)):
        return service.upgrade_prompt(owner, str(conversation_id))

    @app.get("/v1/conversations/{conversation_id}/events")
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

    @app.post("/v1/conversations/{conversation_id}/messages", response_model=RequestOutput)
    def chat(conversation_id: UUID, body: ChatInput, owner: str = Depends(current_user)):
        return service.chat(owner, str(conversation_id), str(body.request_id), body.content)

    @app.get("/v1/requests/{request_id}", response_model=RequestOutput)
    def request_status(request_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.get(Request, (owner, str(request_id)))
            if row is None:
                raise HTTPException(404, "request_not_found")
            return public_request(row)

    @app.post("/v1/scopes", status_code=201, response_model=ScopeOutput)
    def create_scope(body: ScopeInput, owner: str = Depends(current_user)):
        with sessions.begin() as db:
            row = Scope(owner_id=owner, **body.model_dump())
            db.add(row)
            db.flush()
            return public_scope(row)

    @app.get("/v1/scopes", response_model=list[ScopeOutput])
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

    @app.get("/v1/scopes/{scope_id}", response_model=ScopeOutput)
    def scope(scope_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            return public_scope(owned_scope(db, owner, str(scope_id)))

    @app.post(
        "/v1/scopes/{scope_id}/notes",
        status_code=201,
        response_model=SourceVersionOutput,
        responses={200: {"model": SourceVersionOutput, "description": "Same-ID replay"}},
    )
    def create_note(
        scope_id: UUID, body: NoteInput, response: Response, owner: str = Depends(current_user)
    ):
        result, created = memory.note(owner, str(scope_id), body)
        response.status_code = 201 if created else 200
        return result

    @app.get("/v1/scopes/{scope_id}/source-versions", response_model=list[SourceVersionOutput])
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
                .where(SourceVersion.owner_id == owner, SourceVersion.scope_id == str(scope_id))
                .order_by(SourceVersion.created_at, SourceVersion.id)
                .limit(limit)
                .offset(offset)
            )
            return [public_source_version(row) for row in rows]

    @app.get("/v1/source-versions/{source_version_id}", response_model=SourceVersionOutput)
    def source_version(source_version_id: UUID, owner: str = Depends(current_user)):
        with sessions() as db:
            row = db.scalar(
                select(SourceVersion).where(
                    SourceVersion.owner_id == owner, SourceVersion.id == str(source_version_id)
                )
            )
            if row is None:
                raise HTTPException(404, "source_version_not_found")
            return public_source_version(row)

    @app.post(
        "/v1/scopes/{scope_id}/claims",
        status_code=201,
        response_model=ClaimOutput,
        responses={200: {"model": ClaimOutput, "description": "Same-ID replay"}},
    )
    def create_claim(
        scope_id: UUID, body: ClaimInput, response: Response, owner: str = Depends(current_user)
    ):
        result, created = memory.add(owner, str(scope_id), body)
        response.status_code = 201 if created else 200
        return result

    @app.get("/v1/scopes/{scope_id}/claims", response_model=list[ClaimOutput])
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

    @app.get("/v1/claims/{claim_id}", response_model=ClaimOutput)
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
        responses={200: {"model": ClaimOutput, "description": "Same-ID replay"}},
    )
    def supersede_claim(
        claim_id: UUID, body: SupersedeInput, response: Response, owner: str = Depends(current_user)
    ):
        result, created = memory.supersede(owner, str(claim_id), body)
        response.status_code = 201 if created else 200
        return result

    return app
