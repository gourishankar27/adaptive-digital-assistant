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


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("owner_id", "id"),
        ForeignKeyConstraint(
            ["owner_id", "personality_id"], ["personalities.owner_id", "personalities.id"]
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
