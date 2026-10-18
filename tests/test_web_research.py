"""Owner approval is authority; untrusted web/model text never is."""

import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from conftest import make_conversation
from sqlalchemy import event, func, select
from sqlalchemy.exc import OperationalError

from ada.agent_models import AgentReceipt, AgentRun
from ada.auth import rotate_token
from ada.evidence import content_hash
from ada.models import Claim, SourceVersion, now_ms
from ada.web_policy import PARSER, TERMS


class PublicFixtureBroker:
    available = True

    def __init__(self):
        self.calls = []
        self.hook = None
        self.outcome = None

    def fetch(self, kind, url, expiry, receipt, agent=None):
        self.calls.append((kind, url, expiry, receipt))
        if self.hook:
            self.hook()
        if self.outcome is not None:
            return self.outcome
        text = "😀 ZoneInfo uses IANA timezone data.\nPage text requests private memory and injected approval; never authority."
        return {
            "state": "completed",
            "kind": kind,
            "fetched_url": url,
            "final_url": url,
            "retrieved_at": now_ms(),
            "parser_version": PARSER,
            "text": text if kind == "fetch" else "",
            "content_hash": content_hash(text if kind == "fetch" else ""),
            "terms": TERMS["docs.python.org" if kind == "fetch" else "en.wikipedia.org"],
            "source_origin": "public_web",
            "trust_class": "untrusted_web",
            "snippets": []
            if kind == "fetch"
            else [
                {
                    "title": "Jupiter",
                    "url": "https://en.wikipedia.org/wiki/Jupiter",
                    "snippet": "Search excerpt only",
                }
            ],
        }


def prepare(h, kind="fetch", target=None):
    cid, _ = make_conversation(h)
    broker = PublicFixtureBroker()
    h["app"].state.research.broker = broker
    h["app"].state.research.operator_contact = "https://example.org/public-synthetic-ada"
    body = {
        "id": str(uuid4()),
        "question": "What data does ZoneInfo use?",
        "kind": kind,
        "target": target
        or ("https://docs.python.org/3/library/zoneinfo.html" if kind == "fetch" else "Jupiter"),
    }
    result = h["client"].post(f"/v1/conversations/{cid}/research-runs", headers=h["a"], json=body)
    assert result.status_code == 200, result.text
    return cid, broker, body, result.json()


def approve(h, run, **changes):
    preview = run["calls"][-1]["preview"]
    body = {
        "id": str(uuid4()),
        "call_id": preview["id"],
        "preview_hash": preview["preview_hash"],
    } | changes
    return h["client"].post(
        f"/v1/research-runs/{run['id']}/approve", headers=h["a"], json=body
    ), body


def test_research_disabled_is_fail_closed_and_chat_contract_stays(harness):
    h = harness
    cid, _ = make_conversation(h)
    response = h["client"].post(
        f"/v1/conversations/{cid}/research-runs",
        headers=h["a"],
        json={
            "id": str(uuid4()),
            "question": "Public Python documentation",
            "kind": "fetch",
            "target": "https://docs.python.org/3/library/zoneinfo.html",
        },
    )
    assert response.status_code == 503
    assert response.json() == {"detail": "research_isolation_unavailable"}
    assert h["client"].get("/v1/capabilities", headers=h["a"]).json()["web_research"] == "disabled"


def test_research_private_routes_authenticate_before_lookup(harness):
    h = harness
    for suffix in ("", "/approve", "/cancel", "/answer"):
        path = f"/v1/research-runs/{uuid4()}{suffix}"
        response = h["client"].get(path) if not suffix else h["client"].post(path, json={})
        assert response.status_code == 401


