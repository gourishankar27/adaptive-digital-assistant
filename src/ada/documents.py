"""Bounded, authenticated immutable text ingestion; no model or filesystem IO.

UTF-8 identity parser v1 preserves every decoded code point, including BOM and
CRLF. The SHA-256 of parsed UTF-8 is consequently identical to the raw hash.
Raw BYTEA/BLOB storage is private database storage, never a public filesystem URL.
"""

import hashlib
import json
import time
import unicodedata
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from ada.errors import ServiceError
from ada.evidence import content_hash
from ada.memory import owned_scope
from ada.models import (
    DocumentChunk,
    DocumentSearch,
    DocumentUpload,
    Scope,
    Source,
    SourceVersion,
    User,
    new_id,
    now_ms,
)
from ada.search import normalize

PARSER_VERSION = "utf8-identity-v1"
CHUNK_VERSION = "exact-codepoints-lines-v1"
MAX_UPLOAD_BYTES = 256 * 1024
MAX_FILES = 100
MAX_VERSIONS = 20
MAX_OWNER_BYTES = 10 * 1024 * 1024
MAX_CHUNK_CODEPOINTS = 1024
MAX_CHUNKS = 512
MAX_PARSE_SECONDS = 2
PROCESSING_LEASE_MS = 30_000
MAX_ATTEMPTS = 3
MIN_TIME = -62_135_596_800_000
MAX_TIME = 253_402_300_799_999


def _metadata(filename, media_type, available_from, available_to):
    if (
        not isinstance(filename, str)
        or not 1 <= len(filename) <= 120
        or any(c in filename for c in '/\\:<>"|?*')
        or ".." in filename
        or filename != filename.strip()
        or filename.endswith(".")
        or any(unicodedata.category(c).startswith("C") for c in filename)
    ):
        raise ServiceError(422, "document_invalid_filename")
    try:
        if len(filename.encode("utf-8")) > 240:
            raise ServiceError(422, "document_invalid_filename")
    except UnicodeError:
        raise ServiceError(422, "document_invalid_filename") from None
    stem, dot, extension = filename.rpartition(".")
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if (
        not dot
        or not stem
        or stem.split(".", 1)[0].rstrip(" .").upper() in reserved
        or extension.lower() not in {"txt", "md", "markdown"}
    ):
        raise ServiceError(422, "document_invalid_filename")
    if media_type not in {"text/plain", "text/markdown"}:
        raise ServiceError(415, "document_unsupported_type")
    for value in (available_from, available_to):
        if value is not None and (type(value) is not int or not MIN_TIME <= value <= MAX_TIME):
            raise ServiceError(422, "document_invalid_availability")
    if available_from is not None and available_to is not None and available_to <= available_from:
        raise ServiceError(422, "document_invalid_availability")


def parse_text(raw: bytes) -> str:
    if not raw or len(raw) > MAX_UPLOAD_BYTES:
        raise ServiceError(413, "document_size_limit")
    if raw.startswith(
        (
            b"%PDF-",
            b"PK\x03\x04",
            b"PK\x05\x06",
            b"PK\x07\x08",
            b"\x1f\x8b",
            b"Rar!",
            b"7z\xbc\xaf\x27\x1c",
            b"\x89PNG",
            b"\xff\xd8\xff",
        )
    ):
        raise ServiceError(415, "document_unsupported_format")
    try:
        content = raw.decode("utf-8", errors="strict")
    except UnicodeError:
        raise ServiceError(422, "document_invalid_encoding") from None
    if any((ord(c) < 32 and c not in "\t\r\n") or ord(c) == 127 for c in content):
        raise ServiceError(422, "document_invalid_text")
    if not content.removeprefix("\ufeff").strip():
        raise ServiceError(422, "document_empty_text")
    return content


def chunk_text(content: str) -> list[dict]:
    chunks, start, line = [], 0, 1
    while start < len(content):
        end = min(len(content), start + MAX_CHUNK_CODEPOINTS)
        if end < len(content):
            boundary = content.rfind("\n", start, end)
            if boundary >= start:
                end = boundary + 1
        quote = content[start:end]
        next_line = line + quote.count("\n")
        chunks.append(
            {
                "ordinal": len(chunks) + 1,
                "span_start": start,
                "span_end": end,
                "quote": quote,
                "quote_hash": content_hash(quote),
                "line_start": line,
                "line_end": line + quote[:-1].count("\n"),
            }
        )
        if len(chunks) > MAX_CHUNKS:
            raise ServiceError(413, "document_chunk_limit")
        start, line = end, next_line
    return chunks


