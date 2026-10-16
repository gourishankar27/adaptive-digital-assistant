"""Owner-authenticated device lifecycle, compatible with released CLI bearer tokens."""

import hashlib
import json
import secrets
from dataclasses import dataclass, field

from sqlalchemy import func, select, update

from ada.auth import token_hash
from ada.errors import ServiceError
from ada.models import User, now_ms
from ada.security_models import DeviceCredential


@dataclass(frozen=True)
class Principal:
    owner: str
    epoch: int
    digest: str = field(repr=False)
    credential_id: str | None = None


def public_credential(row):
    return {
        key: getattr(row, key)
        for key in (
            "id",
            "label",
            "created_at",
            "expires_at",
            "last_used_at",
            "revoked_at",
            "rotated_from_id",
        )
    }


class CredentialService:
    def __init__(self, sessions, settings):
        self.sessions, self.settings = sessions, settings

    def authenticate(self, token, *, touch=True):
        if not isinstance(token, str) or not 1 <= len(token) <= 200:
            raise ServiceError(401, "invalid_token")
        return self.authenticate_digest(token_hash(token), touch=touch)

    def authenticate_digest(self, digest, *, touch=False):
        instant = now_ms()
        with self.sessions() as db:
            user = db.execute(
                select(User.id, User.data_epoch).where(User.token_hash == digest)
            ).first()
            if user is not None:
                return Principal(user.id, user.data_epoch, digest)
            row = db.execute(
                select(
                    DeviceCredential.id.label("credential_id"),
                    DeviceCredential.last_used_at,
                    User.id.label("owner_id"),
                    User.data_epoch,
                )
                .join(User, User.id == DeviceCredential.owner_id)
                .where(
                    DeviceCredential.token_hash == digest,
                    DeviceCredential.revoked_at.is_(None),
                    DeviceCredential.expires_at > instant,
                )
            ).first()
            if row is None:
                raise ServiceError(401, "invalid_token")
            result = Principal(row.owner_id, row.data_epoch, digest, row.credential_id)
            if touch and (row.last_used_at is None or instant - row.last_used_at >= 60_000):
                db.execute(
                    update(DeviceCredential)
                    .where(
                        DeviceCredential.id == row.credential_id,
                        (DeviceCredential.last_used_at.is_(None))
                        | (DeviceCredential.last_used_at <= instant - 60_000),
                    )
                    .values(last_used_at=instant)
                )
                db.commit()
            return result

    def current(self, principal, *, check_epoch=True):
        try:
            fresh = self.authenticate_digest(principal.digest)
            return fresh.owner == principal.owner and (
                not check_epoch or fresh.epoch == principal.epoch
            )
        except ServiceError:
            return False

    def list(self, owner):
        with self.sessions() as db:
            return [
                public_credential(row)
                for row in db.scalars(
                    select(DeviceCredential)
                    .where(DeviceCredential.owner_id == owner)
                    .order_by(DeviceCredential.created_at.desc(), DeviceCredential.id)
                    .limit(100)
                )
            ]

    def enroll(self, owner, operation, label, lifetime_days, rotated_from=None):
        if not self.settings.device_enrollment_enabled:
            raise ServiceError(503, "device_enrollment_disabled")
        canonical = json.dumps([label, lifetime_days, rotated_from], separators=(",", ":"))
        fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
        with self.sessions.begin() as db:
            db.scalar(select(User).where(User.id == owner).with_for_update())
            existing = db.get(DeviceCredential, operation)
            if existing is not None:
                if existing.owner_id != owner:
                    raise ServiceError(404, "credential_not_found")
                if existing.input_hash != fingerprint:
                    raise ServiceError(409, "credential_operation_conflict")
                return {"credential": public_credential(existing), "token": None}, False
            original = None
            if rotated_from:
                original = db.scalar(
                    select(DeviceCredential)
                    .where(DeviceCredential.id == rotated_from, DeviceCredential.owner_id == owner)
                    .with_for_update()
                )
                if original is None:
                    raise ServiceError(404, "credential_not_found")
                if original.revoked_at is not None:
                    raise ServiceError(409, "credential_revoked")
            count = db.scalar(
                select(func.count())
                .select_from(DeviceCredential)
                .where(DeviceCredential.owner_id == owner)
            )
            if count >= 100:
                raise ServiceError(409, "credential_history_full")
            instant = now_ms()
            active = db.scalar(
                select(func.count())
                .select_from(DeviceCredential)
                .where(
                    DeviceCredential.owner_id == owner,
                    DeviceCredential.revoked_at.is_(None),
                    DeviceCredential.expires_at > instant,
                )
            )
            if active >= 32 and original is None:
                raise ServiceError(409, "credential_limit_reached")
            secret = secrets.token_urlsafe(32)
            credential = DeviceCredential(
                id=operation,
                owner_id=owner,
                token_hash=token_hash(secret),
                input_hash=fingerprint,
                label=label,
                created_at=instant,
                expires_at=instant + lifetime_days * 86_400_000,
                rotated_from_id=rotated_from,
            )
            if original is not None:
                original.revoked_at = instant
            db.add(credential)
            db.flush()
            return {"credential": public_credential(credential), "token": secret}, True

    def revoke(self, owner, credential_id):
        with self.sessions.begin() as db:
            db.scalar(select(User).where(User.id == owner).with_for_update())
            row = db.scalar(
                select(DeviceCredential)
                .where(DeviceCredential.id == credential_id, DeviceCredential.owner_id == owner)
                .with_for_update()
            )
            if row is None:
                raise ServiceError(404, "credential_not_found")
            if row.revoked_at is None:
                row.revoked_at = now_ms()
            return public_credential(row)

    def advance_revision(self, owner):
        with self.sessions.begin() as db:
            db.execute(
                update(User).where(User.id == owner).values(data_revision=User.data_revision + 1)
            )
