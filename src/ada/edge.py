"""An installation signature proves possession, never model execution or factual truth."""

import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import func, select

from ada.edge_models import EdgeDevice, EdgeProposal
from ada.errors import ServiceError
from ada.evidence import content_hash, validate_text
from ada.memory import owned_scope
from ada.models import now_ms
from ada.proposals import fingerprint

MODEL_ID = "Qwen/Qwen3-0.6B-GGUF"
MODEL_DIGEST = "9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031"
RUNTIME = "llama.cpp-620d2225cc436ab0b001e3200e590e3b286ef9ab"
VERSION = "ada-device-drafts-v1"


def signing_message(scope, body):
    sources = "\n".join(
        f"{p['source_version_id']}:{p['version']}:{p['content_hash']}:{p['span_start']}:{p['span_end']}"
        for p in body["sources"]
    )
    fields = [
        VERSION,
        str(scope),
        str(body["proposal_id"]),
        str(body["device_id"]),
        str(body["device_revision"]),
        str(body["sequence"]),
        body["task"],
        body["model_id"],
        body["model_digest"],
        body["runtime"],
        body["prompt_hash"],
        content_hash(body["output"]),
        content_hash(sources),
    ]
    return "\n".join(fields).encode("ascii")


def public_device(row):
    return {
        "version": VERSION,
        **{
            k: getattr(row, k)
            for k in (
                "id",
                "revision",
                "last_sequence",
                "enrollment_id",
                "revocation_id",
                "label",
                "public_key",
                "revoked_at",
                "created_at",
            )
        },
    }


