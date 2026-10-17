"""Explicit calendar windows. Never turn an interval into an as-of timestamp."""

import json
from datetime import UTC, datetime, time, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, BaseModel, Field, field_validator
from sqlalchemy import case, literal, or_

from ada.memory import MemoryInput, Timestamp, time_ms
from ada.models import Claim, ClaimSearch
from ada.retrieval import (
    CANDIDATE_LIMIT,
    CitationOutput,
    _base_query,
    _citation,
    _fts_condition,
    _valid_evidence,
    plan_query,
)


class TimeSelection(MemoryInput):
    version: Literal["ada-time-window-v1"] = "ada-time-window-v1"
    expression: str = Field(min_length=1, max_length=80)
    timezone: str | None = Field(default=None, max_length=100)
    reference: AwareDatetime | None = None

    @field_validator("reference")
    @classmethod
    def precision(cls, value):
        if value is not None:
            time_ms(value)
        return value


class TimeResolution(BaseModel):
    version: Literal["ada-time-window-v1"] = "ada-time-window-v1"
    state: Literal["resolved", "needs_clarification"]
    reason: str
    timezone: str | None = None
    reference: Timestamp | None = None
    start: Timestamp | None = None
    end: Timestamp | None = None
    local_start: str | None = None
    local_end: str | None = None
    semantics: Literal["valid_time_overlap_current_recorded_state"] = (
        "valid_time_overlap_current_recorded_state"
    )


def _boundary(day, zone):
    naive = datetime.combine(day, time())
    instants = {
        value.astimezone(UTC)
        for fold in (0, 1)
        if (value := naive.replace(tzinfo=zone, fold=fold))
        .astimezone(UTC)
        .astimezone(zone)
        .replace(tzinfo=None)
        == naive
    }
    if len(instants) != 1:
        raise ValueError("ambiguous_or_missing_local_boundary")
    return instants.pop().astimezone(zone)


def resolve_time(body: TimeSelection):
    result = TimeResolution(state="needs_clarification", reason="timezone_and_reference_required")
    if not body.timezone or body.reference is None:
        return result
    result.timezone, result.reference = body.timezone, time_ms(body.reference)
    try:
        zone = ZoneInfo(body.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        result.reason = "unknown_timezone"
        return result
    expression = body.expression.strip().casefold().replace("_", " ")
    try:
        today = body.reference.astimezone(zone).date()
        if expression == "yesterday":
            first, last = today - timedelta(days=1), today
        elif expression == "last week":
            last = today - timedelta(days=today.weekday())
            first = last - timedelta(days=7)
        else:
            result.reason = "choose_yesterday_or_previous_monday_to_monday_week"
            return result
        start, end = _boundary(first, zone), _boundary(last, zone)
    except (ValueError, OverflowError):
        result.reason = "ambiguous_or_missing_local_boundary"
        return result
    result.state, result.reason = "resolved", "explicit_calendar_window"
    result.start, result.end = time_ms(start), time_ms(end)
    result.local_start, result.local_end = start.isoformat(), end.isoformat()
    return result


class WindowRetrieveInput(MemoryInput):
    query: str = Field(min_length=1, max_length=4000)
    selection: TimeSelection
    limit: int = Field(default=8, ge=1, le=16, strict=True)
    budget_bytes: int = Field(default=2200, ge=0, le=12000, strict=True)

    @field_validator("query")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("query must not be blank")
        return value.strip()


class WindowRetrievalOutput(BaseModel):
    version: Literal["ada-window-retrieval-v1"] = "ada-window-retrieval-v1"
    resolution: TimeResolution
    selected: list[CitationOutput] = Field(default_factory=list)
    candidate_pool_truncated: bool = False
    candidate_limit: int = CANDIDATE_LIMIT
    used_bytes: int = 0
    omitted_groups: int = 0
    invalid_groups: int = 0
    guidance: str = (
        "Compare exact assertions over the whole half-open valid-time interval. Different values "
        "may describe a change or conflict: ask rather than silently choosing. Recorded state is "
        "current, not a reconstruction of what was known then. Document availability and alias "
        "history are not interpreted by this claim-only version. Nothing was saved."
    )


def retrieve_window(db, owner, scope, body):
    resolution = resolve_time(body.selection)
    out = WindowRetrievalOutput(resolution=resolution)
    if resolution.state != "resolved":
        return out
    # Authorization, trust and both overlap bounds precede candidate selection.
    base = _base_query(owner, scope, None).where(
        Claim.valid_from < resolution.end,
        or_(Claim.valid_to.is_(None), Claim.valid_to > resolution.start),
    )
    plan = plan_query(body.query)
    terms = plan["expanded_terms"]
    if not terms:
        return out
    padded = literal(" ") + ClaimSearch.search_text + literal(" ")
    coverage = sum(
        (case((padded.contains(" " + t + " ", autoescape=True), 1), else_=0) for t in terms),
        literal(0),
    )
    rows = db.execute(
        base.where(_fts_condition(db, terms))
        .order_by(coverage.desc(), Claim.id)
        .limit(CANDIDATE_LIMIT + 1)
    ).all()
    out.candidate_pool_truncated = len(rows) > CANDIDATE_LIMIT
    seen = set()
    for claim, _, projection in rows[:CANDIDATE_LIMIT]:
        slot = (projection.subject_key, projection.predicate_key)
        if slot in seen:
            continue
        seen.add(slot)
        # Retain every overlapping value in the slot, or omit the entire group.
        siblings = db.execute(
            base.where(ClaimSearch.subject_key == slot[0], ClaimSearch.predicate_key == slot[1])
            .order_by(Claim.valid_from, Claim.id)
            .limit(CANDIDATE_LIMIT + 1)
        ).all()
        if len(siblings) > CANDIDATE_LIMIT:
            out.candidate_pool_truncated = True
            out.omitted_groups += 1
            continue
        if not all(_valid_evidence(*row, db=db) for row in siblings):
            out.invalid_groups += 1
            continue
        conflict = len({row[0].value for row in siblings}) > 1
        cards = [card.model_dump(mode="json") for card in out.selected]
        cards += [
            _citation(c, s, conflict=conflict) | {"label": f"M{len(cards) + i}"}
            for i, (c, s, _) in enumerate(siblings, 1)
        ]
        needed = len(json.dumps(cards, ensure_ascii=False, separators=(",", ":")).encode())
        if len(cards) > body.limit or needed > body.budget_bytes:
            out.omitted_groups += 1
            continue
        out.selected = [CitationOutput.model_validate(card) for card in cards]
        out.used_bytes = needed
    return out
