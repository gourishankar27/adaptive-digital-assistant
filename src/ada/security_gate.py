"""Bounded single-worker HTTP admission and owner-aware content-deletion fencing."""

import asyncio
import collections
import json
import re
import threading
import time
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse

from ada.errors import ServiceError
from ada.login_api import ACCESS, PUBLIC, PreAuthBoundary, browser_check, cookies
from ada.models import Scope, User
from ada.security_models import DeletedRequest


class SecurityGate:
    def __init__(self, settings):
        self.settings = settings
        self._lock = threading.Lock()
        self._active = collections.Counter()
        self._rates = collections.OrderedDict()
        self._owner_rejected = collections.Counter()
        self.rejected = 0

    def active(self, owner):
        with self._lock:
            return self._active[owner]

    def enter(self, owner, write):
        instant = time.monotonic()
        key = (owner, write)
        limit = (
            self.settings.private_write_limit_per_minute
            if write
            else self.settings.private_read_limit_per_minute
        )
        with self._lock:
            start, count = self._rates.get(key, (instant, 0))
            if instant - start >= 60:
                start, count = instant, 0
            if count >= limit:
                self.rejected += 1
                self._owner_rejected[owner] += 1
                raise ServiceError(429, "private_rate_limited")
            if self._active[owner] >= 64 or sum(self._active.values()) >= 128:
                self.rejected += 1
                self._owner_rejected[owner] += 1
                raise ServiceError(503, "owner_operation_capacity_busy")
            self._rates[key] = (start, count + 1)
            self._rates.move_to_end(key)
            if len(self._rates) > 4096:
                removed, _ = self._rates.popitem(last=False)
                if not any(key[0] == removed[0] for key in self._rates):
                    self._owner_rejected.pop(removed[0], None)
            self._active[owner] += 1

    def leave(self, owner):
        with self._lock:
            self._active[owner] -= 1
            if self._active[owner] <= 0:
                del self._active[owner]

    def reset_rates(self):
        with self._lock:
            self._rates.clear()

    def snapshot(self, owner):
        with self._lock:
            return {
                "active_http_operations": self._active[owner],
                "rejected_http_operations": self._owner_rejected[owner],
                "scope": "owner_in_single_process",
                "workers_supported": 1,
            }


