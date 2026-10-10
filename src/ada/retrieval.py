"""Scope-first lexical/subject retrieval with exact evidence and valid-time filters.

Ranking never uses global corpus statistics. A bounded candidate pool is reranked
using only the authenticated conversation's scope. This is lexical retrieval,
not semantic inference, entity resolution, or automatic fact verification.
"""

import hashlib
import json
import re
import time
from datetime import UTC, datetime, timedelta
from typing import Literal, NotRequired, TypedDict
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, with_config
from sqlalchemy import case, func, literal, literal_column, or_, select, text
from sqlalchemy.orm import aliased

from ada.contracts import RetrievalBudgetOutput, RetrievalCandidateOutput
from ada.entities import IdentityView, entity_query_keys
from ada.entity_contracts import EntityChoice, EntityResolutionOutput
from ada.entity_models import ClaimEntityLink
from ada.evidence import content_hash
from ada.memory import EvidenceOutput, MemoryInput, Timestamp, time_ms
from ada.models import (
    Claim,
    ClaimSearch,
    DocumentChunk,
    DocumentSearch,
    DocumentUpload,
    Scope,
    Source,
    SourceVersion,
    now_ms,
)
from ada.search import SEARCH_VERSION, normalize, search_fields

CANDIDATE_LIMIT = 64
STOP_WORDS = frozenset(
    "a an and are as at be been by can could did do does for from had has have how i "
    "in is it me my of on or our please should tell that the their them they this to "
    "us was we were what when where which who why will with would you your about "
    "currently now remember memory memories".split()
)
EXPANSIONS = {
    "programming": ("language",),
    "languages": ("language",),
    "preferred": ("prefer", "preference"),
    "preferences": ("prefer", "preferred"),
    "prefer": ("preferred", "preference"),
    "db": ("database",),
    "databases": ("database",),
    "postgres": ("postgresql",),
    "chosen": ("decision", "decided"),
    "decide": ("decision", "decided"),
}


class RetrieveInput(MemoryInput):
    query: str = Field(min_length=1, max_length=4000)
    as_of: AwareDatetime | None = None
    limit: int = Field(default=8, ge=1, le=16, strict=True)
    budget_bytes: int = Field(default=2200, ge=0, le=12000, strict=True)
    use_documents: bool = Field(default=False, strict=True)

    @field_validator("query")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("query must not be blank")
        return value.strip()

    @field_validator("as_of")
    @classmethod
    def millisecond_time(cls, value):
        if value is not None:
            time_ms(value)
        return value


class CitationOutput(BaseModel):
    label: str = Field(pattern=r"^M[1-9][0-9]*$")
    claim_id: UUID
    scope_id: UUID
    subject: str
    predicate: str
    value: str
    kind: Literal["fact", "preference", "decision"]
    valid_from: Timestamp
    valid_to: Timestamp | None
    origin: Literal["user_asserted"]
    evidence: EvidenceOutput
    source_id: UUID
    source_version: int = Field(ge=1)
    conflict: bool
    subject_entity_id: UUID | None = None
    entity: EntityChoice | None = None


class DocumentCitationOutput(BaseModel):
    label: str = Field(pattern=r"^D[1-9][0-9]*$")
    origin: Literal["imported_document"]
    trust_class: Literal["imported_untrusted"]
    scope_id: UUID
    source_id: UUID
    source_version_id: UUID
    source_version: int = Field(ge=1)
    upload_id: UUID
    chunk_id: UUID
    filename: str
    media_type: Literal["text/plain", "text/markdown"]
    raw_hash: str
    available_from: Timestamp
    available_to: Timestamp | None
    published_at: Timestamp
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    evidence: EvidenceOutput


@with_config(ConfigDict(extra="allow"))
class DocumentCandidateOutput(TypedDict):
    chunk_id: UUID
    source_version_id: UUID
    channels: list[str]
    decision: str
    score: NotRequired[float]
    term_coverage: NotRequired[int]


