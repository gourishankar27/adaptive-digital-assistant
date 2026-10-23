"""Synthetic source→proposal→explicit review benchmark; real/stub reports stay separate."""

import argparse
import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from ada.api import create_app
from ada.auth import create_user
from ada.config import Settings
from ada.db import connect
from ada.extraction import OllamaExtractor
from ada.providers import Completion, FakeProvider

ROOT = Path(__file__).resolve().parents[1]


def run_benchmark(sessions, mode="fixture", limit=None):
    # A standalone synchronous corpus must not race unrelated background DB work
    # with its assertion that the provider holds no checked-out transaction.
    settings = Settings(
        provider="fake",
        consolidation_worker_enabled=False,
        scheduler_enabled=False,
        web_research_enabled=False,
        pdf_ingestion_enabled=False,
        edge_draft_sync_enabled=False,
    )
    app = create_app(settings, FakeProvider(), sessions)
    owner, token = create_user(sessions, "Extraction-" + uuid4().hex[:12])
    headers = {"Authorization": "Bearer " + token}
    cases = json.loads(
        (ROOT / "evaluations/memory-extraction-v1.json").read_text(encoding="utf-8")
    )["cases"]
    if limit is not None:
        cases = cases[:limit]
    matched = proposed = expected = exact = reviewed = failures = edits = 0
    outcomes = []
    with TestClient(app) as client:
        for case in cases:
            scope = client.post(
                "/v1/scopes", headers=headers, json={"name": "Synthetic " + case["key"]}
            ).json()["id"]
            if case["origin"] == "imported_document":
                upload = client.post(
                    f"/v1/scopes/{scope}/documents/uploads/{uuid4()}",
                    headers=headers | {"Content-Type": "text/plain"},
                    params={"source_id": str(uuid4()), "filename": "synthetic.txt"},
                    content=case["text"].encode("utf-8"),
                )
                assert upload.status_code == 201
                source = client.get(
                    f"/v1/document-versions/{upload.json()['source_version_id']}", headers=headers
                ).json()
            elif case["origin"] == "model_generated":
                personality = client.post("/v1/personalities", headers=headers, json={}).json()[
                    "id"
                ]
                conv = client.post(
                    "/v1/conversations",
                    headers=headers,
                    json={"scope_id": scope, "personality_id": personality},
                ).json()["id"]
                app.state.chat.provider = type(
                    "SyntheticSource",
                    (),
                    {
                        "id": "fixture",
                        "model": "synthetic",
                        "complete": lambda self, messages: Completion(case["text"], self.model),
                    },
                )()
                assert (
                    client.post(
                        f"/v1/conversations/{conv}/messages",
                        headers=headers,
                        json={"request_id": str(uuid4()), "content": "Synthetic source generation"},
                    ).status_code
                    == 200
                )
                event = client.get(f"/v1/conversations/{conv}/events", headers=headers).json()[-1]
                source = client.get(
                    f"/v1/source-versions/{event['source_version_id']}", headers=headers
                ).json()
            else:
                source = client.post(
                    f"/v1/scopes/{scope}/notes",
                    headers=headers,
                    json={"source_id": str(uuid4()), "content": case["text"]},
                ).json()
            pin = {
                "source_version_id": source["id"],
                "version": source["version"],
                "content_hash": source["content_hash"],
                "span_start": 0,
                "span_end": len(source["content"]),
            }
            if mode == "ollama":
                app.state.proposals.provider = OllamaExtractor(settings)
            else:

                class Fixture:
                    model = "explicit-gold-fixture-v1"

                    def complete(self, messages):
                        assert sessions.kw["bind"].pool.checkedout() == 0
                        return Completion(
                            json.dumps(
                                {
                                    "candidates": [
                                        {
                                            "subject": x[0],
                                            "predicate": x[1],
                                            "value": x[2],
                                            "kind": x[3],
                                            "support": [pin],
                                        }
                                        for x in case["expected"]
                                    ]
                                }
                            ),
                            self.model,
                        )

                app.state.proposals.provider = Fixture()
            job = client.post(
                f"/v1/scopes/{scope}/memory-extractions",
                headers=headers,
                json={"extraction_id": str(uuid4()), "sources": [pin]},
            )
            assert job.status_code == 201, "Synthetic extraction HTTP failure"
            receipt = job.json()
            expected += len(case["expected"])
            failures += receipt["state"] != "completed"
            case_matches = 0
            annotations = []
            for ordinal, key in enumerate(receipt["proposal_ids"]):
                p = client.get(f"/v1/memory-proposals/{key}", headers=headers).json()
                c = p["candidate"]
                annotations.append([c[k] for k in ("subject", "predicate", "value", "kind")])
                proposed += 1
                good = [c[k] for k in ("subject", "predicate", "value", "kind")] in case["expected"]
                matched += good
                case_matches += good
                for evidence in p["support"]:
                    e = evidence["evidence"]
                    assert (
                        e["source_version_id"] == source["id"]
                        and e["content_hash"] == source["content_hash"]
                    )
                    assert source["content"][e["span_start"] : e["span_end"]] == e["quote"]
                    exact += 1
                # The fixture user independently inspects exact expected fields; no model approves itself.
                decision = "accept" if good else "reject"
                if mode == "ollama" and not good and case["expected"] and ordinal == 0:
                    # Independent synthetic reviewer edits to the corpus's known annotation,
                    # then inspects the returned exact revision before explicit endorsement.
                    gold = case["expected"][0]
                    final = c | dict(zip(("subject", "predicate", "value", "kind"), gold))
                    changed = client.post(
                        f"/v1/memory-proposals/{key}/edit",
                        headers=headers,
                        json={
                            "revision": p["revision"],
                            "review_hash": p["review_hash"],
                            "candidate": final,
                        },
                    )
                    assert changed.status_code == 200
                    p, c = changed.json(), changed.json()["candidate"]
                    decision = "accept"
                    edits += 1
                reviewed_receipt = client.post(
                    f"/v1/memory-proposals/{key}/review",
                    headers=headers,
                    json={
                        "review_id": str(uuid4()),
                        "revision": p["revision"],
                        "review_hash": p["review_hash"],
                        "candidate": c,
                        "decision": decision,
                        "annotation": "Synthetic benchmark user decision.",
                    },
                )
                assert reviewed_receipt.status_code == 201
                reviewed += decision == "accept"
            outcomes.append(
                {
                    "key": case["key"],
                    "state": receipt["state"],
                    "error_code": receipt["error_code"],
                    "proposed": len(receipt["proposal_ids"]),
                    "matches": case_matches,
                    "synthetic_annotations": annotations,
                }
            )
            print(
                json.dumps(
                    {
                        "case": case["key"],
                        "state": receipt["state"],
                        "proposals": len(receipt["proposal_ids"]),
                    }
                ),
                flush=True,
            )
    return {
        "corpus": "synthetic-selected-sources-v1",
        "provider": mode,
        "model": settings.ollama_model if mode == "ollama" else "explicit-gold-fixture-v1",
        "cases": outcomes,
        "precision": matched / proposed if proposed else None,
        "recall": matched / expected if expected else None,
        "proposals": proposed,
        "exact_evidence_checks": exact,
        "explicitly_reviewed_claims": reviewed,
        "explicit_review_edits": edits,
        "extraction_failures": failures,
        "limits": "Small synthetic corpus, strict gold strings; fixture quality is tautological. Real paraphrases/entailment and representative authorized data require manual evaluation.",
    }


def evaluate(output, mode="fixture", limit=None):
    previous = os.environ.get("ADA_DATABASE_URL")
    engine = None
    with tempfile.TemporaryDirectory(prefix="ada-extraction-eval-") as directory:
        try:
            url = "sqlite:///" + (Path(directory) / "evaluation.db").as_posix()
            os.environ["ADA_DATABASE_URL"] = url
            command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
            engine, sessions = connect(url)
            report = run_benchmark(sessions, mode, limit)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(
                json.dumps(
                    {k: v for k, v in report.items() if k not in ("cases", "limits")}, indent=2
                )
            )
            return report
        finally:
            if engine:
                engine.dispose()
            if previous is None:
                os.environ.pop("ADA_DATABASE_URL", None)
            else:
                os.environ["ADA_DATABASE_URL"] = previous


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("fixture", "ollama"), default="fixture")
    parser.add_argument("--limit", type=int, choices=range(1, 9))
    parser.add_argument(
        "--output", type=Path, default=Path(".pytest_cache/extraction-evaluation.json")
    )
    args = parser.parse_args()
    evaluate(args.output, args.provider, args.limit)
