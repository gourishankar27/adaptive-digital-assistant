"""Local, explicit grants and fixed-field audit. No private text enters this module."""

import threading
import time
from collections import deque
from uuid import UUID

from sqlalchemy import delete, select, update

from ada.models import AdminAudit, AdminAuditState, AdminGrant, User, now_ms

AUDIT_MAX_ROWS = 10_000
AUDIT_RETENTION_MS = 30 * 24 * 60 * 60 * 1000
# Trusted local database operator, not a user or a remotely assertable principal.
LOCAL_OPERATOR_ID = "00000000-0000-0000-0000-000000000000"


def audit_lock(db):
    # UPDATE also obtains SQLite's write lock, unlike SELECT FOR UPDATE.
    result = db.execute(update(AdminAuditState).where(AdminAuditState.id == 1).values(id=1))
    if result.rowcount != 1:
        raise RuntimeError("admin_audit_state_unavailable")


def audit(db, *, actor_id, actor_kind="user", action, outcome, owner_id=None, request_id=None):
    """Call under audit_lock; pruning and the new row commit atomically."""
    timestamp = now_ms()
    db.execute(delete(AdminAudit).where(AdminAudit.created_at < timestamp - AUDIT_RETENTION_MS))
    cutoff = db.scalar(
        select(AdminAudit.id).order_by(AdminAudit.id.desc()).offset(AUDIT_MAX_ROWS - 2).limit(1)
    )
    if cutoff is not None:
        db.execute(delete(AdminAudit).where(AdminAudit.id < cutoff))
    db.add(
        AdminAudit(
            actor_id=actor_id,
            actor_kind=actor_kind,
            action=action,
            target_owner_id=owner_id,
            target_request_id=request_id,
            outcome=outcome,
            created_at=timestamp,
        )
    )


def set_admin_grant(sessions, user_id: str, enabled: bool):
    user_id = str(UUID(user_id))
    with sessions.begin() as db:
        audit_lock(db)
        if db.scalar(select(User.id).where(User.id == user_id)) is None:
            audit(
                db,
                actor_id=LOCAL_OPERATOR_ID,
                actor_kind="local_operator",
                action="role.grant" if enabled else "role.revoke",
                outcome="not_found",
                owner_id=user_id,
            )
            missing = True
        else:
            missing = False
            row = db.get(AdminGrant, user_id)
            changed = (row.enabled if row else False) != enabled
            if row is None and enabled:
                db.add(AdminGrant(user_id=user_id, enabled=True))
            elif row is not None and changed:
                row.enabled, row.updated_at = enabled, now_ms()
            audit(
                db,
                actor_id=LOCAL_OPERATOR_ID,
                actor_kind="local_operator",
                action="role.grant" if enabled else "role.revoke",
                owner_id=user_id,
                outcome=("granted" if enabled else "revoked") if changed else "unchanged",
            )
    if missing:
        raise ValueError("user_not_found")
    return {"user_id": user_id, "admin_monitoring": enabled}


class PollLimiter:
    """Single-worker, bounded principal and global sliding windows."""

    def __init__(self):
        self.clock = time.monotonic
        self.lock = threading.Lock()
        self.principals = {}
        self.global_calls = deque()
        self.global_denied_at = -60.0

    def admit(self, owner):
        with self.lock:
            current = self.clock()
            while self.global_calls and self.global_calls[0] <= current - 60:
                self.global_calls.popleft()
            self.principals = {k: v for k, v in self.principals.items() if v[1] > current - 60}
            if owner not in self.principals:
                if len(self.principals) >= 4096:
                    return False, False
                self.principals[owner] = (deque(), current, False)
            calls, _, denied = self.principals[owner]
            while calls and calls[0] <= current - 60:
                calls.popleft()
            if len(calls) >= 60 or len(self.global_calls) >= 600:
                record = not denied and self.global_denied_at <= current - 60
                if record:
                    self.global_denied_at = current
                self.principals[owner] = (calls, current, True)
                return False, record
            calls.append(current)
            self.global_calls.append(current)
            self.principals[owner] = (calls, current, False)
            return True, True