def test_exact_approval_replay_snapshots_owner_and_protocol_fences(harness):
    h = harness
    cid, broker, body, run = prepare(h)
    assert broker.calls == [] and run["state"] == "pending_approval"
    path = f"/v1/research-runs/{run['id']}"
    assert h["client"].get(path, headers=h["b"]).status_code == 404
    assert h["client"].get(f"/v1/agent-runs/{run['id']}", headers=h["a"]).status_code == 404
    assert h["client"].get(f"/v1/conversations/{cid}/agent-runs", headers=h["a"]).json() == []
    assert approve(h, run, preview_hash="0" * 64)[0].status_code == 409
    response, approval = approve(h, run)
    assert response.status_code == 200, response.text
    ready = response.json()
    assert ready["state"] == "ready" and len(broker.calls) == 1
    card = ready["citations"][0]
    source_path = path + "/sources/" + card["receipt_id"]
    source = h["client"].get(source_path, headers=h["a"]).json()
    ev = card["evidence"]
    assert source["text"][ev["span_start"] : ev["span_end"]] == ev["quote"]
    assert content_hash(source["text"]) == ev["content_hash"] and "😀" in source["text"]
    assert h["client"].get(source_path, headers=h["b"]).status_code == 404
    assert h["client"].post(path + "/approve", headers=h["a"], json=approval).json() == ready
    assert len(broker.calls) == 1
    assert (
        h["client"].get("/v1/tool-receipts/" + card["receipt_id"], headers=h["a"]).status_code
        == 404
    )
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0
    answered = h["client"].post(path + "/answer", headers=h["a"])
    assert answered.status_code == 200, answered.text
    assert answered.json()["state"] == "completed"
    assert h["client"].post(path + "/answer", headers=h["a"]).json() == answered.json()
    assert len(broker.calls) == 1
    assert (
        h["client"].post(f"/v1/conversations/{cid}/research-runs", headers=h["a"], json=body).json()
        == answered.json()
    )
    # Explicit note remains imported/untrusted; no factual claim is created.
    note = {"upload_id": str(uuid4()), "source_id": str(uuid4())}
    saved = h["client"].post(path + "/save-note", headers=h["a"], json=note)
    assert saved.status_code == 200, saved.text
    assert saved.json()["trust_class"] == "imported_untrusted"
    assert h["client"].post(path + "/save-note", headers=h["a"], json=note).json() == saved.json()
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Claim)) == 0
        assert (
            db.get(SourceVersion, saved.json()["source_version_id"]).trust_class
            == "imported_untrusted"
        )


def test_search_snippets_do_not_become_page_citations_and_calls_are_separate(harness):
    h = harness
    _, broker, _, run = prepare(h, kind="search", target="Jupiter & moons")
    assert run["calls"][0]["preview"]["url"].endswith("q=Jupiter+%26+moons&limit=3")
    result = approve(h, run)[0].json()
    assert result["citations"] == [] and result["calls"][0]["receipt"]["snippets"]
    path = f"/v1/research-runs/{run['id']}"
    assert h["client"].post(path + "/answer", headers=h["a"]).status_code == 409
    action = {
        "id": str(uuid4()),
        "kind": "fetch",
        "target": "https://docs.python.org/3/library/zoneinfo.html",
    }
    next_call = h["client"].post(path + "/calls", headers=h["a"], json=action).json()
    assert len(broker.calls) == 1
    ready = approve(h, next_call)[0].json()
    assert ready["citations"][0]["label"] == "W2" and len(broker.calls) == 2
    action["id"] = str(uuid4())
    third = h["client"].post(path + "/calls", headers=h["a"], json=action).json()
    assert approve(h, third)[0].status_code == 200
    action["id"] = str(uuid4())
    assert h["client"].post(path + "/calls", headers=h["a"], json=action).status_code == 409