class RetrievalPlanOutput(BaseModel):
    entity_keys: list[str] = Field(default_factory=list)
    entity_resolution: list[EntityResolutionOutput] = Field(default_factory=list)
    entity_ambiguity_in_context: bool = False
    entity_resolution_truncated: bool = False
    enabled: bool
    reason: Literal["ready", "date_required", "disabled", "prompt_upgrade_required"]
    time_mode: Literal["current", "as_of", "needs_date"]
    as_of: Timestamp | None
    query_terms: list[str]
    expanded_terms: list[str]
    subject_keys: list[str]
    overview: bool
    prompt_version: str | None = None
    documents_enabled: bool = False
    document_reason: Literal["ready", "date_required", "disabled", "prompt_upgrade_required"] = (
        "disabled"
    )


class RetrievalOutput(BaseModel):
    version: str
    scope_id: UUID
    plan: RetrievalPlanOutput
    candidates: list[RetrievalCandidateOutput]
    selected: list[CitationOutput]
    document_candidates: list[DocumentCandidateOutput] = Field(default_factory=list)
    document_selected: list[DocumentCitationOutput] = Field(default_factory=list)
    budget: RetrievalBudgetOutput
    retrieval_ms: int


def iso_time(ms):
    return (datetime(1970, 1, 1, tzinfo=UTC) + timedelta(milliseconds=ms)).isoformat(
        timespec="milliseconds"
    )


def plan_query(query, as_of=None, *, enabled=True, reason=None):
    normalized = normalize(query)
    dates = re.findall(r"\bas of\s+(\d{4}-\d{2}-\d{2})(?![\dTt]|\s+\d{1,2}:)", query, flags=re.I)
    at, mode = now_ms(), "current"
    if as_of is not None:
        at, mode = time_ms(as_of), "as_of"
    elif len(dates) == 1:
        try:
            at = time_ms(datetime.strptime(dates[0], "%Y-%m-%d").replace(tzinfo=UTC))
            mode = "as_of"
        except ValueError:
            at, mode = None, "needs_date"
    elif dates or re.search(
        r"\b(as of|last (year|month|week)|yesterday|previously|used to|back then|"
        r"before (\d{4}|the change|that|then)|"
        r"(in|on|during|after) \d{4}|at that time)\b|\bdid\b.*\bprefer\b|\bwas my\b",
        query,
        flags=re.I,
    ):
        at, mode = None, "needs_date"
    words = normalized.split()
    words = [w for w in words if w not in STOP_WORDS and not w.isdecimal() and len(w) <= 160]
    terms = list(dict.fromkeys(words))[:24]
    expanded = list(dict.fromkeys(terms + [x for t in terms for x in EXPANSIONS.get(t, ())]))
    raw = normalized.split()
    keys = {" ".join(raw[i : i + size]) for size in range(1, 5) for i in range(len(raw))}
    if any(w in normalized.split() for w in ("i", "me", "my", "we", "us", "our")):
        keys.add("user")
    overview = bool(
        re.search(r"\bwhat do you remember about (me|us)\b|\blist (my|our) memor", query, re.I)
    )
    return {
        "enabled": enabled,
        "reason": reason or ("date_required" if mode == "needs_date" else "ready"),
        "time_mode": mode,
        "as_of": at,
        "query_terms": terms,
        "expanded_terms": expanded,
        "subject_keys": sorted(keys)[:200],
        "overview": overview,
        "entity_keys": entity_query_keys(query),
    }


def message_cost(message):
    # Conservative UTF-8 bound, including fixed allowance for message framing.
    return len(message["content"].encode("utf-8")) + 64


