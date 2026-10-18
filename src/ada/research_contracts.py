"""Additive research protocol, separate from saved chat and legacy agent DTOs."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, StrictStr

from ada.agent_contracts import AgentInputBase
from ada.memory import Timestamp

Kind = Literal["fetch", "search"]


class ResearchAction(AgentInputBase):
    id: UUID
    kind: Kind
    target: StrictStr = Field(min_length=1, max_length=2048)


class ResearchCreate(ResearchAction):
    question: StrictStr = Field(min_length=1, max_length=2000)
    version: Literal["ada-web-research-v1"] = "ada-web-research-v1"


class ResearchApproval(AgentInputBase):
    id: UUID
    call_id: UUID
    preview_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


class ResearchNoteInput(AgentInputBase):
    upload_id: UUID
    source_id: UUID


class WebSnippet(BaseModel):
    title: str
    url: str
    snippet: str


class WebTerms(BaseModel):
    license: str
    terms_url: str
    privacy_url: str


class WebEvidence(BaseModel):
    content_hash: str
    span_start: int
    span_end: int
    quote: str


class WebCitation(BaseModel):
    version: Literal["ada-web-citation-v1"] = "ada-web-citation-v1"
    label: str = Field(pattern=r"^W[1-3]$")
    receipt_id: UUID
    fetched_url: str
    final_url: str
    retrieved_at: Timestamp
    fresh_until: Timestamp
    parser_version: str
    source_origin: Literal["public_web"] = "public_web"
    trust_class: Literal["untrusted_web"] = "untrusted_web"
    terms: WebTerms
    evidence: WebEvidence
    extraction_truncated: bool = False


class WebSnapshotOutput(BaseModel):
    citation: WebCitation
    text: str


class ResearchPreview(BaseModel):
    id: UUID
    kind: Kind
    url: str
    recipient: str
    method: Literal["GET"] = "GET"
    disclosure: str
    preview_hash: str
    expires_at: Timestamp
    max_bytes: int
    deadline_seconds: int
    automatic_redirects: Literal[0] = 0
    external_writes: Literal[False] = False
    headers: dict[str, str]


class ResearchReceipt(BaseModel):
    id: UUID
    call_id: UUID
    state: str
    code: str | None = None
    redirect_url: str | None = None
    snippets: list[WebSnippet] = Field(default_factory=list)
    citation: WebCitation | None = None


class ResearchCall(BaseModel):
    preview: ResearchPreview
    status: str
    receipt: ResearchReceipt | None = None


class ResearchOutput(BaseModel):
    version: Literal["ada-web-research-v1"] = "ada-web-research-v1"
    id: UUID
    scope_id: UUID
    conversation_id: UUID
    question: str
    state: Literal[
        "pending_approval",
        "executing",
        "ready",
        "completed",
        "partial",
        "cancelled",
        "expired",
        "blocked",
        "failed",
        "unknown",
    ]
    response: str | None = None
    calls: list[ResearchCall]
    citations: list[WebCitation]
    citation_warnings: list[str]
    created_at: Timestamp
    remaining_calls: int
