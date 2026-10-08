"""Immutable evidence snapshots. Neither this module nor the memory writer calls a model."""

import hashlib

from ada.models import Event, Source, SourceVersion, new_id, now_ms


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_text(value):
    if isinstance(value, str):
        if "\x00" in value:
            raise ValueError("text cannot contain NUL characters")
        try:
            value.encode("utf-8")
        except UnicodeError:
            raise ValueError("text must be valid Unicode") from None
    return value


def record_source(db, *, owner, scope_id, content, kind, source_id=None, event=None):
    source_id = source_id or new_id()
    timestamp = event.created_at if event is not None else now_ms()
    source = Source(
        id=source_id,
        owner_id=owner,
        scope_id=scope_id,
        kind=kind,
        conversation_id=event.conversation_id if event else None,
        event_id=event.id if event else None,
        created_at=timestamp,
    )
    db.add(source)
    db.flush()
    version = SourceVersion(
        id=source_id,
        owner_id=owner,
        scope_id=scope_id,
        source_id=source_id,
        version=1,
        content=content,
        content_hash=content_hash(content),
        trust_class=event.trust_class if event else "user_explicit",
        created_at=timestamp,
    )
    db.add(version)
    db.flush()
    return version


def record_chat_event(db, conversation, request_id, role, content):
    event = Event(
        id=new_id(),
        owner_id=conversation.owner_id,
        conversation_id=conversation.id,
        request_id=request_id,
        role=role,
        content=content,
        trust_class="user_explicit" if role == "user" else "model_generated",
    )
    db.add(event)
    db.flush()
    record_source(
        db,
        owner=conversation.owner_id,
        scope_id=conversation.scope_id,
        content=content,
        kind="chat_event",
        source_id=event.id,
        event=event,
    )
    return event


def public_source_version(row):
    return {
        "id": row.id,
        "source_id": row.source_id,
        "scope_id": row.scope_id,
        "version": row.version,
        "content": row.content,
        "content_hash": row.content_hash,
        "trust_class": row.trust_class,
        "created_at": row.created_at,
    }
