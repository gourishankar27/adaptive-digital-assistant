"""Execute the explicit alias corpus through owned HTTP on both fixture databases."""

import json
from pathlib import Path
from uuid import uuid4

from test_entities import entity
from test_memory import note, proposal

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_alias_corpus(harness):
    h = harness
    corpus = json.loads((ROOT / "evaluations/entity-aliases-v1.json").read_text(encoding="utf-8"))
    scopes = {}
    for key, who in (("main", "a"), ("other", "a"), ("bob", "b")):
        scopes[key] = (
            h["client"]
            .post("/v1/scopes", headers=h[who], json={"name": "Synthetic " + key})
            .json()["id"]
        )
    claims = {}
    for item in corpus["entities"]:
        key = item.get("scope", "main")
        who = "b" if key == "bob" else "a"
        sid = scopes[key]
        eid = entity(h, sid, item["label"], item["kind"], who).json()["entity"]["id"]
        for label in item["aliases"]:
            response = h["client"].post(
                f"/v1/entities/{eid}/aliases",
                headers=h[who],
                json={"operation_id": str(uuid4()), "alias_id": str(uuid4()), "label": label},
            )
            assert response.status_code == 201
        source = note(h, sid, item["text"], who=who)
        response = h["client"].post(
            f"/v1/scopes/{sid}/claims",
            headers=h[who],
            json=proposal(
                source,
                subject=item["label"],
                predicate="synthetic_setting",
                value="recorded",
                subject_entity_id=eid,
            ),
        )
        assert response.status_code == 201
        claims[item["key"]] = response.json()
        if item.get("self"):
            assert (
                h["client"]
                .post(
                    f"/v1/scopes/{sid}/entities/self",
                    headers=h[who],
                    json={"operation_id": str(uuid4()), "entity_id": eid},
                )
                .status_code
                == 201
            )
    lookup = {row["id"]: key for key, row in claims.items()}
    details = []
    for case in corpus["queries"]:
        response = h["client"].post(
            f"/v1/scopes/{scopes['main']}/retrieve", headers=h["a"], json={"query": case["query"]}
        )
        assert response.status_code == 200
        result = response.json()
        actual = [lookup[r["claim_id"]] for r in result["selected"]]
        assert set(actual) == set(case["expected"])
        resolutions = result["plan"]["entity_resolution"]
        assert (resolutions[0]["state"] if resolutions else "absent") == case["state"]
        for card in result["selected"]:
            assert card["scope_id"] == scopes["main"]
            assert card["evidence"] == claims[lookup[card["claim_id"]]]["evidence"]
        details.append({"query": case["query"], "selected_keys": actual, "state": case["state"]})
    output = ROOT / ".pytest_cache" / f"entity-evaluation-{h['backend']}.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "version": corpus["version"],
                "backend": h["backend"],
                "cases_passed": len(details),
                "scope_violations": 0,
                "exact_evidence_failures": 0,
                "false_resolutions": 0,
                "limitations": corpus["provenance"],
                "cases": details,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
