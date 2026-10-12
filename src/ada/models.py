import time
from uuid import uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
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
        Index("request_admin_created", "created_at", "owner_id", "id"),
        Index("request_admin_status", "status", "created_at", "owner_id", "id"),
        Index("request_admin_owner", "owner_id", "created_at", "id"),
        Index("request_admin_provider", "provider", "created_at", "owner_id", "id"),
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
    expression_snapshot: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    learning_snapshot: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
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
            "OR (kind IN ('user_note', 'imported_document') "
            "AND event_id IS NULL AND conversation_id IS NULL)",
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
            "trust_class IN ('user_explicit', 'model_generated', 'imported_untrusted')",
            name="source_trust_allowed",
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
            ["owner_id", "scope_id", "subject_entity_id"],
            ["entities.owner_id", "entities.scope_id", "entities.id"],
            name="claim_subject_entity_scoped",
        ),
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
    subject_entity_id: Mapped[str | None] = mapped_column(String(36))
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
    provenance: Mapped[dict | None] = mapped_column(JSON)
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
    document_candidates: Mapped[list] = mapped_column(JSON, default=list, server_default="[]")
    document_selected: Mapped[list] = mapped_column(JSON, default=list, server_default="[]")
    budget: Mapped[dict] = mapped_column(JSON)
    retrieval_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class DocumentUpload(Base):
    """Private, owner-bound raw blob and immutable ingestion reservation."""

    __tablename__ = "document_uploads"
    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "scope_id",
            "id",
            "source_version_id",
            "source_id",
            name="document_upload_identity",
        ),
        UniqueConstraint("source_id", "version", name="document_upload_version"),
        UniqueConstraint("source_version_id"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_id"],
            ["sources.owner_id", "sources.scope_id", "sources.id"],
        ),
        CheckConstraint("version >= 1 AND attempt >= 1", name="document_version_attempt_positive"),
        CheckConstraint("raw_size > 0 AND raw_size <= 262144", name="document_raw_size_bounded"),
        CheckConstraint(
            "available_to IS NULL OR available_to > available_from",
            name="document_availability_interval",
        ),
        CheckConstraint(
            "chunk_count >= 0 AND chunk_count <= 512", name="document_chunk_count_bounded"
        ),
        CheckConstraint(
            "(state = 'processing' AND published_at IS NULL AND error_code IS NULL AND chunk_count = 0) OR (state = 'ready' AND published_at IS NOT NULL AND error_code IS NULL AND chunk_count > 0) OR (state = 'failed' AND published_at IS NULL AND error_code IS NOT NULL AND chunk_count = 0)",
            name="document_state_consistent",
        ),
        Index("document_upload_owner_created", "owner_id", "created_at", "id"),
        Index(
            "document_upload_source_available",
            "owner_id",
            "scope_id",
            "source_id",
            "version",
            "state",
            "available_from",
            "published_at",
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    source_id: Mapped[str] = mapped_column(String(36))
    # Reserved before publication; it deliberately has no premature evidence FK.
    source_version_id: Mapped[str] = mapped_column(String(36))
    version: Mapped[int] = mapped_column(Integer)
    filename: Mapped[str] = mapped_column(String(120))
    media_type: Mapped[str] = mapped_column(String(30))
    input_hash: Mapped[str] = mapped_column(String(64))
    raw_hash: Mapped[str] = mapped_column(String(64))
    raw_bytes: Mapped[bytes] = mapped_column(LargeBinary)
    raw_size: Mapped[int] = mapped_column(Integer)
    available_from: Mapped[int] = mapped_column(BigInteger)
    available_to: Mapped[int | None] = mapped_column(BigInteger)
    state: Mapped[str] = mapped_column(String(20))
    error_code: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[int] = mapped_column(BigInteger)
    published_at: Mapped[int | None] = mapped_column(BigInteger)
    started_at: Mapped[int] = mapped_column(BigInteger)
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)


class DocumentChunk(Base):
    """Exact code-point excerpts; imported content never becomes an assertion."""

    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("owner_id", "scope_id", "id"),
        UniqueConstraint("source_version_id", "ordinal", name="document_chunk_ordinal"),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "upload_id", "source_version_id", "source_id"],
            [
                "document_uploads.owner_id",
                "document_uploads.scope_id",
                "document_uploads.id",
                "document_uploads.source_version_id",
                "document_uploads.source_id",
            ],
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        CheckConstraint("ordinal >= 1 AND ordinal <= 512", name="document_chunk_ordinal_bounded"),
        CheckConstraint(
            "span_start >= 0 AND span_end > span_start AND span_end - span_start <= 1024",
            name="document_chunk_span_bounded",
        ),
        CheckConstraint(
            "line_start >= 1 AND line_end >= line_start", name="document_chunk_lines_valid"
        ),
        Index("document_chunk_version", "owner_id", "scope_id", "source_version_id", "ordinal"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    upload_id: Mapped[str] = mapped_column(String(36))
    source_id: Mapped[str] = mapped_column(String(36))
    source_version_id: Mapped[str] = mapped_column(String(36))
    ordinal: Mapped[int] = mapped_column(Integer)
    span_start: Mapped[int] = mapped_column(Integer)
    span_end: Mapped[int] = mapped_column(Integer)
    quote: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    quote_hash: Mapped[str] = mapped_column(String(64))
    line_start: Mapped[int] = mapped_column(Integer)
    line_end: Mapped[int] = mapped_column(Integer)


class DocumentSearch(Base):
    """Rebuildable lexical projection with exact chunks as its mapping."""

    __tablename__ = "document_search"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "chunk_id"],
            ["document_chunks.owner_id", "document_chunks.scope_id", "document_chunks.id"],
            ondelete="CASCADE",
        ),
        Index("document_search_owner_scope", "owner_id", "scope_id"),
    )
    chunk_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    scope_id: Mapped[str] = mapped_column(String(36))
    search_text: Mapped[str] = mapped_column(Text)


class AdminGrant(Base):
    __tablename__ = "admin_grants"
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)


class AdminAuditState(Base):
    """Serializes bounded audit insertion/pruning across local CLI and server."""

    __tablename__ = "admin_audit_state"
    __table_args__ = (CheckConstraint("id = 1", name="admin_audit_singleton"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class AdminAudit(Base):
    __tablename__ = "admin_audit"
    __table_args__ = (
        CheckConstraint("actor_kind IN ('user', 'local_operator')", name="admin_audit_actor"),
        CheckConstraint(
            "action IN ('role.grant', 'role.revoke', 'monitor.me', 'monitor.overview', "
            "'monitor.requests', 'monitor.request', 'monitor.providers', 'monitor.audit')",
            name="admin_audit_action",
        ),
        CheckConstraint(
            "outcome IN ('allowed', 'denied', 'not_found', 'invalid', 'failed', "
            "'granted', 'revoked', 'unchanged', 'rate_limited')",
            name="admin_audit_outcome",
        ),
        Index("admin_audit_created", "created_at", "id"),
        Index("admin_audit_actor_created", "actor_id", "created_at", "id"),
    )
    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(36))
    actor_kind: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(30))
    target_owner_id: Mapped[str | None] = mapped_column(String(36))
    target_request_id: Mapped[str | None] = mapped_column(String(36))
    outcome: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
