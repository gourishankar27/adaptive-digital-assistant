"""Browser fixture must never connect to or drop an application schema."""

import pytest
from sqlalchemy.engine import make_url

from scripts.admin_web_test_server import test_database as fixture_database


@pytest.mark.parametrize(
    "schema", ["", "public", "ada_web_test_;DROP SCHEMA public", "ada_test_old"]
)
def test_browser_fixture_rejects_non_disposable_schema(monkeypatch, schema):
    monkeypatch.setenv("ADA_WEB_TEST_SCHEMA", schema)
    with pytest.raises(SystemExit, match="unique disposable"):
        fixture_database()


@pytest.mark.parametrize("database", ["application", "postgres"])
def test_browser_fixture_rejects_explicit_application_database(monkeypatch, database):
    monkeypatch.setenv("ADA_WEB_TEST_SCHEMA", "ada_web_test_" + "a" * 32)
    monkeypatch.setenv("ADA_TEST_DATABASE_URL", f"postgresql+psycopg://localhost/{database}")
    with pytest.raises(SystemExit, match="must name ada_phase2_test"):
        fixture_database()


def test_browser_fixture_uses_dedicated_schema_and_discards_inherited_search_path(monkeypatch):
    monkeypatch.setenv("ADA_WEB_TEST_SCHEMA", "ada_web_test_" + "a" * 32)
    monkeypatch.setenv(
        "ADA_TEST_DATABASE_URL",
        "postgresql+psycopg://localhost/ada_phase2_test?options=-csearch_path%3Dpublic",
    )
    schema, raw, scoped = fixture_database()
    assert raw.database == "ada_phase2_test" and "options" not in raw.query
    assert make_url(scoped).query["options"] == f"-csearch_path={schema}"
