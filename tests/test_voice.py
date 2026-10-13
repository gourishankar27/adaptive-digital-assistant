from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from uuid import uuid4

import pytest
from alembic import command
from conftest import make_conversation
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError
from test_streaming import attach, wait_state

from ada.admin import set_admin_grant
from ada.models import Event, Request, SourceVersion
from ada.voice_models import VoiceInput


def voice_body(**changes):
    body = {
        "request_id": str(uuid4()),
        "content": "Reviewed kettle 🫖 wording",
        "review": "approve",
        "transcript": {
            "transcript_id": str(uuid4()),
            "engine_id": "android_on_device",
            "engine_version": "Android 16 API36 (client reported)",
            "language": "en-US",
            "duration_ms": 3200,
            "original_text": "Generated cattle 🫖 wording",
        },
    }
    body.update(changes)
    return body


def post(h, cid, body, who="a"):
    return h["client"].post(f"/v1/conversations/{cid}/voice-requests", headers=h[who], json=body)


def test_explicit_review_creates_separate_generated_and_endorsed_lineage(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    body = voice_body()
    try:
        result = post(h, cid, body)
        assert result.status_code == 202 and p.entered.wait(5)
        rid = body["request_id"]
        lineage = h["client"].get(f"/v1/requests/{rid}/voice-input", headers=h["a"]).json()
        assert lineage["original_text"] == body["transcript"]["original_text"]
        assert (
            lineage["original_origin"] == "asr_generated"
            and lineage["original_trust"] == "generated_interpretation"
        )
        assert (
            lineage["reviewed_text"] == body["content"]
            and lineage["reviewed_origin"] == "user_reviewed"
        )
        assert (
            lineage["audio_sha256"] is None and lineage["audio_storage"] == "not_received_by_server"
        )
        version = h["client"].get(
            f"/v1/source-versions/{lineage['endorsement_source_version_id']}", headers=h["a"]
        )
        assert version.status_code == 200 and version.json()["content"] == body["content"]
        assert version.json()["trust_class"] == "user_explicit"
        assert p.calls[0][-1]["content"] == body["content"]
        assert body["transcript"]["original_text"] not in str(p.calls)
        p.release.set()
        assert wait_state(h, rid, "completed")["result"]["status"] == "completed"
        assert post(h, cid, body).status_code == 202 and len(p.calls) == 1
    finally:
        p.release.set()
        h["app"].state.streaming.stop()


@pytest.mark.parametrize(
    "change",
    [
        {"review": None},
        {"review": False},
        {"review": "implicit"},
        {"owner_id": str(uuid4())},
        {"scope_id": str(uuid4())},
        {"audio": "unaccepted encoded audio"},
        {"audio_sha256": "0" * 64},
        {"content": "\x00"},
        {"content": " "},
    ],
)
def test_unreviewed_or_forged_voice_fields_never_reserve(harness, change):
    h = harness
    cid, _ = make_conversation(h)
    body = voice_body(**change)
    if change == {"review": None}:
        del body["review"]
    assert post(h, cid, body).status_code == 422
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Request)) == 0
        assert db.scalar(select(func.count()).select_from(VoiceInput)) == 0
        assert db.scalar(select(func.count()).select_from(Event)) == 0
    assert h["provider"].calls == []


@pytest.mark.parametrize(
    "change",
    [
        {"engine_id": "external_provider"},
        {"engine_version": "bad\nversion"},
        {"duration_ms": True},
        {"duration_ms": 0},
        {"duration_ms": 60001},
        {"language": "en_US"},
        {"language": "x"},
        {"original_text": "\ud800"},
        {"original_text": "\x00"},
        {"original_text": " "},
        {"original_text": "x" * 4001},
        {"trust_class": "user_explicit"},
        {"audio_ref": "external-file"},
    ],
)
def test_transcript_contract_is_bounded_and_interpretation_only(harness, change):
    h = harness
    cid, _ = make_conversation(h)
    body = voice_body()
    body["transcript"].update(change)
    # Sending escaped JSON avoids client-side surrogate encoding failures.
    import json

    r = h["client"].post(
        f"/v1/conversations/{cid}/voice-requests",
        headers={**h["a"], "Content-Type": "application/json"},
        content=json.dumps(body),
    )
    assert r.status_code == 422
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(Request)) == 0