class EdgeService:
    def __init__(self, sessions, settings, scheduling, work):
        self.sessions, self.settings, self.scheduling, self.work = (
            sessions,
            settings,
            scheduling,
            work,
        )

    def _enabled(self):
        if not self.settings.edge_draft_sync_enabled:
            raise ServiceError(503, "edge_sync_disabled")

    def _device(self, db, owner, key, user):
        row = db.get(EdgeDevice, (owner, key))
        if row is None:
            raise ServiceError(404, "edge_device_not_found")
        if row.revoked_at is not None or row.epoch != user.data_epoch:
            raise ServiceError(410, "edge_device_revoked_or_stale")
        return row

    def enroll(self, owner, key, body, principal):
        self._enabled()
        try:
            validate_text(body.label)
            public = serialization.load_der_public_key(
                base64.b64decode(body.public_key, validate=True)
            )
            if (
                not body.label.strip()
                or not isinstance(public, ec.EllipticCurvePublicKey)
                or not isinstance(public.curve, ec.SECP256R1)
            ):
                raise ValueError()
        except (ValueError, TypeError):
            raise ServiceError(422, "edge_public_key_invalid") from None
        hashed = fingerprint({"domain": VERSION, "enrollment": body.model_dump(mode="json")})
        with self.sessions.begin() as db:
            user = self.scheduling._owner(db, owner, principal)
            reused = db.scalar(
                select(EdgeDevice.id).where(
                    EdgeDevice.owner_id == owner, EdgeDevice.enrollment_id == str(body.operation_id)
                )
            )
            if reused is not None and reused != key:
                raise ServiceError(409, "edge_enrollment_id_reused")
            old = db.get(EdgeDevice, (owner, key))
            if old:
                if old.input_hash != hashed:
                    raise ServiceError(409, "edge_enrollment_changed")
                return public_device(old)
            if (
                db.scalar(
                    select(EdgeDevice.id).where(
                        EdgeDevice.owner_id == owner,
                        EdgeDevice.public_key == body.public_key,
                        EdgeDevice.revoked_at.is_(None),
                        EdgeDevice.epoch == user.data_epoch,
                    )
                )
                is not None
            ):
                raise ServiceError(409, "edge_installation_already_registered")
            if (
                db.scalar(
                    select(func.count()).select_from(EdgeDevice).where(EdgeDevice.owner_id == owner)
                )
                >= 5
            ):
                raise ServiceError(413, "edge_device_limit")
            row = EdgeDevice(
                owner_id=owner,
                id=key,
                epoch=user.data_epoch,
                revision=1,
                last_sequence=0,
                label=body.label,
                public_key=body.public_key,
                enrollment_id=str(body.operation_id),
                input_hash=hashed,
                created_at=now_ms(),
            )
            db.add(row)
            db.flush()
            return public_device(row)

    def devices(self, owner):
        with self.sessions() as db:
            return [
                public_device(row)
                for row in db.scalars(
                    select(EdgeDevice)
                    .where(EdgeDevice.owner_id == owner)
                    .order_by(EdgeDevice.created_at, EdgeDevice.id)
                    .limit(5)
                )
            ]

    def revoke(self, owner, key, body, principal):
        hashed = fingerprint(body.model_dump(mode="json"))
        with self.sessions.begin() as db:
            self.scheduling._owner(db, owner, principal)
            row = db.get(EdgeDevice, (owner, key))
            if row is None:
                raise ServiceError(404, "edge_device_not_found")
            if row.revocation_id == str(body.operation_id):
                if row.revocation_hash != hashed:
                    raise ServiceError(409, "edge_revocation_changed")
                return public_device(row)
            if row.revision != body.expected_revision or row.revoked_at is not None:
                raise ServiceError(409, "edge_device_changed")
            row.revision += 1
            row.revoked_at = now_ms()
            row.revocation_id = str(body.operation_id)
            row.revocation_hash = hashed
            return public_device(row)

    def _output(self, db, row, user):
        self._device(db, row.owner_id, row.device_id, user)
        owned_scope(db, row.owner_id, row.scope_id)
        from ada.work_contracts import WorkFields

        self.work._sources(
            db,
            row.owner_id,
            row.scope_id,
            WorkFields(
                kind="task", description="Device lineage validation", pins=row.payload["sources"]
            ),
        )
        return {
            "version": VERSION,
            "id": row.id,
            "scope_id": row.scope_id,
            "device_id": row.device_id,
            "sequence": row.sequence,
            "task": "offline_reply",
            "model_id": row.payload["model_id"],
            "model_digest": row.payload["model_digest"],
            "runtime": row.payload["runtime"],
            "output": row.output,
            "prompt_hash": row.payload["prompt_hash"],
            "sources": row.payload["sources"],
            "trust_class": "model_generated",
            "state": "draft",
            "created_at": row.created_at,
        }

    def sync(self, owner, scope, key, body, principal):
        self._enabled()
        payload = body.model_dump(mode="json")
        if str(body.proposal_id) != key or content_hash(body.prompt) != body.prompt_hash:
            raise ServiceError(409, "edge_proposal_input_changed")
        hashed = fingerprint({"scope": scope, "input": payload})
        with self.sessions.begin() as db:
            user = self.scheduling._owner(db, owner, principal)
            owned_scope(db, owner, scope, lock=True)
            device = self._device(db, owner, str(body.device_id), user)
            old = db.get(EdgeProposal, (owner, key))
            if old:
                if old.input_hash != hashed:
                    raise ServiceError(409, "edge_proposal_changed")
                return self._output(db, old, user)
            if device.revision != body.device_revision or body.sequence != device.last_sequence + 1:
                raise ServiceError(409, "edge_sequence_changed")
            try:
                public = serialization.load_der_public_key(
                    base64.b64decode(device.public_key, validate=True)
                )
                public.verify(
                    base64.b64decode(body.signature, validate=True),
                    signing_message(scope, payload),
                    ec.ECDSA(hashes.SHA256()),
                )
            except (ValueError, TypeError, InvalidSignature):
                raise ServiceError(422, "edge_signature_invalid") from None
            if (
                db.scalar(
                    select(func.count())
                    .select_from(EdgeProposal)
                    .where(EdgeProposal.owner_id == owner)
                )
                >= 300
            ):
                raise ServiceError(413, "edge_proposal_limit")
            row = EdgeProposal(
                owner_id=owner,
                id=key,
                scope_id=scope,
                device_id=device.id,
                epoch=user.data_epoch,
                sequence=body.sequence,
                input_hash=hashed,
                payload=payload,
                output=body.output,
                created_at=now_ms(),
            )
            result = self._output(db, row, user)
            device.last_sequence = body.sequence
            db.add(row)
            return result

    def get(self, owner, key):
        with self.sessions.begin() as db:
            user = self.scheduling._owner(db, owner)
            row = db.get(EdgeProposal, (owner, key))
            if row is None:
                raise ServiceError(404, "edge_proposal_not_found")
            if row.epoch != user.data_epoch:
                raise ServiceError(410, "edge_proposal_stale")
            return self._output(db, row, user)
