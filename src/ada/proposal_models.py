"""Private proposals, immutable review receipts and scoped supporting links."""

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class MemoryExtraction(Base):
    __tablename__ = "memory_extractions"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        CheckConstraint("state IN ('processing', 'completed', 'failed')", name="extraction_state"),
        Index("extraction_owner_created", "owner_id", "scope_id", "created_at", "id"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    sources: Mapped[list] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(120))
    extractor_version: Mapped[str] = mapped_column(String(40))
    validation: Mapped[dict] = mapped_column(JSON)
    error_code: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[int] = mapped_column(BigInteger)


class MemoryProposal(Base):
    __tablename__ = "memory_proposals"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "extraction_id"],
            ["memory_extractions.owner_id", "memory_extractions.scope_id", "memory_extractions.id"],
        ),
        CheckConstraint("status IN ('pending', 'accepted', 'rejected')", name="proposal_status"),
        CheckConstraint("revision >= 1", name="proposal_revision"),
        Index("proposal_inbox", "owner_id", "scope_id", "status", "created_at", "id"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    extraction_id: Mapped[str] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(String(20))
    revision: Mapped[int] = mapped_column(Integer)
    original_candidate: Mapped[dict] = mapped_column(JSON)
    candidate: Mapped[dict] = mapped_column(JSON)
    edits: Mapped[list] = mapped_column(JSON)
    support: Mapped[list] = mapped_column(JSON)
    model: Mapped[str] = mapped_column(String(120))
    extractor_version: Mapped[str] = mapped_column(String(40))
    validation: Mapped[dict] = mapped_column(JSON)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column(BigInteger)


class MemoryReview(Base):
    __tablename__ = "memory_reviews"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        UniqueConstraint("owner_id", "proposal_id"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "proposal_id"],
            ["memory_proposals.owner_id", "memory_proposals.scope_id", "memory_proposals.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "endorsement_source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        CheckConstraint(
            "(decision = 'accept' AND claim_id IS NOT NULL AND endorsement_source_version_id IS NOT NULL) OR (decision = 'reject' AND claim_id IS NULL AND endorsement_source_version_id IS NULL)",
            name="review_decision_consistent",
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    proposal_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    decision: Mapped[str] = mapped_column(String(20))
    revision: Mapped[int] = mapped_column(Integer)
    review_hash: Mapped[str] = mapped_column(String(64))
    annotation: Mapped[str] = mapped_column(Text)
    claim_id: Mapped[str | None] = mapped_column(String(36))
    endorsement_source_version_id: Mapped[str | None] = mapped_column(String(36))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)


class ClaimSupport(Base):
    __tablename__ = "claim_support"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "review_id"],
            ["memory_reviews.owner_id", "memory_reviews.scope_id", "memory_reviews.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        CheckConstraint("span_start >= 0 AND span_end > span_start", name="support_valid_span"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    claim_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ordinal: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    review_id: Mapped[str] = mapped_column(String(36))
    source_version_id: Mapped[str] = mapped_column(String(36))
    evidence_hash: Mapped[str] = mapped_column(String(64))
    span_start: Mapped[int] = mapped_column(Integer)
    span_end: Mapped[int] = mapped_column(Integer)
    quote: Mapped[str] = mapped_column(Text)