def test_private_voice_routes_replay_and_cancellation_do_not_change_original(harness):
    h = harness
    cid, _ = make_conversation(h)
    set_admin_grant(h["sessions"], h["b_id"], True)
    p = attach(h)
    body = voice_body()
    rid = body["request_id"]
    try:
        assert post(h, cid, body, "b").status_code == 404
        assert (
            h["client"].post(f"/v1/conversations/{cid}/voice-requests", json=body).status_code
            == 401
        )
        assert post(h, cid, body).status_code == 202 and p.entered.wait(5)
        assert post(h, cid, body).status_code == 202
        original = h["client"].get(f"/v1/requests/{rid}/voice-input", headers=h["a"]).json()
        for path in (f"/v1/requests/{rid}/voice-input", f"/v1/conversations/{cid}/voice-inputs"):
            assert h["client"].get(path, headers=h["b"]).status_code == 404
            assert h["client"].get(path).status_code == 401
        for field, value in (
            ("original_text", "Changed ASR"),
            ("transcript_id", str(uuid4())),
            ("language", "hi-IN"),
            ("duration_ms", 1),
        ):
            altered = deepcopy(body)
            altered["transcript"][field] = value
            assert post(h, cid, altered).status_code == 409
        assert post(h, cid, {**body, "content": "Changed review"}).status_code == 409
        assert post(h, cid, {**body, "use_memory": False}).status_code == 409
        for route in ("messages", "stream-requests"):
            assert (
                h["client"]
                .post(
                    f"/v1/conversations/{cid}/{route}",
                    headers=h["a"],
                    json={"request_id": rid, "content": body["content"]},
                )
                .status_code
                == 409
            )
        assert (
            h["client"]
            .post(f"/v1/requests/{rid}/cancel", headers=h["b"], json={"attempt": 1})
            .status_code
            == 404
        )
        cancelled = h["client"].post(
            f"/v1/requests/{rid}/cancel", headers=h["a"], json={"attempt": 1}
        )
        assert cancelled.status_code == 200
        assert wait_state(h, rid, "cancelled")["result"]["error_code"] == "request_cancelled"
        assert post(h, cid, body).status_code == 202
        p.release.set()
        assert wait_state(h, rid, "completed")["attempt"] == 2
        assert len(p.calls) == 2 and p.calls[0] == p.calls[1]
        assert h["client"].get(f"/v1/requests/{rid}/voice-input", headers=h["a"]).json() == original
        assert h["client"].get(f"/v1/conversations/{cid}/voice-inputs", headers=h["a"]).json() == [
            original
        ]
        assert post(h, cid, {**body, "request_id": str(uuid4())}).status_code == 409
        with h["sessions"]() as db:
            assert db.scalar(select(func.count()).select_from(VoiceInput)) == 1
            assert db.scalar(select(func.count()).select_from(Request)) == 1
            assert (
                db.scalar(select(func.count()).select_from(Event).where(Event.role == "user")) == 1
            )
    finally:
        p.release.set()
        h["app"].state.streaming.stop()


def test_voice_quota_rolls_back_reservation_and_corrupt_lineage_fails_closed(harness, monkeypatch):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    body = voice_body()
    try:
        monkeypatch.setattr("ada.voice.MAX_VOICE_INPUTS", 1)
        assert post(h, cid, body).status_code == 202
        p.release.set()
        wait_state(h, body["request_id"], "completed")
        second = voice_body()
        assert post(h, cid, second).status_code == 413
        with h["sessions"].begin() as db:
            assert db.get(Request, (h["a_id"], second["request_id"])) is None
            assert db.scalar(select(func.count()).select_from(VoiceInput)) == 1
            row = db.get(VoiceInput, (h["a_id"], body["request_id"]))
            row.original_text = "Changed storage without matching hash"
        assert (
            h["client"]
            .get(f"/v1/requests/{body['request_id']}/voice-input", headers=h["a"])
            .status_code
            == 409
        )
    finally:
        p.release.set()
        h["app"].state.streaming.stop()


def test_voice_schema_owner_duration_and_lossy_downgrade_guards(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    body = voice_body()
    try:
        assert post(h, cid, body).status_code == 202
        p.release.set()
        wait_state(h, body["request_id"], "completed")
        for field, value in (
            ("owner_id", h["b_id"]),
            ("scope_id", str(uuid4())),
            ("duration_ms", 60001),
            ("endorsement_source_version_id", str(uuid4())),
        ):
            with pytest.raises(IntegrityError), h["sessions"].begin() as db:
                row = db.get(VoiceInput, (h["a_id"], body["request_id"]))
                setattr(row, field, value)
                db.flush()
        with pytest.raises(RuntimeError, match="[Vv]oice"):
            command.downgrade(h["config"], "0013")
        with h["sessions"]() as db:
            assert "voice_inputs" in inspect(db.connection()).get_table_names()
            assert db.get(VoiceInput, (h["a_id"], body["request_id"])) is not None
    finally:
        p.release.set()
        h["app"].state.streaming.stop()


def test_concurrent_voice_metadata_conflict_has_single_endorsement(harness):
    h = harness
    cid, _ = make_conversation(h)
    p = attach(h)
    body = voice_body()
    altered = deepcopy(body)
    altered["transcript"]["original_text"] = "Other generated interpretation"
    try:
        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda b: post(h, cid, b).status_code, (body, altered)))
        assert sorted(results) == [202, 409]
        with h["sessions"]() as db:
            assert db.scalar(select(func.count()).select_from(VoiceInput)) == 1
            assert (
                db.scalar(
                    select(func.count())
                    .select_from(SourceVersion)
                    .where(SourceVersion.trust_class == "user_explicit")
                )
                == 1
            )
    finally:
        p.release.set()
        h["app"].state.streaming.stop()


def test_populated_0013_upgrade_preserves_plain_text_completed_replay(harness):
    from conftest import send

    h = harness
    cid, _ = make_conversation(h)
    old = send(h, cid, "Synthetic old completed text").json()
    command.downgrade(h["config"], "0013")
    command.upgrade(h["config"], "head")
    command.check(h["config"])
    assert send(h, cid, "Synthetic old completed text", old["request_id"]).json() == old
    assert (
        h["client"].get(f"/v1/requests/{old['request_id']}/voice-input", headers=h["a"]).status_code
        == 404
    )
