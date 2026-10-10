import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from ada.documents import DocumentService, chunk_text, parse_text, rebuild_document_search
from ada.errors import ServiceError
from ada.models import DocumentChunk, DocumentSearch, DocumentUpload, Scope, SourceVersion


def scope(h, owner="a"):
    with h["sessions"].begin() as db:
        row = Scope(owner_id=h[owner + "_id"], kind="project", name="Synthetic documents")
        db.add(row)
        db.flush()
        return row.id


def upload(service, h, scope_id, raw=b"Synthetic atlas cobalt setting.\n", **kwargs):
    return service.upload(
        h["a_id"],
        scope_id,
        str(uuid4()),
        raw,
        source_id=str(uuid4()),
        filename="atlas.txt",
        media_type="text/plain",
        **kwargs,
    )


def test_exact_unicode_utf8_and_deterministic_chunk_spans():
    raw = ("\ufeffSynthetic 🙂 alpha\r\n" + "β data " * 400 + "\nFinal e\u0301.").encode()
    text = parse_text(raw)
    assert text.encode() == raw
    chunks = chunk_text(text)
    assert chunks == chunk_text(text)
    assert "".join(c["quote"] for c in chunks) == text
    for ordinal, c in enumerate(chunks, 1):
        assert c["ordinal"] == ordinal
        assert text[c["span_start"] : c["span_end"]] == c["quote"]
        assert len(c["quote"]) <= 1024
        assert c["quote_hash"] == hashlib.sha256(c["quote"].encode()).hexdigest()


def test_line_ranges_are_inclusive_when_an_excerpt_ends_with_newline():
    chunks = chunk_text("Synthetic first\nSecond\n")
    assert chunks[0]["line_start"] == 1 and chunks[0]["line_end"] == 2
    assert chunk_text("Synthetic first\n")[0]["line_end"] == 1
    assert chunk_text("\n")[0]["line_end"] == 1
    # The next excerpt starts on the next line despite the previous range
    # excluding the trailing empty line.
    chunks = chunk_text("x" * 1023 + "\nSecond\n")
    assert [(c["line_start"], c["line_end"]) for c in chunks] == [(1, 1), (2, 2)]


@pytest.mark.parametrize(
    "raw", [b"\xff", b"text\x00tail", b"%PDF-1.7\ntext", b"PK\x03\x04", b"\x1f\x8b", b"   "]
)
def test_parser_rejects_malformed_binary_unsupported_and_blank(raw):
    with pytest.raises(ServiceError):
        parse_text(raw)


def test_upload_replay_exact_version_chunk_and_private_raw(harness):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    upload_id, source_id = str(uuid4()), str(uuid4())
    raw = "\ufeffSynthetic 🙂 atlas\r\nOlive threshold: 7.\n".encode()
    kwargs = dict(source_id=source_id, filename="atlas.md", media_type="text/markdown")
    receipt, created = service.upload(h["a_id"], s, upload_id, raw, **kwargs)
    replay, again = service.upload(h["a_id"], s, upload_id, raw, **kwargs)
    assert created and not again and receipt == replay
    assert receipt["state"] == "ready" and receipt["version"] == 1
    assert receipt["origin"] == "imported_document"
    assert receipt["trust_class"] == "imported_untrusted"
    assert receipt["raw_hash"] == hashlib.sha256(raw).hexdigest()
    version = service.version(h["a_id"], s, receipt["source_version_id"])
    assert version["content"].encode() == raw and version["content_hash"] == receipt["raw_hash"]
    assert service.raw(h["a_id"], s, receipt["source_version_id"])[0] == raw
    chunks = service.chunks(h["a_id"], s, receipt["source_version_id"])
    assert "".join(c["quote"] for c in chunks) == version["content"]
    with pytest.raises(ServiceError, match="document_upload_id_reused"):
        service.upload(h["a_id"], s, upload_id, raw + b"changed", **kwargs)
    with pytest.raises(ServiceError, match="document_upload_id_reused"):
        service.upload(h["a_id"], s, upload_id, raw, **(kwargs | {"filename": "other.md"}))
    claim = h["client"].post(
        f"/v1/scopes/{s}/claims",
        headers=h["a"],
        json={
            "claim_id": str(uuid4()),
            "source_version_id": receipt["source_version_id"],
            "span_start": 0,
            "span_end": 9,
            "subject": "Synthetic",
            "predicate": "setting",
            "value": "7",
        },
    )
    assert claim.status_code == 422 and claim.json()["detail"] == "source_not_user_evidence"


