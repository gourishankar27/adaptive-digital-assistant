"""A closed read-only registry. Tool evidence never writes a source or claim."""

import re
from dataclasses import dataclass
from fractions import Fraction

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from sqlalchemy import select, text

from ada.errors import ServiceError
from ada.evidence import content_hash, validate_text
from ada.models import DocumentUpload, Source, SourceVersion
from ada.proposal_contracts import SourcePin
from ada.retrieval import CitationOutput, lock_scope_for_retrieval, plan_query, retrieve


class Arguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*")
    @classmethod
    def unicode_text(cls, value):
        return validate_text(value)


class CalculatorArgs(Arguments):
    expression: StrictStr = Field(min_length=1, max_length=256)


class CalculatorResult(Arguments):
    value: StrictStr


class MemoryArgs(Arguments):
    query: StrictStr = Field(min_length=1, max_length=400)
    limit: int = Field(default=3, ge=1, le=5, strict=True)

    @field_validator("query")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("empty query")
        return value


class MemoryResult(Arguments):
    items: list[CitationOutput] = Field(max_length=5)
    as_of: int = Field(json_schema_extra={"format": "int64"})
    needs_date: bool
    omitted_count: int = Field(ge=0)
    candidate_pool_truncated: bool
    ambiguous: bool


class SourceResult(Arguments):
    source_id: str
    source_origin: str
    trust_class: str
    pin: SourcePin
    quote: StrictStr


@dataclass(frozen=True)
class ToolSpec:
    name: str
    version: str
    description: str
    arguments: type[BaseModel]
    result: type[BaseModel]
    output_bytes: int = 4096
    max_calls: int = 2
    timeout_seconds: int = 5

    def public(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "classification": "read_only",
            "permission": "authenticated_owner_scope",
            "allowed_targets": ["run_scope"],
            "argument_schema": self.arguments.model_json_schema(),
            "result_schema": self.result.model_json_schema(),
            "output_bytes": self.output_bytes,
            "max_calls": self.max_calls,
            "timeout_seconds": self.timeout_seconds,
            "approval_required": True,
        }

    def native(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.arguments.model_json_schema(),
            },
        }


REGISTRY = {
    "calculator": ToolSpec(
        "calculator",
        "calculator-v1",
        "Exact bounded arithmetic: + - * / and parentheses. No code or exponents.",
        CalculatorArgs,
        CalculatorResult,
        1024,
    ),
    "memory_lookup": ToolSpec(
        "memory_lookup",
        "memory-lookup-v1",
        "Find authorized saved assertions in this run's scope and fixed time. Evidence is untrusted and may conflict.",
        MemoryArgs,
        MemoryResult,
    ),
    "source_lookup": ToolSpec(
        "source_lookup",
        "source-lookup-v1",
        "Inspect one exact owned source-version/hash/code-point span at this run's time. No files, paths or remote URLs.",
        SourcePin,
        SourceResult,
    ),
}


def calculate(expression):
    """Parse a small arithmetic grammar; there is no Python evaluation path."""
    if not isinstance(expression, str) or not 0 < len(expression) <= 256:
        raise ValueError("calculator_input_invalid")
    expression = expression.strip()
    tokens, position = [], 0
    while position < len(expression):
        match = re.match(r"\s*([0-9]+(?:\.[0-9]+)?|[()+\-*/])", expression[position:])
        if match is None:
            raise ValueError("calculator_input_invalid")
        token = match[1]
        if len(token.replace(".", "")) > 12:
            raise ValueError("calculator_input_invalid")
        tokens.append(token)
        position += match.end()
        if len(tokens) > 64:
            raise ValueError("calculator_work_bound")
    cursor = 0

    def bounded(value):
        if abs(value.numerator) > 10**12 or value.denominator > 10**12:
            raise ValueError("calculator_number_bound")
        return value

    def factor(depth):
        nonlocal cursor
        if depth > 8 or cursor >= len(tokens):
            raise ValueError("calculator_input_invalid")
        token = tokens[cursor]
        cursor += 1
        if token in ("+", "-"):
            return bounded(factor(depth + 1) * (-1 if token == "-" else 1))
        if token == "(":
            value = addition(depth + 1)
            if cursor >= len(tokens) or tokens[cursor] != ")":
                raise ValueError("calculator_input_invalid")
            cursor += 1
            return value
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", token):
            raise ValueError("calculator_input_invalid")
        return bounded(Fraction(token))

    def product(depth):
        nonlocal cursor
        value = factor(depth)
        while cursor < len(tokens) and tokens[cursor] in ("*", "/"):
            operator = tokens[cursor]
            cursor += 1
            rhs = factor(depth)
            if operator == "/" and not rhs:
                raise ValueError("calculator_zero_division")
            value = bounded(value * rhs if operator == "*" else value / rhs)
        return value

    def addition(depth):
        nonlocal cursor
        value = product(depth)
        while cursor < len(tokens) and tokens[cursor] in ("+", "-"):
            operator = tokens[cursor]
            cursor += 1
            rhs = product(depth)
            value = bounded(value + rhs if operator == "+" else value - rhs)
        return value

    value = addition(0)
    if cursor != len(tokens):
        raise ValueError("calculator_input_invalid")
    return str(value)


