"""Opt-in bounded idle drafts. Authority is checked before input and publication.

The existing scheduler queues units and the existing consolidation worker runs
them. No independent daemon, factual write, external action or hidden reasoning.
"""

import re
import threading
import time
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid4, uuid5

from sqlalchemy import func, inspect, or_, select
from sqlalchemy.orm import defer

from ada.consolidation import MAX_INPUT_BYTES, MAX_JOBS
from ada.consolidation_models import ConsolidationJob
from ada.curiosity import CATALOG
from ada.curiosity_contracts import CuriosityCreate, CuriosityOpen, CuriosityPinInput
from ada.curiosity_models import CuriosityPolicy, CuriosityQuestion
from ada.errors import ServiceError
from ada.memory import owned_scope
from ada.models import Claim, DocumentUpload, Event, Request, Source, SourceVersion, User, now_ms
from ada.proposals import fingerprint
from ada.providers import ProviderError
from ada.reflection_contracts import VERSION, ReflectionContent, ReflectionSettings
from ada.reflection_models import (
    ReflectionArtifact,
    ReflectionPolicy,
    ReflectionProviderState,
    ReflectionReceipt,
    ReflectionRun,
)
from ada.review_integrity import valid_review
from ada.schedule_models import ScheduleConsent
from ada.schedule_time import DAY, TIMEZONE_DATA, zone
from ada.security_models import DeviceCredential

MAX_RUNS = 100
MAX_RECEIPTS = 5000


def stable_id(*parts):
    return str(uuid5(NAMESPACE_URL, VERSION + "/" + "/".join(map(str, parts))))


def pause_reflection(db, owner, reason, origin_kind=None, origin_id=None):
    """Credential/automation hooks already hold the owner lock; old schemas work."""
    if not inspect(db.connection()).has_table("reflection_policies"):
        return
    row = db.get(ReflectionPolicy, owner)
    if row is None or (
        origin_kind and (row.origin_kind != origin_kind or row.origin_id != origin_id)
    ):
        return
    row.enabled = False
    row.revision += 1
    row.settings = row.settings | {"enabled": False}
    row.last_decision, row.updated_at = reason, now_ms()
    for run in db.scalars(
        select(ReflectionRun).where(
            ReflectionRun.owner_id == owner, ReflectionRun.status.in_(["queued", "running"])
        )
    ):
        run.status, run.reason, run.finished_at = "suppressed", reason, now_ms()
        run.lease_until = run.lease_token = None