def test_document_reads_are_owner_and_scope_bound_identical_bytes(harness):
    h = harness
    service = DocumentService(h["sessions"])
    s, other, b_scope = scope(h), scope(h), scope(h, "b")
    receipt, _ = upload(service, h, s)
    b_receipt, _ = service.upload(
        h["b_id"],
        b_scope,
        receipt["id"],
        b"Synthetic atlas cobalt setting.\n",
        source_id=str(uuid4()),
        filename="atlas.txt",
        media_type="text/plain",
    )
    assert b_receipt["raw_hash"] == receipt["raw_hash"]
    assert b_receipt["source_version_id"] != receipt["source_version_id"]
    for owner, sid in ((h["b_id"], s), (h["a_id"], other)):
        for read in (
            lambda: service.get(owner, sid, receipt["id"]),
            lambda: service.version(owner, sid, receipt["source_version_id"]),
            lambda: service.chunks(owner, sid, receipt["source_version_id"]),
            lambda: service.raw(owner, sid, receipt["source_version_id"]),
        ):
            with pytest.raises(ServiceError) as error:
                read()
            assert error.value.status == 404
    assert service.list(h["a_id"], other) == []


@pytest.mark.parametrize(
    "filename",
    [
        "../atlas.txt",
        r"C:\atlas.txt",
        "CON.txt",
        "a\n.txt",
        "a\u202e.txt",
        "a.txt.",
        "atlas.pdf",
        'a".txt',
        "a*.txt",
        "a|.md",
        "a?.md",
        "a<.txt",
        "a>.txt",
        "CON.extra.md",
    ],
)
def test_names_never_paths_and_invalid_metadata_not_reserved(harness, filename):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    with pytest.raises(ServiceError):
        service.upload(
            h["a_id"],
            s,
            str(uuid4()),
            b"Synthetic text",
            source_id=str(uuid4()),
            filename=filename,
            media_type="text/plain",
        )
    assert service.list(h["a_id"], s) == []


def test_failed_parse_and_publish_leave_no_partial_evidence(harness, monkeypatch):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    bad, created = upload(service, h, s, b"not utf8\xff")
    assert created and bad["state"] == "failed" and bad["error_code"] == "document_invalid_encoding"
    assert bad["chunk_count"] == 0

    def fail_publish(*args):
        raise RuntimeError("synthetic confidential parser detail")

    monkeypatch.setattr(service, "_publish", fail_publish)
    failed, _ = upload(service, h, s)
    assert failed["state"] == "failed" and failed["error_code"] == "document_processing_failed"
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(DocumentChunk)) == 0
        assert db.scalar(select(func.count()).select_from(DocumentSearch)) == 0
        assert db.scalar(select(func.count()).select_from(SourceVersion)) == 0


def test_bounds_version_history_and_rebuild(harness, monkeypatch):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    with pytest.raises(ServiceError) as error:
        upload(service, h, s, b"x" * (256 * 1024 + 1))
    assert error.value.status == 413
    one, _ = upload(service, h, s, available_from=10, available_to=30)
    two, _ = service.upload(
        h["a_id"],
        s,
        str(uuid4()),
        b"Synthetic second version",
        source_id=one["source_id"],
        filename="atlas.txt",
        media_type="text/plain",
        available_from=20,
    )
    assert two["version"] == 2 and one["source_version_id"] != two["source_version_id"]
    assert service.get(h["a_id"], s, one["id"]) == one
    with h["sessions"].begin() as db:
        db.query(DocumentSearch).delete()
    assert rebuild_document_search(h["sessions"]) == 2
    monkeypatch.setattr("ada.documents.MAX_FILES", 2)
    with pytest.raises(ServiceError, match="document_file_quota"):
        upload(service, h, s)


def test_projection_failure_after_first_chunk_rolls_back_entire_publication(harness, monkeypatch):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    original = __import__("ada.documents", fromlist=["normalize"]).normalize
    calls = 0

    def fail_second(quote):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("synthetic projection failure after first insert")
        return original(quote)

    monkeypatch.setattr("ada.documents.normalize", fail_second)
    receipt, _ = upload(service, h, s, ("Synthetic atlas " * 150).encode())
    assert calls == 2 and receipt["state"] == "failed"
    with h["sessions"]() as db:
        for model in (SourceVersion, DocumentChunk, DocumentSearch):
            assert db.scalar(select(func.count()).select_from(model)) == 0


