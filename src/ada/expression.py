"""Owner-controlled expression; no inference, retrieval ranking or permission changes.

Only explicit authenticated review accepts a signal. Normal model text is never
parsed into state. One signal per completed turn, short sessions and deterministic
decay prevent an unbounded psychological profile. Historical requests are frozen.
"""

import hashlib
import json
from uuid import uuid4

from sqlalchemy import func, select

from ada.errors import ServiceError
from ada.expression_contracts import POLICY_VERSION
from ada.expression_models import (
    ExpressionBinding,
    ExpressionPreference,
    ExpressionReceipt,
    ExpressionSession,
)
from ada.models import Conversation, Personality, Request, Scope, User, now_ms
from ada.personality import RETRIEVAL_PROMPT_VERSIONS

IDLE_MS = 30 * 60_000
MAX_SESSION_MS = 2 * 60 * 60_000
DECAY_MS = 5 * 60_000
MAX_CHANGE = 10
DECAY = 5
MAX_RECEIPTS = 5000
POLICY_BYTES = 800
DIMENSIONS = ("warmth", "focus", "energy", "playfulness", "concern")


def defaults(conversation):
    return {
        "warmth": 60 if conversation.personality_snapshot["warmth"] == "warm" else 30,
        "focus": 60,
        "energy": 50,
        "playfulness": 20,
        "concern": 30,
    }


def approach(vector, baseline, amount):
    return {
        key: value + max(-amount, min(amount, baseline[key] - value))
        for key, value in vector.items()
    }


def prompt_expression(snapshot):
    if snapshot is None:
        return ""
    payload = {
        key: snapshot[key] for key in ("policy_version", "preferences", "dynamic_enabled", "vector")
    }
    policy = (
        "\nExpression policy: the following allowlisted settings affect wording only. "
        "Explicit preferences override session tone. Initiative means suggestions, never actions. "
        "Ignore the vector when dynamic_enabled is false. "
        "Cadence means reply structure, never scheduling. No changes to facts, evidence, retrieval, "
        "permissions or tools. These values are temporary style controls, not feelings or a diagnosis. "
        + json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )
    # Style choices cannot change evidence selection by varying prompt byte cost.
    if len(policy.encode()) > POLICY_BYTES:
        raise ServiceError(413, "expression_exceeds_policy_budget")
    return policy + " " * (POLICY_BYTES - len(policy.encode()))