def public_upload(row):
    fields = (
        "id",
        "scope_id",
        "source_id",
        "source_version_id",
        "version",
        "filename",
        "media_type",
        "input_hash",
        "raw_hash",
        "raw_size",
        "available_from",
        "available_to",
        "state",
        "error_code",
        "created_at",
        "published_at",
        "chunk_count",
    )
    return {name: getattr(row, name) for name in fields} | {
        "origin": "imported_document",
        "trust_class": "imported_untrusted",
    }


def public_chunk(row):
    fields = (
        "id",
        "scope_id",
        "upload_id",
        "source_id",
        "source_version_id",
        "ordinal",
        "span_start",
        "span_end",
        "quote",
        "content_hash",
        "quote_hash",
        "line_start",
        "line_end",
    )
    return {name: getattr(row, name) for name in fields}


def _owned_upload(db, owner, scope_id, *, upload_id=None, source_version_id=None):
    query = select(DocumentUpload).where(DocumentUpload.owner_id == owner)
    if scope_id is not None:
        query = query.where(DocumentUpload.scope_id == scope_id)
    if upload_id is not None:
        query = query.where(DocumentUpload.id == upload_id)
    if source_version_id is not None:
        query = query.where(
            DocumentUpload.source_version_id == source_version_id, DocumentUpload.state == "ready"
        )
    row = db.scalar(query)
    if row is None:
        raise ServiceError(404, "document_not_found")
    owned_scope(db, owner, row.scope_id)
    return row


def _validate_parsed(raw, text, chunks, extraction=None):
    if extraction is not None:
        from ada.pdfs import pdf_chunks, validate_extraction

        validate_extraction(raw, extraction | {"text": text})
        if chunks != pdf_chunks(text, extraction["pages"]):
            raise ServiceError(422, "pdf_invalid_projection")
        return
    if (
        not isinstance(text, str)
        or text.encode("utf-8") != raw
        or not 1 <= len(chunks) <= MAX_CHUNKS
    ):
        raise ServiceError(422, "document_invalid_projection")
    offset, line = 0, 1
    for ordinal, chunk in enumerate(chunks, 1):
        quote = chunk["quote"]
        end = offset + len(quote)
        if (
            chunk["ordinal"] != ordinal
            or chunk["span_start"] != offset
            or chunk["span_end"] != end
            or not 1 <= len(quote) <= MAX_CHUNK_CODEPOINTS
            or text[offset:end] != quote
            or chunk["quote_hash"] != content_hash(quote)
            or chunk["line_start"] != line
            or chunk["line_end"] != line + quote[:-1].count("\n")
        ):
            raise ServiceError(422, "document_invalid_projection")
        offset, line = end, line + quote.count("\n")
    if offset != len(text):
        raise ServiceError(422, "document_invalid_projection")