def memory_message(selected, plan, document_selected=()):
    ambiguities = (
        [r for r in plan.get("entity_resolution", []) if r["state"] == "ambiguous"]
        if plan.get("entity_ambiguity_in_context")
        else []
    )
    if not selected and not document_selected and not ambiguities:
        return None
    items = [
        {
            "label": item["label"],
            "subject": item["subject"],
            "predicate": item["predicate"],
            "value": item["value"],
            "kind": item["kind"],
            "valid_from": iso_time(item["valid_from"]),
            "valid_to": iso_time(item["valid_to"]) if item["valid_to"] is not None else None,
            "quote": item["evidence"]["quote"],
            "conflict": item["conflict"],
        }
        for item in selected
    ]
    items += [
        {
            "label": item["label"],
            "origin": item["origin"],
            "trust_class": item["trust_class"],
            "source_id": item["source_id"],
            "source_version": item["source_version"],
            "filename": item["filename"],
            "media_type": item["media_type"],
            "available_from": iso_time(item["available_from"]),
            "available_to": iso_time(item["available_to"])
            if item["available_to"] is not None
            else None,
            "published_at": iso_time(item["published_at"]),
            "line_start": item["line_start"],
            "line_end": item["line_end"],
            "quote": item["evidence"]["quote"],
        }
        for item in document_selected
    ]
    for item, original in zip(items, selected):
        if original.get("entity"):
            item["entity"] = original["entity"]
    payload = {"type": "ada_memory_evidence", "as_of": iso_time(plan["as_of"]), "items": items}
    if ambiguities:
        ambiguous = ambiguities[0]
        payload["entity_ambiguity"] = {
            "name": ambiguous["name"],
            "alternatives": ambiguous["candidates"][:2],
            "more": len(ambiguous["candidates"]) > 2
            or ambiguous["truncated"]
            or len(ambiguities) > 1,
            "instruction": "Ask which explicit scoped entity is intended. Do not choose an ambiguous identity.",
        }
    return {
        "role": "user",
        "content": json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    }


def _base_query(owner, scope_id, at):
    return (
        select(Claim, SourceVersion, ClaimSearch)
        .join(
            ClaimSearch,
            (ClaimSearch.claim_id == Claim.id)
            & (ClaimSearch.owner_id == Claim.owner_id)
            & (ClaimSearch.scope_id == Claim.scope_id),
        )
        .join(
            SourceVersion,
            (SourceVersion.id == Claim.source_version_id)
            & (SourceVersion.owner_id == Claim.owner_id)
            & (SourceVersion.scope_id == Claim.scope_id),
        )
        .where(
            Claim.owner_id == owner,
            Claim.scope_id == scope_id,
            Claim.valid_from <= at,
            or_(Claim.valid_to.is_(None), Claim.valid_to > at),
            SourceVersion.trust_class == "user_explicit",
        )
    )


def _fts_condition(db, terms):
    if db.bind.dialect.name == "postgresql":
        config = literal_column("'simple'::regconfig")
        match = " | ".join("'" + word + "'" for word in terms)
        return func.to_tsvector(config, ClaimSearch.search_text).op("@@")(
            func.to_tsquery(config, match)
        )
    match = " OR ".join('"' + word + '"' for word in terms)
    ids = (
        select(literal_column("rowid"))
        .select_from(text("claim_fts"))
        .where(text("claim_fts MATCH :memory_fts"))
    )
    return literal_column("claim_search.rowid").in_(ids).params(memory_fts=match)


def _valid_evidence(claim, source, projection):
    # A projection is never factual authority. Refuse stale projections too.
    return (
        source.content_hash == claim.evidence_hash == content_hash(source.content)
        and 0 <= claim.span_start < claim.span_end <= len(source.content)
        and source.content[claim.span_start : claim.span_end] == claim.quote
        and bool(claim.quote.strip())
        and all(getattr(projection, key) == value for key, value in search_fields(claim).items())
    )


def _citation(claim, source, *, conflict):
    return {
        "claim_id": claim.id,
        "scope_id": claim.scope_id,
        "subject": claim.subject,
        "predicate": claim.predicate,
        "value": claim.value,
        "kind": claim.kind,
        "valid_from": claim.valid_from,
        "valid_to": claim.valid_to,
        "origin": "user_asserted",
        "evidence": {
            "source_version_id": source.id,
            "span_start": claim.span_start,
            "span_end": claim.span_end,
            "quote": claim.quote,
            "content_hash": source.content_hash,
        },
        "source_id": source.source_id,
        "source_version": source.version,
        "conflict": conflict,
    }


