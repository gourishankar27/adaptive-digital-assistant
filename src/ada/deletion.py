"""Explicit, owner-wide saved-content erasure with atomic publication and tombstones."""

import hashlib
import json
import threading
from uuid import uuid4

from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError

from ada.agent_models import AgentRun
from ada.consolidation_models import ConsolidationJob
from ada.errors import ServiceError
from ada.inventory import content_tables
from ada.models import Request, User, now_ms
from ada.security_models import DeletedRequest, DeletionJob, DeletionPreview

LEASE_MS = 120_000


def public_job(row):
    return {
        "id": row.id,
        "status": row.status,
        "attempt": row.attempt,
        "created_at": row.created_at,
        "finished_at": row.finished_at,
        "error_code": row.error_code,
        "counts": row.counts,
        "backups_may_retain_content": True,
        "offline_clients_may_retain_content": True,
    }


class DeletionService:
    def __init__(self, sessions, settings, gate):
        self.sessions, self.settings, self.gate = sessions, settings, gate
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self.settings.deletion_worker_enabled and self._thread is None:
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._loop, daemon=True, name="ada-private-deletion"
            )
            self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None

    def _loop(self):
        while not self._stop.is_set():
            try:
                self.process_one()
            except (SQLAlchemyError, ServiceError):
                pass  # Readiness/status reports storage loss; no payload/SQL parameters logged.
            self._stop.wait(0.25)

    def _owner(self, db, owner):
        row = db.scalar(select(User).where(User.id == owner).with_for_update())
        if row is None:
            raise ServiceError(404, "owner_not_found")
        return row

    def _quiet(self, db, owner):
        if self.gate.active(owner) > 1:
            raise ServiceError(409, "owner_operation_busy")
        for model, states in (
            (Request, ("running",)),
            (ConsolidationJob, ("queued", "running")),
            (AgentRun, ("running", "pending_approval")),
        ):
            if db.scalar(
                select(func.count())
                .select_from(model)
                .where(model.owner_id == owner, model.status.in_(states))
            ):
                raise ServiceError(409, "owner_work_in_progress")

    def _counts(self, db, owner):
        return {
            table.name: db.scalar(
                select(func.count()).select_from(table).where(table.c.owner_id == owner)
            )
            for table in content_tables()
        }

    def preview(self, owner):
        with self.sessions.begin() as db:
            user = self._owner(db, owner)
            if user.deletion_job_id:
                raise ServiceError(409, "private_deletion_pending")
            self._quiet(db, owner)
            instant = now_ms()
            # Previews contain only bounded counts and UUIDs, not the content being erased.
            db.execute(
                delete(DeletionPreview).where(
                    DeletionPreview.owner_id == owner, DeletionPreview.expires_at <= instant
                )
            )
            count = db.scalar(
                select(func.count())
                .select_from(DeletionPreview)
                .where(DeletionPreview.owner_id == owner)
            )
            if count >= 25:
                raise ServiceError(409, "deletion_preview_limit")
            row = DeletionPreview(
                owner_id=owner,
                id=str(uuid4()),
                revision=user.data_revision,
                created_at=instant,
                expires_at=instant + 600_000,
                counts=self._counts(db, owner),
            )
            db.add(row)
            return {
                "id": row.id,
                "revision": row.revision,
                "created_at": row.created_at,
                "expires_at": row.expires_at,
                "counts": row.counts,
                "retained": [
                    "account",
                    "device_credentials",
                    "password_credentials",
                    "login_sessions_and_refresh_verifiers",
                    "admin_grants",
                    "minimal_operation_metadata",
                ],
                "backups_may_retain_content": True,
                "offline_clients_may_retain_content": True,
            }

    def confirm(self, owner, job_id, preview_id):
        fingerprint = hashlib.sha256(
            json.dumps([preview_id, "erase_saved_content"], separators=(",", ":")).encode()
        ).hexdigest()
        with self.sessions.begin() as db:
            user = self._owner(db, owner)
            existing = db.get(DeletionJob, (owner, job_id))
            if existing:
                if existing.input_hash != fingerprint:
                    raise ServiceError(409, "deletion_operation_conflict")
                return public_job(existing)
            if not self.settings.deletion_worker_enabled:
                raise ServiceError(503, "deletion_worker_disabled")
            if user.deletion_job_id:
                raise ServiceError(409, "private_deletion_pending")
            self._quiet(db, owner)
            preview = db.get(DeletionPreview, (owner, preview_id))
            if preview is None:
                raise ServiceError(404, "deletion_preview_not_found")
            if (
                preview.expires_at <= now_ms()
                or preview.revision != user.data_revision
                or preview.counts != self._counts(db, owner)
            ):
                raise ServiceError(409, "deletion_preview_stale")
            if (
                db.scalar(
                    select(func.count())
                    .select_from(DeletionJob)
                    .where(DeletionJob.owner_id == owner)
                )
                >= 100
            ):
                raise ServiceError(409, "deletion_history_full")
            row = DeletionJob(
                owner_id=owner,
                id=job_id,
                preview_id=preview_id,
                input_hash=fingerprint,
                revision=preview.revision,
                counts=preview.counts,
                status="queued",
                attempt=0,
                created_at=now_ms(),
            )
            db.add(row)
            user.deletion_job_id = job_id
            db.flush()
            return public_job(row)

    def get(self, owner, job_id):
        with self.sessions() as db:
            row = db.get(DeletionJob, (owner, job_id))
            if row is None:
                raise ServiceError(404, "deletion_job_not_found")
            return public_job(row)

    def list(self, owner):
        with self.sessions() as db:
            return [
                public_job(row)
                for row in db.scalars(
                    select(DeletionJob)
                    .where(DeletionJob.owner_id == owner)
                    .order_by(DeletionJob.created_at.desc(), DeletionJob.id)
                    .limit(25)
                )
            ]

    def process_one(self):
        instant = now_ms()
        with self.sessions.begin() as db:
            candidate = db.execute(
                select(DeletionJob.owner_id, DeletionJob.id)
                .where(
                    or_(
                        DeletionJob.status == "queued",
                        (DeletionJob.status == "running") & (DeletionJob.lease_until <= instant),
                    )
                )
                .order_by(DeletionJob.created_at, DeletionJob.id)
                .limit(1)
            ).first()
            if candidate is None:
                return False
            owner, key = candidate
            # Every path locks owner before job, including confirmation and failure.
            user = self._owner(db, owner)
            row = db.get(DeletionJob, (owner, key), with_for_update=True)
            if row.status not in ("queued", "running") or (
                row.status == "running" and row.lease_until > instant
            ):
                return False
            if user.deletion_job_id != key:
                row.status = "failed"
                row.error_code = "deletion_fence_lost"
                row.finished_at = instant
                row.lease_until = None
                return True
            if row.attempt >= 3:
                row.status = "failed"
                row.error_code = "deletion_attempt_limit"
                row.finished_at = instant
                row.lease_until = None
                user.deletion_job_id = None
                return True
            row.attempt += 1
            row.status = "running"
            row.lease_until = instant + LEASE_MS
            attempt = row.attempt
        try:
            with self.sessions.begin() as db:
                user = self._owner(db, owner)
                row = db.get(DeletionJob, (owner, key), with_for_update=True)
                if row.status != "running" or row.attempt != attempt or user.deletion_job_id != key:
                    raise ServiceError(409, "deletion_fence_lost")
                if db.bind.dialect.name == "postgresql":
                    db.execute(text("SET LOCAL statement_timeout = '60s'"))
                for rid in db.scalars(select(Request.id).where(Request.owner_id == owner)):
                    if db.get(DeletedRequest, (owner, rid)) is None:
                        db.add(
                            DeletedRequest(
                                owner_id=owner, request_id=rid, job_id=key, deleted_at=instant
                            )
                        )
                db.flush()
                for table in content_tables():
                    db.execute(delete(table).where(table.c.owner_id == owner))
                if any(self._counts(db, owner).values()):
                    raise ServiceError(503, "deletion_inventory_incomplete")
                user.data_epoch += 1
                user.data_revision += 1
                user.deletion_job_id = None
                row.status = "completed"
                row.finished_at = now_ms()
                row.lease_until = None
                row.error_code = None
                db.execute(delete(DeletionPreview).where(DeletionPreview.owner_id == owner))
        except (SQLAlchemyError, ServiceError):
            # The erasure transaction rolled back. Publish only a fixed failure code.
            with self.sessions.begin() as db:
                user = self._owner(db, owner)
                row = db.get(DeletionJob, (owner, key), with_for_update=True)
                if row.status == "running" and row.attempt == attempt:
                    row.status = "failed"
                    row.error_code = "deletion_storage_failed"
                    row.finished_at = now_ms()
                    row.lease_until = None
                    if user.deletion_job_id == key:
                        user.deletion_job_id = None
        return True
