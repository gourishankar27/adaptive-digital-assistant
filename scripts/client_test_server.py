"""Test-only loopback ADA server with disposable migrated SQLite and a fake model.

Browser/device tests supply an ephemeral ADA_WEB_TEST_TOKEN in their environment.
This helper never loads, migrates, or authenticates against the configured database.
It is not an enrollment service or a production server entry point.
"""

import argparse
import json
import os
import re
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import uvicorn
from alembic import command
from alembic.config import Config

from ada.api import create_app
from ada.auth import token_hash
from ada.config import Settings
from ada.db import connect
from ada.memory import ClaimInput, MemoryService, NoteInput
from ada.models import Personality, Scope, User
from ada.providers import Completion, FakeProvider

ROOT = Path(__file__).resolve().parents[1]


class AndroidChatProvider(FakeProvider):
    """Explicit deterministic UI fixture, never used by the production app."""

    def complete(self, messages):
        if any(
            re.search(r'"label"\s*:\s*"C1"', message.get("content", "")) for message in messages
        ):
            return Completion("[FAKE provider] Synthetic continuity reference [C1].", self.model)
        if any(
            re.search(r'"label"\s*:\s*"D1"', message.get("content", "")) for message in messages
        ):
            return Completion("[FAKE provider] Synthetic imported document reply [D1].", self.model)
        return Completion("[FAKE provider] Synthetic test reply [M1].", self.model)

    def stream(self, messages, cancel):
        if messages[-1]["content"].startswith("Synthetic streaming"):
            text = ""
            for _ in range(60):
                if cancel.wait(0.1):
                    time.sleep(
                        0.3
                    )  # Explicit delayed-shutdown fixture, never production inference.
                    return
                text += "synthetic "
                yield "synthetic "
            text += "reply."
            yield "reply."
            yield Completion(text, self.model, 10, 60)
        else:
            yield from super().stream(messages, cancel)


class AndroidAgentProvider:
    """Native calculator proposals only in the explicitly selected disposable helper."""

    id, model = "fixture", "synthetic-agent-v1"

    def complete(self, messages, tools):
        if messages[-1]["role"] == "tool":
            return {"role": "assistant", "content": "The recorded calculator value is 7."}
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": "calculator", "arguments": {"expression": "3+4"}}}
            ],
        }


class AndroidProposalExtractor(FakeProvider):
    """Explicit deterministic suggestions only in the disposable device helper."""

    model = "synthetic-proposals-v1"

    def complete(self, messages):
        selected = json.loads(messages[-1]["content"])["selected_sources"][0]
        pin = {
            key: selected[key]
            for key in ("source_version_id", "version", "content_hash", "span_start", "span_end")
        }
        return Completion(
            json.dumps(
                {
                    "candidates": [
                        {
                            "subject": "Android verification project",
                            "predicate": "color",
                            "value": "Oxford Blue",
                            "kind": "preference",
                            "support": [pin],
                            "confidence": 0.9,
                        }
                    ]
                }
            ),
            self.model,
        )


class AndroidEpisodeSummarizer:
    """Exact support mapping only in the explicitly selected disposable UI fixture."""

    id, model = "fixture", "synthetic-episode-v1"

    def complete(self, messages, schema):
        selected = json.loads(messages[-1]["content"])["selected_sources"][0]
        pin = {
            key: selected[key]
            for key in ("source_version_id", "version", "content_hash", "span_start", "span_end")
        }
        return Completion(
            json.dumps(
                {
                    "sections": [{"text": "A synthetic navigation summary.", "support": [pin]}],
                    "tags": ["verification"],
                    "omissions": [],
                }
            ),
            self.model,
        )


def seed_android_chat(sessions, owner):
    """Seed synthetic owned evidence only in the helper's disposable database."""
    with sessions.begin() as db:
        db.add(
            Personality(
                owner_id=owner,
                name="ADA Test",
                style="conversational",
                warmth="warm",
                detail="balanced",
            )
        )
        scope = Scope(owner_id=owner, kind="project", name="Android verification")
        db.add(scope)
        db.flush()
        scope_id = scope.id
    memory = MemoryService(sessions)
    text = (
        "The Android verification project uses Oxford Blue.\n" + "Readable evidence. " * 20 + "😀"
    )
    note, _ = memory.note(owner, scope_id, NoteInput(source_id=uuid4(), content=text))
    memory.add(
        owner,
        scope_id,
        ClaimInput(
            claim_id=uuid4(),
            source_version_id=note["id"],
            span_start=0,
            span_end=len(text),
            subject="Android verification project",
            predicate="color",
            value="Oxford Blue",
            valid_from=datetime(2026, 10, 1, tzinfo=UTC),
        ),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=18763)
    parser.add_argument("--android-chat-fixtures", action="store_true")
    parser.add_argument("--workspace-temp", action="store_true")
    parser.add_argument("--security-fixtures", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    credential = os.environ.get("ADA_WEB_TEST_TOKEN", "")
    if not credential or len(credential) > 200:
        parser.error("supply an ephemeral ADA_WEB_TEST_TOKEN (1–200 characters)")

    task_temp = ROOT / ".pytest_cache" / "client-fixtures" if args.workspace_temp else None
    if task_temp is not None:
        task_temp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ada-client-foundations-", dir=task_temp) as directory:
        database_url = "sqlite:///" + (Path(directory) / "client-test.db").as_posix()
        # Alembic reads Settings, so explicitly replace the inherited database URL.
        os.environ["ADA_DATABASE_URL"] = database_url
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        engine, sessions = connect(database_url)
        try:
            with sessions.begin() as db:
                user = User(name="Foundation Test", token_hash=token_hash(credential))
                db.add(user)
                db.flush()
                owner = user.id
            if args.android_chat_fixtures:
                seed_android_chat(sessions, owner)
            settings = Settings(
                database_url=database_url,
                provider="fake",
                max_parallel=1,
                device_enrollment_enabled=args.security_fixtures,
                deletion_worker_enabled=args.security_fixtures,
            )
            provider = AndroidChatProvider() if args.android_chat_fixtures else FakeProvider()
            app = create_app(settings, provider, sessions)
            if args.android_chat_fixtures:
                app.state.proposals.provider = AndroidProposalExtractor()
                app.state.agents.provider = AndroidAgentProvider()
                app.state.consolidation.provider = AndroidEpisodeSummarizer()
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=args.port,
                # UI review pauses exceed the default five-second idle lifetime.
                # Keep fixture sockets alive through a review; production retry policy is unchanged.
                timeout_keep_alive=90,
                workers=1,
                access_log=False,
                log_level="error",
            )
        finally:
            engine.dispose()


if __name__ == "__main__":
    main()