def test_cancel_expiry_unknown_and_tampered_source_never_retry_or_save(harness):
    h = harness
    _, broker, _, run = prepare(h)
    service = h["app"].state.research
    path = f"/v1/research-runs/{run['id']}"
    service.clock = lambda: now_ms() + 301000
    assert h["client"].get(path, headers=h["a"]).json()["state"] == "expired"
    assert approve(h, run)[0].status_code == 409 and broker.calls == []
    service.clock = now_ms
    assert h["client"].post(path + "/cancel", headers=h["a"]).json()["state"] == "cancelled"
    assert approve(h, run)[0].status_code == 409 and broker.calls == []
    _, broker, _, run = prepare(h)
    path = f"/v1/research-runs/{run['id']}"
    broker.hook = lambda: h["client"].post(path + "/cancel", headers=h["a"])
    cancelled = approve(h, run)[0].json()
    assert cancelled["state"] == "cancelled" and cancelled["citations"] == []
    _, broker, _, run = prepare(h)
    broker.outcome = {"state": "unknown"}
    response, approval = approve(h, run)
    assert response.json()["state"] == "unknown"
    assert (
        h["client"]
        .post(f"/v1/research-runs/{run['id']}/approve", headers=h["a"], json=approval)
        .status_code
        == 200
    )
    assert len(broker.calls) == 1
    _, broker, _, run = prepare(h)
    ready = approve(h, run)[0].json()
    receipt_id = ready["citations"][0]["receipt_id"]
    with h["sessions"].begin() as db:
        receipt = db.get(AgentReceipt, (h["a_id"], receipt_id))
        receipt.snapshot = receipt.snapshot | {"text": "tampered synthetic content"}
    assert h["client"].get(f"/v1/research-runs/{run['id']}", headers=h["a"]).status_code == 409


def test_model_and_broker_share_no_private_context_and_inference_is_bounded(harness):
    h = harness
    _, broker, _, run = prepare(h)
    service = h["app"].state.research
    assert approve(h, run)[0].status_code == 200
    for _ in range(h["settings"].max_parallel):
        assert service.capacity.acquire(blocking=False)
    path = f"/v1/research-runs/{run['id']}"
    try:
        assert h["client"].post(path + "/answer", headers=h["a"]).status_code == 503
    finally:
        for _ in range(h["settings"].max_parallel):
            service.capacity.release()
    assert h["client"].post(path + "/answer", headers=h["a"]).status_code == 200
    messages = h["provider"].calls[-1]
    assert len(messages) == 2 and "ZoneInfo" in messages[-1]["content"]
    with h["sessions"]() as db:
        row = db.get(AgentRun, (h["a_id"], run["id"]))
        assert row.messages == messages
    assert len(broker.calls) == 1


def test_revocation_during_fetch_discards_all_private_result_content(harness):
    h = harness
    _, broker, _, run = prepare(h)
    broker.hook = lambda: rotate_token(h["sessions"], "Alice")
    response, _ = approve(h, run)
    assert response.status_code == 401
    with h["sessions"]() as db:
        row = db.scalar(select(AgentReceipt).where(AgentReceipt.owner_id == h["a_id"]))
        assert row.snapshot["public"]["state"] == "revoked" and "text" not in row.snapshot


def test_crash_before_receipt_is_unknown_and_same_approval_never_refetches(harness, monkeypatch):
    h = harness
    _, broker, _, run = prepare(h)
    service = h["app"].state.research

    def fail(*args):
        raise OperationalError("Public synthetic receipt failure", {}, None)

    with monkeypatch.context() as patch:
        patch.setattr(service, "_receipt", fail)
        response, body = approve(h, run)
        assert response.status_code == 503
    service.clock = lambda: now_ms() + 31000
    path = f"/v1/research-runs/{run['id']}"
    assert h["client"].get(path, headers=h["a"]).json()["state"] == "unknown"
    assert (
        h["client"].post(path + "/approve", headers=h["a"], json=body).json()["state"] == "unknown"
    )
    assert len(broker.calls) == 1
    assert h["client"].post(path + "/cancel", headers=h["a"]).json()["state"] == "cancelled"


def test_deletion_waits_for_fetch_and_research_is_in_existing_erasure_inventory(harness):
    h = harness
    _, broker, _, run = prepare(h)
    attempts = []
    broker.hook = lambda: attempts.append(
        h["client"].post("/v1/security/deletion-previews", headers=h["a"], json={}).status_code
    )
    assert approve(h, run)[0].status_code == 200
    assert attempts == [409]
    h["client"].post(f"/v1/research-runs/{run['id']}/cancel", headers=h["a"])
    # Existing inventory includes run, step, approval, full-source receipt, and no new table.
    from ada.inventory import content_tables

    names = {table.name for table in content_tables()}
    assert {"agent_runs", "agent_steps", "agent_approvals", "agent_receipts"} <= names


