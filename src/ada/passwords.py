"""Bounded Argon2id verification, explicit enrollment and rotating opaque sessions."""

import collections
import contextlib
import secrets
import threading
import time
import unicodedata

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import delete, func, select, update

from ada.auth import token_hash
from ada.errors import ServiceError
from ada.login_models import LoginSession, PasswordCredential, RefreshVerifier
from ada.models import User, new_id, now_ms

# RFC 9106 low-memory profile: measured separately, never user-controlled parameters.
HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, type=Type.ID)
_DUMMY = HASHER.hash(secrets.token_urlsafe(32))


def normalize_login(value):
    result = unicodedata.normalize("NFKC", value.strip()).casefold()
    if not 1 <= len(result) <= 160 or any(
        unicodedata.category(c)[0] == "C" or c.isspace() for c in result
    ):
        raise ValueError("Login must contain 1–160 visible characters without spaces")
    return result


def validate_password(value):
    if not 15 <= len(value) <= 1024 or any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError("Password must contain 15–1024 Unicode characters")


class PasswordSessions:
    def __init__(self, sessions, settings):
        self.sessions, self.settings = sessions, settings
        self.slots = threading.BoundedSemaphore(2)
        self.lock = threading.Lock()
        self.rates = collections.OrderedDict()

    @contextlib.contextmanager
    def hashing(self):
        if not self.slots.acquire(blocking=False):
            raise ServiceError(503, "authentication_busy")
        try:
            yield
        finally:
            self.slots.release()

    def admit(self, ip, identifier=None):
        # Digest keys only, bounded memory; fixed windows are not permanent account locks.
        instant = time.monotonic()
        keys = (
            [("global", "", 120), ("ip", token_hash(ip), 30)]
            if identifier is None
            else [("account", token_hash(identifier), 10)]
        )
        with self.lock:
            for kind, key, maximum in keys:
                start, count = self.rates.get((kind, key), (instant, 0))
                if instant - start >= 60:
                    start, count = instant, 0
                self.rates[(kind, key)] = (start, count + 1)
                self.rates.move_to_end((kind, key))
                if count >= maximum:
                    raise ServiceError(429, "authentication_rate_limited")
            while len(self.rates) > 4096:
                self.rates.popitem(last=False)

    def set_password(self, owner, login, password):
        login = normalize_login(login)
        validate_password(password)
        with self.hashing():
            verifier = HASHER.hash(password)
        with self.sessions.begin() as db:
            # Assignment is local-operator only; never infer identity from a display name.
            users = list(db.scalars(select(User).order_by(User.id).with_for_update()))
            if owner not in {u.id for u in users}:
                raise ValueError("Account not found")
            matches = []
            for u in users:
                try:
                    if normalize_login(u.name) == login:
                        matches.append(u.id)
                except ValueError:
                    pass
            existing = db.scalar(
                select(PasswordCredential).where(PasswordCredential.login == login)
            )
            if (
                len(matches) > 1
                or (matches and owner not in matches)
                or (existing and existing.owner_id != owner)
            ):
                raise ValueError("Normalized login collision; select a distinct identifier")
            row = db.get(PasswordCredential, owner)
            if row is None:
                row = PasswordCredential(owner_id=owner, login=login, changed_at=now_ms())
                db.add(row)
            row.login, row.verifier, row.changed_at = login, verifier, now_ms()
            from ada.scheduling import pause_automation

            pause_automation(db, owner, "password_reset")
            db.execute(
                update(LoginSession)
                .where(LoginSession.owner_id == owner, LoginSession.revoked_at.is_(None))
                .values(revoked_at=now_ms())
            )

    def verify(self, verifier, password):
        try:
            return HASHER.verify(verifier or _DUMMY, password)
        except (VerificationError, InvalidHashError, UnicodeError):
            return False

    def login(self, username, password, label="Android"):
        try:
            username = normalize_login(username)
        except ValueError:
            username = ""  # Still do dummy verification for invalid identifiers.
        with self.sessions() as db:
            row = db.scalar(select(PasswordCredential).where(PasswordCredential.login == username))
            verifier, owner = (row.verifier, row.owner_id) if row else (None, None)
        with self.hashing():
            valid = self.verify(verifier, password)
            replacement = (
                HASHER.hash(password)
                if valid and verifier and HASHER.check_needs_rehash(verifier)
                else None
            )
        if not valid or verifier is None:
            raise ServiceError(401, "invalid_login")
        with self.sessions.begin() as db:
            db.scalar(select(User).where(User.id == owner).with_for_update())
            current = db.get(PasswordCredential, owner)
            if current is None or current.verifier != verifier:
                raise ServiceError(401, "invalid_login")
            if replacement:
                current.verifier = replacement
            instant = now_ms()
            expired = select(LoginSession.id).where(
                LoginSession.owner_id == owner, LoginSession.expires_at <= instant
            )
            db.execute(delete(RefreshVerifier).where(RefreshVerifier.family_id.in_(expired)))
            db.execute(
                delete(LoginSession).where(
                    LoginSession.owner_id == owner, LoginSession.expires_at <= instant
                )
            )
            count = db.scalar(
                select(func.count()).select_from(LoginSession).where(LoginSession.owner_id == owner)
            )
            if count >= 128:
                obsolete = db.scalar(
                    select(LoginSession.id)
                    .where(LoginSession.owner_id == owner, LoginSession.revoked_at.is_not(None))
                    .order_by(LoginSession.created_at, LoginSession.id)
                    .limit(1)
                )
                if obsolete:
                    db.execute(delete(RefreshVerifier).where(RefreshVerifier.family_id == obsolete))
                    db.execute(delete(LoginSession).where(LoginSession.id == obsolete))
                    count -= 1
            if count >= 128:
                raise ServiceError(429, "session_history_full")
            family = LoginSession(
                id=new_id(),
                owner_id=owner,
                label=label,
                created_at=instant,
                expires_at=instant + self.settings.session_absolute_seconds * 1000,
                generation=0,
            )
            db.add(family)
            return self._issue(db, family, instant)

    def _issue(self, db, family, instant):
        access, refresh = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
        family.access_hash = token_hash(access)
        family.access_expires_at = min(
            family.expires_at, instant + self.settings.session_access_seconds * 1000
        )
        family.idle_expires_at = min(
            family.expires_at, instant + self.settings.session_idle_seconds * 1000
        )
        db.flush()
        db.add(RefreshVerifier(digest=token_hash(refresh), family_id=family.id))
        return {
            "access_token": access,
            "refresh_token": refresh,
            "session_id": family.id,
            "access_expires_at": family.access_expires_at,
            "expires_at": family.expires_at,
        }

    def refresh(self, token):
        digest = token_hash(token)
        with self.sessions() as db:
            owner = db.scalar(
                select(LoginSession.owner_id)
                .join(RefreshVerifier, RefreshVerifier.family_id == LoginSession.id)
                .where(RefreshVerifier.digest == digest)
            )
        if owner is None:
            raise ServiceError(401, "invalid_login")
        result = None
        with self.sessions.begin() as db:
            db.scalar(select(User).where(User.id == owner).with_for_update())
            row = db.get(RefreshVerifier, digest)
            family = db.get(LoginSession, row.family_id) if row else None
            instant = now_ms()
            if family and family.revoked_at is None:
                if (
                    row.used_at is not None
                    or family.expires_at <= instant
                    or family.idle_expires_at <= instant
                    or family.generation >= 4096
                ):
                    family.revoked_at = instant
                else:
                    row.used_at = instant
                    family.generation += 1
                    result = self._issue(db, family, instant)
        # Revocation MUST commit even though the HTTP response is an authentication failure.
        if result is None:
            raise ServiceError(401, "invalid_login")
        return result

    def revoke(self, owner, family_id=None):
        with self.sessions.begin() as db:
            db.scalar(select(User).where(User.id == owner).with_for_update())
            query = update(LoginSession).where(
                LoginSession.owner_id == owner, LoginSession.revoked_at.is_(None)
            )
            if family_id is not None:
                if not db.scalar(
                    select(LoginSession.id).where(
                        LoginSession.owner_id == owner, LoginSession.id == family_id
                    )
                ):
                    raise ServiceError(404, "session_not_found")
                query = query.where(LoginSession.id == family_id)
            db.execute(query.values(revoked_at=now_ms()))
            if family_id is None:
                from ada.scheduling import pause_automation

                pause_automation(db, owner, "all_sessions_revoked")

    def change_password(self, owner, old, new):
        validate_password(new)
        with self.sessions() as db:
            row = db.get(PasswordCredential, owner)
            verifier = row.verifier if row else None
        with self.hashing():
            valid = self.verify(verifier, old)
            replacement = HASHER.hash(new) if valid and verifier else None
        if replacement is None:
            raise ServiceError(401, "invalid_login")
        with self.sessions.begin() as db:
            db.scalar(select(User).where(User.id == owner).with_for_update())
            row = db.get(PasswordCredential, owner)
            if row is None or row.verifier != verifier:
                raise ServiceError(401, "invalid_login")
            row.verifier, row.changed_at = replacement, now_ms()
            from ada.scheduling import pause_automation

            pause_automation(db, owner, "password_changed")
            db.execute(
                update(LoginSession)
                .where(LoginSession.owner_id == owner, LoginSession.revoked_at.is_(None))
                .values(revoked_at=now_ms())
            )

    def list(self, owner):
        with self.sessions() as db:
            return [
                {
                    key: getattr(row, key)
                    for key in ("id", "label", "created_at", "expires_at", "revoked_at")
                }
                for row in db.scalars(
                    select(LoginSession)
                    .where(LoginSession.owner_id == owner)
                    .order_by(LoginSession.created_at.desc())
                    .limit(128)
                )
            ]
