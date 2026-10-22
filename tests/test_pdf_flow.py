"""Actual isolated parser/API/source projection; synthetic PDFs on both databases."""

import os
from pathlib import Path
from uuid import uuid4

import pytest
from conftest import make_conversation
from pdf_fixtures import text_pdf
from sqlalchemy import func, select

from ada.evidence import content_hash
from ada.models import DocumentUpload, SourceVersion
from ada.pdf_sandbox import DockerPdfParser


@pytest.fixture
def pdf_parser():
    path = os.environ.get("ADA_TEST_PDF_MANIFEST")
    if not path:
        pytest.skip("Explicit isolated PDF image manifest required")
    parser = DockerPdfParser(Path(path))
    assert parser.available
    return parser


def prepare(h, parser):
    h["app"].state.pdfs.parser = parser
    cid, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    return cid, scope


def post_pdf(h, scope, raw, upload=None, source=None, who="a", filename="public.pdf"):
    return h["client"].post(
        f"/v1/scopes/{scope}/documents/pdf-uploads/{upload or uuid4()}",
        headers=h[who] | {"Content-Type": "application/pdf"},
        params={"source_id": source or str(uuid4()), "filename": filename},
        content=raw,
    )


def test_actual_pages_quotes_trust_original_bytes_duplicate_and_retrieval(harness, pdf_parser):
    h = harness
    _, scope = prepare(h, pdf_parser)
    raw = text_pdf(("Public orbit launch is Monday.", "Public table: Mars 3; Venus 5."))
    uid, sid = str(uuid4()), str(uuid4())
    result = post_pdf(h, scope, raw, uid, sid)
    assert result.status_code == 201
    receipt = result.json()
    assert receipt["state"] == "ready"
    assert post_pdf(h, scope, raw, uid, sid).json() == receipt
    assert post_pdf(h, scope, raw + b" ", uid, sid).status_code == 409
    version = (
        h["client"]
        .get("/v1/document-versions/" + receipt["source_version_id"], headers=h["a"])
        .json()
    )
    assert version["content_hash"] != receipt["raw_hash"]
    assert version["content_hash"] == content_hash(version["content"])
    assert len(version["extraction"]["pages"]) == 2
    chunks = (
        h["client"].get("/v1/document-versions/" + version["id"] + "/chunks", headers=h["a"]).json()
    )
    assert [c["pdf"]["page"] for c in chunks] == [1, 2]
    assert "".join(c["quote"] for c in chunks) == version["content"]
    assert (
        h["client"].get("/v1/document-versions/" + version["id"] + "/raw", headers=h["a"]).content
        == raw
    )
    retrieved = h["client"].post(
        f"/v1/scopes/{scope}/retrieve",
        headers=h["a"],
        json={"query": "orbit launch", "use_documents": True},
    )
    assert retrieved.status_code == 200
    card = retrieved.json()["document_selected"][0]
    assert card["pdf"]["page"] == 1 and card["trust_class"] == "imported_untrusted"
    assert (
        card["raw_hash"] == receipt["raw_hash"]
        and card["evidence"]["content_hash"] == version["content_hash"]
    )
    assert (
        h["client"].get("/v1/document-versions/" + version["id"], headers=h["b"]).status_code == 404
    )


def test_unicode_codepoints_repeated_headers_and_explicit_new_version_preserve_old_text(
    harness, pdf_parser
):
    h = harness
    _, scope = prepare(h, pdf_parser)
    raw = text_pdf(
        ("Public header \xa0 \xa1 Mars 3 Venus 5", "Public header \xa0 \xa1 Mars 4 Venus 6"),
        unicode_map=True,
    )
    source = str(uuid4())
    first = post_pdf(h, scope, raw, source=source).json()
    assert first["state"] == "ready"
    before = (
        h["client"]
        .get("/v1/document-versions/" + first["source_version_id"], headers=h["a"])
        .json()
    )
    assert "😀" in before["content"] and "e\u0301" in before["content"]
    assert before["content"].count("Public header") == 2
    pages = before["extraction"]["pages"]
    assert pages[-1]["span_end"] == len(before["content"])
    second = post_pdf(h, scope, text_pdf(("Public corrected page",)), source=source).json()
    assert second["state"] == "ready" and second["version"] == 2
    assert (
        h["client"]
        .get("/v1/document-versions/" + first["source_version_id"], headers=h["a"])
        .json()
        == before
    )


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        (b"%PDF-broken\n%%EOF", "pdf_malformed"),
        (text_pdf(("",)), "pdf_ocr_required"),
        (text_pdf(("Public",) * 17), "pdf_page_limit"),
        (
            text_pdf(catalog_extra=b"/OpenAction << /S /JavaScript /JS (unsafe) >>"),
            "pdf_active_content",
        ),
    ],
    ids=["malformed", "scan", "page-limit", "active-content"],
)
def test_unsupported_or_active_pdfs_fail_visibly_without_partial_sources(
    harness, pdf_parser, raw, code
):
    h = harness
    _, scope = prepare(h, pdf_parser)
    result = post_pdf(h, scope, raw)
    assert result.status_code == 201
    assert result.json()["state"] == "failed" and result.json()["error_code"] == code
    original = h["client"].get(
        "/v1/document-uploads/" + result.json()["id"] + "/raw", headers=h["a"]
    )
    assert (
        original.status_code == 200
        and original.content == raw
        and original.headers["cache-control"] == "no-store"
    )
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(SourceVersion)
                .where(SourceVersion.scope_id == scope)
            )
            == 0
        )