class SecurityMiddleware:
    def __init__(self, app, credentials, gate):
        self.app, self.credentials, self.gate = app, credentials, gate
        self.preauth = PreAuthBoundary(credentials.passwords)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope.get("path", "").startswith("/v1/"):
            await self.app(scope, receive, send)
            return
        if scope["method"] == "POST" and scope["path"] in PUBLIC:
            await self.preauth.dispatch(self.app, scope, receive, send)
            return
        principal = None
        entered = False
        response_status = None
        sent_started = False
        overridden = False
        is_stream = False
        write = scope["method"] not in ("GET", "HEAD", "OPTIONS")
        path = scope["path"]
        metadata = path.startswith("/v1/auth/") or (
            re.fullmatch(
                r"/v1/security/(?:status|credentials(?:/[0-9a-fA-F-]{36}/(?:rotate|revoke))?|"
                r"deletion-previews|deletions(?:/[0-9a-fA-F-]{36})?)",
                path,
            )
            is not None
        )
        admin_read = path.startswith("/v1/admin/")
        privacy_epoch = None
        raw_headers = [(key.lower(), value) for key, value in scope.get("headers", [])]
        headers = dict(raw_headers)
        try:
            authorization_count = sum(key == b"authorization" for key, _ in raw_headers)
            cookie = cookies(scope).get(ACCESS)
            if authorization_count and cookie:
                raise ServiceError(401, "conflicting_credentials")
            if cookie:
                browser_check(scope, self.gate.settings, write=write)
                principal = self.credentials.authenticate(cookie)
            elif authorization_count == 0:
                raise ServiceError(401, "authentication_required")
            elif authorization_count != 1:
                raise ServiceError(401, "invalid_token")
            for name in (
                b"content-length",
                b"content-type",
                b"content-encoding",
                b"origin",
                b"x-ada-csrf",
            ):
                if sum(key == name for key, _ in raw_headers) > 1:
                    raise ServiceError(400, "ambiguous_request_headers")
            if principal is None:
                authorization = headers.get(b"authorization", b"").decode("latin1")
                parts = authorization.split()
                if len(parts) != 2 or parts[0].lower() != "bearer":
                    raise ServiceError(401, "authentication_required")
                principal = self.credentials.authenticate(parts[1])
            scope["ada.principal"] = principal
            self.gate.enter(principal.owner, write)
            entered = True
            with self.credentials.sessions() as db:
                if admin_read:
                    privacy_epoch = db.scalar(select(func.coalesce(func.sum(User.data_epoch), 0)))
                pending_deletion = db.scalar(
                    select(User.deletion_job_id).where(User.id == principal.owner)
                )
                if pending_deletion and not metadata:
                    raise ServiceError(409, "private_deletion_pending")
                upload = re.fullmatch(r"/v1/scopes/([^/]+)/documents/uploads/[^/]+", path)
                if upload:
                    try:
                        sid = str(UUID(upload.group(1)))
                    except ValueError:
                        raise ServiceError(404, "scope_not_found") from None
                    if (
                        db.scalar(
                            select(Scope.id).where(
                                Scope.owner_id == principal.owner, Scope.id == sid
                            )
                        )
                        is None
                    ):
                        raise ServiceError(404, "scope_not_found")
                request_path = re.match(r"/v1/requests/([0-9a-fA-F-]{36})(?:/|$)", path)
                request_key = None
                if request_path:
                    try:
                        request_key = str(UUID(request_path.group(1)))
                    except ValueError:
                        pass  # The route validator owns malformed identifiers.
                if (
                    request_key
                    and db.get(DeletedRequest, (principal.owner, request_key)) is not None
                ):
                    raise ServiceError(410, "private_content_deleted")
            maximum = self.gate.settings.private_max_body_bytes
            length = headers.get(b"content-length")
            if length is not None:
                try:
                    declared = int(length)
                except ValueError:
                    raise ServiceError(400, "invalid_content_length") from None
                if declared < 0:
                    raise ServiceError(400, "invalid_content_length")
                if declared > maximum:
                    raise ServiceError(413, "request_too_large")
            if headers.get(b"content-encoding", b"identity").lower() != b"identity":
                raise ServiceError(415, "unsupported_content_encoding")
            messages = []
            body = bytearray()
            try:
                async with asyncio.timeout(15):
                    while True:
                        message = await receive()
                        if message["type"] != "http.request":
                            return
                        body.extend(message.get("body", b""))
                        if len(body) > maximum:
                            raise ServiceError(413, "request_too_large")
                        messages.append(message)
                        if not message.get("more_body", False):
                            break
            except TimeoutError:
                raise ServiceError(408, "request_body_timeout") from None
            if headers.get(b"content-type", b"").startswith(b"application/json"):
                # Bound JSON nesting before the framework parses hostile input.
                depth = 0
                quoted = escaped = False
                for value in body:
                    if quoted:
                        if escaped:
                            escaped = False
                        elif value == 92:
                            escaped = True
                        elif value == 34:
                            quoted = False
                    elif value == 34:
                        quoted = True
                    elif value in (91, 123):
                        depth += 1
                        if depth > 64:
                            raise ServiceError(400, "json_nesting_limit")
                    elif value in (93, 125):
                        depth -= 1
            if write and path.endswith(
                ("/messages", "/stream-requests", "/voice-requests", "/long-voice-requests")
            ):
                try:
                    rid = str(UUID(json.loads(body).get("request_id", "")))
                except (ValueError, UnicodeError, TypeError, AttributeError, RecursionError):
                    rid = None
                if rid:
                    with self.credentials.sessions() as db:
                        if db.get(DeletedRequest, (principal.owner, rid)) is not None:
                            raise ServiceError(410, "private_content_deleted")
            iterator = iter(messages)

            async def replay():
                try:
                    return next(iterator)
                except StopIteration:
                    return await receive()

            async def guarded_send(message):
                nonlocal response_status, overridden, is_stream, sent_started
                if overridden:
                    return
                if message["type"] == "http.response.start":
                    response_status = message["status"]
                    is_stream = any(
                        key.lower() == b"content-type" and value.startswith(b"text/event-stream")
                        for key, value in message.get("headers", [])
                    )
                    chosen = scope.get("ada.replacement_principal", principal)
                    privacy_current = privacy_epoch
                    if admin_read and response_status < 400:
                        with self.credentials.sessions() as db:
                            privacy_current = db.scalar(
                                select(func.coalesce(func.sum(User.data_epoch), 0))
                            )
                    self_revoked = scope.get("ada.self_revoked", False)
                    if not self_revoked and (
                        not self.credentials.current(chosen, check_epoch=not metadata)
                        or privacy_current != privacy_epoch
                    ):
                        overridden = True
                        await JSONResponse(
                            {"detail": "invalid_token"},
                            401,
                            headers={"WWW-Authenticate": "Bearer", "Cache-Control": "no-store"},
                        )(scope, replay, send)
                        return
                    output = [
                        (key, value)
                        for key, value in message.get("headers", [])
                        if key.lower()
                        not in (b"cache-control", b"x-ada-data-epoch", b"x-ada-owner")
                    ]
                    output.extend(
                        [
                            (b"cache-control", b"no-store"),
                            (b"x-ada-data-epoch", str(chosen.epoch).encode()),
                            (b"x-ada-owner", chosen.owner.encode()),
                        ]
                    )
                    if admin_read and response_status < 400:
                        output.append((b"x-ada-privacy-epoch", str(privacy_current).encode()))
                    message = {**message, "headers": output}
                elif (
                    message["type"] == "http.response.body"
                    and is_stream
                    and not self.credentials.current(
                        scope.get("ada.replacement_principal", principal)
                    )
                ):
                    # Stream generators also recheck each batch. Never forward a stale private batch.
                    overridden = True
                    await send(
                        {
                            "type": "http.response.body",
                            "body": b'event: access_lost\ndata: {"detail":"invalid_token"}\n\n',
                            "more_body": False,
                        }
                    )
                    return
                await send(message)
                if message["type"] == "http.response.start":
                    sent_started = True

            if write and not metadata:
                # Reserve revision before dispatch, never after sending a committed result.
                # Even a failed private write attempt conservatively invalidates old previews.
                self.credentials.advance_revision(principal.owner)
            await self.app(scope, replay, guarded_send)
        except ServiceError as exc:
            if not sent_started:
                extra = {"Cache-Control": "no-store"}
                if exc.status == 401:
                    extra["WWW-Authenticate"] = "Bearer"
                if exc.status in (429, 503):
                    extra["Retry-After"] = "60" if exc.status == 429 else "3"
                await JSONResponse({"detail": exc.code}, exc.status, headers=extra)(
                    scope, receive, send
                )
            else:
                raise
        except SQLAlchemyError:
            if not sent_started:
                await JSONResponse(
                    {"detail": "database_not_ready"}, 503, headers={"Cache-Control": "no-store"}
                )(scope, receive, send)
            elif not overridden:
                await send(
                    {
                        "type": "http.response.body",
                        "body": b'event: access_lost\ndata: {"detail":"database_not_ready"}\n\n'
                        if is_stream
                        else b"",
                        "more_body": False,
                    }
                )
        finally:
            if entered:
                self.gate.leave(principal.owner)
