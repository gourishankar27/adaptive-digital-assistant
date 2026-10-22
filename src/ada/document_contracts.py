"""Output-only contracts for authenticated imported document evidence."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from ada.memory import Timestamp


class DocumentUploadOutput(BaseModel):
    id: UUID
    scope_id: UUID
    source_id: UUID
    source_version_id: UUID
    version: int
    filename: str
    media_type: Literal["text/plain", "text/markdown", "application/pdf"]
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


class PdfPageOutput(BaseModel):
    page: int = Field(ge=1, le=16)
    span_start: int = Field(ge=0)
    span_end: int = Field(gt=0)
    text_hash: str


class PdfExtractionOutput(BaseModel):
    parser: Literal["pypdf-6.21.2-text-v1"]
    normalization: Literal["lf-page-newline-v1"]
    raw_hash: str
    text_hash: str
    image_id: str
    pages: list[PdfPageOutput] = Field(min_length=1, max_length=16)
    warnings: list[str]


class PdfLocationOutput(BaseModel):
    page: int = Field(ge=1, le=16)
    page_span_start: int = Field(ge=0)
    page_span_end: int = Field(gt=0)
    parser: Literal["pypdf-6.21.2-text-v1"]
    text_hash: str
    raw_hash: str


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
    extraction: PdfExtractionOutput | None = None


class DocumentChunkOutput(BaseModel):
    pdf: PdfLocationOutput | None = None
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
