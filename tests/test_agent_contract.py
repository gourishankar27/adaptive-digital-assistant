import json

from test_agents import prepared
from test_client_contract import OPENAPI, assert_schema, response_schema


def test_real_agent_http_matches_exported_contract_and_never_exposes_private_reads(harness):
    h = harness
    document = json.loads(OPENAPI.read_text(encoding="utf-8"))
    for path in ("/v1/tools", "/v1/agent-protocols"):
        assert h["client"].get(path).status_code == 401
        result = h["client"].get(path, headers=h["a"])
        assert result.status_code == 200 and result.headers["cache-control"] == "no-store"
        assert_schema(result.json(), response_schema(document, path, "get", 200), document)
    caps = h["client"].get("/v1/capabilities", headers=h["a"]).json()
    assert caps["tools"] is False and caps["agent_tools"] == "unsupported"
    run, approval, route, _ = prepared(h)
    caps = h["client"].get("/v1/capabilities", headers=h["a"]).json()
    assert caps["tools"] is False and caps["agent_tools"] == "approval_read_only_v1"
    assert_schema(run, document["components"]["schemas"]["AgentRunOutput"], document)
    receipt = h["client"].post(route + "/approve", headers=h["a"], json=approval)
    assert receipt.status_code == 201 and receipt.headers["cache-control"] == "no-store"
    assert_schema(receipt.json(), document["components"]["schemas"]["ToolReceiptOutput"], document)
    fetched = h["client"].get(f"/v1/agent-runs/{run['id']}", headers=h["a"])
    assert_schema(fetched.json(), document["components"]["schemas"]["AgentRunOutput"], document)
    assert h["client"].get(f"/v1/agent-runs/{run['id']}").status_code == 401
    assert (
        h["client"].get(f"/v1/tool-receipts/{receipt.json()['id']}", headers=h["b"]).status_code
        == 404
    )