class ReflectionService:
    def __init__(self, sessions, settings, scheduler, consolidation, chat, clock=now_ms):
        self.sessions, self.settings, self.scheduler = sessions, settings, scheduler
        self.consolidation, self.curiosity, self.chat = consolidation, scheduler.curiosity, chat
        self.clock = clock
        self._boot = self._last_activity = clock()
        self._lock = threading.Lock()
        self._active = None
        # The existing host observer supplies fresh measurements. Unknown is unsafe;
        # workers never run OS sensors while holding database locks or inference.
        self.resources = lambda: {}
        self.provider = None  # Only the separately validated cancellable adapter can be used.
        self.cancel_budget_seconds = 2.0
        self._stop = threading.Event()

    def _measure(self):
        try:
            return dict(self.resources())
        except Exception:
            return {}

    def activity(self, owner):
        # Authenticated ADA activity only; no OS keyboard/screen/phone surveillance.
        with self._lock:
            self._last_activity = self.clock()
            active = self._active
            if active:
                active["reason"] = "foreground_arrival"
                active["cancel"].set()
            return active is not None

    def stop(self):
        self._stop.set()
        with self._lock:
            if self._active:
                self._active["reason"] = "server_stopping"
                self._active["cancel"].set()

    def _row(self, db, owner, *, payload=True):
        statement = select(ReflectionPolicy).where(ReflectionPolicy.owner_id == owner)
        if not payload:
            statement = statement.options(defer(ReflectionPolicy.settings, raiseload=True))
        return db.scalar(statement)

    def _consent(self, db, user, row):
        if not row.enabled or row.epoch != user.data_epoch or row.version != VERSION:
            return "consent_or_epoch_changed"
        grant = db.get(ScheduleConsent, user.id)
        if not grant or not grant.enabled or grant.revision != row.consent_revision:
            return "automation_consent_changed"
        if user.deletion_job_id:
            return "owner_deletion_pending"
        if row.origin_kind == "device":
            device = db.get(DeviceCredential, row.origin_id)
            if (
                not device
                or device.owner_id != user.id
                or device.revoked_at is not None
                or device.expires_at <= self.clock()
            ):
                return "origin_device_unavailable"
        return None

    def _authority(self, db, owner, row):
        user = self.scheduler._owner(db, owner)
        db.refresh(
            row,
            attribute_names=[
                "enabled",
                "revision",
                "epoch",
                "consent_revision",
                "origin_kind",
                "origin_id",
            ],
        )
        reason = self._consent(db, user, row)
        if reason:
            return reason, None
        db.refresh(row, attribute_names=["settings"])
        settings = ReflectionSettings(**row.settings)
        return None, settings

    def globally_enabled(self):
        return (
            self.settings.reflection_enabled
            and self.settings.scheduler_enabled
            and self.settings.consolidation_worker_enabled
        )

    @staticmethod
    def _policy_hash(settings):
        values = settings.model_dump(mode="json") | {"enabled": True}
        for key in ("scope_ids", "source_types", "job_kinds"):
            values[key] = sorted(values[key])
        return fingerprint({"version": VERSION, "settings": values, "timezone_data": TIMEZONE_DATA})

    def _room(self, settings, values):
        if self._stop.is_set() or not self.globally_enabled():
            return "global_automation_stopped"
        if self.clock() - max(self._boot, self._last_activity) < settings.idle_seconds * 1000:
            return "foreground_active"
        local = datetime.fromtimestamp(self.clock() / 1000, timezone.utc).astimezone(
            zone(settings.timezone)
        )
        if not settings.allowed_start <= local.hour * 60 + local.minute < settings.allowed_end:
            return "outside_allowed_hours"
        try:
            if values.get("ac_power") is not True:
                return "ac_power_unknown_or_off"
            limits = (
                ("disk_free_bytes", settings.minimum_disk_mib * 1024**2, False),
                ("memory_available_percent", settings.minimum_memory_percent, False),
                ("thermal_c", settings.maximum_thermal_c, True),
            )
            for key, bound, upper in limits:
                value = values.get(key)
                if type(value) not in (float, int) or not float("-inf") < value < float("inf"):
                    return "resource_state_unknown"
                if (value >= bound) if upper else (value < bound):
                    return "resource_pressure"
        except Exception:
            return "resource_state_unknown"
        return None

    def _old(self, db, owner, operation, payload):
        row = db.get(ReflectionReceipt, (owner, str(operation)))
        if row and row.input_hash != fingerprint(payload):
            raise ServiceError(409, "reflection_operation_reused")
        return row.result if row else None

    def _receipt(self, db, owner, operation, payload, action, *, off=False, **result):
        count = db.scalar(
            select(func.count())
            .select_from(ReflectionReceipt)
            .where(ReflectionReceipt.owner_id == owner)
        )
        if count >= MAX_RECEIPTS - (0 if off else 1):
            raise ServiceError(413, "reflection_receipt_limit")
        output = {
            "version": VERSION,
            "operation_id": str(operation),
            "action": action,
            "state": "completed",
            "created_at": self.clock(),
            **result,
        }
        db.add(
            ReflectionReceipt(
                owner_id=owner,
                id=str(operation),
                input_hash=fingerprint(payload),
                result=output,
                created_at=self.clock(),
            )
        )
        return output

    def receipt(self, owner, operation):
        with self.sessions() as db:
            row = db.get(ReflectionReceipt, (owner, operation))
            if row is None:
                raise ServiceError(404, "reflection_receipt_not_found")
            return row.result

    def summary_available(self, db=None):
        if (
            not self.settings.reflection_summary_enabled
            or self.provider is None
            or self.settings.max_parallel != 1
        ):
            return False
        if db is None:
            with self.sessions() as session:
                return self.summary_available(session)
        state = db.get(ReflectionProviderState, self.provider.key)
        return bool(state and state.ready)

    def policy(self, owner):
        with self.sessions() as db:
            row = self._row(db, owner)
            consent = db.get(ScheduleConsent, owner)
            settings = ReflectionSettings(**row.settings) if row else ReflectionSettings()
            return {
                "revision": row.revision if row else 0,
                "settings": settings.model_dump(mode="json"),
                "globally_enabled": self.globally_enabled(),
                "scheduling_consent": bool(consent and consent.enabled),
                "summary_generation": self.summary_available(db),
                "last_decision": row.last_decision if row else None,
                "foreground_idle_seconds": max(
                    0, (self.clock() - max(self._boot, self._last_activity)) // 1000
                ),
            }

    def write_policy(self, owner, body, principal):
        payload = body.model_dump(mode="json")
        with self.sessions.begin() as db:
            user = self.scheduler._owner(db, owner, principal)
            previous = self._old(db, owner, body.operation_id, payload)
            if previous:
                return previous
            row = self._row(db, owner)
            revision = row.revision if row else 0
            if revision != body.expected_revision:
                raise ServiceError(409, "reflection_revision_changed")
            selected = body.settings
            for scope in selected.scope_ids:
                owned_scope(db, owner, str(scope), lock=True)
            grant = db.get(ScheduleConsent, owner)
            if selected.enabled and (not grant or not grant.enabled):
                raise ServiceError(409, "reflection_automation_consent_required")
            if (
                selected.enabled
                and "summary" in selected.job_kinds
                and not self.summary_available(db)
            ):
                raise ServiceError(409, "reflection_summary_not_validated")
            if row:
                pause_reflection(db, owner, "policy_changed")
            else:
                row = ReflectionPolicy(owner_id=owner, revision=0)
                db.add(row)
            row.revision = revision + 1
            row.version = VERSION
            row.enabled, row.epoch = selected.enabled, user.data_epoch
            row.origin_kind, row.origin_id = self.scheduler._origin(principal)
            row.consent_revision = grant.revision if grant else 0
            row.settings, row.updated_at, row.last_decision = (
                payload["settings"],
                self.clock(),
                "awaiting_idle" if selected.enabled else "owner_off",
            )
            return self._receipt(
                db,
                owner,
                body.operation_id,
                payload,
                "policy",
                off=not selected.enabled,
                revision=row.revision,
            )

    def _sources(self, db, owner, scope, settings):
        owned_scope(db, owner, scope, lock=True)
        # Select only bounded metadata before loading any source bodies.
        selected = db.execute(
            select(
                SourceVersion.id,
                SourceVersion.source_id,
                SourceVersion.version,
                Source.kind,
                Source.event_id,
                func.length(SourceVersion.content),
            )
            .join(
                Source,
                (Source.id == SourceVersion.source_id)
                & (Source.owner_id == SourceVersion.owner_id)
                & (Source.scope_id == SourceVersion.scope_id),
            )
            .where(
                SourceVersion.owner_id == owner,
                SourceVersion.scope_id == scope,
                SourceVersion.created_at <= self.clock(),
                SourceVersion.created_at >= self.clock() - settings.lookback_days * DAY,
            )
            .order_by(SourceVersion.created_at.desc(), SourceVersion.id)
            .limit(100)
        ).all()
        pins, snapshot, size = [], [], 0
        omissions = {"too_large": 0, "unavailable": 0, "selection_bound": int(len(selected) == 100)}
        for identifier, source_id, version, kind, event_id, length in selected:
            latest = db.scalar(
                select(func.max(SourceVersion.version)).where(
                    SourceVersion.owner_id == owner,
                    SourceVersion.scope_id == scope,
                    SourceVersion.source_id == source_id,
                )
            )
            if latest != version:
                continue
            source_type = {
                "user_note": "user_notes",
                "imported_document": "imported_documents",
            }.get(kind)
            if kind == "chat_event":
                if not settings.automatic_completed_turns:
                    continue
                event = db.get(Event, event_id)
                request = (
                    db.get(Request, (owner, event.request_id))
                    if event and event.owner_id == owner
                    else None
                )
                if not request or request.status != "completed":
                    continue
                source_type = (
                    "completed_user_turns" if event.role == "user" else "completed_model_turns"
                )
            if source_type not in settings.source_types:
                continue
            if not length or length > MAX_INPUT_BYTES:
                omissions["too_large"] += 1
                continue
            try:
                self._pin_metadata(db, owner, scope, [{"source_version_id": identifier}])
            except ServiceError:
                omissions["unavailable"] += 1
                continue
            row = db.get(SourceVersion, identifier)
            cost = len(row.content.encode("utf-8"))
            if cost == 0 or cost + size > MAX_INPUT_BYTES:
                omissions["too_large"] += 1
                continue
            pin = {
                "source_version_id": row.id,
                "version": row.version,
                "content_hash": row.content_hash,
                "span_start": 0,
                "span_end": len(row.content),
            }
            try:
                chosen = self.consolidation._sources(db, owner, scope, [pin], self.clock())
            except ServiceError:
                omissions["unavailable"] += 1
                continue
            pins.append(pin)
            snapshot.extend(chosen)
            size += cost
            if len(pins) == 4:
                omissions["selection_bound"] += 1
                break
        return pins, snapshot, omissions

    def _pin_metadata(self, db, owner, scope, pins):
        owned_scope(db, owner, scope)
        for pin in pins:
            row = db.execute(
                select(
                    SourceVersion.version,
                    SourceVersion.content_hash,
                    SourceVersion.source_id,
                    Source.kind,
                    Source.event_id,
                )
                .join(
                    Source,
                    (Source.id == SourceVersion.source_id)
                    & (Source.owner_id == SourceVersion.owner_id)
                    & (Source.scope_id == SourceVersion.scope_id),
                )
                .where(
                    SourceVersion.id == pin["source_version_id"],
                    SourceVersion.owner_id == owner,
                    SourceVersion.scope_id == scope,
                )
            ).first()
            if row is None:
                raise ServiceError(409, "reflection_source_changed")
            version, digest, source_id, kind, event_id = row
            latest = db.scalar(
                select(func.max(SourceVersion.version)).where(
                    SourceVersion.owner_id == owner,
                    SourceVersion.scope_id == scope,
                    SourceVersion.source_id == source_id,
                )
            )
            if latest != version or (
                "version" in pin and (pin["version"] != version or pin["content_hash"] != digest)
            ):
                raise ServiceError(409, "reflection_source_changed")
            if kind == "imported_document":
                upload = db.execute(
                    select(DocumentUpload.id).where(
                        DocumentUpload.owner_id == owner,
                        DocumentUpload.scope_id == scope,
                        DocumentUpload.source_version_id == pin["source_version_id"],
                        DocumentUpload.state == "ready",
                        DocumentUpload.published_at <= self.clock(),
                        DocumentUpload.available_from <= self.clock(),
                        or_(
                            DocumentUpload.available_to.is_(None),
                            DocumentUpload.available_to > self.clock(),
                        ),
                    )
                ).first()
                if upload is None:
                    raise ServiceError(409, "reflection_source_unavailable")
            if kind == "chat_event":
                event = db.get(Event, event_id)
                request = db.get(Request, (owner, event.request_id)) if event else None
                if not request or request.status != "completed":
                    raise ServiceError(409, "reflection_source_unavailable")

    def _fresh(self, db, run, *, lock=True):
        owned_scope(db, run.owner_id, run.scope_id, lock=lock)
        self._pin_metadata(db, run.owner_id, run.scope_id, run.pins)
        current = self.consolidation._sources(
            db, run.owner_id, run.scope_id, run.pins, run.created_at
        )
        if current != run.snapshot:
            raise ServiceError(409, "reflection_source_changed")
        for pin in run.pins:
            version = db.get(SourceVersion, pin["source_version_id"])
            latest = db.scalar(
                select(func.max(SourceVersion.version)).where(
                    SourceVersion.owner_id == run.owner_id,
                    SourceVersion.scope_id == run.scope_id,
                    SourceVersion.source_id == version.source_id,
                )
            )
            if latest != version.version:
                raise ServiceError(409, "reflection_source_changed")

    def queue_once(self):
        if self._stop.is_set() or not self.globally_enabled():
            return False
        measured = self._measure()
        with self.sessions() as db:
            owners = db.scalars(
                select(ReflectionPolicy.owner_id)
                .where(ReflectionPolicy.enabled.is_(True))
                .order_by(ReflectionPolicy.updated_at, ReflectionPolicy.owner_id)
                .limit(20)
            ).all()
        for owner in owners:
            with self.sessions.begin() as db:
                row = self._row(db, owner, payload=False)
                reason, settings = self._authority(db, owner, row)
                if reason:
                    pause_reflection(db, owner, reason)
                    continue
                row.updated_at = self.clock()
                reason = self._room(settings, measured)
                if reason:
                    row.last_decision = reason
                    continue
                day = datetime.fromtimestamp(self.clock() / 1000, timezone.utc).date().isoformat()
                rows = db.scalars(
                    select(ReflectionRun)
                    .options(
                        defer(ReflectionRun.snapshot, raiseload=True),
                        defer(ReflectionRun.pins, raiseload=True),
                    )
                    .where(ReflectionRun.owner_id == owner)
                ).all()
                if any(r.budget_day > day for r in rows):
                    row.last_decision = "clock_moved_backwards"
                    continue
                if len(rows) >= MAX_RUNS:
                    row.last_decision = "retained_job_limit"
                    continue
                if sum(r.budget_day == day for r in rows) >= settings.max_jobs:
                    row.last_decision = "nightly_job_limit"
                    continue
                if (
                    sum(r.charged_ms for r in rows if r.budget_day == day)
                    >= settings.nightly_seconds * 1000
                ):
                    row.last_decision = "nightly_time_limit"
                    continue
                semantic = self._policy_hash(settings)
                for scope in map(str, settings.scope_ids):
                    if (
                        db.scalar(
                            select(func.count())
                            .select_from(ConsolidationJob)
                            .where(
                                ConsolidationJob.owner_id == owner,
                                ConsolidationJob.scope_id == scope,
                            )
                        )
                        + sum(r.scope_id == scope for r in rows)
                        >= MAX_JOBS
                    ):
                        row.last_decision = "retained_job_limit"
                        continue
                    pins, snapshot, omissions = self._sources(db, owner, scope, settings)
                    reason = self._room(settings, measured)
                    if reason:
                        row.last_decision = reason
                        return False
                    if not pins:
                        row.last_decision = (
                            "empty_selection"
                            if settings.allow_empty
                            else "empty_selection_needs_review"
                        )
                        continue
                    for kind in settings.job_kinds:
                        if kind == "summary" and not self.summary_available(db):
                            row.last_decision = "summary_class_disabled"
                            continue
                        if kind == "question":
                            curiosity = db.get(CuriosityPolicy, owner)
                            if (
                                not curiosity
                                or not curiosity.settings["enabled"]
                                or not curiosity.settings["inbox_enabled"]
                                or not self.curiosity._allowed(
                                    curiosity.settings, settings.question_topic
                                )
                            ):
                                row.last_decision = "question_consent_missing"
                                continue
                        key = stable_id(owner, scope, kind, semantic, fingerprint(pins))
                        if db.get(ReflectionRun, (owner, key)):
                            row.last_decision = "source_set_already_considered"
                            continue
                        db.add(
                            ReflectionRun(
                                owner_id=owner,
                                id=key,
                                scope_id=scope,
                                revision=row.revision,
                                epoch=row.epoch,
                                kind=kind,
                                policy_hash=semantic,
                                question_revision=curiosity.revision
                                if kind == "question"
                                else None,
                                provider_key=self.provider.key if kind == "summary" else None,
                                status="queued",
                                reason=None,
                                attempt=0,
                                lease_until=None,
                                lease_token=None,
                                budget_day=day,
                                charged_ms=0,
                                expires_at=self.clock() + DAY,
                                snapshot=snapshot,
                                pins=pins,
                                omissions=omissions,
                                created_at=self.clock(),
                            )
                        )
                        row.last_decision = "queued"
                        return True
        return False

    @staticmethod
    def _terminal(run, state, reason, instant):
        run.status, run.reason, run.finished_at = state, reason, instant
        run.lease_until = run.lease_token = None

    def _run_authority(self, db, row, run, settings):
        if run.revision != row.revision or run.epoch != row.epoch:
            return "policy_or_epoch_changed"
        if run.expires_at <= self.clock():
            return "unit_expired"
        if run.policy_hash != self._policy_hash(settings):
            return "time_rules_or_policy_changed"
        if run.kind == "summary" and not self.summary_available(db):
            return "summary_class_disabled"
        if run.kind == "question":
            question = db.get(CuriosityPolicy, run.owner_id)
            if (
                not question
                or question.revision != run.question_revision
                or not question.settings["enabled"]
                or not question.settings["inbox_enabled"]
                or not self.curiosity._allowed(question.settings, settings.question_topic)
            ):
                return "question_consent_changed"
        return None

    def claim(self, measured=None):
        measured = self._measure() if measured is None else measured
        with self.sessions() as db:
            key = db.execute(
                select(ReflectionRun.owner_id, ReflectionRun.id)
                .where(
                    or_(
                        ReflectionRun.status == "queued",
                        (ReflectionRun.status == "running")
                        & (ReflectionRun.lease_until <= self.clock()),
                    )
                )
                .order_by(ReflectionRun.created_at, ReflectionRun.id)
                .limit(1)
            ).first()
        if not key:
            return None
        owner, identifier = key
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner)
            policy = self._row(db, owner, payload=False)
            reason, settings = self._authority(db, owner, policy)
            run = db.scalar(
                select(ReflectionRun)
                .options(
                    defer(ReflectionRun.snapshot, raiseload=True),
                    defer(ReflectionRun.pins, raiseload=True),
                )
                .where(ReflectionRun.owner_id == owner, ReflectionRun.id == identifier)
                .with_for_update()
            )
            if run.status not in ("queued", "running") or (
                run.status == "running" and run.lease_until > self.clock()
            ):
                return None
            reason = reason or self._run_authority(db, policy, run, settings)
            if reason:
                self._terminal(run, "suppressed", reason, self.clock())
                return None
            reason = self._room(settings, measured)
            if reason:
                policy.last_decision = reason
                return None
            day = datetime.fromtimestamp(self.clock() / 1000, timezone.utc).date().isoformat()
            charged = db.scalar(
                select(func.coalesce(func.sum(ReflectionRun.charged_ms), 0)).where(
                    ReflectionRun.owner_id == owner, ReflectionRun.budget_day == day
                )
            )
            if (
                run.attempt >= 3
                or charged + settings.unit_seconds * 1000 > settings.nightly_seconds * 1000
            ):
                self._terminal(run, "suppressed", "attempt_or_time_limit", self.clock())
                return None
            try:
                db.refresh(run, attribute_names=["pins"])
                self._pin_metadata(db, owner, run.scope_id, run.pins)
                db.refresh(run, attribute_names=["snapshot"])
                self._fresh(db, run)
            except ServiceError:
                self._terminal(run, "suppressed", "source_changed", self.clock())
                return None
            run.status, run.reason, run.started_at = "running", None, self.clock()
            run.attempt += 1
            run.charged_ms += settings.unit_seconds * 1000
            run.budget_day = day
            run.lease_token, run.lease_until = (
                str(uuid4()),
                self.clock() + (settings.unit_seconds + 7) * 1000,
            )
            return run, settings

    def _report(self, run):
        states = {}
        for pin, source in sorted(
            zip(run.pins, run.snapshot),
            key=lambda pair: (pair[1]["created_at"], pair[0]["source_version_id"]),
        ):
            if source["trust_class"] != "user_explicit":
                continue
            for match in re.finditer(
                r"(?im)^\s*(TODO|OPEN|DONE):\s*(.{1,600})$", source["evidence"]["quote"]
            ):
                label, text = match.groups()
                key = " ".join(text.split()).casefold()
                states[key] = (label.upper(), text, pin)
        findings = [
            {
                "category": "owner_marked_open_item",
                "text": "Owner-marked open item; completion outside these selected sources has not been checked: "
                + text,
                "support": [pin],
                "claim_ids": [],
            }
            for label, text, pin in states.values()
            if label != "DONE"
        ]
        with self.sessions() as db:
            claims = db.scalars(
                select(Claim)
                .where(
                    Claim.owner_id == run.owner_id,
                    Claim.scope_id == run.scope_id,
                    Claim.source_version_id.in_([p["source_version_id"] for p in run.pins]),
                )
                .order_by(Claim.id)
                .limit(16)
            ).all()
            claims = [c for c in claims if valid_review(db, c)]
            for i, left in enumerate(claims):
                for right in claims[i + 1 :]:
                    if (
                        left.subject_entity_id or left.subject.casefold(),
                        left.predicate.casefold(),
                    ) != (
                        right.subject_entity_id or right.subject.casefold(),
                        right.predicate.casefold(),
                    ) or left.value.casefold() == right.value.casefold():
                        continue
                    if max(left.valid_from, right.valid_from) >= min(
                        left.valid_to if left.valid_to is not None else 2**63 - 1,
                        right.valid_to if right.valid_to is not None else 2**63 - 1,
                    ):
                        continue
                    support = [
                        p
                        for p in run.pins
                        if p["source_version_id"]
                        in (left.source_version_id, right.source_version_id)
                    ]
                    findings.append(
                        {
                            "category": "possible_change_or_conflict",
                            "text": "Two endorsed statements have different values in overlapping recorded time. They may describe a change or unresolved disagreement; no truth was selected.",
                            "support": support,
                            "claim_ids": [left.id, right.id],
                        }
                    )
        return ReflectionContent(findings=findings[:8]).model_dump(mode="json")

    def _question(self, run, settings):
        with self.sessions() as db:
            policy = db.get(CuriosityPolicy, run.owner_id)
            if policy is None or policy.revision != run.question_revision:
                raise ServiceError(409, "reflection_question_consent_changed")
            used = set(
                db.scalars(
                    select(CuriosityQuestion.template_key).where(
                        CuriosityQuestion.owner_id == run.owner_id
                    )
                )
            ) | set(policy.suppressed)
            used |= set(
                db.scalars(
                    select(ReflectionArtifact.question_template).where(
                        ReflectionArtifact.owner_id == run.owner_id,
                        ReflectionArtifact.kind == "question",
                    )
                )
            )
            original = next(
                (
                    pin
                    for pin, s in zip(run.pins, run.snapshot)
                    if s["trust_class"] == "user_explicit"
                ),
                None,
            )
            source = (
                self.curiosity._pin(
                    db,
                    run.owner_id,
                    run.scope_id,
                    {k: original[k] for k in ("source_version_id", "span_start", "span_end")},
                )
                if original
                else None
            )
            choices = (
                [
                    (
                        settings.question_topic + ".source",
                        "Would you like to revisit this original statement and tell me what has changed?",
                    )
                ]
                if source
                else [
                    (settings.question_topic + "." + str(i), value)
                    for i, value in enumerate(CATALOG.get(settings.question_topic, ()))
                ]
            )
            choice = next(((key, text) for key, text in choices if key not in used), None)
            if choice is None:
                return None
            key, text = choice
            return ReflectionContent(
                question={
                    "topic": settings.question_topic,
                    "template_key": key,
                    "text": text,
                    "source": source,
                }
            ).model_dump(mode="json")

    def _watch(self, active, run, settings, done):
        while not done.wait(0.1):
            reason = active["reason"]
            if reason is None and time.monotonic() - active["started"] >= settings.unit_seconds:
                reason = "unit_deadline"
            if reason is None:
                try:
                    measured = self._measure()
                    with self.sessions.begin() as db:
                        policy = self._row(db, run.owner_id, payload=False)
                        reason, current = self._authority(db, run.owner_id, policy)
                        reason = (
                            reason
                            or self._run_authority(db, policy, run, current)
                            or self._room(current, measured)
                        )
                except Exception:
                    reason = "authority_unavailable"
            if reason:
                active["reason"] = reason
                active["cancel"].set()
                if active.get("cancel_at") is None:
                    active["cancel_at"] = time.monotonic()
            if (
                run.kind == "summary"
                and active.get("cancel_at") is not None
                and time.monotonic() - active["cancel_at"] > self.cancel_budget_seconds
            ):
                try:
                    with self.sessions.begin() as db:
                        db.merge(
                            ReflectionProviderState(
                                id=run.provider_key,
                                ready=False,
                                reason="provider_cancel_ignored",
                                observed_at=self.clock(),
                            )
                        )
                finally:
                    active["reason"] = "provider_cancel_ignored"
                return

    def _finish(self, reserved, content, reason, elapsed, model_elapsed):
        measured = self._measure() if reason is None else {}
        with self.sessions.begin() as db:
            self.scheduler._owner(db, reserved.owner_id)
            run = db.scalar(
                select(ReflectionRun)
                .options(
                    defer(ReflectionRun.snapshot, raiseload=True),
                    defer(ReflectionRun.pins, raiseload=True),
                )
                .where(ReflectionRun.owner_id == reserved.owner_id, ReflectionRun.id == reserved.id)
                .with_for_update()
            )
            if (
                run is None
                or run.status != "running"
                or run.attempt != reserved.attempt
                or run.lease_token != reserved.lease_token
                or run.lease_until <= self.clock()
            ):
                return False
            row = self._row(db, run.owner_id, payload=False)
            invalid, settings = self._authority(db, run.owner_id, row)
            invalid = invalid or self._run_authority(db, row, run, settings)
            if invalid:
                self._terminal(run, "suppressed", invalid, self.clock())
                return False
            run.elapsed_ms, run.model_elapsed_ms = elapsed, model_elapsed
            if reason:
                if (
                    reason in ("foreground_arrival", "foreground_active", "server_stopping")
                    and run.attempt < 3
                ):
                    run.status, run.reason = "queued", reason
                    run.lease_until = run.lease_token = None
                else:
                    self._terminal(run, "failed", reason, self.clock())
                return False
            invalid = self._room(settings, measured)
            if invalid:
                self._terminal(run, "suppressed", invalid, self.clock())
                return False
            try:
                db.refresh(run, attribute_names=["pins"])
                self._pin_metadata(db, run.owner_id, run.scope_id, run.pins)
                db.refresh(run, attribute_names=["snapshot"])
                self._fresh(db, run)
            except ServiceError:
                self._terminal(run, "suppressed", "source_changed", self.clock())
                return False
            if content is None:
                self._terminal(run, "completed", "no_useful_findings", self.clock())
                return True
            checked = ReflectionContent.model_validate(content).model_dump(mode="json")
            template = checked["question"]["template_key"] if run.kind == "question" else None
            if template and db.scalar(
                select(ReflectionArtifact.id)
                .where(
                    ReflectionArtifact.owner_id == run.owner_id,
                    ReflectionArtifact.question_template == template,
                )
                .limit(1)
            ):
                self._terminal(run, "completed", "no_useful_findings", self.clock())
                return True
            key = stable_id(run.owner_id, run.id, "artifact")
            db.add(
                ReflectionArtifact(
                    owner_id=run.owner_id,
                    id=key,
                    scope_id=run.scope_id,
                    run_id=run.id,
                    epoch=run.epoch,
                    kind=run.kind,
                    status="pending",
                    rationale="no_useful_findings"
                    if checked.get("findings") == []
                    else "owner_marked_material"
                    if run.kind == "report"
                    else "optional_question_draft"
                    if run.kind == "question"
                    else "generated_summary_draft",
                    content=checked,
                    question_template=template,
                    sources=run.snapshot,
                    omissions=run.omissions,
                    created_at=self.clock(),
                    elapsed_ms=elapsed,
                    model_elapsed_ms=model_elapsed,
                )
            )
            run.artifact_id = key
            self._terminal(run, "completed", None, self.clock())
            return True

    def run_once(self):
        if self._stop.is_set() or not self.globally_enabled():
            return False
        measured = self._measure()
        with self._lock:
            if self._active is not None:
                return False
            active = {"cancel": threading.Event(), "reason": None, "started": time.monotonic()}
            self._active = active
        acquired = False
        try:
            acquired = self.chat.capacity.acquire(blocking=False)
            if not acquired:
                return False
            claimed = self.claim(measured)
            if claimed is None:
                return False
            run, settings = claimed
            done = threading.Event()
            watcher = threading.Thread(
                target=self._watch,
                args=(active, run, settings, done),
                name="ada-idle-unit-watch",
                daemon=True,
            )
            watcher.start()
            content, reason, model_elapsed = None, None, None
            try:
                if active["cancel"].is_set():
                    reason = active["reason"] or "foreground_arrival"
                elif run.kind == "report":
                    content = self._report(run)
                elif run.kind == "question":
                    content = self._question(run, settings)
                else:
                    generated_at = time.monotonic()
                    content = self.provider.generate(
                        run, self.consolidation, active["cancel"], settings.unit_seconds
                    )
                    model_elapsed = int((time.monotonic() - generated_at) * 1000)
            except ProviderError as error:
                reason = "generation_unavailable_or_invalid"
                if error.code == "reflection_model_changed":
                    with self.sessions.begin() as db:
                        db.merge(
                            ReflectionProviderState(
                                id=run.provider_key,
                                ready=False,
                                reason="model_digest_changed",
                                observed_at=self.clock(),
                            )
                        )
                    reason = "model_digest_changed"
            except Exception:
                reason = "generation_unavailable_or_invalid"
            finally:
                done.set()
                watcher.join(timeout=self.cancel_budget_seconds + 1)
            reason = active["reason"] or reason
            self._finish(
                run,
                content,
                reason,
                int((time.monotonic() - active["started"]) * 1000),
                model_elapsed,
            )
            return True
        finally:
            if acquired:
                self.chat.capacity.release()
            with self._lock:
                self._active = None

    def _artifact(self, db, owner, key, *, lock=False):
        query = (
            select(ReflectionArtifact)
            .options(
                defer(ReflectionArtifact.content, raiseload=True),
                defer(ReflectionArtifact.sources, raiseload=True),
            )
            .where(ReflectionArtifact.owner_id == owner, ReflectionArtifact.id == key)
        )
        row = db.scalar(query.with_for_update() if lock else query)
        if row is None:
            raise ServiceError(404, "reflection_artifact_not_found")
        owned_scope(db, owner, row.scope_id, lock=lock)
        return row

    def _artifact_output(self, db, row):
        unavailable = None
        run = db.scalar(
            select(ReflectionRun)
            .options(
                defer(ReflectionRun.snapshot, raiseload=True),
                defer(ReflectionRun.pins, raiseload=True),
            )
            .where(ReflectionRun.owner_id == row.owner_id, ReflectionRun.id == row.run_id)
        )
        user = db.get(User, row.owner_id)
        if user.data_epoch != row.epoch:
            unavailable = "epoch_changed"
        elif row.status != "dismissed":
            try:
                db.refresh(run, attribute_names=["pins"])
                self._pin_metadata(db, row.owner_id, row.scope_id, run.pins)
                db.refresh(run, attribute_names=["snapshot"])
                self._fresh(db, run, lock=False)
            except ServiceError:
                unavailable = "source_changed"
        if not unavailable and row.status != "dismissed":
            db.refresh(row, attribute_names=["content", "sources"])
        return {
            "id": row.id,
            "scope_id": row.scope_id,
            "run_id": row.run_id,
            "kind": row.kind,
            "state": row.status,
            "provenance": "model_generated" if row.kind == "summary" else "rule_generated",
            "rationale": row.rationale,
            "content": row.content if not unavailable and row.status != "dismissed" else None,
            "sources": row.sources if not unavailable and row.status != "dismissed" else [],
            "omissions": row.omissions,
            "created_at": row.created_at,
            "elapsed_ms": row.elapsed_ms,
            "model_elapsed_ms": row.model_elapsed_ms,
            "episode_id": row.episode_id,
            "question_id": row.question_id,
            "conversation_id": row.conversation_id,
            "unavailable_reason": unavailable,
        }

    def artifacts(self, owner, limit=100, offset=0):
        with self.sessions() as db:
            rows = db.scalars(
                select(ReflectionArtifact)
                .options(
                    defer(ReflectionArtifact.content, raiseload=True),
                    defer(ReflectionArtifact.sources, raiseload=True),
                )
                .where(ReflectionArtifact.owner_id == owner)
                .order_by(ReflectionArtifact.created_at.desc(), ReflectionArtifact.id)
                .limit(limit)
                .offset(offset)
            ).all()
            return [self._artifact_output(db, row) for row in rows]

    def artifact(self, owner, key):
        with self.sessions() as db:
            return self._artifact_output(db, self._artifact(db, owner, key))

    def runs(self, owner, limit=100, offset=0):
        with self.sessions() as db:
            rows = (
                db.execute(
                    select(
                        ReflectionRun.id,
                        ReflectionRun.scope_id,
                        ReflectionRun.kind,
                        ReflectionRun.status.label("state"),
                        ReflectionRun.attempt,
                        ReflectionRun.reason,
                        ReflectionRun.artifact_id,
                        ReflectionRun.created_at,
                        ReflectionRun.finished_at,
                        ReflectionRun.elapsed_ms,
                        ReflectionRun.charged_ms,
                    )
                    .where(ReflectionRun.owner_id == owner)
                    .order_by(ReflectionRun.created_at.desc(), ReflectionRun.id)
                    .limit(limit)
                    .offset(offset)
                )
                .mappings()
                .all()
            )
            return [dict(row) for row in rows]

    def action(self, owner, key, body, principal):
        payload = {"artifact_id": key, **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner, principal)
            previous = self._old(db, owner, body.operation_id, payload)
            if previous:
                return previous
            row = self._artifact(db, owner, key, lock=True)
            if row.status == "dismissed" and body.action != "dismiss":
                raise ServiceError(409, "reflection_artifact_dismissed")
            result = {"artifact_id": key}
            if body.action == "dismiss":
                row.status, row.content, row.sources = "dismissed", None, []
            else:
                if row.epoch != db.get(User, owner).data_epoch:
                    raise ServiceError(409, "reflection_epoch_changed")
                run = db.get(ReflectionRun, (owner, row.run_id))
                self._fresh(db, run)
                db.refresh(row, attribute_names=["content", "sources"])
                if body.action == "open_question":
                    if (
                        row.kind != "question"
                        or body.conversation_id is None
                        or body.personality_id is None
                    ):
                        raise ServiceError(422, "reflection_question_open_input_required")
                    policy = db.get(CuriosityPolicy, owner)
                    question = row.content["question"]
                    if not policy or not self.curiosity._allowed(
                        policy.settings, question["topic"]
                    ):
                        raise ServiceError(409, "reflection_question_consent_changed")
                    if row.question_id is None:
                        pin = question.get("source")
                        source = (
                            CuriosityPinInput(
                                **{
                                    k: pin[k]
                                    for k in ("source_version_id", "span_start", "span_end")
                                }
                            )
                            if pin
                            else None
                        )
                        created = self.curiosity.create_in(
                            db,
                            owner,
                            row.scope_id,
                            CuriosityCreate(
                                operation_id=stable_id(owner, body.operation_id, "offer"),
                                policy_revision=policy.revision,
                                channel="inbox",
                                topic=question["topic"],
                                source=source,
                            ),
                        )
                        if created["state"] != "created":
                            raise ServiceError(409, "reflection_question_no_longer_available")
                        offered = db.get(CuriosityQuestion, (owner, created["question_id"]))
                        if (
                            offered.template_key != question["template_key"]
                            or not offered.payload
                            or offered.payload["text"] != question["text"]
                        ):
                            raise ServiceError(409, "reflection_question_draft_changed")
                        row.question_id = created["question_id"]
                    opened = self.curiosity.open_in(
                        db,
                        owner,
                        row.question_id,
                        CuriosityOpen(
                            operation_id=stable_id(owner, body.operation_id, "open"),
                            conversation_id=body.conversation_id,
                            personality_id=body.personality_id,
                        ),
                    )
                    row.conversation_id = opened["conversation_id"]
                    result.update(question_id=row.question_id, conversation_id=row.conversation_id)
                elif row.kind == "summary" and row.episode_id is None:
                    if self.provider is None or self.provider.key != run.provider_key:
                        raise ServiceError(409, "reflection_provider_context_changed")
                    row.episode_id = self.consolidation.keep_idle_summary(
                        db,
                        owner,
                        row.scope_id,
                        row.id,
                        row.content["summary"],
                        run.pins,
                        run.snapshot,
                    )
                    result["episode_id"] = row.episode_id
                row.status = "kept"
                if row.episode_id:
                    result["episode_id"] = row.episode_id
            return self._receipt(db, owner, body.operation_id, payload, body.action, **result)

    def metadata(self):
        with self.sessions() as db:
            suspended = bool(
                db.scalar(
                    select(ReflectionProviderState.id)
                    .where(ReflectionProviderState.ready.is_(False))
                    .limit(1)
                )
            )
            return {
                "globally_enabled": self.globally_enabled(),
                "summary_generation": self.summary_available(db),
                "suspended_model_class": suspended,
                "policies_enabled": db.scalar(
                    select(func.count())
                    .select_from(ReflectionPolicy)
                    .where(ReflectionPolicy.enabled.is_(True))
                ),
                "runs": dict(
                    db.execute(
                        select(ReflectionRun.status, func.count()).group_by(ReflectionRun.status)
                    ).all()
                ),
                "artifacts": dict(
                    db.execute(
                        select(ReflectionArtifact.status, func.count()).group_by(
                            ReflectionArtifact.status
                        )
                    ).all()
                ),
                "updated_at": self.clock(),
            }