def _document_base_query(owner, scope_id, at):
    # Select a source's latest available published version BEFORE checking expiry.
    # An expired replacement cannot silently reveal an older version again.
    newer = aliased(DocumentUpload)
    replaced = (
        select(newer.id)
        .where(
            newer.owner_id == DocumentUpload.owner_id,
            newer.scope_id == DocumentUpload.scope_id,
            newer.source_id == DocumentUpload.source_id,
            newer.state == "ready",
            newer.published_at <= at,
            newer.available_from <= at,
            newer.version > DocumentUpload.version,
        )
        .exists()
    )
    return (
        select(DocumentChunk, SourceVersion, DocumentUpload, DocumentSearch)
        .join(
            DocumentUpload,
            (DocumentUpload.id == DocumentChunk.upload_id)
            & (DocumentUpload.owner_id == DocumentChunk.owner_id)
            & (DocumentUpload.scope_id == DocumentChunk.scope_id)
            & (DocumentUpload.source_id == DocumentChunk.source_id)
            & (DocumentUpload.source_version_id == DocumentChunk.source_version_id),
        )
        .join(
            SourceVersion,
            (SourceVersion.id == DocumentChunk.source_version_id)
            & (SourceVersion.owner_id == DocumentChunk.owner_id)
            & (SourceVersion.scope_id == DocumentChunk.scope_id)
            & (SourceVersion.source_id == DocumentChunk.source_id),
        )
        .join(
            Source,
            (Source.id == SourceVersion.source_id)
            & (Source.owner_id == SourceVersion.owner_id)
            & (Source.scope_id == SourceVersion.scope_id),
        )
        .join(
            DocumentSearch,
            (DocumentSearch.chunk_id == DocumentChunk.id)
            & (DocumentSearch.owner_id == DocumentChunk.owner_id)
            & (DocumentSearch.scope_id == DocumentChunk.scope_id),
        )
        .where(
            DocumentChunk.owner_id == owner,
            DocumentChunk.scope_id == scope_id,
            DocumentUpload.state == "ready",
            DocumentUpload.published_at <= at,
            DocumentUpload.available_from <= at,
            or_(DocumentUpload.available_to.is_(None), DocumentUpload.available_to > at),
            ~replaced,
            Source.kind == "imported_document",
            SourceVersion.trust_class == "imported_untrusted",
            SourceVersion.version == DocumentUpload.version,
        )
    )


def _document_fts_condition(db, terms):
    if db.bind.dialect.name == "postgresql":
        config = literal_column("'simple'::regconfig")
        match = " | ".join("'" + word + "'" for word in terms)
        return func.to_tsvector(config, DocumentSearch.search_text).op("@@")(
            func.to_tsquery(config, match)
        )
    match = " OR ".join('"' + word + '"' for word in terms)
    ids = (
        select(literal_column("rowid"))
        .select_from(text("document_fts"))
        .where(text("document_fts MATCH :document_fts_query"))
    )
    return literal_column("document_search.rowid").in_(ids).params(document_fts_query=match)


def _valid_document(chunk, source, upload, projection):
    if not (0 <= chunk.span_start < chunk.span_end <= len(source.content)):
        return False
    return (
        source.content_hash == chunk.content_hash == upload.raw_hash == content_hash(source.content)
        and upload.raw_hash == hashlib.sha256(upload.raw_bytes).hexdigest()
        and upload.raw_size == len(upload.raw_bytes)
        and source.content[chunk.span_start : chunk.span_end] == chunk.quote
        and chunk.quote_hash == content_hash(chunk.quote)
        and bool(chunk.quote.strip())
        and projection.search_text == normalize(chunk.quote)
        and chunk.line_start == source.content.count("\n", 0, chunk.span_start) + 1
        and chunk.line_end == source.content.count("\n", 0, chunk.span_end - 1) + 1
    )


def _document_citation(chunk, source, upload):
    return {
        "origin": "imported_document",
        "trust_class": "imported_untrusted",
        "scope_id": chunk.scope_id,
        "source_id": source.source_id,
        "source_version_id": source.id,
        "source_version": source.version,
        "upload_id": upload.id,
        "chunk_id": chunk.id,
        "filename": upload.filename,
        "media_type": upload.media_type,
        "raw_hash": upload.raw_hash,
        "available_from": upload.available_from,
        "available_to": upload.available_to,
        "published_at": upload.published_at,
        "line_start": chunk.line_start,
        "line_end": chunk.line_end,
        "evidence": {
            "source_version_id": source.id,
            "span_start": chunk.span_start,
            "span_end": chunk.span_end,
            "quote": chunk.quote,
            "content_hash": source.content_hash,
        },
    }