def test_quotas_parser_time_and_projection_failure_are_sanitized(harness, monkeypatch):
    h = harness
    service = DocumentService(h["sessions"])
    s, other = scope(h), scope(h)
    ready, _ = upload(service, h, s)
    monkeypatch.setattr("ada.documents.MAX_OWNER_BYTES", ready["raw_size"])
    with pytest.raises(ServiceError, match="document_storage_quota"):
        upload(service, h, other)
    monkeypatch.setattr("ada.documents.MAX_OWNER_BYTES", 10 * 1024 * 1024)
    monkeypatch.setattr("ada.documents.MAX_VERSIONS", 1)
    with pytest.raises(ServiceError, match="document_version_quota"):
        service.upload(
            h["a_id"],
            s,
            str(uuid4()),
            b"Synthetic changed",
            source_id=ready["source_id"],
            filename="atlas.txt",
            media_type="text/plain",
        )
    times = iter([0, 3])
    monkeypatch.setattr("ada.documents.time", SimpleNamespace(monotonic=lambda: next(times)))
    failed, _ = upload(service, h, s)
    assert failed["state"] == "failed" and failed["error_code"] == "document_parse_time_limit"


def test_stale_processing_recovery_fences_older_attempt(harness, monkeypatch):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    upload_id, source_id = str(uuid4()), str(uuid4())
    raw = b"Synthetic recovery exact input."
    kwargs = dict(source_id=source_id, filename="atlas.txt", media_type="text/plain")
    original = service._publish
    monkeypatch.setattr(service, "_publish", lambda *args: None)
    receipt, _ = service.upload(h["a_id"], s, upload_id, raw, **kwargs)
    assert receipt["state"] == "processing"
    with h["sessions"].begin() as db:
        row = db.get(DocumentUpload, (h["a_id"], upload_id))
        row.started_at -= 60_000
    monkeypatch.setattr(service, "_publish", original)
    replay, created = service.upload(h["a_id"], s, upload_id, raw, **kwargs)
    assert replay["state"] == "ready" and not created
    text, chunks = service._parse(raw)
    service._publish(h["a_id"], s, upload_id, 1, text, chunks)
    with h["sessions"]() as db:
        assert db.get(DocumentUpload, (h["a_id"], upload_id)).attempt == 2
        assert db.scalar(select(func.count()).select_from(SourceVersion)) == 1


def test_owned_scope_source_and_upload_collisions_preserve_the_original(harness):
    h = harness
    service = DocumentService(h["sessions"])
    first_scope, second_scope = scope(h), scope(h)
    receipt, _ = upload(service, h, first_scope)
    for upload_id, error in (
        (receipt["id"], "document_upload_id_reused"),
        (str(uuid4()), "document_source_id_reused"),
    ):
        with pytest.raises(ServiceError, match=error):
            service.upload(
                h["a_id"],
                second_scope,
                upload_id,
                b"Synthetic changed text",
                source_id=receipt["source_id"],
                filename="atlas.txt",
                media_type="text/plain",
            )
    assert service.list(h["a_id"], second_scope) == []
    assert service.get(h["a_id"], first_scope, receipt["id"]) == receipt
    assert (
        service.raw(h["a_id"], first_scope, receipt["source_version_id"])[0]
        == b"Synthetic atlas cobalt setting.\n"
    )
    # The existing note writer must not overwrite/launder imported provenance.
    result = h["client"].post(
        f"/v1/scopes/{first_scope}/notes",
        headers=h["a"],
        json={
            "source_id": receipt["source_id"],
            "content": "Synthetic imported text endorsed as note",
        },
    )
    assert result.status_code == 409 and result.json()["detail"] == "source_id_reused"


def test_terminal_failed_replay_and_failed_version_gap_are_immutable(harness, monkeypatch):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    upload_id, source_id = str(uuid4()), str(uuid4())
    kwargs = dict(source_id=source_id, filename="atlas.txt", media_type="text/plain")
    bad = b"Synthetic malformed \xff"
    receipt, created = service.upload(h["a_id"], s, upload_id, bad, **kwargs)
    assert created and receipt["state"] == "failed"
    original_parser = service._parse
    monkeypatch.setattr(
        service,
        "_parse",
        lambda raw: pytest.fail("A terminal failed receipt must not silently reparse"),
    )
    replay, created = service.upload(h["a_id"], s, upload_id, bad, **kwargs)
    assert not created and replay == receipt
    monkeypatch.setattr(service, "_parse", original_parser)
    ready, created = service.upload(
        h["a_id"], s, str(uuid4()), b"Synthetic repaired text", **kwargs
    )
    assert created and ready["state"] == "ready" and ready["version"] == 2
    assert service.versions(h["a_id"], source_id) == [ready]
    with pytest.raises(ServiceError) as missing:
        service.version(h["a_id"], s, receipt["source_version_id"])
    assert missing.value.status == 404