def test_foreign_scope_and_raw_limits_precede_parser(harness, pdf_parser, monkeypatch):
    h = harness
    _, scope = prepare(h, pdf_parser)
    monkeypatch.setattr(
        pdf_parser, "parse", lambda raw: pytest.fail("Unauthorized/oversized PDF reached parser")
    )
    assert post_pdf(h, scope, text_pdf(), who="b").status_code == 404
    assert post_pdf(h, scope, b"%PDF-" + b"x" * 262144).status_code == 413
    assert post_pdf(h, scope, b"plain text").status_code == 415


def test_deleted_reservation_cannot_be_resurrected_by_late_extraction(
    harness, pdf_parser, monkeypatch
):
    h = harness
    _, scope = prepare(h, pdf_parser)
    uid = str(uuid4())
    original = pdf_parser.parse

    def deleted(raw):
        result = original(raw)
        with h["sessions"].begin() as db:
            db.delete(db.get(DocumentUpload, (h["a_id"], uid)))
        return result

    monkeypatch.setattr(pdf_parser, "parse", deleted)
    assert post_pdf(h, scope, text_pdf(), upload=uid).status_code == 404
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(SourceVersion)
                .where(SourceVersion.scope_id == scope)
            )
            == 0
        )


def test_tampered_mapping_or_original_is_withheld_from_retrieval(harness, pdf_parser):
    h = harness
    _, scope = prepare(h, pdf_parser)
    response = post_pdf(h, scope, text_pdf())
    assert response.json()["state"] == "ready"
    uid = response.json()["id"]
    with h["sessions"].begin() as db:
        row = db.get(DocumentUpload, (h["a_id"], uid))
        row.raw_bytes = b"%PDF-tampered"
    result = h["client"].post(
        f"/v1/scopes/{scope}/retrieve",
        headers=h["a"],
        json={"query": "orbit launch", "use_documents": True},
    )
    assert result.status_code == 200 and result.json()["document_selected"] == []


@pytest.mark.parametrize("failure", ["raw", "future", "expired"])
def test_invalid_pdf_lineage_or_availability_never_enters_memory_extraction_context(
    harness, pdf_parser, failure
):
    from ada.providers import Completion

    h = harness
    _, scope = prepare(h, pdf_parser)
    receipt = post_pdf(h, scope, text_pdf()).json()
    version = (
        h["client"]
        .get("/v1/document-versions/" + receipt["source_version_id"], headers=h["a"])
        .json()
    )
    with h["sessions"].begin() as db:
        row = db.get(DocumentUpload, (h["a_id"], receipt["id"]))
        if failure == "raw":
            row.raw_bytes = b"%PDF-tampered"
        elif failure == "future":
            from ada.models import now_ms

            row.available_from = now_ms() + 86400000
        else:
            row.available_from, row.available_to = 0, 1

    class Extractor:
        model = "public-source-validation-fixture"
        calls = 0

        def complete(self, messages):
            self.calls += 1
            return Completion('{"candidates":[]}', self.model)

    extractor = Extractor()
    h["app"].state.proposals.provider = extractor
    pin = {
        "source_version_id": version["id"],
        "version": version["version"],
        "content_hash": version["content_hash"],
        "span_start": 0,
        "span_end": len(version["content"]),
    }
    result = h["client"].post(
        f"/v1/scopes/{scope}/memory-extractions",
        headers=h["a"],
        json={"extraction_id": str(uuid4()), "sources": [pin]},
    )
    assert result.status_code in (409, 422) and extractor.calls == 0


def test_current_principal_is_rechecked_after_parser_before_publication(
    harness, pdf_parser, monkeypatch
):
    from ada.models import User

    h = harness
    _, scope = prepare(h, pdf_parser)
    original = pdf_parser.parse

    def changed_epoch(raw):
        assert h["sessions"].kw["bind"].pool.checkedout() == 0
        artifact = original(raw)
        with h["sessions"].begin() as db:
            db.get(User, h["a_id"]).data_epoch += 1
        return artifact

    monkeypatch.setattr(pdf_parser, "parse", changed_epoch)
    result = post_pdf(h, scope, text_pdf())
    assert result.status_code == 401
    with h["sessions"]() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(SourceVersion)
                .where(SourceVersion.scope_id == scope)
            )
            == 0
        )


def test_busy_parser_has_one_capacity_slot_and_retained_fixed_failure(harness, pdf_parser):
    from ada.pdf_sandbox import CAPACITY

    h = harness
    _, scope = prepare(h, pdf_parser)
    upload = str(uuid4())
    assert CAPACITY.acquire(blocking=False)
    try:
        assert post_pdf(h, scope, text_pdf(), upload=upload).status_code == 429
    finally:
        CAPACITY.release()
    receipt = h["client"].get("/v1/document-uploads/" + upload, headers=h["a"]).json()
    assert receipt["state"] == "failed" and receipt["error_code"] == "pdf_parser_busy"