class DocumentService:
    def __init__(self, sessions):
        self.sessions = sessions

    @staticmethod
    def _parse(raw):
        start = time.monotonic()
        text = parse_text(raw)
        chunks = chunk_text(text)
        _validate_parsed(raw, text, chunks)
        if time.monotonic() - start > MAX_PARSE_SECONDS:
            raise ServiceError(422, "document_parse_time_limit")
        return text, chunks

    def upload(
        self,
        owner,
        scope_id,
        upload_id,
        raw,
        *,
        source_id,
        filename,
        media_type,
        available_from=None,
        available_to=None,
    ):
        # Every durable read/write starts with an authenticated owner and owned scope.
        with self.sessions() as db:
            owned_scope(db, owner, scope_id)
        _metadata(filename, media_type, available_from, available_to)
        if not isinstance(raw, bytes) or not 1 <= len(raw) <= MAX_UPLOAD_BYTES:
            raise ServiceError(413, "document_size_limit")
        raw_hash = hashlib.sha256(raw).hexdigest()
        fingerprint = content_hash(
            json.dumps(
                {
                    "scope_id": scope_id,
                    "source_id": source_id,
                    "filename": filename,
                    "media_type": media_type,
                    "raw_hash": raw_hash,
                    "available_from": available_from,
                    "available_to": available_to,
                    "parser": PARSER_VERSION,
                    "chunker": CHUNK_VERSION,
                },
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        try:
            row, created, process = self._reserve(
                owner,
                scope_id,
                upload_id,
                source_id,
                raw,
                raw_hash,
                fingerprint,
                filename,
                media_type,
                available_from,
                available_to,
            )
        except IntegrityError as error:
            raise ServiceError(409, "document_conflict") from error
        if not process:
            return public_upload(row), created
        attempt = row.attempt
        try:
            # No DB transaction or network/provider work occurs while parsing.
            text, chunks = self._parse(raw)
            _validate_parsed(raw, text, chunks)
            self._publish(owner, scope_id, upload_id, attempt, text, chunks)
        except ServiceError as error:
            allowed = {
                "document_invalid_encoding",
                "document_invalid_text",
                "document_empty_text",
                "document_unsupported_format",
                "document_chunk_limit",
                "document_parse_time_limit",
                "document_invalid_projection",
            }
            self._fail(
                owner,
                scope_id,
                upload_id,
                attempt,
                error.code if error.code in allowed else "document_processing_failed",
            )
        except Exception:
            # Do not persist exception messages, bytes, paths or parser internals.
            self._fail(owner, scope_id, upload_id, attempt, "document_processing_failed")
        return self.get(owner, scope_id, upload_id), created

    def _reserve(
        self,
        owner,
        scope_id,
        upload_id,
        source_id,
        raw,
        raw_hash,
        fingerprint,
        filename,
        media_type,
        available_from,
        available_to,
    ):
        with self.sessions.begin() as db:
            # Cross-scope quotas serialize on the owner first; all document writes
            # use owner -> scope -> upload. Retrieval/claims need only scope locks.
            if db.scalar(select(User).where(User.id == owner).with_for_update()) is None:
                raise ServiceError(404, "scope_not_found")
            owned_scope(db, owner, scope_id, lock=True)
            timestamp = now_ms()
            existing = db.get(DocumentUpload, (owner, upload_id))
            if existing is not None:
                if (
                    existing.input_hash != fingerprint
                    or existing.scope_id != scope_id
                    or existing.raw_bytes != raw
                ):
                    raise ServiceError(409, "document_upload_id_reused")
                if (
                    existing.state != "processing"
                    or existing.started_at + PROCESSING_LEASE_MS > timestamp
                ):
                    return existing, False, False
                if existing.attempt >= MAX_ATTEMPTS:
                    existing.state, existing.error_code = (
                        "failed",
                        "document_processing_interrupted",
                    )
                    return existing, False, False
                existing.attempt += 1
                existing.started_at = timestamp
                return existing, False, True
            source = db.scalar(
                select(Source).where(Source.id == source_id, Source.owner_id == owner)
            )
            if source is not None and (
                source.scope_id != scope_id or source.kind != "imported_document"
            ):
                raise ServiceError(409, "document_source_id_reused")
            count, size = db.execute(
                select(func.count(), func.coalesce(func.sum(DocumentUpload.raw_size), 0)).where(
                    DocumentUpload.owner_id == owner
                )
            ).one()
            if count >= MAX_FILES:
                raise ServiceError(413, "document_file_quota")
            if size + len(raw) > MAX_OWNER_BYTES:
                raise ServiceError(413, "document_storage_quota")
            last_version = (
                db.scalar(
                    select(func.max(DocumentUpload.version)).where(
                        DocumentUpload.owner_id == owner, DocumentUpload.source_id == source_id
                    )
                )
                or 0
            )
            if last_version >= MAX_VERSIONS:
                raise ServiceError(413, "document_version_quota")
            availability = available_from if available_from is not None else timestamp
            if available_to is not None and available_to <= availability:
                raise ServiceError(422, "document_invalid_availability")
            if source is None:
                db.add(
                    Source(
                        id=source_id,
                        owner_id=owner,
                        scope_id=scope_id,
                        kind="imported_document",
                        created_at=timestamp,
                    )
                )
                db.flush()
            row = DocumentUpload(
                owner_id=owner,
                id=upload_id,
                scope_id=scope_id,
                source_id=source_id,
                source_version_id=new_id(),
                version=last_version + 1,
                filename=filename,
                media_type=media_type,
                input_hash=fingerprint,
                raw_hash=raw_hash,
                raw_bytes=raw,
                raw_size=len(raw),
                available_from=availability,
                available_to=available_to,
                state="processing",
                error_code=None,
                created_at=timestamp,
                started_at=timestamp,
                attempt=1,
                chunk_count=0,
                published_at=None,
            )
            db.add(row)
            db.flush()
            return row, True, True

    def _publish(self, owner, scope_id, upload_id, attempt, text, chunks, extraction=None):
        with self.sessions.begin() as db:
            owned_scope(db, owner, scope_id, lock=True)
            row = _owned_upload(db, owner, scope_id, upload_id=upload_id)
            if row.state != "processing" or row.attempt != attempt:
                return
            _validate_parsed(row.raw_bytes, text, chunks, extraction)
            parsed_hash = content_hash(text)
            if (extraction is None and parsed_hash != row.raw_hash) or (extraction is not None and row.media_type != "application/pdf"):
                raise ServiceError(409, "document_invalid_projection")
            row.extraction = extraction
            timestamp = now_ms()
            db.add(
                SourceVersion(
                    id=row.source_version_id,
                    owner_id=owner,
                    scope_id=scope_id,
                    source_id=row.source_id,
                    version=row.version,
                    content=text,
                    content_hash=parsed_hash,
                    trust_class="imported_untrusted",
                    created_at=timestamp,
                )
            )
            db.flush()
            for fields in chunks:
                chunk_id = str(
                    uuid5(
                        NAMESPACE_URL, f"ada/document/{row.source_version_id}/{fields['ordinal']}"
                    )
                )
                chunk = DocumentChunk(
                    id=chunk_id,
                    owner_id=owner,
                    scope_id=scope_id,
                    upload_id=upload_id,
                    source_id=row.source_id,
                    source_version_id=row.source_version_id,
                    content_hash=parsed_hash,
                    **fields,
                )
                db.add(chunk)
                db.flush()
                db.add(
                    DocumentSearch(
                        chunk_id=chunk_id,
                        owner_id=owner,
                        scope_id=scope_id,
                        search_text=normalize(chunk.quote),
                    )
                )
            db.flush()
            row.state, row.published_at, row.chunk_count = "ready", timestamp, len(chunks)

    def _fail(self, owner, scope_id, upload_id, attempt, error_code):
        with self.sessions.begin() as db:
            owned_scope(db, owner, scope_id, lock=True)
            row = _owned_upload(db, owner, scope_id, upload_id=upload_id)
            if row.state == "processing" and row.attempt == attempt:
                row.state, row.error_code = "failed", error_code

    def get(self, owner, scope_id, upload_id):
        with self.sessions() as db:
            return public_upload(_owned_upload(db, owner, scope_id, upload_id=upload_id))

    def list(self, owner, scope_id, *, limit=50, offset=0):
        with self.sessions() as db:
            owned_scope(db, owner, scope_id)
            rows = db.scalars(
                select(DocumentUpload)
                .where(DocumentUpload.owner_id == owner, DocumentUpload.scope_id == scope_id)
                .order_by(DocumentUpload.created_at.desc(), DocumentUpload.id)
                .limit(limit)
                .offset(offset)
            )
            return [public_upload(row) for row in rows]

    def versions(self, owner, source_id, *, limit=50, offset=0):
        with self.sessions() as db:
            source = db.scalar(
                select(Source).where(
                    Source.owner_id == owner,
                    Source.id == source_id,
                    Source.kind == "imported_document",
                )
            )
            if source is None:
                raise ServiceError(404, "document_not_found")
            owned_scope(db, owner, source.scope_id)
            rows = db.scalars(
                select(DocumentUpload)
                .where(
                    DocumentUpload.owner_id == owner,
                    DocumentUpload.scope_id == source.scope_id,
                    DocumentUpload.source_id == source_id,
                    DocumentUpload.state == "ready",
                )
                .order_by(DocumentUpload.version.desc())
                .limit(limit)
                .offset(offset)
            )
            return [public_upload(row) for row in rows]

    def version(self, owner, scope_id, source_version_id):
        from ada.pdfs import projection_hash
        with self.sessions() as db:
            row = _owned_upload(db, owner, scope_id, source_version_id=source_version_id)
            version = db.scalar(
                select(SourceVersion).where(
                    SourceVersion.owner_id == owner,
                    SourceVersion.scope_id == row.scope_id,
                    SourceVersion.id == source_version_id,
                    SourceVersion.source_id == row.source_id,
                    SourceVersion.trust_class == "imported_untrusted",
                )
            )
            if (
                version is None
                or content_hash(version.content) != projection_hash(row, version.content)
                or version.content_hash != projection_hash(row, version.content)
            ):
                raise ServiceError(409, "document_content_changed")
            return {
                "id": version.id,
                "source_id": version.source_id,
                "scope_id": version.scope_id,
                "version": version.version,
                "content": version.content,
                "content_hash": version.content_hash,
                "trust_class": version.trust_class,
                "created_at": version.created_at,
                "upload": public_upload(row),
                **({"extraction": row.extraction} if row.extraction is not None else {}),
            }

    def chunks(self, owner, scope_id, source_version_id, *, limit=50, offset=0):
        from ada.pdfs import page_location
        with self.sessions() as db:
            row = _owned_upload(db, owner, scope_id, source_version_id=source_version_id)
            chunks = db.scalars(
                select(DocumentChunk)
                .where(
                    DocumentChunk.owner_id == owner,
                    DocumentChunk.scope_id == row.scope_id,
                    DocumentChunk.source_version_id == source_version_id,
                    DocumentChunk.upload_id == row.id,
                )
                .order_by(DocumentChunk.ordinal)
                .limit(limit)
                .offset(offset)
            )
            return [public_chunk(chunk) | ({"pdf": page_location(row, chunk.span_start, chunk.span_end)} if row.media_type == "application/pdf" else {}) for chunk in chunks]

    def raw(self, owner, scope_id, source_version_id):
        with self.sessions() as db:
            row = _owned_upload(db, owner, scope_id, source_version_id=source_version_id)
            if (
                hashlib.sha256(row.raw_bytes).hexdigest() != row.raw_hash
                or len(row.raw_bytes) != row.raw_size
            ):
                raise ServiceError(409, "document_content_changed")
            return row.raw_bytes, row.media_type, row.filename


def rebuild_document_search(sessions):
    from ada.pdfs import projection_hash
    """Local operator rebuild, validating imported evidence before indexing."""
    count = 0
    with sessions.begin() as db:
        scopes = db.scalars(select(Scope).order_by(Scope.id).with_for_update()).all()
        for scope in scopes:
            db.execute(
                delete(DocumentSearch).where(
                    DocumentSearch.owner_id == scope.owner_id, DocumentSearch.scope_id == scope.id
                )
            )
            rows = db.execute(
                select(DocumentChunk, SourceVersion, DocumentUpload)
                .join(
                    SourceVersion,
                    (SourceVersion.owner_id == DocumentChunk.owner_id)
                    & (SourceVersion.scope_id == DocumentChunk.scope_id)
                    & (SourceVersion.id == DocumentChunk.source_version_id),
                )
                .join(
                    DocumentUpload,
                    (DocumentUpload.owner_id == DocumentChunk.owner_id)
                    & (DocumentUpload.scope_id == DocumentChunk.scope_id)
                    & (DocumentUpload.id == DocumentChunk.upload_id),
                )
                .where(
                    DocumentChunk.owner_id == scope.owner_id,
                    DocumentChunk.scope_id == scope.id,
                    DocumentUpload.state == "ready",
                )
            )
            for chunk, version, upload in rows:
                if (
                    version.trust_class != "imported_untrusted"
                    or version.content_hash != content_hash(version.content)
                    or chunk.content_hash != version.content_hash
                    or projection_hash(upload, version.content) != version.content_hash
                    or version.content[chunk.span_start : chunk.span_end] != chunk.quote
                    or chunk.quote_hash != content_hash(chunk.quote)
                ):
                    raise ServiceError(409, "document_content_changed")
                db.add(
                    DocumentSearch(
                        chunk_id=chunk.id,
                        owner_id=scope.owner_id,
                        scope_id=scope.id,
                        search_text=normalize(chunk.quote),
                    )
                )
                count += 1
    return count
