"""Explicit isolated test-clock adapter, imported only by the disposable fixture."""

import threading

from fastapi import HTTPException, Request

from ada.models import now_ms


def enable_scheduling_fixture(app):
    service = app.state.scheduling
    offset = [0]
    lock = threading.Lock()
    service.clock = lambda: now_ms() + offset[0]
    app.state.curiosity.clock = service.clock

    @app.post("/v1/fixture/scheduling/run")
    def advance_and_run(request: Request):
        principal = request.scope.get("ada.principal")
        if principal is None or not app.state.security.current(principal):
            raise HTTPException(401, "authentication_required")
        if not app.state.admin.authorize(principal.owner):
            raise HTTPException(403, "admin_required")
        with lock:
            offset[0] += 10 * 60000
            service.settings.scheduler_enabled = True
            try:
                iterations = 0
                while iterations < 25 and service.run_once():
                    iterations += 1
            finally:
                service.settings.scheduler_enabled = False
        return {"iterations": iterations, "synthetic_clock": True}