def test_exhausted_stale_recovery_and_old_attempt_cannot_fail_new_reservation(harness, monkeypatch):
    h = harness
    service = DocumentService(h["sessions"])
    s = scope(h)
    upload_id, source_id = str(uuid4()), str(uuid4())
    raw = b"Synthetic attempt fencing."
    kwargs = dict(source_id=source_id, filename="atlas.txt", media_type="text/plain")
    monkeypatch.setattr(service, "_publish", lambda *args: None)
    receipt, _ = service.upload(h["a_id"], s, upload_id, raw, **kwargs)
    for attempt in (2, 3):
        with h["sessions"].begin() as db:
            db.get(DocumentUpload, (h["a_id"], upload_id)).started_at -= 60_000
        replay, created = service.upload(h["a_id"], s, upload_id, raw, **kwargs)
        assert not created and replay["state"] == "processing"
        service._fail(h["a_id"], s, upload_id, attempt - 1, "document_processing_failed")
        assert service.get(h["a_id"], s, upload_id)["state"] == "processing"
    with h["sessions"].begin() as db:
        db.get(DocumentUpload, (h["a_id"], upload_id)).started_at -= 60_000
    exhausted, created = service.upload(h["a_id"], s, upload_id, raw, **kwargs)
    assert not created and exhausted["state"] == "failed"
    assert exhausted["error_code"] == "document_processing_interrupted"
    assert exhausted["source_version_id"] == receipt["source_version_id"]
    with h["sessions"]() as db:
        assert db.scalar(select(func.count()).select_from(SourceVersion)) == 0


def test_cross_scope_owner_quota_race_on_postgresql(harness, monkeypatch):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("PostgreSQL row locks are required for owner quota serialization")
    service = DocumentService(h["sessions"])
    scopes = [scope(h), scope(h)]
    monkeypatch.setattr("ada.documents.MAX_OWNER_BYTES", 10)
    barrier = threading.Barrier(2)

    def reserve(scope_id):
        barrier.wait(5)
        try:
            return upload(service, h, scope_id, b"atlas 7")
        except ServiceError as error:
            return error.code

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(reserve, scopes))
    assert sum(isinstance(result, tuple) for result in results) == 1
    assert "document_storage_quota" in results
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.sum(DocumentUpload.raw_size)).where(
                    DocumentUpload.owner_id == h["a_id"]
                )
            )
            == 7
        )
        assert db.scalar(select(func.count()).select_from(DocumentUpload)) == 1


def test_concurrent_upload_replay_and_versions_on_postgresql(harness, monkeypatch):
    h = harness
    if h["backend"] != "postgres":
        pytest.skip("PostgreSQL row locks are required for upload serialization")
    service = DocumentService(h["sessions"])
    s = scope(h)
    entered, release = threading.Event(), threading.Event()
    original = service._parse

    def pause(raw):
        entered.set()
        assert release.wait(5)
        return original(raw)

    monkeypatch.setattr(service, "_parse", pause)
    upload_id, source_id = str(uuid4()), str(uuid4())
    kwargs = dict(source_id=source_id, filename="atlas.txt", media_type="text/plain")
    with ThreadPoolExecutor(2) as pool:
        future = pool.submit(service.upload, h["a_id"], s, upload_id, b"Synthetic first", **kwargs)
        assert entered.wait(5)
        replay, created = service.upload(h["a_id"], s, upload_id, b"Synthetic first", **kwargs)
        assert replay["state"] == "processing" and not created
        # Parsing deliberately runs after reservation has committed.
        with h["sessions"]() as db:
            assert db.get(DocumentUpload, (h["a_id"], upload_id)).state == "processing"
        release.set()
        ready, _ = future.result(5)
    assert ready["state"] == "ready"
    monkeypatch.setattr(service, "_parse", original)
    with ThreadPoolExecutor(2) as pool:
        results = list(
            pool.map(
                lambda _: service.upload(h["a_id"], s, str(uuid4()), b"Synthetic next", **kwargs),
                range(2),
            )
        )
    assert {result[0]["version"] for result in results} == {2, 3}
