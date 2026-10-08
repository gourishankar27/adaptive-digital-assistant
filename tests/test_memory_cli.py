import json
import sys

from ada.cli import main


def test_cli_memory_roundtrip_and_historical_query(harness, monkeypatch, capsys):
    h = harness
    monkeypatch.setenv("ADA_TOKEN", h["a"]["Authorization"][7:])

    class ApiClient:
        def __init__(self, **kwargs):
            self.headers = kwargs["headers"]

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def request(self, method, path, **kwargs):
            return h["client"].request(method, path, headers=self.headers, **kwargs)

    monkeypatch.setattr("ada.cli_memory.httpx.Client", ApiClient)

    def run(*args):
        monkeypatch.setattr(sys, "argv", ["ada", *args])
        main()
        return json.loads(capsys.readouterr().out)

    scope = run("scopes", "create", "ADA development")
    old = run(
        "memory",
        "remember",
        "--scope",
        scope["id"],
        "--predicate",
        "database",
        "--value",
        "SQLite",
        "--text",
        "We chose SQLite.",
        "--kind",
        "decision",
        "--valid-from",
        "2026-01-01T00:00:00Z",
    )
    new = run(
        "memory",
        "correct",
        old["id"],
        "--value",
        "PostgreSQL",
        "--text",
        "We now use PostgreSQL.",
        "--effective-at",
        "2026-02-01T00:00:00Z",
    )
    assert run("memory", "show", old["id"])["superseded_by"] == new["id"]
    assert (
        run("memory", "list", "--scope", scope["id"], "--at", "2026-01-15T00:00:00Z")[0]["value"]
        == "SQLite"
    )
    assert (
        run("memory", "list", "--scope", scope["id"], "--at", "2026-02-01T00:00:00Z")[0]["value"]
        == "PostgreSQL"
    )
    assert len(run("memory", "list", "--scope", scope["id"], "--history")) == 2
    historical = run(
        "memory", "search", "database", "--scope", scope["id"], "--at", "2026-01-15T00:00:00Z"
    )
    assert historical["selected"][0]["claim_id"] == old["id"]
    current = run("memory", "search", "database", "--scope", scope["id"])
    assert current["selected"][0]["claim_id"] == new["id"]
    assert h["provider"].calls == []