def _retrieve_documents(db, owner, scope_id, plan, result, *, limit, budget_bytes):
    terms = plan["expanded_terms"]
    if not terms:
        return
    padded = literal(" ") + DocumentSearch.search_text + literal(" ")
    coverage = sum(
        (case((padded.contains(" " + t + " ", autoescape=True), 1), else_=0) for t in terms),
        literal(0),
    )
    hits = db.execute(
        _document_base_query(owner, scope_id, plan["as_of"])
        .where(_document_fts_condition(db, terms))
        .order_by(coverage.desc(), DocumentChunk.id)
        .limit(CANDIDATE_LIMIT + 1)
    ).all()
    result["budget"]["candidate_pool_truncated"] |= len(hits) > CANDIDATE_LIMIT
    for rank, row in enumerate(hits[:CANDIDATE_LIMIT], 1):
        chunk, source, upload, projection = row
        candidate = {
            "chunk_id": chunk.id,
            "source_version_id": source.id,
            "channels": ["document_lexical"],
            "score": round(1 / (60 + rank), 8),
            "term_coverage": len(set(terms) & set(projection.search_text.split())),
            "decision": "invalid_evidence",
        }
        result["document_candidates"].append(candidate)
        if not _valid_document(*row):
            continue
        selected = result["document_selected"]
        tentative = selected + [
            _document_citation(chunk, source, upload) | {"label": f"D{len(selected) + 1}"}
        ]
        needed = message_cost(memory_message(result["selected"], plan, tentative))
        if len(result["selected"]) + len(tentative) > limit or needed > budget_bytes:
            candidate["decision"] = "context_budget"
            continue
        result["document_selected"] = tentative
        result["budget"]["memory_used_bytes"] = needed
        candidate["decision"] = "selected"


