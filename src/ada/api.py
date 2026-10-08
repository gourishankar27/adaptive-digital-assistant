from contextlib import asynccontextmanager
from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi import Request as HttpRequest
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import case, select, text

from ada.auth import token_hash
from ada.config import Settings
from ada.db import connect
from ada.models import Conversation, Event, Personality, Request, User
from ada.personality import PROMPT_VERSION, build_prompt
from ada.providers import FakeProvider, OllamaProvider
from ada.service import ChatService, ServiceError, public_request


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PersonalityInput(StrictInput):
    name: str = Field(default="ADA", min_length=1, max_length=40, pattern=r"^[\w .-]+$")
    style: Literal["direct", "conversational", "formal"] = "conversational"
    warmth: Literal["reserved", "warm"] = "warm"
    detail: Literal["concise", "balanced", "detailed"] = "balanced"


class ConversationInput(StrictInput):
    personality_id: UUID
    title: str = Field(default="New conversation", min_length=1, max_length=120)


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

    @asynccontextmanager
    async def lifespan(_):
        yield
        if engine is not None:
            engine.dispose()

    app = FastAPI(
        title="ADA",
        version="0.0.1",
        lifespan=lifespan,
        description="Phase 0. Bearer tokens are issued by the local administrator CLI.",
    )
    app.state.sessions, app.state.chat = sessions, service

    @app.exception_handler(ServiceError)
    async def service_error(_: HttpRequest, exc: ServiceError):
        headers = {"Retry-After": "3"} if exc.status == 503 else None
        return JSONResponse(status_code=exc.status, content={"detail": exc.code}, headers=headers)

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
                if version != "0001":
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
            "structured_memory": False,
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
            row = Conversation(
                owner_id=owner,
                personality_id=personality.id,
                title=body.title,
                personality_snapshot=snapshot,
                system_prompt=build_prompt(snapshot),
                prompt_version=PROMPT_VERSION,
            )
            db.add(row)
            db.flush()
            return {
                "id": row.id,
                "title": row.title,
                "scope_id": row.scope_id,
                "personality": snapshot,
                "prompt_version": row.prompt_version,
            }

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
            return [
                {
                    "id": c.id,
                    "title": c.title,
                    "personality": c.personality_snapshot,
                    "revision": c.revision,
                }
                for c in rows
            ]

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

    return app
