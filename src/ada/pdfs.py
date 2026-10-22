"""Versioned text-PDF projection. No PDF parser is imported into the API process."""

import hashlib
import re

from ada.errors import ServiceError
from ada.evidence import content_hash, validate_text

PARSER = "pypdf-6.21.2-text-v1"
PDF_PROTOCOL = "ada-text-pdf-v1"
MAX_PAGES = 16


def require(condition):
    if not condition:
        raise ValueError("Invalid projection")


def validate_extraction(raw, result):
    try:
        require(
            set(result)
            == {
                "text",
                "pages",
                "raw_hash",
                "text_hash",
                "parser",
                "normalization",
                "warnings",
                "image_id",
            }
        )
        require(re.fullmatch(r"sha256:[a-f0-9]{64}", result["image_id"]) is not None)
        text, pages = result["text"], result["pages"]
        require(result["parser"] == PARSER and result["normalization"] == "lf-page-newline-v1")
        require(raw.startswith(b"%PDF-") and 0 < len(raw) <= 262144)
        require(result["raw_hash"] == hashlib.sha256(raw).hexdigest())
        require(isinstance(text, str) and 0 < len(text.encode("utf-8")) <= 262144)
        validate_text(text)
        require(not any(ord(c) < 32 and c not in "\n\t" for c in text))
        require(result["text_hash"] == content_hash(text) and 1 <= len(pages) <= MAX_PAGES)
        offset = 0
        for index, page in enumerate(pages, 1):
            require(set(page) == {"page", "span_start", "span_end", "text_hash"})
            require(
                page["page"] == index
                and type(page["span_start"]) is int
                and type(page["span_end"]) is int
            )
            require(page["span_start"] == offset and offset < page["span_end"] <= len(text))
            part = text[offset : page["span_end"]]
            require(
                part.strip() and part.endswith("\n") and content_hash(part) == page["text_hash"]
            )
            offset = page["span_end"]
        require(offset == len(text))
        require(
            result["warnings"]
            == [
                "Reading order, columns, tables and hidden text require visual verification; OCR is disabled."
            ]
        )
    except (AssertionError, KeyError, TypeError, ValueError, UnicodeError):
        raise ServiceError(422, "pdf_invalid_projection") from None
    return result


def projection_hash(upload, text):
    if upload.media_type != "application/pdf":
        if upload.extraction is not None:
            raise ServiceError(409, "document_content_changed")
        return upload.raw_hash
    artifact = dict(upload.extraction or {}) | {"text": text}
    validate_extraction(upload.raw_bytes, artifact)
    return artifact["text_hash"]


def page_location(upload, start, end):
    if upload.media_type != "application/pdf":
        return None
    matches = [
        p
        for p in (upload.extraction or {}).get("pages", [])
        if p["span_start"] <= start < end <= p["span_end"]
    ]
    if len(matches) != 1:
        raise ServiceError(409, "pdf_page_mapping_changed")
    return {
        "page": matches[0]["page"],
        "page_span_start": start - matches[0]["span_start"],
        "page_span_end": end - matches[0]["span_start"],
        "parser": upload.extraction["parser"],
        "text_hash": upload.extraction["text_hash"],
        "raw_hash": upload.raw_hash,
    }


def pdf_chunks(text, pages):
    from ada.documents import chunk_text

    result = []
    for page in pages:
        start, end = page["span_start"], page["span_end"]
        line = text.count("\n", 0, start)
        for chunk in chunk_text(text[start:end]):
            result.append(
                chunk
                | {
                    "ordinal": len(result) + 1,
                    "span_start": start + chunk["span_start"],
                    "span_end": start + chunk["span_end"],
                    "line_start": line + chunk["line_start"],
                    "line_end": line + chunk["line_end"],
                }
            )
    if len(result) > 512:
        raise ServiceError(413, "document_chunk_limit")
    return result