def retrieve(db, owner, scope_id, plan, *, limit=8, budget_bytes=2200, use_documents=False):
    """Caller must hold the owned scope's shared lock for a consistent snapshot."""
    started = time.perf_counter_ns()
    plan = dict(plan)
    documents_enabled = use_documents and plan["enabled"] and plan["time_mode"] != "needs_date"
    plan["documents_enabled"] = documents_enabled
    plan.setdefault(
        "document_reason",
        "ready" if documents_enabled else ("date_required" if use_documents else "disabled"),
    )
    result = {
        "version": "lexical-documents-v1" if documents_enabled else SEARCH_VERSION,
        "scope_id": scope_id,
        "plan": plan,
        "candidates": [],
        "selected": [],
        "document_candidates": [],
        "document_selected": [],
        "budget": {
            "memory_limit_bytes": budget_bytes,
            "memory_used_bytes": 0,
            "selected_limit": limit,
            "candidate_limit_per_channel": CANDIDATE_LIMIT,
            "candidate_pool_truncated": False,
        },
        "retrieval_ms": 0,
    }
    if not plan["enabled"] or plan["time_mode"] == "needs_date":
        return result
    base = _base_query(owner, scope_id, plan["as_of"])
    view = IdentityView(db, owner, scope_id, plan["as_of"])
    links = {
        r.claim_id: r.entity_id
        for r in db.scalars(
            select(ClaimEntityLink).where(
                ClaimEntityLink.owner_id == owner,
                ClaimEntityLink.scope_id == scope_id,
                ClaimEntityLink.created_at <= plan["as_of"],
                or_(ClaimEntityLink.valid_to.is_(None), ClaimEntityLink.valid_to > plan["as_of"]),
            )
        )
        if r.entity_id is not None
    }
    roots = {cid: view.root(eid) for cid, eid in links.items()}
    resolutions = [view.resolve(key) for key in plan.get("entity_keys", [])]
    matches = [r for r in resolutions if r["state"] != "absent"]
    # Exclude every ambiguous identity before truncating the display snapshot.
    # A truncated alias result cannot prove which linked claims are safe.
    ambiguous_roots = {
        str(c["id"]) for r in matches if r["state"] == "ambiguous" for c in r["candidates"]
    }
    if any(r["truncated"] for r in matches):
        ambiguous_roots.update(roots.values())
    matches.sort(key=lambda r: r["state"] != "ambiguous")
    resolutions = matches[:16]
    plan["entity_resolution_truncated"] = len(matches) > 16
    if "user" in plan["subject_keys"] and view.self_id:
        resolutions.append(view.resolve(self_reference=True))
    plan["entity_resolution"] = resolutions
    plan["entity_ambiguity_in_context"] = any(r["state"] == "ambiguous" for r in resolutions)
    clarification = memory_message([], plan)
    if clarification and message_cost(clarification) > budget_bytes:
        plan["entity_ambiguity_in_context"] = False
    elif clarification:
        result["budget"]["memory_used_bytes"] = message_cost(clarification)
    resolved_roots = {
        str(r["entity_id"]) for r in resolutions if r["state"] == "resolved"
    } - ambiguous_roots
    forbidden = [cid for cid, root in roots.items() if root in ambiguous_roots]
    if forbidden:
        base = base.where(Claim.id.not_in(forbidden))
    terms = plan["expanded_terms"]
    padded = literal(" ") + ClaimSearch.search_text + literal(" ")
    coverage = sum(
        (case((padded.contains(" " + t + " ", autoescape=True), 1), else_=0) for t in terms),
        literal(0),
    )
    ordered = base.order_by(coverage.desc(), Claim.id)
    channels = {}
    entity_claims = [cid for cid, root in roots.items() if root in resolved_roots]
    if entity_claims:
        channels["entity_alias"] = db.execute(
            ordered.where(Claim.id.in_(entity_claims)).limit(CANDIDATE_LIMIT + 1)
        ).all()
    if plan["overview"]:
        channels["overview"] = db.execute(
            base.order_by(Claim.valid_from.desc(), Claim.id).limit(CANDIDATE_LIMIT + 1)
        ).all()
    elif terms:
        channels["lexical"] = db.execute(
            ordered.where(_fts_condition(db, terms)).limit(CANDIDATE_LIMIT + 1)
        ).all()
        # The self-subject is useful only with a lexical hit. A pronoun alone
        # must not attach unrelated preferences to every question.
        keys = plan["subject_keys"]
        subject = or_(
            ClaimSearch.subject_key.in_([key for key in keys if key != "user"]),
            (ClaimSearch.subject_key == "user") & (coverage > 0) if "user" in keys else False,
        )
        channels["subject"] = db.execute(ordered.where(subject).limit(CANDIDATE_LIMIT + 1)).all()
    ranks, rows = {}, {}
    for channel, hits in channels.items():
        result["budget"]["candidate_pool_truncated"] |= len(hits) > CANDIDATE_LIMIT
        for rank, row in enumerate(hits[:CANDIDATE_LIMIT], 1):
            claim, _, projection = row
            rows[claim.id] = row
            detail = ranks.setdefault(claim.id, {"score": 0.0, "channels": []})
            detail["score"] += 1 / (60 + rank)
            detail["channels"].append(channel)
            detail["coverage"] = len(set(terms) & set(projection.search_text.split()))
    sorted_ids = sorted(rows, key=lambda key: (-ranks[key]["coverage"], -ranks[key]["score"], key))
    decisions, groups, seen = {}, [], set()
    for claim_id in sorted_ids:
        claim, source, projection = rows[claim_id]
        detail = ranks[claim_id]
        decisions[claim_id] = {
            "claim_id": claim_id,
            "score": round(detail["score"], 8),
            "term_coverage": detail["coverage"],
            "channels": detail["channels"],
            "decision": "ranked",
        }
        if not _valid_evidence(claim, source, projection):
            decisions[claim_id]["decision"] = "invalid_evidence"
            continue
        root = roots.get(claim.id)
        slot = (
            "entity" if root else "string",
            root or projection.subject_key,
            projection.predicate_key,
        )
        if slot in seen:
            continue
        seen.add(slot)
        # Fetch other currently valid values in this slot, even when they do
        # not match the query. Never present a convenient conflicting value alone.
        subject_condition = (
            Claim.id.in_([cid for cid, rid in roots.items() if rid == root])
            if root
            else (ClaimSearch.subject_key == projection.subject_key) & Claim.id.not_in(list(roots))
        )
        siblings = db.execute(
            base.where(subject_condition, ClaimSearch.predicate_key == projection.predicate_key)
            .order_by(Claim.id)
            .limit(CANDIDATE_LIMIT + 1)
        ).all()
        if len(siblings) > CANDIDATE_LIMIT:
            decisions[claim_id]["decision"] = "slot_too_large"
            result["budget"]["candidate_pool_truncated"] = True
            continue
        if not all(_valid_evidence(*sibling) for sibling in siblings):
            decisions[claim_id]["decision"] = "invalid_evidence"
            continue
        unique = {}
        siblings.sort(
            key=lambda row: (sorted_ids.index(row[0].id) if row[0].id in rows else 999, row[0].id)
        )
        for sibling, sibling_source, _ in siblings:
            key = (sibling.value, sibling.kind)
            unique.setdefault(key, (sibling, sibling_source))
            decisions.setdefault(
                sibling.id,
                {"claim_id": sibling.id, "channels": ["slot_check"], "decision": "ranked"},
            )
        conflict = len({key[0] for key in unique}) > 1
        group = []
        for c, s in unique.values():
            card = _citation(c, s, conflict=conflict)
            if c.id in roots:
                card.update(subject_entity_id=links[c.id], entity=view.choice(roots[c.id]))
            group.append(card)
        groups.append(group)
    selected = []
    for group in groups:
        tentative = selected + [
            item | {"label": f"M{len(selected) + i}"} for i, item in enumerate(group, 1)
        ]
        needed = message_cost(memory_message(tentative, plan))
        if len(tentative) > limit or needed > budget_bytes:
            for item in group:
                decisions[item["claim_id"]]["decision"] = "context_budget"
            continue
        selected = tentative
        for item in group:
            decisions[item["claim_id"]]["decision"] = "selected"
    result["selected"] = selected
    result["candidates"] = list(decisions.values())
    if selected:
        result["budget"]["memory_used_bytes"] = message_cost(memory_message(selected, plan))
    if documents_enabled:
        _retrieve_documents(
            db, owner, scope_id, plan, result, limit=limit, budget_bytes=budget_bytes
        )
    result["retrieval_ms"] = (time.perf_counter_ns() - started) // 1_000_000
    return result


