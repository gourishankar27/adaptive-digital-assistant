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
    assert "CREATE TABLE retrieval_traces" in sql
    assert "USING GIN (to_tsvector('simple'::regconfig, search_text))" in sql
    assert "CREATE TABLE claim_search" in sql


def test_phase2_openapi_describes_evidence_citations_and_64_bit_times(monkeypatch):
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
    assert models["RequestOutput"]["properties"]["request_id"]["format"] == "uuid"
    assert models["CitationOutput"]["properties"]["valid_from"]["format"] == "int64"
    assert "as_of" in models["ChatInput"]["properties"]
    assert "/v1/requests/{request_id}/retrieval" in schema["paths"]
    assert "/v1/scopes/{scope_id}/retrieve" in schema["paths"]


def test_postgresql_retrieval_query_compiles_with_scoped_temporal_predicates():
    from types import SimpleNamespace

    from sqlalchemy.dialects import postgresql

    from ada.retrieval import _base_query, _fts_condition

    dialect = postgresql.dialect()
    db = SimpleNamespace(bind=SimpleNamespace(dialect=dialect))
    query = _base_query("owner", "scope", 123).where(_fts_condition(db, ["python", "language"]))
    compiled = query.compile(dialect=dialect)
    sql = str(compiled)
    assert "@@ to_tsquery('simple'::regconfig" in sql
    assert "claims.owner_id =" in sql and "claims.scope_id =" in sql
    assert "claims.valid_from <=" in sql and "claims.valid_to >" in sql
    assert "'python' | 'language'" in compiled.params.values()
