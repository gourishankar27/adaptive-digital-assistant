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
    import uvicorn

    from ada.api import create_app
    from ada.host_security import timestamp
    from ada.service import recover_stale

    root = Path(os.environ["LOCALAPPDATA"]) / "ADA/operations"
    if not root.exists():
        private_directory(root)
    with admission_owner(settings, root):
        app = create_app(settings)
        recover_stale(app.state.sessions, timestamp() + 1)
        uvicorn.run(
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
