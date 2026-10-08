import time
from uuid import uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def new_id() -> str:
    return str(uuid4())


def now_ms() -> int:
    return time.time_ns() // 1_000_000


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class Personality(Base):
    __tablename__ = "personalities"
    __table_args__ = (UniqueConstraint("owner_id", "id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    style: Mapped[str] = mapped_column(String(20))
    warmth: Mapped[str] = mapped_column(String(20))
    detail: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class Scope(Base):
    __tablename__ = "scopes"
    __table_args__ = (
        UniqueConstraint("owner_id", "id"),
        UniqueConstraint("owner_id", "id", "kind"),
        CheckConstraint("kind IN ('personal', 'project')", name="scope_kind_allowed"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("owner_id", "id"),
        UniqueConstraint("owner_id", "id", "scope_id", name="conversation_scope_identity"),
        ForeignKeyConstraint(
            ["owner_id", "personality_id"], ["personalities.owner_id", "personalities.id"]
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "scope_kind"],
            ["scopes.owner_id", "scopes.id", "scopes.kind"],
            name="conversation_scope_owner",
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    personality_id: Mapped[str] = mapped_column(String(36))
    scope_kind: Mapped[str] = mapped_column(String(20), default="personal")
    scope_id: Mapped[str] = mapped_column(String(36), default=new_id)
    title: Mapped[str] = mapped_column(String(120))
    personality_snapshot: Mapped[dict] = mapped_column(JSON)
    system_prompt: Mapped[str] = mapped_column(Text)
    prompt_version: Mapped[str] = mapped_column(String(30))
    revision: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class Request(Base):
    __tablename__ = "requests"
    __table_args__ = (
        UniqueConstraint("owner_id", "id", "conversation_id"),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id"], ["conversations.owner_id", "conversations.id"]
        ),
        CheckConstraint("status IN ('running', 'completed', 'failed')"),
        Index(
            "one_running_per_conversation",
            "conversation_id",
            unique=True,
            postgresql_where=text("status = 'running'"),
            sqlite_where=text("status = 'running'"),
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20))
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    base_revision: Mapped[int] = mapped_column(Integer)
    messages: Mapped[list] = mapped_column(JSON)
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    response: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(40))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
    started_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
    finished_at: Mapped[int | None] = mapped_column(BigInteger)


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "conversation_id"], ["conversations.owner_id", "conversations.id"]
        ),
        ForeignKeyConstraint(
            ["owner_id", "request_id", "conversation_id"],
            ["requests.owner_id", "requests.id", "requests.conversation_id"],
        ),
        UniqueConstraint("owner_id", "request_id", "role"),
        UniqueConstraint("owner_id", "conversation_id", "id", name="event_source_identity"),
        CheckConstraint("role IN ('user', 'assistant')"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(36), index=True)
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    request_id: Mapped[str] = mapped_column(String(36))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    trust_class: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class Source(Base):
    __tablename__ = "sources"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        UniqueConstraint("event_id"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "event_id"],
            ["events.owner_id", "events.conversation_id", "events.id"],
        ),
        CheckConstraint(
            "(kind = 'chat_event' AND event_id IS NOT NULL AND conversation_id IS NOT NULL) "
            "OR (kind = 'user_note' AND event_id IS NULL AND conversation_id IS NULL)",
            name="source_origin_allowed",
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(36), index=True)
    scope_id: Mapped[str] = mapped_column(String(36), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    conversation_id: Mapped[str | None] = mapped_column(String(36))
    event_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class SourceVersion(Base):
    __tablename__ = "source_versions"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        UniqueConstraint("source_id", "version"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_id"],
            ["sources.owner_id", "sources.scope_id", "sources.id"],
        ),
        CheckConstraint("version >= 1", name="source_version_positive"),
        CheckConstraint(
            "trust_class IN ('user_explicit', 'model_generated')", name="source_trust_allowed"
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(36), index=True)
    scope_id: Mapped[str] = mapped_column(String(36), index=True)
    source_id: Mapped[str] = mapped_column(String(36))
    version: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    trust_class: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        UniqueConstraint("owner_id", "scope_id", "write_hash", name="claim_write_unique"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "superseded_by"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
        ),
        CheckConstraint("kind IN ('fact', 'preference', 'decision')", name="claim_kind_allowed"),
        CheckConstraint("valid_to IS NULL OR valid_to > valid_from", name="claim_valid_interval"),
        CheckConstraint("span_start >= 0 AND span_end > span_start", name="claim_valid_span"),
        CheckConstraint(
            "(status = 'active' AND superseded_by IS NULL) OR "
            "(status = 'superseded' AND superseded_by IS NOT NULL AND valid_to IS NOT NULL)",
            name="claim_status_consistent",
        ),
        Index("claim_temporal_lookup", "owner_id", "scope_id", "valid_from", "valid_to"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    subject: Mapped[str] = mapped_column(String(160))
    predicate: Mapped[str] = mapped_column(String(160))
    value: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="active")
    valid_from: Mapped[int] = mapped_column(BigInteger)
    valid_to: Mapped[int | None] = mapped_column(BigInteger)
    source_version_id: Mapped[str] = mapped_column(String(36))
    span_start: Mapped[int] = mapped_column(Integer)
    span_end: Mapped[int] = mapped_column(Integer)
    quote: Mapped[str] = mapped_column(Text)
    evidence_hash: Mapped[str] = mapped_column(String(64))
    write_hash: Mapped[str] = mapped_column(String(64))
    superseded_by: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class PromptChange(Base):
    __tablename__ = "conversation_prompt_changes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "conversation_id"], ["conversations.owner_id", "conversations.id"]
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(36))
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    previous_version: Mapped[str] = mapped_column(String(30))
    new_version: Mapped[str] = mapped_column(String(30))
    previous_prompt: Mapped[str] = mapped_column(Text)
    new_prompt: Mapped[str] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class ClaimSearch(Base):
    """Rebuildable search projection. Claims and source versions remain authoritative."""

    __tablename__ = "claim_search"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
            ondelete="CASCADE",
        ),
        Index("claim_search_subject", "owner_id", "scope_id", "subject_key", "predicate_key"),
    )
    claim_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    subject_key: Mapped[str] = mapped_column(String(640))
    predicate_key: Mapped[str] = mapped_column(String(640))
    search_text: Mapped[str] = mapped_column(Text)


class RetrievalTrace(Base):
    __tablename__ = "retrieval_traces"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "request_id", "conversation_id"],
            ["requests.owner_id", "requests.id", "requests.conversation_id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "conversation_id", "scope_id"],
            ["conversations.owner_id", "conversations.id", "conversations.scope_id"],
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    version: Mapped[str] = mapped_column(String(40))
    plan: Mapped[dict] = mapped_column(JSON)
    candidates: Mapped[list] = mapped_column(JSON)
    selected: Mapped[list] = mapped_column(JSON)
    budget: Mapped[dict] = mapped_column(JSON)
    retrieval_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
