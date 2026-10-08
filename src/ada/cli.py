import argparse
import json
import os
from uuid import uuid4

import httpx
from sqlalchemy.exc import IntegrityError

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
    recover = sub.add_parser("recover-stale")
    recover.add_argument("--older-than-seconds", type=int, default=300)
    chat = sub.add_parser("chat")
    chat.add_argument("--url", default="http://127.0.0.1:8000")
    chat.add_argument("--conversation", help="Resume an existing conversation UUID")
    chat.add_argument("--personality", help="Use an existing personality UUID")
    chat.add_argument("--scope", help="Create a new conversation inside an existing scope UUID")
    chat.add_argument("--title", default="New conversation")
    sub.add_parser("doctor")
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
        if args.command == "create-user":
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
        parser.exit(1, "User name already exists. Use rotate-token if you lost access.\n")
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
        print(f"Conversation: {conversation}\n/quit to leave. /retry resends the last request ID.")
        pending = None
        while True:
            try:
                line = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if line == "/quit":
                break
            if not line:
                continue
            if line != "/retry":
                pending = {"request_id": str(uuid4()), "content": line}
            if pending is None:
                continue
            print("Request:", pending["request_id"])
            try:
                out = post(f"/v1/conversations/{conversation}/messages", pending)
                print("ADA:", out["response"])
            except httpx.HTTPStatusError as exc:
                print("Request failed:", exc.response.status_code, exc.response.text)
            except httpx.RequestError:
                print(
                    "Connection failed. /retry uses the same ID; do not invent a new ID for a retry."
                )


if __name__ == "__main__":
    main()
