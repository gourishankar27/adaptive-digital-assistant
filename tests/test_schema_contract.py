import io
from pathlib import Path

from alembic import command
from alembic.config import Config


def test_postgresql_migration_compiles(monkeypatch):
    monkeypatch.setenv("ADA_DATABASE_URL", "postgresql+psycopg://unused/unused")
    output = io.StringIO()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"), output_buffer=output)
    command.upgrade(config, "head", sql=True)
    sql = output.getvalue()
    assert "CREATE UNIQUE INDEX one_running_per_conversation" in sql
    assert "WHERE status = 'running'" in sql
    assert "REFERENCES requests (owner_id, id, conversation_id)" in sql
    assert "CREATE TABLE personalities" in sql
