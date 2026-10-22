"""Review creates generated navigation or an explicitly opened owned question only."""

from uuid import uuid4

from conftest import make_conversation
from sqlalchemy import func, select
from test_curiosity import enabled as curiosity_enabled
from test_reflection import enabled
from test_reflection_failures import summary

from ada.admin import set_admin_grant
from ada.consolidation_models import Episode
from ada.curiosity_models import CuriosityQuestion
from ada.models import Claim, Event


def test_question_draft_does_not_offer_until_explicit_open_and_has_no_user_turn(harness):
    h = harness
    curiosity_enabled(h)
    service, clock, _, _, _ = enabled(h, kinds=["question"])
    assert service.queue_once() and service.run_once()
    items = service.artifacts(h["a_id"])
    assert items[0]["content"]["question"]["source"]["trust_class"] == "user_explicit"
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(CuriosityQuestion)) == 0
    _, personality = make_conversation(h)
    conversation = str(uuid4())
    body = {
        "operation_id": str(uuid4()),
        "action": "open_question",
        "conversation_id": conversation,
        "personality_id": personality,
    }
    path = f"/v1/reflection/artifacts/{items[0]['id']}/actions"
    response = h["client"].post(path, headers=h["a"], json=body)
    assert response.status_code == 200
    assert response.json()["conversation_id"] == conversation
    assert h["client"].post(path, headers=h["a"], json=body).json() == response.json()
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count()).select_from(Event).where(Event.conversation_id == conversation)
            )
            == 0
        )
        assert db.scalar(select(func.count()).select_from(Claim)) == 0
        assert db.scalar(select(func.count()).select_from(CuriosityQuestion)) == 1


def test_keep_summary_reuses_generated_episode_records_and_never_endorses(harness):
    service, _, provider = summary(harness, ignore=True)
    provider.release.set()
    assert service.run_once()
    item = service.artifacts(harness["a_id"])[0]
    assert item["provenance"] == "model_generated"
    with harness["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Episode)) == 0
    body = {"operation_id": str(uuid4()), "action": "keep"}
    response = harness["client"].post(
        f"/v1/reflection/artifacts/{item['id']}/actions", headers=harness["a"], json=body
    )
    assert response.status_code == 200
    with harness["sessions"]() as db:
        episode = db.get(Episode, (harness["a_id"], response.json()["episode_id"]))
        assert episode.trust_class == "model_generated"
        assert db.scalar(select(func.count()).select_from(Claim)) == 0


def test_admin_reflection_exposes_only_fixed_counts_and_budget_metadata(harness):
    h = harness
    enabled(h)
    ordinary = h["client"].get("/v1/admin/reflection", headers=h["a"])
    assert ordinary.status_code == 403
    set_admin_grant(h["sessions"], h["a_id"], True)
    response = h["client"].get("/v1/admin/reflection", headers=h["a"])
    assert response.status_code == 200
    assert set(response.json()) == {
        "globally_enabled",
        "summary_generation",
        "suspended_model_class",
        "policies_enabled",
        "runs",
        "artifacts",
        "maximum_nightly_seconds",
        "maximum_jobs",
        "minimum_idle_seconds",
        "updated_at",
    }
    assert response.json()["maximum_jobs"] == 3
    assert "TODO" not in response.text and h["a_id"] not in response.text
