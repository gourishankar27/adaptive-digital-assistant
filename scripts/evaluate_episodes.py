"""Public synthetic job lifecycle, exact mapping and omission-marker evaluation.

Reports include only this committed synthetic corpus. Marker coverage and exact
spans cannot establish semantic faithfulness; inspect the documented checklist.
"""

import argparse
import json
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from threading import local
from uuid import uuid4

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.engine import make_url

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.consolidation_provider import OllamaConsolidator
from ada.db import connect
from ada.evidence import content_hash
from ada.models import Claim
from ada.providers import Completion, FakeProvider

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def transaction_observer(engine):
    held = local()

    def checkout(*_):
        held.connections = getattr(held, "connections", 0) + 1

    def checkin(*_):
        held.connections = max(0, getattr(held, "connections", 0) - 1)

    event.listen(engine, "checkout", checkout)
    event.listen(engine, "checkin", checkin)
    try:
        yield held
    finally:
        event.remove(engine, "checkout", checkout)
        event.remove(engine, "checkin", checkin)


def run_benchmark(sessions, mode="fixture"):
    settings = Settings(provider="fake", consolidation_worker_enabled=False)
    app = create_app(settings, FakeProvider(), sessions)
    owner, token = create_user(sessions, "Episode-" + uuid4().hex[:12])
    headers = {"Authorization": "Bearer " + token}
    corpus = json.loads((ROOT / "evaluations/episode-summary-v1.json").read_text(encoding="utf-8"))
    outcomes, exact, expected, covered = [], 0, 0, 0
    service = app.state.consolidation
    with transaction_observer(sessions.kw["bind"]) as held, TestClient(app) as client:
        for case in corpus["cases"]:
            scope = client.post(
                "/v1/scopes", headers=headers, json={"name": "Synthetic " + case["key"]}
            ).json()["id"]
            pins, sources = [], []
            for source in case["sources"]:
                if source["origin"] == "imported_document":
                    upload = client.post(
                        f"/v1/scopes/{scope}/documents/uploads/{uuid4()}",
                        headers=headers | {"Content-Type": "text/plain"},
                        params={"source_id": str(uuid4()), "filename": "synthetic.txt"},
                        content=source["text"].encode("utf-8"),
                    )
                    assert upload.status_code == 201
                    version = client.get(
                        f"/v1/document-versions/{upload.json()['source_version_id']}",
                        headers=headers,
                    ).json()
                elif source["origin"] == "model_generated":
                    profile = client.post("/v1/personalities", headers=headers, json={}).json()[
                        "id"
                    ]
                    conv = client.post(
                        "/v1/conversations",
                        headers=headers,
                        json={"personality_id": profile, "scope_id": scope},
                    ).json()["id"]

                    class SourceFixture:
                        id, model = "fixture", "synthetic-source"

                        def complete(self, _):
                            return Completion(source["text"], self.model)

                    app.state.chat.provider = SourceFixture()
                    assert (
                        client.post(
                            f"/v1/conversations/{conv}/messages",
                            headers=headers,
                            json={
                                "request_id": str(uuid4()),
                                "content": "Synthetic generated source",
                            },
                        ).status_code
                        == 200
                    )
                    event = client.get(f"/v1/conversations/{conv}/events", headers=headers).json()[
                        -1
                    ]
                    version = client.get(
                        f"/v1/source-versions/{event['source_version_id']}", headers=headers
                    ).json()
                else:
                    version = client.post(
                        f"/v1/scopes/{scope}/notes",
                        headers=headers,
                        json={"source_id": str(uuid4()), "content": source["text"]},
                    ).json()
                sources.append(version)
                pins.append(
                    {
                        "source_version_id": version["id"],
                        "version": version["version"],
                        "content_hash": version["content_hash"],
                        "span_start": 0,
                        "span_end": len(version["content"]),
                    }
                )
            if mode == "ollama":

                class ObservedOllama(OllamaConsolidator):
                    def complete(self, messages, schema):
                        assert getattr(held, "connections", 0) == 0
                        return super().complete(messages, schema)

                service.provider = ObservedOllama(settings)
            else:

                class Fixture:
                    id, model = "fixture", "explicit-gold-summary-v1"

                    def complete(self, messages, schema):
                        assert getattr(held, "connections", 0) == 0
                        return Completion(
                            json.dumps(
                                {
                                    "sections": [{"text": case["gold"], "support": pins}],
                                    "tags": [case["key"]],
                                    "omissions": [],
                                }
                            ),
                            self.model,
                        )

                service.provider = Fixture()
            key = str(uuid4())
            body = {"job_id": key, "kind": "episode", "sources": pins}
            queued = client.post(
                f"/v1/scopes/{scope}/consolidation-jobs", json=body, headers=headers
            )
            assert queued.status_code == 201 and queued.json()["status"] == "queued"
            # Exercise the actual bounded worker, not a fabricated completion callback.
            service.start()
            deadline = time.monotonic() + 75
            while True:
                result = client.get(f"/v1/consolidation-jobs/{key}", headers=headers).json()
                if result["status"] in ("completed", "failed", "stale"):
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError("Synthetic job lifecycle deadline exceeded")
                time.sleep(0.05)
            service.stop()
            summary = None
            if result["status"] == "completed":
                summary = client.get(
                    f"/v1/episodes/{result['receipt']['episode_id']}", headers=headers
                ).json()
                for section in summary["sections"]:
                    for p in section["support"]:
                        v = next(v for v in sources if v["id"] == p["source_version_id"])
                        assert v["content_hash"] == p["content_hash"] == content_hash(v["content"])
                        assert p["version"] == v["version"] and 0 <= p["span_start"] < p[
                            "span_end"
                        ] <= len(v["content"])
                        exact += 1
                assert summary["trust_class"] == "model_generated"
            output = " ".join(s["text"] for s in summary["sections"]) if summary else ""
            markers = [m for m in case["markers"] if m.lower() in output.lower()]
            covered += len(markers)
            expected += len(case["markers"])
            assert (
                client.post(
                    f"/v1/scopes/{scope}/consolidation-jobs", json=body, headers=headers
                ).json()
                == result
            )
            with sessions() as db:
                assert (
                    db.scalar(
                        select(func.count()).select_from(Claim).where(Claim.owner_id == owner)
                    )
                    == 0
                )
            outcomes.append(
                {
                    "key": case["key"],
                    "status": result["status"],
                    "elapsed_ms": result["elapsed_ms"],
                    "attempt": result["attempt"],
                    "covered_markers": markers,
                    "omitted_markers": [m for m in case["markers"] if m not in markers],
                    "synthetic_sections": summary["sections"] if summary else [],
                    "synthetic_omissions": summary["omissions"] if summary else [],
                    "review_checklist": case["review"],
                }
            )
            print(
                json.dumps(
                    {
                        "case": case["key"],
                        "status": result["status"],
                        "elapsed_ms": result["elapsed_ms"],
                    }
                ),
                flush=True,
            )
    return {
        "corpus": corpus["corpus"],
        "provider": mode,
        "model": service.provider.model,
        "cases": outcomes,
        "completed": sum(x["status"] == "completed" for x in outcomes),
        "exact_support_checks": exact,
        "marker_coverage": covered / expected,
        "endorsed_claims": 0,
        "limits": "Small public synthetic corpus; fixture wording is gold. Exact mapping and lexical marker coverage are not entailment, truth or representative quality. Review uncertainty/attribution/unsupported detail manually.",
    }


