"""Disposable HTTP fixture only: synthetic resource values and an explicit idle clock."""

import threading

from fastapi import HTTPException, Request

from ada.models import now_ms


def enable_reflection_fixture(app):
    service = app.state.reflection
    offset, lock = [0], threading.Lock()
    service.clock = lambda: now_ms() + offset[0]
    service.resources = lambda: {
        "ac_power": True,
        "disk_free_bytes": 10 * 1024**3,
        "memory_available_percent": 80,
        "thermal_c": 40,
    }
    service.settings.reflection_enabled = True
    service.settings.scheduler_enabled = True
    service.settings.consolidation_worker_enabled = True
    service.settings.reflection_summary_enabled = False
    # Tests exercise real dispatch/leases synchronously, without an autonomous test loop.
    app.state.scheduling.start = lambda: None
    app.state.consolidation.start = lambda: None
    counts = {"reflection_posts": 0}

    @app.middleware("http")
    async def count_mutations(request, call_next):
        if request.method == "POST" and request.url.path.startswith("/v1/reflection/"):
            counts["reflection_posts"] += 1
        return await call_next(request)

    @app.post("/v1/fixture/reflection/run")
    def advance_and_run(request: Request):
        principal = request.scope.get("ada.principal")
        if principal is None or not app.state.security.current(principal):
            raise HTTPException(401, "authentication_required")
        if not app.state.admin.authorize(principal.owner):
            raise HTTPException(403, "admin_required")
        with lock:
            offset[0] += 901000
            queued = service.queue_once()
            ran = service.run_once()
        return {"queued": queued, "ran": ran, **counts, "synthetic_clock": True}

    @app.get("/v1/fixture/reflection/counts")
    def counters(request: Request):
        principal = request.scope.get("ada.principal")
        if principal is None or not app.state.security.current(principal):
            raise HTTPException(401, "authentication_required")
        if not app.state.admin.authorize(principal.owner):
            raise HTTPException(403, "admin_required")
        return counts