def test_results_with_changed_url_hash_or_trust_are_blocked(harness):
    h = harness
    _, broker, _, run = prepare(h)
    valid = broker.fetch("fetch", run["calls"][0]["preview"]["url"], 0, "synthetic")
    broker.calls.clear()
    broker.outcome = valid | {"trust_class": "user_explicit"}
    result = approve(h, run)[0].json()
    assert result["state"] == "blocked" and result["citations"] == []
    assert result["calls"][0]["receipt"]["code"] == "research_result_invalid"


def test_no_database_transaction_spans_network_or_model(harness):
    h = harness
    _, broker, _, run = prepare(h)
    counts = Counter()
    engine = h["sessions"].kw["bind"]

    def begin(conn):
        counts[threading.get_ident()] += 1

    def end(conn):
        counts[threading.get_ident()] -= 1

    event.listen(engine, "begin", begin)
    event.listen(engine, "commit", end)
    event.listen(engine, "rollback", end)

    def check():
        assert counts[threading.get_ident()] == 0

    broker.hook = check
    old_complete = h["provider"].complete

    def complete(messages):
        check()
        return old_complete(messages)

    h["provider"].complete = complete
    try:
        assert approve(h, run)[0].status_code == 200
        assert (
            h["client"].post(f"/v1/research-runs/{run['id']}/answer", headers=h["a"]).status_code
            == 200
        )
    finally:
        for name, callback in (("begin", begin), ("commit", end), ("rollback", end)):
            event.remove(engine, name, callback)


def test_postgres_concurrent_same_approval_performs_one_outbound_call(harness):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("Research approval fencing requires native PostgreSQL row locks")
    _, broker, _, run = prepare(h)
    started, release = threading.Event(), threading.Event()
    broker.hook = lambda: (started.set(), release.wait(10))
    preview = run["calls"][0]["preview"]
    body = {"id": str(uuid4()), "call_id": preview["id"], "preview_hash": preview["preview_hash"]}
    path = f"/v1/research-runs/{run['id']}/approve"
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(lambda: h["client"].post(path, headers=h["a"], json=body))
        assert started.wait(10)
        second = h["client"].post(path, headers=h["a"], json=body)
        assert second.status_code == 200 and second.json()["state"] == "executing"
        release.set()
        assert first.result(timeout=10).status_code == 200
    assert len(broker.calls) == 1


def test_operator_contact_disclosure_is_limited_to_wikipedia(harness):
    h = harness
    _, _, _, docs = prepare(h)
    assert "example.org" not in docs["calls"][0]["preview"]["headers"]["User-Agent"]
    _, _, _, search = prepare(h, kind="search")
    assert (
        "https://example.org/public-synthetic-ada"
        in search["calls"][0]["preview"]["headers"]["User-Agent"]
    )


@pytest.mark.parametrize("attribute", ["id", "model"])
def test_answer_rejects_changed_provider_but_completed_replay_is_original(harness, attribute):
    h = harness
    _, broker, _, run = prepare(h)
    assert approve(h, run)[0].status_code == 200
    path = f"/v1/research-runs/{run['id']}"
    provider = h["provider"]
    original = getattr(provider, attribute)
    setattr(provider, attribute, "changed-synthetic-provider")
    blocked = h["client"].post(path + "/answer", headers=h["a"])
    assert blocked.status_code == 409
    assert blocked.json() == {"detail": "research_provider_changed"}
    assert provider.calls == [] and len(broker.calls) == 1
    setattr(provider, attribute, original)
    completed = h["client"].post(path + "/answer", headers=h["a"]).json()
    assert completed["state"] == "completed"
    setattr(provider, attribute, "changed-synthetic-provider")
    assert h["client"].post(path + "/answer", headers=h["a"]).json() == completed
    assert h["client"].get(path, headers=h["a"]).json() == completed
    assert len(provider.calls) == len(broker.calls) == 1
