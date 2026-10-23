"""Measured layout families retain exact page evidence, not table/column semantics."""

# ruff: noqa: F811 -- the imported pytest fixture is an explicit dependency.

import pytest
from pdf_fixtures import public_pdf_profiles
from test_pdf_flow import pdf_parser  # noqa: F401

from ada.pdfs import pdf_chunks, validate_extraction


@pytest.mark.parametrize("profile", public_pdf_profiles(), ids=lambda value: value["key"])
def test_public_layout_profiles_preserve_page_spans_and_warn_about_reading_order(
    pdf_parser, profile
):
    result = validate_extraction(profile["raw"], pdf_parser.parse(profile["raw"]))
    assert len(profile["raw"]) <= 262144
    assert len(result["pages"]) == profile["pages"]
    assert all(fragment in result["text"] for fragment in profile["fragments"])
    chunks = pdf_chunks(result["text"], result["pages"])
    assert "".join(chunk["quote"] for chunk in chunks) == result["text"]
    for chunk in chunks:
        assert (
            sum(
                page["span_start"] <= chunk["span_start"] < chunk["span_end"] <= page["span_end"]
                for page in result["pages"]
            )
            == 1
        )
    if profile["key"] == "table-repeated-header":
        assert result["text"].count("Public inventory") == 2
    if profile["key"] == "dense-16-pages":
        assert len(profile["raw"]) > 65536  # Server-only sample; Android must use smaller sections.
    assert "tables" in result["warnings"][0] and "visual verification" in result["warnings"][0]
