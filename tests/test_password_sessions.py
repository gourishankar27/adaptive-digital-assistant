"""Public synthetic credentials only; exercise real migrated HTTP authorization."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from ada.errors import ServiceError
from ada.models import User
from ada.passwords import normalize_login

PASSWORD = "public synthetic passphrase 123"


def setup(h):
    service = h["app"].state.passwords
    service.set_password(h["a_id"], "Alice", PASSWORD)
    return service


def login(h, username="alice", password=PASSWORD):
    return h["client"].post("/v1/auth/login", json={"username": username, "password": password})


def test_disabled_generic_and_legacy_compatible(harness):
    h = harness
    assert login(h).status_code == 401
    assert login(h, "absent").json() == login(h, password="incorrect").json()
    setup(h)
    result = login(h, "ＡＬＩＣＥ")
    assert result.status_code == 200
    auth = {"Authorization": "Bearer " + result.json()["access_token"]}
    assert h["client"].get("/v1/me", headers=auth).json()["id"] == h["a_id"]
    assert h["client"].get("/v1/admin/me", headers=auth).status_code == 403
    assert h["client"].get("/v1/me", headers=h["a"]).status_code == 200


def test_collision_and_password_policy(harness):
    h = harness
    service = setup(h)
    with pytest.raises(ValueError):
        service.set_password(h["b_id"], "ＡＬＩＣＥ", PASSWORD)
    for password in ("short", "x" * 1025):
        with pytest.raises(ValueError):
            service.set_password(h["b_id"], "bob", password)
    assert normalize_login("  Straße ") == "strasse"
    with h["sessions"]() as db:
        assert db.get(User, h["a_id"]).name == "Alice"


def test_rotation_reuse_reset_and_logout(harness):
    h = harness
    service = setup(h)
    first = login(h).json()
    second = h["client"].post("/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert second.status_code == 200
    auth = {"Authorization": "Bearer " + second.json()["access_token"]}
    assert h["client"].get("/v1/me", headers=auth).status_code == 200
    assert (
        h["client"]
        .post("/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
        .status_code
        == 401
    )
    assert h["client"].get("/v1/me", headers=auth).status_code == 401
    fresh = login(h).json()
    principal = h["app"].state.security.authenticate(fresh["access_token"])
    service.set_password(h["a_id"], "alice", PASSWORD + " changed")
    assert not h["app"].state.security.current(principal)
    assert h["client"].get("/v1/me", headers=h["a"]).status_code == 200
    auth = {
        "Authorization": "Bearer " + login(h, password=PASSWORD + " changed").json()["access_token"]
    }
    assert h["client"].post("/v1/auth/logout", headers=auth).status_code == 200
    assert h["client"].get("/v1/me", headers=auth).status_code == 401


def test_concurrent_refresh_revokes_family(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("requires PostgreSQL row locks")
    service = setup(h)
    token = login(h).json()["refresh_token"]

    def rotate():
        try:
            return service.refresh(token)
        except ServiceError as exc:
            return exc.status

    with ThreadPoolExecutor(2) as pool:
        outcomes = list(pool.map(lambda _: rotate(), range(2)))
    assert sum(isinstance(item, dict) for item in outcomes) == 1
    winner = next(item for item in outcomes if isinstance(item, dict))
    with pytest.raises(ServiceError):
        h["app"].state.security.authenticate(winner["access_token"])


def test_preauth_bounds_and_no_bypass(harness):
    h = harness
    assert h["client"].get("/v1/auth/login").status_code == 401
    assert h["client"].post("/v1/auth/login/extra", json={}).status_code == 401
    assert h["client"].post("/v1/auth/login", content=b"x" * 9000).status_code == 413
    for _ in range(10):
        assert login(h, "absent").status_code == 401
    assert login(h, "absent").status_code == 429
    assert len(h["app"].state.passwords.rates) <= 4096


def test_browser_csrf_and_conflicting_principals(harness):
    h = harness
    setup(h)
    h["settings"].browser_origin = "https://testserver"
    client = h["client"]
    body = {"username": "alice", "password": PASSWORD}
    url = "https://testserver/v1/auth/browser/login"
    assert client.post(url, json=body).status_code == 403
    headers = {"Origin": "https://testserver", "X-ADA-CSRF": "1"}
    response = client.post(url, headers=headers, json=body)
    assert response.status_code == 200
    assert "access_token" not in response.text and "refresh_token" not in response.text
    for cookie in response.headers.get_list("set-cookie"):
        assert "Secure" in cookie and "HttpOnly" in cookie and "SameSite=strict" in cookie
        assert "Domain=" not in cookie and "Path=/" in cookie
    assert client.get("https://testserver/v1/me").status_code == 200
    assert client.get("https://testserver/v1/me", headers=h["b"]).status_code == 401
    assert client.post("https://testserver/v1/auth/logout").status_code == 403
    assert client.post("https://testserver/v1/auth/logout", headers=headers).status_code == 200
    assert client.get("https://testserver/v1/me").status_code == 401


def test_hash_capacity_dummy_rehash_expiry_and_owner_fences(harness, monkeypatch):
    from argon2 import PasswordHasher

    from ada.auth import token_hash
    from ada.login_models import LoginSession, PasswordCredential

    h = harness
    service = setup(h)
    assert service.slots.acquire(False) and service.slots.acquire(False)
    try:
        assert login(h).status_code == 503
    finally:
        service.slots.release()
        service.slots.release()
    old = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1).hash(PASSWORD)
    with h["sessions"].begin() as db:
        db.get(PasswordCredential, h["a_id"]).verifier = old
    credentials = login(h).json()
    with h["sessions"]() as db:
        assert db.get(PasswordCredential, h["a_id"]).verifier != old
        family = db.get(LoginSession, credentials["session_id"])
        assert family.access_hash == token_hash(credentials["access_token"])
    assert (
        h["client"]
        .post(f"/v1/auth/sessions/{credentials['session_id']}/revoke", headers=h["b"])
        .status_code
        == 404
    )
    auth = {"Authorization": "Bearer " + credentials["access_token"]}
    assert (
        h["client"]
        .post(
            "/v1/auth/password",
            headers=auth,
            json={"current_password": "wrong", "new_password": PASSWORD},
        )
        .status_code
        == 401
    )
    with h["sessions"].begin() as db:
        db.get(LoginSession, credentials["session_id"]).idle_expires_at = 0
    assert (
        h["client"]
        .post("/v1/auth/refresh", json={"refresh_token": credentials["refresh_token"]})
        .status_code
        == 401
    )
    assert h["client"].get("/v1/me", headers=auth).status_code == 401


def test_populated_upgrade_preserves_owners_legacy_and_replay(harness):
    from alembic import command
    from conftest import make_conversation, send

    from ada.login_models import PasswordCredential

    h = harness
    conversation, _ = make_conversation(h)
    original = send(h, conversation).json()
    with h["sessions"]() as db:
        digest = db.get(User, h["a_id"]).token_hash
    command.downgrade(h["config"], "0015")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    with h["sessions"]() as db:
        assert db.get(User, h["a_id"]).token_hash == digest
        assert db.get(PasswordCredential, h["a_id"]) is None
    replay = h["client"].get(f"/v1/requests/{original['request_id']}", headers=h["a"])
    assert replay.json() == original


@pytest.mark.parametrize("action", ["logout", "reset", "refresh"])
def test_session_change_blocks_next_sse_batch(harness, action):
    import asyncio

    from ada.security_gate import SecurityMiddleware

    h = harness
    service = setup(h)
    issued = service.login("alice", PASSWORD)
    output = []

    async def endpoint(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/event-stream")],
            }
        )
        await send({"type": "http.response.body", "body": b"event: public\n\n", "more_body": True})
        if action == "logout":
            service.revoke(h["a_id"], issued["session_id"])
        elif action == "reset":
            service.set_password(h["a_id"], "alice", PASSWORD + " reset")
        else:
            service.refresh(issued["refresh_token"])
        await send({"type": "http.response.body", "body": b"private-blocked", "more_body": False})

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        output.append(message)

    middleware = SecurityMiddleware(endpoint, h["app"].state.security, h["app"].state.security_gate)
    scope = {
        "type": "http",
        "path": "/v1/test-stream",
        "method": "GET",
        "headers": [(b"authorization", ("Bearer " + issued["access_token"]).encode())],
    }
    asyncio.run(middleware(scope, receive, send))
    bodies = b"".join(item.get("body", b"") for item in output)
    assert b"private-blocked" not in bodies and b"access_lost" in bodies


def test_revocation_remains_available_during_content_deletion(harness):
    from uuid import uuid4

    h = harness
    service = setup(h)
    issued = service.login("alice", PASSWORD)
    auth = {"Authorization": "Bearer " + issued["access_token"]}
    with h["sessions"].begin() as db:
        user = db.get(User, h["a_id"])
        user.deletion_job_id = str(uuid4())
        revision = user.data_revision
    assert h["client"].get("/v1/me", headers=auth).status_code == 409
    assert h["client"].get("/v1/auth/sessions", headers=auth).status_code == 200
    assert h["client"].post("/v1/auth/logout", headers=auth).status_code == 200
    with h["sessions"]() as db:
        assert db.get(User, h["a_id"]).data_revision == revision


def test_operator_hidden_enrollment_and_metadata_never_print_secrets(harness, monkeypatch, capsys):
    import getpass
    import os
    import sys

    from ada.cli import main

    h = harness
    monkeypatch.setattr(sys, "argv", ["ada", "set-password", h["a_id"], "alice"])
    monkeypatch.setattr(os, "isatty", lambda _: False)
    with pytest.raises(SystemExit):
        main()
    assert login(h).status_code == 401
    monkeypatch.setattr(os, "isatty", lambda _: True)
    monkeypatch.setattr(getpass, "getpass", lambda _: PASSWORD)
    main()
    assert login(h).status_code == 200
    monkeypatch.setattr(sys, "argv", ["ada", "login-accounts"])
    main()
    output = capsys.readouterr().out
    assert PASSWORD not in output and "argon2" not in output and "token_hash" not in output
    assert '"active_device_credentials"' in output and '"password_enabled": true' in output


def test_password_reset_recovers_a_full_session_history(harness):
    from ada.auth import token_hash
    from ada.login_models import LoginSession
    from ada.models import now_ms

    h = harness
    service = setup(h)
    instant = now_ms()
    with h["sessions"].begin() as db:
        for index in range(128):
            db.add(
                LoginSession(
                    owner_id=h["a_id"],
                    label="Synthetic capacity",
                    access_hash=token_hash(str(index)),
                    created_at=instant,
                    access_expires_at=instant + 60000,
                    expires_at=instant + 86400000,
                    idle_expires_at=instant + 60000,
                    generation=0,
                )
            )
    assert login(h).status_code == 429
    service.set_password(h["a_id"], "alice", PASSWORD)
    assert login(h).status_code == 200
    assert len(service.list(h["a_id"])) == 128
