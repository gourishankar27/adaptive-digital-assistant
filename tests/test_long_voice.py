"""Long speech is one reviewed turn; immutable originals never become model context."""

from copy import deepcopy
from uuid import uuid4

import pytest
from conftest import make_conversation
from sqlalchemy import func, select
from test_streaming import attach, wait_state

from ada.evidence import content_hash
from ada.models import Request


def body(epoch=0):
    original = "Public synthetic recognition. " * 200
    reviewed = "Public synthetic reviewed story. " * 200
    return {
        "request_id": str(uuid4()),
        "content": reviewed[:100],
        "review": "approve",
        "data_epoch": epoch,
        "reviewed_text": reviewed,
        "context_start": 0,
        "context_end": 100,
        "transcript": {
            "transcript_id": str(uuid4()),
            "engine_id": "sherpa_zipformer_en_v1",
            "engine_version": "sherpa-onnx-1.13.8",
            "model_sha256": "a" * 64,
            "language": "en-US",
            "duration_ms": 125000,
            "segments": [
                {
                    "id": str(uuid4()),
                    "sequence": 0,
                    "end_ms": 125000,
                    "text": original,
                    "sha256": content_hash(original),
                }
            ],
        },
    }


def post(h, cid, value, who="a"):
    return h["client"].post(
        f"/v1/conversations/{cid}/long-voice-requests", headers=h[who], json=value
    )


def test_reviewed_narrative_exact_context_replay_and_owner_isolation(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    value = body()
    try:
        assert post(h, cid, value).status_code == 202
        assert p.entered.wait(5)
        route = f"/v1/requests/{value['request_id']}/long-voice-input"
        saved = h["client"].get(route, headers=h["a"]).json()
        assert saved["transcript"] == value["transcript"]
        assert saved["reviewed_text"] == value["reviewed_text"]
        assert saved["audio_storage"] == "not_received_by_server"
        assert saved["original_trust"] == "generated_interpretation"
        assert p.calls[0][-1]["content"] == value["content"]
        assert "Listen patiently" in p.calls[0][0]["content"]
        assert value["reviewed_text"] not in str(p.calls)
        assert h["client"].get(route, headers=h["b"]).status_code == 404
        assert post(h, cid, value, "b").status_code == 404
        p.release.set()
        wait_state(h, value["request_id"], "completed")
        assert post(h, cid, value).status_code == 202 and len(p.calls) == 1
        changed = deepcopy(value)
        changed["reviewed_text"] += " changed"
        assert post(h, cid, changed).status_code == 409
        changed = deepcopy(value)
        changed["conversation_style"] = "suggestions"
        assert post(h, cid, changed).status_code == 409
    finally:
        p.release.set()
        h["app"].state.streaming.stop()


@pytest.mark.parametrize(
    "mutation", ["hash", "sequence", "duplicate", "context", "epoch", "audio", "duration"]
)
def test_bad_lineage_and_stale_epoch_never_reserve(harness, mutation):
    h = harness
    cid, _ = make_conversation(h)
    value = body()
    if mutation == "hash":
        value["transcript"]["segments"][0]["sha256"] = "b" * 64
    if mutation == "sequence":
        value["transcript"]["segments"][0]["sequence"] = 1
    if mutation == "duplicate":
        value["transcript"]["segments"] *= 2
    if mutation == "context":
        value["content"] = "unbound wording"
    if mutation == "epoch":
        value["data_epoch"] = 999
    if mutation == "audio":
        value["transcript"]["audio"] = "forbidden"
    if mutation == "duration":
        value["transcript"]["duration_ms"] = 60000
    assert post(h, cid, value).status_code in (409, 422)
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Request)) == 0
    assert h["provider"].calls == []


def test_old_voice_contract_still_rejects_new_engine_and_long_duration(harness):
    from test_voice import post as old_post
    from test_voice import voice_body

    h = harness
    cid, _ = make_conversation(h)
    value = voice_body()
    value["transcript"].update(engine_id="sherpa_zipformer_en_v1", duration_ms=125000)
    assert old_post(h, cid, value).status_code == 422


def test_concurrent_duplicate_and_transcript_reuse_publish_one_turn(harness):
    from concurrent.futures import ThreadPoolExecutor

    from ada.long_voice import LongVoiceInput

    h = harness
    cid, _ = make_conversation(h)
    value = body()
    p = attach(h)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(lambda _: post(h, cid, value), range(2)))
        assert [r.status_code for r in responses] == [202, 202]
        assert p.entered.wait(5) and len(p.calls) == 1
        p.release.set()
        wait_state(h, value["request_id"], "completed")
        changed = deepcopy(value)
        changed["request_id"] = str(uuid4())
        assert post(h, cid, changed).status_code == 409
        with h["sessions"]() as db:
            assert db.scalar(select(func.count()).select_from(LongVoiceInput)) == 1
            assert db.scalar(select(func.count()).select_from(Request)) == 1
    finally:
        p.release.set()
        h["app"].state.streaming.stop()


def test_populated_upgrade_preserves_old_voice_replay_and_schema_checks(harness):
    from alembic import command
    from test_voice import post as old_post
    from test_voice import voice_body

    h = harness
    command.downgrade(h["config"], "0021")
    cid, _ = make_conversation(h)
    p = attach(h)
    value = voice_body()
    try:
        assert old_post(h, cid, value).status_code == 202
        assert p.entered.wait(5)
        p.release.set()
        before = wait_state(h, value["request_id"], "completed")
        lineage = (
            h["client"]
            .get(f"/v1/requests/{value['request_id']}/voice-input", headers=h["a"])
            .json()
        )
        command.upgrade(h["config"], "head")
        command.check(h["config"])
        assert old_post(h, cid, value).json() == before
        assert (
            h["client"]
            .get(f"/v1/requests/{value['request_id']}/voice-input", headers=h["a"])
            .json()
            == lineage
        )
        assert len(p.calls) == 1
    finally:
        p.release.set()
        h["app"].state.streaming.stop()
