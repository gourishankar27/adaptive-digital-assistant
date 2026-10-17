"""Password/session HTTP boundary. Browser secrets never enter response JSON."""

import asyncio
import json
import threading
from http.cookies import CookieError, SimpleCookie
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import JSONResponse

from ada.errors import ServiceError
from ada.memory import Timestamp
from ada.passwords import normalize_login, validate_password

ACCESS = "__Host-ada-access"
REFRESH = "__Host-ada-refresh"
PUBLIC = frozenset(
    {"/v1/auth/login", "/v1/auth/refresh", "/v1/auth/browser/login", "/v1/auth/browser/refresh"}
)


def cookies(scope):
    headers = scope.get("headers", [])
    values = [v.decode("latin1") for k, v in headers if k.lower() == b"cookie"]
    raw = "; ".join(values)
    if (
        len(raw) > 8192
        or sum(part.strip().startswith(ACCESS + "=") for part in raw.split(";")) > 1
        or sum(part.strip().startswith(REFRESH + "=") for part in raw.split(";")) > 1
    ):
        raise ServiceError(401, "invalid_token")
    result = SimpleCookie()
    try:
        result.load(raw)
    except CookieError:
        raise ServiceError(401, "invalid_token") from None
    return {key: value.value for key, value in result.items()}


def browser_check(scope, settings, *, write=True):
    headers = dict(scope.get("headers", []))
    expected = settings.browser_origin
    host = headers.get(b"host", b"").decode("latin1")
    if not expected or host != urlsplit(expected).netloc:
        raise ServiceError(403, "browser_origin_required")
    if write and (
        headers.get(b"origin", b"").decode("latin1") != expected
        or headers.get(b"x-ada-csrf") != b"1"
    ):
        raise ServiceError(403, "browser_origin_required")


def set_cookies(response, result, settings):
    response.headers["X-ADA-Access-Expires-At"] = str(result["access_expires_at"])
    for name, secret, lifetime in (
        (ACCESS, result["access_token"], settings.session_access_seconds),
        (REFRESH, result["refresh_token"], settings.session_absolute_seconds),
    ):
        response.set_cookie(
            name, secret, max_age=lifetime, path="/", secure=True, httponly=True, samesite="strict"
        )


def clear_cookies(response):
    for name in (ACCESS, REFRESH):
        response.delete_cookie(name, path="/", secure=True, httponly=True, samesite="strict")


class PreAuthBoundary:
    def __init__(self, service):
        self.service = service
        self.slots = threading.BoundedSemaphore(16)

    async def dispatch(self, app, scope, receive, send):
        if not self.slots.acquire(False):
            await JSONResponse(
                {"detail": "authentication_busy"},
                503,
                headers={"Cache-Control": "no-store", "Retry-After": "3"},
            )(scope, receive, send)
            return
        try:
            ip = (scope.get("client") or ("unknown", 0))[0]
            # Ignore forwarding headers entirely; proxy aggregation is conservative.
            self.service.admit(ip)
            raw = scope.get("headers", [])
            headers = dict(raw)
            if b"authorization" in headers:
                raise ServiceError(401, "conflicting_credentials")
            for name in (
                b"content-length",
                b"content-type",
                b"content-encoding",
                b"origin",
                b"x-ada-csrf",
            ):
                if sum(k == name for k, _ in raw) > 1:
                    raise ServiceError(400, "ambiguous_request_headers")
            if headers.get(b"content-encoding", b"identity").lower() != b"identity":
                raise ServiceError(415, "unsupported_content_encoding")
            try:
                length = int(headers.get(b"content-length", b"0"))
            except ValueError:
                raise ServiceError(400, "invalid_content_length") from None
            if length < 0 or length > 8192:
                raise ServiceError(413, "request_too_large")
            body = bytearray()
            try:
                async with asyncio.timeout(5):
                    while True:
                        message = await receive()
                        if message["type"] != "http.request":
                            return
                        body.extend(message.get("body", b""))
                        if len(body) > 8192:
                            raise ServiceError(413, "request_too_large")
                        if not message.get("more_body"):
                            break
            except TimeoutError:
                raise ServiceError(408, "request_body_timeout") from None
            try:
                data = json.loads(body)
                identifier = data.get("username", "") if isinstance(data, dict) else ""
                if not isinstance(identifier, str) or len(identifier) > 160:
                    identifier = ""
                try:
                    identifier = normalize_login(identifier)
                except ValueError:
                    identifier = ""
            except (ValueError, UnicodeError, RecursionError):
                raise ServiceError(400, "invalid_authentication_input") from None
            if scope["path"].endswith("/login"):
                self.service.admit(ip, identifier)
            if "/browser/" in scope["path"]:
                browser_check(scope, self.service.settings)
            sent = False

            async def replay():
                nonlocal sent
                if not sent:
                    sent = True
                    return {"type": "http.request", "body": bytes(body)}
                return await receive()

            async def no_store(message):
                if message["type"] == "http.response.start":
                    message = {
                        **message,
                        "headers": [*message.get("headers", []), (b"cache-control", b"no-store")],
                    }
                await send(message)

            await app(scope, replay, no_store)
        except ServiceError as exc:
            await JSONResponse(
                {"detail": exc.code},
                exc.status,
                headers={
                    "Cache-Control": "no-store",
                    "Retry-After": "60" if exc.status == 429 else "3",
                },
            )(scope, receive, send)
        finally:
            self.slots.release()


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=1, max_length=1024, repr=False)


class RefreshInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str = Field(min_length=1, max_length=200, repr=False)


class PasswordChangeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = Field(min_length=1, max_length=1024, repr=False)
    new_password: str = Field(min_length=15, max_length=1024, repr=False)


class SessionOutput(BaseModel):
    access_token: str = Field(repr=False)
    refresh_token: str = Field(repr=False)
    session_id: UUID
    access_expires_at: Timestamp
    expires_at: Timestamp


class SessionMetadata(BaseModel):
    id: UUID
    label: str
    created_at: Timestamp
    expires_at: Timestamp
    revoked_at: Timestamp | None


class AuthAcknowledgement(BaseModel):
    status: str


def login_router(service, current_user, errors):
    router = APIRouter(prefix="/v1/auth", tags=["password sessions"])
    private = Depends(current_user)
    failures = errors(400, 401, 403, 404, 422, 429, 503)

    @router.post("/login", response_model=SessionOutput, responses=failures)
    def login(body: LoginInput):
        return service.login(body.username, body.password)

    @router.post("/refresh", response_model=SessionOutput, responses=failures)
    def refresh(body: RefreshInput):
        return service.refresh(body.refresh_token)

    @router.post("/browser/login", response_model=AuthAcknowledgement, responses=failures)
    def browser_login(body: LoginInput, response: Response):
        result = service.login(body.username, body.password, "Admin browser")
        set_cookies(response, result, service.settings)
        return {"status": "authenticated"}

    @router.post("/browser/refresh", response_model=AuthAcknowledgement, responses=failures)
    def browser_refresh(request: Request, response: Response):
        token = cookies(request.scope).get(REFRESH)
        if not token:
            raise ServiceError(401, "invalid_login")
        result = service.refresh(token)
        set_cookies(response, result, service.settings)
        return {"status": "authenticated"}

    @router.get("/sessions", response_model=list[SessionMetadata], responses=failures)
    def sessions(owner: str = private):
        return service.list(owner)

    @router.post("/logout", response_model=AuthAcknowledgement, responses=failures)
    def logout(request: Request, response: Response, owner: str = private):
        family = request.scope["ada.principal"].session_id
        if family:
            service.revoke(owner, family)
            request.scope["ada.self_revoked"] = True
        clear_cookies(response)
        return {"status": "signed_out"}

    @router.post("/logout-all", response_model=AuthAcknowledgement, responses=failures)
    def logout_all(request: Request, response: Response, owner: str = private):
        service.revoke(owner)
        request.scope["ada.self_revoked"] = True
        clear_cookies(response)
        return {"status": "signed_out"}

    @router.post(
        "/sessions/{session_id}/revoke", response_model=AuthAcknowledgement, responses=failures
    )
    def revoke(session_id: UUID, request: Request, owner: str = private):
        service.revoke(owner, str(session_id))
        request.scope["ada.self_revoked"] = request.scope["ada.principal"].session_id == str(
            session_id
        )
        return {"status": "revoked"}

    @router.post("/password", response_model=AuthAcknowledgement, responses=failures)
    def password(
        body: PasswordChangeInput, request: Request, response: Response, owner: str = private
    ):
        service.admit((request.scope.get("client") or ("unknown", 0))[0])
        service.admit("", owner)
        try:
            validate_password(body.new_password)
        except ValueError:
            raise ServiceError(422, "invalid_password") from None
        service.change_password(owner, body.current_password, body.new_password)
        request.scope["ada.self_revoked"] = True
        clear_cookies(response)
        return {"status": "password_changed_sign_in_again"}

    return router
