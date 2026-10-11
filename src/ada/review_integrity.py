"""Recheck review provenance before any support enters fresh model context."""

from sqlalchemy import select

from ada.evidence import content_hash
from ada.models import Source, SourceVersion
from ada.proposal_models import ClaimSupport, MemoryProposal, MemoryReview


def valid_review(db, claim):
    if claim.provenance is None:
        return True
    if db is None or not isinstance(claim.provenance, dict):
        return False
    p = claim.provenance
    receipt = db.get(MemoryReview, (claim.owner_id, p.get("review_id")))
    proposal = db.get(MemoryProposal, (claim.owner_id, p.get("proposal_id")))
    if (
        receipt is None
        or proposal is None
        or receipt.scope_id != claim.scope_id
        or proposal.scope_id != claim.scope_id
        or receipt.proposal_id != proposal.id
        or receipt.decision != "accept"
        or receipt.claim_id != claim.id
        or receipt.endorsement_source_version_id != claim.source_version_id
    ):
        return False
    expected = {
        "version": "review-v1",
        "origin": "user_reviewed",
        "proposal_id": proposal.id,
        "review_id": receipt.id,
        "model": proposal.model,
        "extractor_version": proposal.extractor_version,
        "support": proposal.support,
    }
    if p != expected or not 1 <= len(proposal.support) <= 4:
        return False
    rows = db.scalars(
        select(ClaimSupport)
        .where(
            ClaimSupport.owner_id == claim.owner_id,
            ClaimSupport.scope_id == claim.scope_id,
            ClaimSupport.claim_id == claim.id,
        )
        .order_by(ClaimSupport.ordinal)
        .limit(5)
    ).all()
    if len(rows) != len(proposal.support):
        return False
    for row, frozen in zip(rows, proposal.support):
        source = db.scalar(
            select(SourceVersion).where(
                SourceVersion.owner_id == claim.owner_id,
                SourceVersion.scope_id == claim.scope_id,
                SourceVersion.id == row.source_version_id,
            )
        )
        origin = (
            db.scalar(
                select(Source.kind).where(
                    Source.owner_id == claim.owner_id,
                    Source.scope_id == claim.scope_id,
                    Source.id == source.source_id,
                )
            )
            if source
            else None
        )
        if source is None or row.review_id != receipt.id:
            return False
        if (
            source.content_hash != row.evidence_hash
            or content_hash(source.content) != row.evidence_hash
            or not 0 <= row.span_start < row.span_end <= len(source.content)
            or source.content[row.span_start : row.span_end] != row.quote
        ):
            return False
        current = {
            "source_id": source.source_id,
            "source_version": source.version,
            "source_origin": origin,
            "trust_class": source.trust_class,
            "evidence": {
                "source_version_id": source.id,
                "span_start": row.span_start,
                "span_end": row.span_end,
                "quote": row.quote,
                "content_hash": row.evidence_hash,
            },
        }
        if current != frozen:
            return False
    return True
