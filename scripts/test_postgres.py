"""Run SQLite and PostgreSQL fixtures against a dedicated disposable test database."""

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

from ada.config import Settings

TEST_DATABASE = "ada_phase2_test"


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    url = make_url(Settings().database_url)
    if url.get_backend_name() != "postgresql":
        raise SystemExit("Configure a PostgreSQL ADA_DATABASE_URL before running this script.")
    if url.database == TEST_DATABASE:
        raise SystemExit(
            "The production database name must differ from the dedicated test database."
        )
    engine = create_engine(url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            exists = connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DATABASE}
            )
            if not exists:
                connection.exec_driver_sql('CREATE DATABASE "ada_phase2_test"')
    except SQLAlchemyError:
        raise SystemExit(
            "Could not prepare the test database. Check PostgreSQL connectivity and CREATEDB "
            "permission, or create ada_phase2_test with Docker and set ADA_TEST_DATABASE_URL manually."
        ) from None
    finally:
        engine.dispose()
    environment = os.environ.copy()
    environment["ADA_TEST_DATABASE_URL"] = url.set(database=TEST_DATABASE).render_as_string(
        hide_password=False
    )
    print("Running tests with dedicated PostgreSQL database ada_phase2_test.", flush=True)
    raise SystemExit(
        subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=root, env=environment)
    )


if __name__ == "__main__":
    main()
