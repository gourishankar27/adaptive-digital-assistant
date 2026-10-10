"""Exercise a Phase 1 -> 2 HTTP upgrade using disposable SQLite and the fake provider."""

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[1]


def child_environment(root, database):
    environment = os.environ.copy()
    environment.update(
        PYTHONPATH=str(root / "src"),
        ADA_DATABASE_URL="sqlite:///" + str(database),
        ADA_PROVIDER="fake",
        ADA_MAX_PARALLEL="1",
    )
    return environment


def migrate(root, database):
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=root,
        env=child_environment(root, database),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def users(root, database):
    code = (
        "import json; from ada.auth import create_user; from ada.db import connect; "
        "from ada.config import Settings; e,s=connect(Settings().database_url); "
        "a=create_user(s,'Smoke Alice'); b=create_user(s,'Smoke Bob'); "
        "print(json.dumps([a[1],b[1]])); e.dispose()"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=root,
        env=child_environment(root, database),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def start(root, database, port):
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "ada.api:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-access-log",
        ],
        cwd=root,
        env=child_environment(root, database),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 20
    with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=1, trust_env=False) as client:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Test API process exited before readiness")
            try:
                if client.get("/health/ready").status_code == 200:
                    return process
            except httpx.RequestError:
                pass
            time.sleep(0.05)
    stop(process)
    raise RuntimeError("Test API readiness timed out")


def stop(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def run(phase1, output):
    if not (phase1 / "src/ada/api.py").is_file():
        raise ValueError("--phase1-root must point to the original Phase 1 source bundle")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, checks = None, []
    with tempfile.TemporaryDirectory(prefix="ada-upgrade-smoke-") as directory:
        database = Path(directory) / "smoke.db"
        try:
            migrate(phase1, database)
            alice, bob = users(phase1, database)
            process = start(phase1, database, port)
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}",
                timeout=5,
                headers={"Authorization": "Bearer " + alice},
                trust_env=False,
            ) as client:

                def post(path, body=None):
                    response = client.post(path, json=body)
                    response.raise_for_status()
                    return response.json()

                def get(path):
                    response = client.get(path)
                    response.raise_for_status()
                    return response.json()

                profile = post("/v1/personalities", {"style": "direct"})
                conversation = post("/v1/conversations", {"personality_id": profile["id"]})
                c, s = conversation["id"], conversation["scope_id"]
                path = f"/v1/conversations/{c}/messages"
                old_body = {"request_id": str(uuid4()), "content": "Hello ADA"}
                old_reply = post(path, old_body)
                old_events = get(f"/v1/conversations/{c}/events")
                source = post(
                    f"/v1/scopes/{s}/notes",
                    {"source_id": str(uuid4()), "content": "I prefer Python."},
                )
                claim = post(
                    f"/v1/scopes/{s}/claims",
                    {
                        "claim_id": str(uuid4()),
                        "subject": "user",
                        "predicate": "preferred_language",
                        "value": "Python",
                        "kind": "preference",
                        "valid_from": "2025-01-01T00:00:00Z",
                        "source_version_id": source["id"],
                        "span_start": 0,
                        "span_end": len(source["content"]),
                    },
                )
                assert get("/health/ready")["schema"] == "0002"
                stop(process)
                migrate(ROOT, database)
                process = start(ROOT, database, port)
                from ada.schema import SCHEMA_HEAD

                assert get("/health/ready")["schema"] == SCHEMA_HEAD
                assert get(f"/v1/claims/{claim['id']}") == claim
                assert get(f"/v1/conversations/{c}")["prompt_version"] == "ada-baseline-v2"
                assert get(f"/v1/conversations/{c}/events") == old_events
                assert post(path, old_body)["response"] == old_reply["response"]
                assert (
                    client.get(f"/v1/requests/{old_body['request_id']}/retrieval").status_code
                    == 404
                )
                checks.append(
                    "populated_phase1_migration_preserves_claims_prompt_events_and_replay"
                )
                legacy = post(
                    path, {"request_id": str(uuid4()), "content": "My preferred language?"}
                )
                trace = get(f"/v1/requests/{legacy['request_id']}/retrieval")
                assert (
                    trace["plan"]["reason"] == "prompt_upgrade_required" and trace["selected"] == []
                )
                post(f"/v1/conversations/{c}/prompt-upgrade")
                upgraded = get(f"/v1/conversations/{c}")
                assert (
                    upgraded["prompt_version"] == "ada-baseline-v4"
                    and upgraded["personality"]["style"] == "direct"
                )
                checks.append("explicit_v4_upgrade_preserves_personality")
                # The fake provider echoes the test label. This verifies HTTP
                # citation mapping, not natural-language answer correctness.
                body = {"request_id": str(uuid4()), "content": "Which language do I prefer? [M1]"}
                reply = post(path, body)
                frozen = get(f"/v1/requests/{body['request_id']}/retrieval")
                assert reply["citations"][0]["claim_id"] == claim["id"]
                assert frozen["selected"][0]["evidence"]["quote"] == source["content"]
                checks.append("retrieval_and_citation_snapshot_saved_over_http")
                new_source = post(
                    f"/v1/scopes/{s}/notes",
                    {"source_id": str(uuid4()), "content": "I prefer Java."},
                )
                replacement = post(
                    f"/v1/claims/{claim['id']}/supersede",
                    {
                        "claim_id": str(uuid4()),
                        "value": "Java",
                        "effective_at": "2025-06-01T00:00:00Z",
                        "source_version_id": new_source["id"],
                        "span_start": 0,
                        "span_end": len(new_source["content"]),
                    },
                )
                event_count = len(get(f"/v1/conversations/{c}/events"))
                stop(process)
                process = start(ROOT, database, port)
                assert post(path, body) == reply
                assert get(f"/v1/requests/{body['request_id']}/retrieval") == frozen
                assert len(get(f"/v1/conversations/{c}/events")) == event_count
                now = post(f"/v1/scopes/{s}/retrieve", {"query": "preferred language"})
                then = post(
                    f"/v1/scopes/{s}/retrieve",
                    {"query": "preferred language", "as_of": "2025-05-01T00:00:00Z"},
                )
                assert now["selected"][0]["claim_id"] == replacement["id"]
                assert then["selected"][0]["claim_id"] == claim["id"]
                checks.append(
                    "restart_replay_keeps_old_citations_while_new_search_observes_correction"
                )
                private_path = f"/v1/requests/{body['request_id']}/retrieval"
                assert (
                    client.get(private_path, headers={"Authorization": "Bearer " + bob}).status_code
                    == 404
                )
                assert client.get(private_path, headers={"Authorization": ""}).status_code == 401
                checks.append("private_trace_authentication_and_owner_isolation")
        finally:
            stop(process)
    report = {
        "status": "passed",
        "backend": "sqlite",
        "provider": "fake",
        "from_schema": "0002",
        "to_schema": "0005",
        "checks": checks,
        "real_llm_tested": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1-root", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluations/http-upgrade-smoke.json")
    args = parser.parse_args()
    run(args.phase1_root.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