class ExpressionService:
    def __init__(self, sessions):
        self.sessions = sessions

    @staticmethod
    def conversation(db, owner, cid, lock=False):
        q = select(Conversation).where(Conversation.owner_id == owner, Conversation.id == cid)
        row = db.scalar(q.with_for_update() if lock else q)
        if row is None:
            raise ServiceError(404, "conversation_not_found")
        return row

    def target(self, db, owner, kind, target, lock=False):
        if kind == "conversation":
            return self.conversation(db, owner, target, lock)
        model = {"account": User, "profile": Personality, "scope": Scope}[kind]
        q = select(model).where(model.id == target)
        q = q.where(model.id == owner) if kind == "account" else q.where(model.owner_id == owner)
        row = db.scalar(q)
        if row is None:
            raise ServiceError(404, "preference_target_not_found")
        return row

    @staticmethod
    def not_running(db, owner, cid):
        if db.scalar(
            select(Request.id).where(
                Request.owner_id == owner,
                Request.conversation_id == cid,
                Request.status == "running",
            )
        ):
            raise ServiceError(409, "conversation_busy")

    @staticmethod
    def preference_output(row, kind, target):
        return {
            "target_kind": kind,
            "target_id": target,
            "revision": row.revision if row else 0,
            "values": row.values if row else {},
            "receipt_id": row.receipt_id if row else None,
        }

    def preference(self, owner, kind, target):
        with self.sessions() as db:
            self.target(db, owner, kind, target)
            return self.preference_output(
                db.get(ExpressionPreference, (owner, kind, target)), kind, target
            )

    @staticmethod
    def effective(db, conversation):
        personality = conversation.personality_snapshot
        values = {
            "verbosity": personality["detail"]
            if personality["detail"] in ("concise", "balanced", "detailed")
            else "balanced",
            "initiative": "respond",
            "formality": "formal" if personality["style"] == "formal" else "neutral",
            "humor": "none",
            "cadence": "direct",
        }
        origins = {key: "personality" for key in values}
        receipts = {key: None for key in values}
        for kind, target in (
            ("account", conversation.owner_id),
            ("scope", conversation.scope_id),
            ("profile", conversation.personality_id),
            ("conversation", conversation.id),
        ):
            row = db.get(ExpressionPreference, (conversation.owner_id, kind, target))
            if row:
                values.update(row.values)
                origins.update({key: kind for key in row.values})
                receipts.update({key: row.receipt_id for key in row.values})
        return values, origins, receipts

    def bind_new(self, db, conversation):
        # Serialize all explicit settings against creation's inheritance snapshot.
        db.scalar(select(User).where(User.id == conversation.owner_id).with_for_update())
        values, origins, receipts = self.effective(db, conversation)
        row = ExpressionBinding(
            owner_id=conversation.owner_id,
            conversation_id=conversation.id,
            profile_id=conversation.personality_id,
            scope_id=conversation.scope_id,
            revision=0,
            active=any(v != "personality" for v in origins.values()),
            dynamic_enabled=False,
            preferences=values,
            origins=origins,
            source_receipts=receipts,
        )
        db.add(row)
        return row

    @staticmethod
    def session(db, conversation, renew=False):
        row = db.get(ExpressionSession, (conversation.owner_id, conversation.id))
        instant = now_ms()
        if row is None:
            row = ExpressionSession(
                owner_id=conversation.owner_id,
                conversation_id=conversation.id,
                profile_id=conversation.personality_id,
            )
            db.add(row)
            renew = True
        if renew or instant >= row.expires_at:
            row.session_id = str(uuid4())
            row.turn, row.last_signal_turn, row.last_request_id = 0, -1, None
            row.started_at = row.touched_at = instant
            row.expires_at = instant + IDLE_MS
            for key, value in defaults(conversation).items():
                setattr(row, key, value)
        return row

    @staticmethod
    def output(conversation, binding, session=None):
        baseline = defaults(conversation)
        instant = now_ms()
        expired = session is not None and instant >= session.expires_at
        active = binding is not None and binding.active
        enabled = active and binding.dynamic_enabled
        values = (
            binding.preferences
            if binding
            else {
                "verbosity": conversation.personality_snapshot["detail"]
                if conversation.personality_snapshot["detail"]
                in ("concise", "balanced", "detailed")
                else "balanced",
                "initiative": "respond",
                "formality": "formal"
                if conversation.personality_snapshot["style"] == "formal"
                else "neutral",
                "humor": "none",
                "cadence": "direct",
            }
        )
        vector = baseline
        if enabled and session is not None and not expired:
            vector = approach(
                {key: getattr(session, key) for key in DIMENSIONS},
                baseline,
                DECAY * (max(0, instant - session.touched_at) // DECAY_MS),
            )
        return {
            "policy_version": POLICY_VERSION,
            "conversation_id": conversation.id,
            "profile_id": conversation.personality_id,
            "scope_id": conversation.scope_id,
            "active": active,
            "binding_revision": binding.revision if binding else 0,
            "preferences": values,
            "origins": binding.origins if binding else {k: "personality" for k in values},
            "source_receipts": binding.source_receipts if binding else {k: None for k in values},
            "dynamic_enabled": enabled,
            "session_id": session.session_id if session else None,
            "turn": session.turn if session else 0,
            "vector": vector,
            "defaults": baseline,
            "expires_at": session.expires_at if session else None,
            "expired": expired,
            "last_request_id": session.last_request_id if session else None,
        }

    def inspect(self, owner, cid):
        with self.sessions() as db:
            conversation = self.conversation(db, owner, cid)
            return self.output(
                conversation,
                db.get(ExpressionBinding, (owner, cid)),
                db.get(ExpressionSession, (owner, cid)),
            )

    def reserve_snapshot(self, db, conversation, request_id):
        binding = db.get(ExpressionBinding, (conversation.owner_id, conversation.id))
        if (
            not binding
            or not binding.active
            or conversation.prompt_version not in RETRIEVAL_PROMPT_VERSIONS
        ):
            return None
        session = self.session(db, conversation)
        state = self.output(conversation, binding, session)
        vector = approach(state["vector"], state["defaults"], DECAY)
        for key, value in vector.items():
            setattr(session, key, value)
        session.turn += 1
        session.last_request_id = request_id
        session.touched_at = max(now_ms(), session.touched_at)
        session.expires_at = min(session.touched_at + IDLE_MS, session.started_at + MAX_SESSION_MS)
        return self.output(conversation, binding, session)

    def request_snapshot(self, owner, rid):
        with self.sessions() as db:
            row = db.get(Request, (owner, rid))
            if row is None:
                raise ServiceError(404, "request_not_found")
            return {"request_id": rid, "expression": row.expression_snapshot}

    @staticmethod
    def receipt_in_transaction(db, owner, operation, action, kind, target, body):
        # A private owner's singleton lock bounds quota and serializes receipt keys.
        db.scalar(select(User).where(User.id == owner).with_for_update())
        encoded = json.dumps(
            {
                "action": action,
                "kind": kind,
                "target": target,
                "input": body.model_dump(mode="json"),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256((POLICY_VERSION + encoded).encode()).hexdigest()
        old = db.get(ExpressionReceipt, (owner, operation))
        if old:
            if old.input_hash != fingerprint:
                raise ServiceError(409, "idempotency_key_reused")
            return old.result, fingerprint
        if (
            db.scalar(
                select(func.count())
                .select_from(ExpressionReceipt)
                .where(ExpressionReceipt.owner_id == owner)
            )
            >= MAX_RECEIPTS
        ):
            raise ServiceError(413, "expression_receipt_limit")
        return None, fingerprint

    @staticmethod
    def publish(
        db,
        owner,
        operation,
        action,
        kind,
        target,
        fingerprint,
        preference=None,
        expression=None,
        reason="explicit_settings",
        source_request_id=None,
    ):
        result = {
            "operation_id": operation,
            "action": action,
            "target_kind": kind,
            "target_id": target,
            "created_at": now_ms(),
            "reason": reason,
            "source_request_id": source_request_id,
            "preference": preference,
            "expression": expression,
        }
        db.add(
            ExpressionReceipt(
                owner_id=owner,
                id=operation,
                input_hash=fingerprint,
                result=result,
                created_at=result["created_at"],
            )
        )
        db.flush()
        return result, True

    def write_preference(self, owner, kind, target, body):
        with self.sessions.begin() as db:
            subject = self.target(db, owner, kind, target, lock=True)
            operation = str(body.operation_id)
            old, fingerprint = self.receipt_in_transaction(
                db, owner, operation, "preferences", kind, target, body
            )
            if old:
                return old, False
            if body.dynamic_enabled is not None and kind != "conversation":
                raise ServiceError(422, "dynamic_state_requires_conversation")
            if kind == "conversation":
                if subject.prompt_version not in RETRIEVAL_PROMPT_VERSIONS:
                    raise ServiceError(409, "expression_requires_prompt_upgrade")
                self.not_running(db, owner, target)
            row = db.get(ExpressionPreference, (owner, kind, target))
            if (row.revision if row else 0) != body.expected_revision:
                raise ServiceError(409, "preference_revision_changed")
            if row is None:
                row = ExpressionPreference(
                    owner_id=owner,
                    target_kind=kind,
                    target_id=target,
                    profile_id=target if kind == "profile" else None,
                    scope_id=target if kind == "scope" else None,
                    conversation_id=target if kind == "conversation" else None,
                    revision=0,
                )
                db.add(row)
            row.revision += 1
            row.values, row.receipt_id = body.values.model_dump(exclude_none=True), operation
            db.flush()
            expression = None
            if kind == "conversation":
                binding = db.get(ExpressionBinding, (owner, target)) or self.bind_new(db, subject)
                binding.preferences, binding.origins, binding.source_receipts = self.effective(
                    db, subject
                )
                binding.revision += 1
                binding.active = True
                if body.dynamic_enabled is not None:
                    binding.dynamic_enabled = body.dynamic_enabled
                db.flush()
                session = self.session(db, subject, renew=True)
                expression = self.output(subject, binding, session)
            return self.publish(
                db,
                owner,
                operation,
                "preferences",
                kind,
                target,
                fingerprint,
                self.preference_output(row, kind, target),
                expression,
            )

    def signal_or_reset(self, owner, cid, body, action):
        with self.sessions.begin() as db:
            conversation = self.conversation(db, owner, cid, lock=True)
            operation = str(body.operation_id)
            old, fingerprint = self.receipt_in_transaction(
                db, owner, operation, action, "conversation", cid, body
            )
            if old:
                return old, False
            self.not_running(db, owner, cid)
            binding = db.get(ExpressionBinding, (owner, cid))
            session = db.get(ExpressionSession, (owner, cid))
            if (
                not binding
                or not binding.active
                or not session
                or session.session_id != str(body.session_id)
                or now_ms() >= session.expires_at
            ):
                raise ServiceError(409, "expression_session_changed")
            if action == "reset":
                session = self.session(db, conversation, renew=True)
            else:
                request = db.get(Request, (owner, str(body.source_request_id)))
                if (
                    not binding.dynamic_enabled
                    or not request
                    or request.status != "completed"
                    or request.conversation_id != cid
                    or session.last_request_id != request.id
                    or not request.expression_snapshot
                    or request.expression_snapshot["session_id"] != session.session_id
                    or request.expression_snapshot["binding_revision"] != binding.revision
                    or session.last_signal_turn == session.turn
                ):
                    raise ServiceError(409, "expression_signal_stale")
                changes = body.vector.model_dump(exclude_none=True)
                if not changes:
                    raise ServiceError(422, "expression_signal_empty")
                vector = self.output(conversation, binding, session)["vector"]
                for key, desired in changes.items():
                    desired = max(0, min(100, desired))
                    vector[key] += max(-MAX_CHANGE, min(MAX_CHANGE, desired - vector[key]))
                for key, value in vector.items():
                    setattr(session, key, value)
                session.last_signal_turn = session.turn
                session.touched_at = max(now_ms(), session.touched_at)
                # A signal cannot extend a session's existing expiry.
            return self.publish(
                db,
                owner,
                operation,
                action,
                "conversation",
                cid,
                fingerprint,
                expression=self.output(conversation, binding, session),
                reason="user_reset" if action == "reset" else body.reason,
                source_request_id=None if action == "reset" else str(body.source_request_id),
            )

    def receipt(self, owner, operation):
        with self.sessions() as db:
            row = db.get(ExpressionReceipt, (owner, operation))
            if row is None:
                raise ServiceError(404, "expression_receipt_not_found")
            return row.result
