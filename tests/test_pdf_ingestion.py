"""PDF publication is atomic, owner-bound and distinct from original bytes."""

from uuid import uuid4

from conftest import make_conversation
from pdf_fixtures import text_pdf

from ada.pdfs import validate_extraction


def test_pdf_rejects_a_forged_page_or_original_hash():
    import pytest

    from ada.errors import ServiceError

    with pytest.raises(ServiceError):
        validate_extraction(text_pdf(), {"text": "Forged", "pages": []})


def test_pdf_requires_real_boundary_and_old_text_route_still_rejects_it(harness):
    h = harness
    cid, _ = make_conversation(h)
    scope = h["client"].get(f"/v1/conversations/{cid}", headers=h["a"]).json()["scope_id"]
    params = {"source_id": str(uuid4()), "filename": "public.pdf"}
    result = h["client"].post(
        f"/v1/scopes/{scope}/documents/pdf-uploads/{uuid4()}",
        headers=h["a"] | {"Content-Type": "application/pdf"},
        params=params,
        content=text_pdf(),
    )
    assert result.status_code == 503
    old = h["client"].post(
        f"/v1/scopes/{scope}/documents/uploads/{uuid4()}",
        headers=h["a"] | {"Content-Type": "application/pdf"},
        params=params,
        content=text_pdf(),
    )
    assert old.status_code == 415
    assert h["client"].get(f"/v1/scopes/{scope}/document-uploads", headers=h["a"]).json() == []
