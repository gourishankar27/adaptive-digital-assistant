"""Synthetic Android fixtures stay confined to the explicit disposable helper."""

from uuid import uuid4

from fastapi.testclient import TestClient

from ada.api import create_app
from scripts.client_test_server import AndroidChatProvider, seed_android_chat


def test_fake_android_provider_only_cites_documents_from_selected_context():
    provider = AndroidChatProvider()
    claim = provider.complete([{"role": "user", "content": "Synthetic input"}])
    assert claim.text == "[FAKE provider] Synthetic test reply [M1]."
    imported = provider.complete(
        [{"role": "system", "content": '{"excerpts":[{"label":"D1","quote":"synthetic"}]}'}]
    )
    assert imported.text == "[FAKE provider] Synthetic imported document reply [D1]."


def test_helper_seed_has_owned_evidence_and_completed_replay(harness):
    h = harness
    seed_android_chat(h["sessions"], h["a_id"])
    app = create_app(h["settings"], AndroidChatProvider(), h["sessions"])
    with TestClient(app) as client:
        profiles = client.get("/v1/personalities", headers=h["a"]).json()
        scopes = client.get("/v1/scopes", headers=h["a"]).json()
        scope = next(s for s in scopes if s["name"] == "Android verification")
        conversation = client.post(
            "/v1/conversations",
            headers=h["a"],
            json={"personality_id": profiles[0]["id"], "scope_id": scope["id"]},
        ).json()
        path = f"/v1/conversations/{conversation['id']}/messages"
        payload = {
            "request_id": str(uuid4()),
            "content": "Which color does the Android verification project use?",
        }
        first = client.post(path, headers=h["a"], json=payload)
        assert first.status_code == 200
        result = first.json()
        assert result["status"] == "completed"
        assert result["citations"][0]["label"] == "M1"
        assert "Oxford Blue" in result["citations"][0]["evidence"]["quote"]
        assert client.post(path, headers=h["a"], json=payload).json() == result
        events = client.get(f"/v1/conversations/{conversation['id']}/events", headers=h["a"]).json()
        assert [e["role"] for e in events] == ["user", "assistant"]
        assert (
            client.get(f"/v1/requests/{payload['request_id']}", headers=h["b"]).status_code == 404
        )
        assert client.get("/v1/scopes", headers=h["b"]).json() == []