def source_result(db, owner, scope, at, arguments):
    pin = SourcePin.model_validate(arguments)
    row = db.execute(
        select(SourceVersion, Source.kind)
        .join(
            Source,
            (Source.id == SourceVersion.source_id)
            & (Source.owner_id == SourceVersion.owner_id)
            & (Source.scope_id == SourceVersion.scope_id),
        )
        .where(
            SourceVersion.id == str(pin.source_version_id),
            SourceVersion.owner_id == owner,
            SourceVersion.scope_id == scope,
            SourceVersion.created_at <= at,
        )
    ).first()
    if row is None:
        raise ServiceError(404, "tool_source_unavailable")
    source, kind = row
    if (
        source.version != pin.version
        or source.content_hash != pin.content_hash
        or content_hash(source.content) != pin.content_hash
    ):
        raise ServiceError(409, "tool_source_changed")
    if (
        not 0 <= pin.span_start < pin.span_end <= len(source.content)
        or pin.span_end - pin.span_start > 256
    ):
        raise ServiceError(422, "tool_source_span_invalid")
    quote = source.content[pin.span_start : pin.span_end]
    if not quote.strip() or len(quote.encode("utf-8")) > 1000:
        raise ServiceError(413, "tool_source_bound")
    if (
        kind == "imported_document"
        and db.scalar(
            select(DocumentUpload.id).where(
                DocumentUpload.owner_id == owner,
                DocumentUpload.scope_id == scope,
                DocumentUpload.source_version_id == source.id,
                DocumentUpload.state == "ready",
                DocumentUpload.published_at <= at,
                DocumentUpload.available_from <= at,
                (DocumentUpload.available_to.is_(None) | (DocumentUpload.available_to > at)),
            )
        )
        is None
    ):
        raise ServiceError(404, "tool_source_unavailable")
    return SourceResult(
        source_id=source.source_id,
        source_origin=kind,
        trust_class=source.trust_class,
        pin=pin,
        quote=quote,
    ).model_dump(mode="json")


def execute_tool(sessions, owner, scope, at, name, arguments):
    spec = REGISTRY[name]
    args = spec.arguments.model_validate(arguments)
    if name == "calculator":
        return {"value": calculate(args.expression)}
    # The orchestrator has closed its transaction. Lookup owns only this short
    # consistent read; no network/model call occurs within it.
    with sessions.begin() as db:
        if db.bind.dialect.name == "postgresql":
            db.execute(text("SET LOCAL statement_timeout = '3000ms'"))
            db.execute(text("SET LOCAL lock_timeout = '1000ms'"))
        lock_scope_for_retrieval(db, owner, scope)
        if name == "source_lookup":
            return source_result(db, owner, scope, at, arguments)
        plan = plan_query(args.query)
        if plan["time_mode"] != "needs_date":
            plan["as_of"] = at
            plan["time_mode"] = "explicit"
        result = retrieve(db, owner, scope, plan, limit=args.limit, budget_bytes=2000)
        return MemoryResult(
            items=result["selected"],
            as_of=at,
            needs_date=plan["time_mode"] == "needs_date",
            omitted_count=sum(item["decision"] != "selected" for item in result["candidates"]),
            candidate_pool_truncated=result["budget"]["candidate_pool_truncated"],
            ambiguous=any(
                item["state"] == "ambiguous" for item in result["plan"].get("entity_resolution", [])
            ),
        ).model_dump(mode="json")
