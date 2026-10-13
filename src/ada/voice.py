"""Explicitly reviewed on-device transcripts. No server audio/ASR or automatic claims."""

import hashlib
import json

from sqlalchemy import func, select

from ada.errors import ServiceError
from ada.evidence import content_hash
from ada.models import Conversation, Event, SourceVersion, User, now_ms
from ada.voice_models import VoiceInput

MAX_VOICE_INPUTS = 1000


class VoiceService:
    def __init__(self, streaming):
        self.streaming, self.sessions = streaming, streaming.sessions

    def submit(self, owner, cid, body):
        transcript = body.transcript.model_dump(mode="json")
        binding = hashlib.sha256(
            json.dumps(
                transcript, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest()

        def register(db, request):
            previous = db.get(VoiceInput, (owner, str(body.request_id)))
            if previous:
                if previous.input_hash != binding:
                    raise ServiceError(409, "idempotency_key_reused")
                return
            db.scalar(select(User).where(User.id == owner).with_for_update())
            count = db.scalar(
                select(func.count()).select_from(VoiceInput).where(VoiceInput.owner_id == owner)
            )
            if count >= MAX_VOICE_INPUTS:
                raise ServiceError(413, "voice_history_limit")
            conversation = db.get(Conversation, cid)
            event = db.scalar(
                select(Event).where(
                    Event.owner_id == owner, Event.request_id == request.id, Event.role == "user"
                )
            )
            db.add(
                VoiceInput(
                    owner_id=owner,
                    request_id=request.id,
                    conversation_id=cid,
                    scope_id=conversation.scope_id,
                    input_hash=binding,
                    transcript_id=transcript["transcript_id"],
                    engine_id=transcript["engine_id"],
                    engine_version=transcript["engine_version"],
                    language=transcript["language"],
                    duration_ms=transcript["duration_ms"],
                    original_text=transcript["original_text"],
                    original_hash=content_hash(transcript["original_text"]),
                    endorsement_source_version_id=event.id,
                    reviewed_hash=content_hash(body.content),
                    approved_at=now_ms(),
                )
            )
            db.flush()

        return self.streaming.submit(
            owner,
            cid,
            str(body.request_id),
            body.content,
            as_of=body.as_of,
            use_memory=body.use_memory,
            use_documents=body.use_documents,
            input_binding=binding,
            register=register,
        )

    @staticmethod
    def public(db, row):
        version = db.get(SourceVersion, row.endorsement_source_version_id)
        if (
            version is None
            or version.owner_id != row.owner_id
            or version.scope_id != row.scope_id
            or version.trust_class != "user_explicit"
            or version.content_hash != row.reviewed_hash
            or content_hash(version.content) != row.reviewed_hash
            or content_hash(row.original_text) != row.original_hash
        ):
            raise ServiceError(409, "voice_lineage_unavailable")
        return {
            "request_id": row.request_id,
            "conversation_id": row.conversation_id,
            "scope_id": row.scope_id,
            "transcript_id": row.transcript_id,
            "engine_id": row.engine_id,
            "engine_version": row.engine_version,
            "language": row.language,
            "duration_ms": row.duration_ms,
            "original_text": row.original_text,
            "original_hash": row.original_hash,
            "reviewed_text": version.content,
            "reviewed_hash": row.reviewed_hash,
            "endorsement_source_version_id": row.endorsement_source_version_id,
            "approved_at": row.approved_at,
        }

    def get(self, owner, rid):
        with self.sessions() as db:
            row = db.get(VoiceInput, (owner, rid))
            if row is None:
                raise ServiceError(404, "voice_input_not_found")
            return self.public(db, row)

    def list(self, owner, cid, limit, offset):
        with self.sessions() as db:
            if (
                db.scalar(
                    select(Conversation.id).where(
                        Conversation.owner_id == owner, Conversation.id == cid
                    )
                )
                is None
            ):
                raise ServiceError(404, "conversation_not_found")
            rows = db.scalars(
                select(VoiceInput)
                .where(VoiceInput.owner_id == owner, VoiceInput.conversation_id == cid)
                .order_by(VoiceInput.approved_at, VoiceInput.request_id)
                .limit(limit)
                .offset(offset)
            ).all()
            return [self.public(db, row) for row in rows]
