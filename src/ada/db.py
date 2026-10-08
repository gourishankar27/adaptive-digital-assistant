from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def connect(url: str):
    engine = create_engine(url, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":
        # SQLite is only a fast test/local smoke backend; deployment uses PostgreSQL.
        @event.listens_for(engine, "connect")
        def sqlite_settings(dbapi_connection, _):
            dbapi_connection.execute("PRAGMA foreign_keys=ON")
            dbapi_connection.execute("PRAGMA busy_timeout=5000")

    return engine, sessionmaker(engine, expire_on_commit=False)