def lock_scope_for_retrieval(db, owner, scope_id):
    from ada.errors import ServiceError

    scope = db.scalar(
        select(Scope)
        .where(Scope.owner_id == owner, Scope.id == scope_id)
        .with_for_update(read=True)
    )
    if scope is None:
        raise ServiceError(404, "scope_not_found")
    return scope


def public_trace(trace):
    return {
        "request_id": trace.request_id,
        "conversation_id": trace.conversation_id,
        "scope_id": trace.scope_id,
        "version": trace.version,
        "plan": trace.plan,
        "candidates": trace.candidates,
        "selected": trace.selected,
        "document_candidates": trace.document_candidates or [],
        "document_selected": trace.document_selected or [],
        "budget": trace.budget,
        "retrieval_ms": trace.retrieval_ms,
        "created_at": trace.created_at,
    }


def response_citations(response, trace):
    labels = list(dict.fromkeys(re.findall(r"\[(M\d+)\]", response or "")))
    selected = {item["label"]: item for item in trace.selected} if trace else {}
    return (
        [selected[label] for label in labels if label in selected],
        ["unknown_label:" + label for label in labels if label not in selected],
    )


def response_document_citations(response, trace):
    if trace is None or not (trace.plan.get("documents_enabled") or trace.document_selected):
        # Old saved answers only defined M labels. Do not reinterpret their
        # literal D text or alter completed replay warnings during an upgrade.
        return [], []
    labels = list(dict.fromkeys(re.findall(r"\[(D\d+)\]", response or "")))
    selected = {item["label"]: item for item in (trace.document_selected or [])} if trace else {}
    return (
        [selected[label] for label in labels if label in selected],
        ["unknown_label:" + label for label in labels if label not in selected],
    )
