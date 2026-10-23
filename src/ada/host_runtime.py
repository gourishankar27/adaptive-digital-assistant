"""Supported one-worker entry point and database-scoped inference ownership gate."""

import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, text

from ada.host_security import HostError, Singleton, acl, private_directory


@contextmanager
def admission_owner(settings, root):
    # Kernel lock spans disconnect/reconnect; PG lock catches other configured profiles.
    acl(root)
    with Singleton(root / "api.lock"):
        engine, connection = None, None
        try:
            engine = create_engine(settings.database_url, connect_args={"connect_timeout": 5})
            connection = engine.connect()
            acquired = connection.execute(
                text("SELECT pg_try_advisory_lock(4277313, 26)")
            ).scalar_one()
            connection.commit()  # Session lock remains; no open transaction during inference.
            if not acquired:
                raise HostError("inference_owner_already_running")
            yield
        except HostError:
            raise
        except Exception:
            raise HostError("database_ownership_gate_unavailable") from None
        finally:
            if connection is not None:
                connection.close()
            if engine is not None:
                engine.dispose()


def foreground(settings, address, port):
    print("[ADA] Loading the API and runtime dependencies...", flush=True)
    import uvicorn

    from ada.api import create_app
    from ada.host_security import timestamp
    from ada.service import recover_stale

    class ForegroundServer(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets=sockets)
            # A lifespan callback alone cannot prove that the socket was bound.
            if self.started:
                host = f"[{address}]" if ":" in address else address
                origin = f"http://{host}:{port}"
                print(f"\nADA API is running at {origin} (one worker).", flush=True)
                print(f"  Readiness: {origin}/health/ready (expect status: ready)", flush=True)
                print(f"  Local API explorer: {origin}/docs", flush=True)
                if settings.browser_origin:
                    print("  With the private proxy and HTTPS route running:", flush=True)
                    print(f"    Admin: {settings.browser_origin}/admin/", flush=True)
                    print(f"    Android server: {settings.browser_origin}", flush=True)
                else:
                    print(
                        "  Phone/password setup: docs/PRIVATE-SETUP-WINDOWS-TAILSCALE.md",
                        flush=True,
                    )
                print("Leave this window open. Press Ctrl+C to stop ADA.\n", flush=True)

    print("[ADA] Checking the protected runtime directory and database ownership...", flush=True)
    root = Path(os.environ["LOCALAPPDATA"]) / "ADA/operations"
    if not root.exists():
        private_directory(root)
    with admission_owner(settings, root):
        print("[ADA] Preparing the application and recovering interrupted requests...", flush=True)
        app = create_app(settings)
        recover_stale(app.state.sessions, timestamp() + 1)
        print("[ADA] Starting the HTTP listener...", flush=True)
        config = uvicorn.Config(
            app,
            host=address,
            port=port,
            workers=1,
            access_log=False,
            proxy_headers=False,
            limit_concurrency=128,
            timeout_keep_alive=5,
            h11_max_incomplete_event_size=16384,
            log_config=None,
        )
        server = ForegroundServer(config)
        try:
            server.run()
        except KeyboardInterrupt:
            pass  # Match uvicorn.run's normal Ctrl+C exit after graceful shutdown.
        finally:
            print("[ADA] API stopped; this window is no longer serving requests.", flush=True)
        if not server.started:
            raise SystemExit(1)
