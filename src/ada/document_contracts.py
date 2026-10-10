"""Output-only contracts for authenticated imported document evidence."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from ada.memory import Timestamp


class DocumentUploadOutput(BaseModel):
    id: UUID
    scope_id: UUID
    source_id: UUID
    source_version_id: UUID
    version: int
    filename: str
    media_type: Literal["text/plain", "text/markdown"]
    input_hash: str
    raw_hash: str
    raw_size: int
    available_from: Timestamp
    available_to: Timestamp | None
    state: Literal["processing", "ready", "failed"]
    error_code: str | None
    created_at: Timestamp
    published_at: Timestamp | None
    chunk_count: int
    origin: Literal["imported_document"]
    trust_class: Literal["imported_untrusted"]


class DocumentVersionOutput(BaseModel):
    id: UUID
    source_id: UUID
    scope_id: UUID
    version: int
    content: str
    content_hash: str
    trust_class: Literal["imported_untrusted"]
    created_at: Timestamp
    upload: DocumentUploadOutput


class DocumentChunkOutput(BaseModel):
    id: UUID
    scope_id: UUID
    upload_id: UUID
    source_id: UUID
    source_version_id: UUID
    ordinal: int
    span_start: int
    span_end: int
    quote: str
    content_hash: str
    quote_hash: str
    line_start: int
    line_end: int
