import argparse
import getpass
import json
import os
from uuid import UUID, uuid4

import httpx
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ada.admin import set_admin_grant
from ada.auth import create_user, rotate_token
from ada.cli_memory import add_arguments, run_remote
from ada.config import Settings
from ada.db import connect
from ada.models import now_ms
from ada.service import recover_stale


def main():
    parser = argparse.ArgumentParser(
        description="ADA administration, text chat and explicit memory"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("create-user", "rotate-token"):
        p = sub.add_parser(name)
        p.add_argument("name")
    for name in ("grant-admin", "revoke-admin"):
        p = sub.add_parser(name, help="Local database operator: change explicit monitoring grant")
        p.add_argument(
            "user_id", type=UUID, help="Exact issued account UUID, never an account name"
        )
    password = sub.add_parser(
        "set-password",
        help="Local operator: assign login/reset password; revoke password sessions only",
    )
    password.add_argument("user_id", type=UUID)
    password.add_argument("login")
    sub.add_parser("login-accounts", help="Local operator: credential metadata, never verifiers")
    recover = sub.add_parser("recover-stale")
    recover.add_argument("--older-than-seconds", type=int, default=300)
    chat = sub.add_parser("chat")
    chat.add_argument("--url", default="http://127.0.0.1:8000")
    chat.add_argument("--conversation", help="Resume an existing conversation UUID")
    chat.add_argument("--personality", help="Use an existing personality UUID")
    chat.add_argument("--scope", help="Create a new conversation inside an existing scope UUID")
    chat.add_argument("--title", default="New conversation")
    chat.add_argument("--at", help="Use a fixed ISO 8601 memory time with timezone")
    chat.add_argument("--no-memory", action="store_true", help="Disable fresh memory retrieval")
    sub.add_parser("doctor")
    sub.add_parser("rebuild-search", help="Rebuild the derived full-text projection locally")
    sub.add_parser(
        "rebuild-document-search", help="Rebuild imported-document lexical projection locally"
    )
    add_arguments(sub)
    args = parser.parse_args()
    settings = Settings()
    if args.command in ("chat", "memory", "scopes", "upgrade-prompt"):
        try:
            if args.command == "chat":
                if args.conversation and (args.scope or args.personality):
                    parser.error("--scope/--personality apply only to new conversations")
                run_chat(args, settings.timeout_seconds)
            else:
                run_remote(args, settings.timeout_seconds)
        except httpx.HTTPStatusError as exc:
            parser.exit(1, f"API error {exc.response.status_code}: {exc.response.text}\n")
        except httpx.RequestError:
            parser.exit(
                1, "Connection failed. Reuse the printed IDs and identical input on retry.\n"
            )
        except ValueError as exc:
            parser.exit(1, f"{exc}\n")
        return
    engine, sessions = connect(settings.database_url)
    try:
        if args.command == "set-password":
            from ada.passwords import PasswordSessions

            if not os.isatty(0):
                parser.exit(1, "Use an interactive terminal for the hidden password prompt.\n")
            first = getpass.getpass("New password (15–1024 characters): ")
            second = getpass.getpass("Repeat password: ")
            if first != second:
                parser.exit(1, "Passwords differ; no change.\n")
            PasswordSessions(sessions, settings).set_password(str(args.user_id), args.login, first)
            print(
                "Password set; password sessions revoked. Legacy/device credentials are unchanged."
            )
        elif args.command == "login-accounts":
            from sqlalchemy import func, select

            from ada.login_models import LoginSession, PasswordCredential
            from ada.models import User
            from ada.security_models import DeviceCredential

            with sessions() as db:
                for user, password in db.execute(
                    select(User, PasswordCredential).outerjoin(
                        PasswordCredential, PasswordCredential.owner_id == User.id
                    )
                ):
                    print(
                        json.dumps(
                            {
                                "owner_id": user.id,
                                "display_name": user.name,
                                "login": password.login if password else None,
                                "password_enabled": bool(password and password.verifier),
                                "legacy_credential_present": True,
                                "active_device_credentials": db.scalar(
                                    select(func.count())
                                    .select_from(DeviceCredential)
                                    .where(
                                        DeviceCredential.owner_id == user.id,
                                        DeviceCredential.revoked_at.is_(None),
                                        DeviceCredential.expires_at > now_ms(),
                                    )
                                ),
                                "active_password_sessions": db.scalar(
                                    select(func.count())
                                    .select_from(LoginSession)
                                    .where(
                                        LoginSession.owner_id == user.id,
                                        LoginSession.revoked_at.is_(None),
                                        LoginSession.expires_at > now_ms(),
                                        LoginSession.idle_expires_at > now_ms(),
                                    )
                                ),
                            }
                        )
                    )
        elif args.command in ("grant-admin", "revoke-admin"):
            print(
                json.dumps(
                    set_admin_grant(sessions, str(args.user_id), args.command == "grant-admin")
                )
            )
        elif args.command == "create-user":
            user_id, token = create_user(sessions, args.name)
            print(
                json.dumps(
                    {
                        "user_id": user_id,
                        "token": token,
                        "note": "Save this secret securely. Only its hash is stored.",
                    },
                    indent=2,
                )
            )
        elif args.command == "rotate-token":
            print(json.dumps({"token": rotate_token(sessions, args.name)}, indent=2))
        elif args.command == "recover-stale":
            if args.older_than_seconds < settings.timeout_seconds + 60:
                parser.error("recovery age must exceed ADA_TIMEOUT_SECONDS by at least 60 seconds")
            n = recover_stale(sessions, now_ms() - args.older_than_seconds * 1000)
            print(f"Marked {n} interrupted requests retryable.")
        elif args.command == "rebuild-search":
            from ada.search import rebuild_search

            print(f"Reindexed {rebuild_search(sessions)} source-backed claims.")
        elif args.command == "rebuild-document-search":
            from ada.documents import rebuild_document_search

            print(f"Reindexed {rebuild_document_search(sessions)} imported-document chunks.")
        else:
            from sqlalchemy import text

            with sessions() as db:
                print(
                    "Database schema:",
                    db.execute(text("SELECT version_num FROM alembic_version")).scalar_one(),
                )
            if settings.provider == "fake":
                print("FAKE provider selected; no LLM will run.")
            else:
                with httpx.Client(
                    base_url=settings.ollama_url, timeout=10, trust_env=False
                ) as client:
                    response = client.get("/api/tags")
                    response.raise_for_status()
                    names = [m["name"] for m in response.json()["models"]]
                    print("Configured model:", settings.ollama_model)
                    print("Installed models:", ", ".join(names))
                    if settings.ollama_model not in names:
                        raise ValueError(
                            "Configured model is not installed. Pull that exact tag first."
                        )
    except IntegrityError:
        if args.command in ("grant-admin", "revoke-admin"):
            parser.exit(1, "Admin operation failed; no grant change was committed.\n")
        parser.exit(1, "User name already exists. Use rotate-token if you lost access.\n")
    except SQLAlchemyError:
        parser.exit(1, "Database operation failed. Check connectivity and schema migration.\n")
    except (ValueError, httpx.HTTPError) as exc:
        parser.exit(1, f"{exc}\n")
    finally:
        engine.dispose()


def run_chat(args, timeout):
    token = os.environ.get("ADA_TOKEN")
    if not token:
        raise SystemExit("Set ADA_TOKEN to your issued bearer token.")
    with httpx.Client(
        base_url=args.url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout + 30,
        trust_env=False,
    ) as client:

        def post(path, body):
            r = client.post(path, json=body)
            r.raise_for_status()
            return r.json()

        conversation = args.conversation
        if not conversation:
            personality = args.personality or post("/v1/personalities", {})["id"]
            body = {"personality_id": personality, "title": args.title}
            if args.scope:
                body["scope_id"] = args.scope
            conversation = post("/v1/conversations", body)["id"]
        response = client.get(f"/v1/conversations/{conversation}")
        response.raise_for_status()
        print("Scope:", response.json()["scope_id"])
        from ada.personality import PROMPT_VERSION, RETRIEVAL_PROMPT_VERSIONS

        if response.json()["prompt_version"] != PROMPT_VERSION:
            if response.json()["prompt_version"] in RETRIEVAL_PROMPT_VERSIONS:
                print(
                    "Claim retrieval remains available. Document retrieval needs an explicit prompt upgrade:"
                )
            else:
                print("Saved prompt needs an explicit upgrade for memory retrieval:")
            print(f"ada upgrade-prompt {conversation}")
        print(
            f"Conversation: {conversation}\n/quit to leave. /retry resends the last request ID. "
            "/sources shows cited evidence. /trace shows retrieval decisions."
        )
        pending = None
        last_out = None
        while True:
            try:
                line = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if line == "/quit":
                break
            if not line:
                continue
            if line == "/sources":
                print(
                    json.dumps((last_out or {}).get("citations", []), ensure_ascii=False, indent=2)
                )
                continue
            if line == "/trace":
                if pending is None:
                    print("Send a message first.")
                    continue
                try:
                    r = client.get(f"/v1/requests/{pending['request_id']}/retrieval")
                    r.raise_for_status()
                    print(json.dumps(r.json(), ensure_ascii=False, indent=2))
                except httpx.HTTPStatusError as exc:
                    print("Trace unavailable:", exc.response.status_code, exc.response.text)
                except httpx.RequestError:
                    print("Connection failed. Try /trace again.")
                continue
            if line != "/retry":
                pending = {"request_id": str(uuid4()), "content": line}
                last_out = None
                if args.at:
                    pending["as_of"] = args.at
                if args.no_memory:
                    pending["use_memory"] = False
            if pending is None:
                continue
            print("Request:", pending["request_id"])
            try:
                out = post(f"/v1/conversations/{conversation}/messages", pending)
                last_out = out
                print("ADA:", out["response"])
                if out.get("citation_warnings"):
                    print("Citation warnings:", ", ".join(out["citation_warnings"]))
            except httpx.HTTPStatusError as exc:
                print("Request failed:", exc.response.status_code, exc.response.text)
            except httpx.RequestError:
                print(
                    "Connection failed. /retry uses the same ID; do not invent a new ID for a retry."
                )


if __name__ == "__main__":
    main()
