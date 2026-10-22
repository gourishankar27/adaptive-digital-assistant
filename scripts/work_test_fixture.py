"""Explicit disposable fixture only: count owned work POSTs without recording payloads."""

from collections import Counter
from threading import Lock

from fastapi import HTTPException, Request


def enable_work_fixture(app):
    counts, lock = Counter(), Lock()

    @app.middleware("http")
    async def count_work(request, call_next):
        response = await call_next(request)
        principal = request.scope.get("ada.principal")
        if (
            principal
            and request.method == "POST"
            and (request.url.path.startswith("/v1/work/") or "/work/" in request.url.path)
        ):
            with lock:
                counts[principal.owner] += 1
        return response

    @app.get("/v1/fixture/work/counts")
    def counters(request: Request):
        principal = request.scope.get("ada.principal")
        if principal is None or not app.state.security.current(principal):
            raise HTTPException(401, "authentication_required")
        with lock:
            return {"work_posts": counts[principal.owner]}
