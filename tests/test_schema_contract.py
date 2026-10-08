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
    assert "CREATE TABLE claims" in sql
    assert "REFERENCES source_versions (owner_id, scope_id, id)" in sql
    assert "encode(sha256(convert_to(e.content, 'UTF8')), 'hex')" in sql


def test_phase1_openapi_describes_evidence_and_64_bit_times(monkeypatch):
    from ada.api import create_app
    from ada.config import Settings
    from ada.providers import FakeProvider

    app = create_app(Settings(provider="fake", database_url="sqlite://"), FakeProvider())
    schema = app.openapi()
    models = schema["components"]["schemas"]
    assert models["ClaimOutput"]["properties"]["valid_from"]["format"] == "int64"
    assert models["SourceVersionOutput"]["properties"]["id"]["format"] == "uuid"
    response = schema["paths"]["/v1/scopes/{scope_id}/claims"]["post"]["responses"]
    assert "200" in response and "201" in response