def evaluate(output, mode="fixture", postgres=False):
    prior = os.environ.get("ADA_DATABASE_URL")
    admin = engine = schema = None
    with tempfile.TemporaryDirectory(prefix="ada-episodes-eval-") as directory:
        try:
            url = "sqlite:///" + (Path(directory) / "evaluation.db").as_posix()
            if postgres:
                raw = os.environ.get("ADA_TEST_DATABASE_URL")
                if (
                    not raw
                    or make_url(raw).get_backend_name() != "postgresql"
                    or make_url(raw).database != "ada_phase2_test"
                ):
                    raise ValueError(
                        "Use the dedicated ada_phase2_test database for PostgreSQL evaluation"
                    )
                schema = "ada_eval_" + uuid4().hex
                admin = create_engine(raw)
                with admin.begin() as db:
                    db.execute(text(f'CREATE SCHEMA "{schema}"'))
                url = (
                    make_url(raw)
                    .update_query_dict({"options": "-csearch_path=" + schema})
                    .render_as_string(hide_password=False)
                )
            os.environ["ADA_DATABASE_URL"] = url
            command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
            engine, sessions = connect(url)
            report = run_benchmark(sessions, mode)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({k: v for k, v in report.items() if k not in ("cases", "limits")}))
            return report
        finally:
            if engine:
                engine.dispose()
            if admin:
                with admin.begin() as db:
                    db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
                admin.dispose()
            if prior is None:
                os.environ.pop("ADA_DATABASE_URL", None)
            else:
                os.environ["ADA_DATABASE_URL"] = prior


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("fixture", "ollama"), default="fixture")
    parser.add_argument("--postgres", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path(".pytest_cache/episode-evaluation.json")
    )
    args = parser.parse_args()
    evaluate(args.output, args.provider, args.postgres)
