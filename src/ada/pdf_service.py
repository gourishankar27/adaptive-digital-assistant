"""Reserve original bytes, extract outside DB transactions, then publish atomically."""

import hashlib
import json

from ada.documents import MAX_UPLOAD_BYTES, DocumentService, _metadata, public_upload
from ada.errors import ServiceError
from ada.evidence import content_hash
from ada.pdfs import PARSER, pdf_chunks, validate_extraction


class PdfService(DocumentService):
    def __init__(self, sessions, parser):
        super().__init__(sessions)
        self.parser = parser

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
        authorize=None,
    ):
        from ada.memory import owned_scope

        with self.sessions() as db:
            owned_scope(db, owner, scope_id)
        if not filename.lower().endswith(".pdf") or media_type != "application/pdf":
            raise ServiceError(415, "pdf_type_invalid")
        _metadata(filename[:-4] + ".txt", "text/plain", available_from, available_to)
        if not self.parser.available:
            raise ServiceError(503, "pdf_parser_unavailable")
        if not isinstance(raw, bytes) or not 1 <= len(raw) <= MAX_UPLOAD_BYTES:
            raise ServiceError(413, "document_size_limit")
        if not raw.startswith(b"%PDF-"):
            raise ServiceError(415, "pdf_signature_invalid")
        hashed = hashlib.sha256(raw).hexdigest()
        fingerprint = content_hash(
            json.dumps(
                {
                    "scope": scope_id,
                    "source": source_id,
                    "filename": filename,
                    "media_type": media_type,
                    "raw_hash": hashed,
                    "from": available_from,
                    "to": available_to,
                    "parser": PARSER,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        row, created, process = self._reserve(
            owner,
            scope_id,
            upload_id,
            source_id,
            raw,
            hashed,
            fingerprint,
            filename,
            media_type,
            available_from,
            available_to,
            authorize=authorize,
        )
        if not process:
            return public_upload(row), created
        attempt = row.attempt
        try:
            result = validate_extraction(raw, self.parser.parse(raw))
            chunks = pdf_chunks(result["text"], result["pages"])
            self._publish(
                owner,
                scope_id,
                upload_id,
                attempt,
                result["text"],
                chunks,
                extraction={k: v for k, v in result.items() if k != "text"},
                authorize=authorize,
            )
        except ServiceError as error:
            self._fail(
                owner,
                scope_id,
                upload_id,
                attempt,
                error.code if error.code.startswith("pdf_") else "pdf_processing_failed",
            )
            if error.status in (401, 403, 404, 429, 503):
                raise
        except Exception:
            self._fail(owner, scope_id, upload_id, attempt, "pdf_processing_failed")
        return self.get(owner, scope_id, upload_id), created
