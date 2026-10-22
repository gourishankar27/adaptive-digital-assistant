"""Single-process dispatcher; short owner-locked transactions, no inference or push.

UTC plans are finite and previewed. A committed lease is not delivery authority:
publication rechecks consent, generation, device, scope, source and data epoch.
"""

import threading
from uuid import NAMESPACE_URL, uuid4, uuid5

from sqlalchemy import exists, func, inspect, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import defer

from ada.curiosity_contracts import CuriosityCreate, CuriosityOpen
from ada.curiosity_models import CuriosityPolicy
from ada.errors import ServiceError
from ada.login_models import LoginSession
from ada.memory import owned_scope
from ada.models import Conversation, Personality, User, now_ms
from ada.personality import PROMPT_VERSION, build_prompt
from ada.proposals import fingerprint
from ada.schedule_contracts import VERSION, ScheduleDefinition
from ada.schedule_models import (
    Schedule,
    ScheduleConsent,
    ScheduleInboxItem,
    ScheduleOccurrence,
    ScheduleReceipt,
)
from ada.schedule_time import DAY, TIMEZONE_DATA, allowed, resolve_plan
from ada.security_models import DeviceCredential

LEASE_MS = 30000
MAX_RECEIPTS = 5000
MAX_SCHEDULES = 100
MAX_OCCURRENCES = 1000
MAX_INBOX = 1000


def scrub_question_inbox(db, owner, question, *, detach=False):
    from sqlalchemy import update

    if inspect(db.connection()).has_table("schedule_inbox"):
        values = {"text": ""}
        if detach:
            values["question_id"] = None
        db.execute(
            update(ScheduleInboxItem)
            .where(ScheduleInboxItem.owner_id == owner, ScheduleInboxItem.question_id == question)
            .values(**values)
        )


def stable_id(*parts):
    return str(uuid5(NAMESPACE_URL, VERSION + "/" + "/".join(map(str, parts))))


def pause_automation(db, owner, reason):
    """Called within credential revocation's owner lock, including old-schema tools."""
    if not inspect(db.connection()).has_table("schedule_consents"):
        return
    from ada.reflection import pause_reflection

    pause_reflection(db, owner, reason)
    consent = db.get(ScheduleConsent, owner)
    if consent:
        consent.enabled = False
        consent.revision += 1
        consent.updated_at = now_ms()
    for row in db.scalars(
        select(Schedule).where(Schedule.owner_id == owner, Schedule.status == "active")
    ):
        row.generation += 1
        row.status, row.reason, row.updated_at = "paused", reason, now_ms()
    for row in db.scalars(
        select(ScheduleOccurrence).where(
            ScheduleOccurrence.owner_id == owner,
            ScheduleOccurrence.status.in_(["queued", "running"]),
        )
    ):
        row.status, row.reason = "suppressed", reason
        row.lease_until = row.lease_token = None


def pause_origin(db, owner, kind, identifier, reason):
    if not inspect(db.connection()).has_table("schedules"):
        return
    from ada.reflection import pause_reflection

    pause_reflection(db, owner, reason, kind, identifier)
    for row in db.scalars(
        select(Schedule).where(
            Schedule.owner_id == owner,
            Schedule.origin_kind == kind,
            Schedule.origin_id == identifier,
            Schedule.status == "active",
        )
    ):
        row.generation += 1
        row.status, row.reason, row.updated_at = "paused", reason, now_ms()
        for occurrence in db.scalars(
            select(ScheduleOccurrence).where(
                ScheduleOccurrence.owner_id == owner,
                ScheduleOccurrence.schedule_id == row.id,
                ScheduleOccurrence.status.in_(["queued", "running"]),
            )
        ):
            occurrence.status, occurrence.reason = "suppressed", reason
            occurrence.lease_until = occurrence.lease_token = None


def pause_question_schedules(db, owner):
    if not inspect(db.connection()).has_table("schedules"):
        return
    for row in db.scalars(
        select(Schedule).where(Schedule.owner_id == owner, Schedule.status == "active")
    ):
        if row.definition and row.definition["kind"] == "curiosity_question":
            row.generation += 1
            row.status, row.reason, row.updated_at = "paused", "curiosity_consent_changed", now_ms()
            for occurrence in db.scalars(
                select(ScheduleOccurrence).where(
                    ScheduleOccurrence.owner_id == owner,
                    ScheduleOccurrence.schedule_id == row.id,
                    ScheduleOccurrence.status.in_(["queued", "running"]),
                )
            ):
                occurrence.status, occurrence.reason = "suppressed", "curiosity_consent_changed"
                occurrence.lease_until = occurrence.lease_token = None


class SchedulingService:
    def __init__(self, sessions, settings, curiosity, clock=now_ms):
        self.sessions, self.settings, self.curiosity, self.clock = (
            sessions,
            settings,
            curiosity,
            clock,
        )
        self.discretionary_allowed = lambda: True
        self.idle_dispatch = lambda: False
        self._stop, self._thread = threading.Event(), None
        self.process_error_count, self.last_error_code = 0, None

    def _owner(self, db, owner, principal=None):
        if db.bind.dialect.name == "postgresql":
            db.execute(text("SET LOCAL lock_timeout = '2s'"))
            db.execute(text("SET LOCAL statement_timeout = '5s'"))
        user = self.curiosity._owner(db, owner)
        if principal is None:
            return user
        valid = principal.owner == owner and principal.epoch == user.data_epoch
        instant = (
            now_ms()
        )  # Authentication uses real time, independently of the calendar test clock.
        if principal.credential_id:
            device = db.get(DeviceCredential, principal.credential_id)
            valid = (
                valid
                and device is not None
                and device.owner_id == owner
                and device.revoked_at is None
                and device.expires_at > instant
                and device.token_hash == principal.digest
            )
        elif principal.session_id:
            session = db.get(LoginSession, principal.session_id)
            valid = (
                valid
                and session is not None
                and session.owner_id == owner
                and session.revoked_at is None
                and session.access_expires_at > instant
                and session.expires_at > instant
                and session.idle_expires_at > instant
                and session.access_hash == principal.digest
            )
        else:
            valid = valid and user.token_hash == principal.digest
        if not valid:
            raise ServiceError(401, "invalid_token")
        return user

    def _old(self, db, owner, operation, payload):
        old = db.get(ScheduleReceipt, (owner, str(operation)))
        if old and old.input_hash != fingerprint({"domain": VERSION, "input": payload}):
            raise ServiceError(409, "schedule_operation_reused")
        return old

    def _receipt(self, db, owner, operation, payload, action, *, allow_off=False, **fields):
        count = db.scalar(
            select(func.count())
            .select_from(ScheduleReceipt)
            .where(ScheduleReceipt.owner_id == owner)
        )
        if count >= MAX_RECEIPTS - (0 if allow_off else 1):
            raise ServiceError(413, "schedule_receipt_limit")
        row = ScheduleReceipt(
            owner_id=owner,
            id=str(operation),
            input_hash=fingerprint({"domain": VERSION, "input": payload}),
            created_at=self.clock(),
            result={
                "version": VERSION,
                "operation_id": str(operation),
                "action": action,
                "state": "completed",
                "created_at": self.clock(),
                **fields,
            },
        )
        db.add(row)
        db.flush()
        return row.result

    def policy(self, owner):
        with self.sessions() as db:
            row = db.get(ScheduleConsent, owner)
            return {
                "revision": row.revision if row else 0,
                "enabled": row.enabled if row else False,
                "globally_enabled": self.settings.scheduler_enabled,
            }

    def write_policy(self, owner, body, principal=None):
        payload = {"action": "policy", **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old.result
            row = db.get(ScheduleConsent, owner)
            if body.expected_revision != (row.revision if row else 0):
                raise ServiceError(409, "schedule_consent_changed")
            if row is None:
                row = ScheduleConsent(
                    owner_id=owner, revision=1, enabled=body.enabled, updated_at=self.clock()
                )
                db.add(row)
            else:
                row.revision += 1
                row.enabled, row.updated_at = body.enabled, self.clock()
            # Re-enabling consent never silently resumes old schedules.
            from ada.reflection import pause_reflection

            pause_reflection(db, owner, "automation_consent_changed")
            for schedule in db.scalars(
                select(Schedule).where(Schedule.owner_id == owner, Schedule.status == "active")
            ):
                self._pause(db, schedule, "consent_changed")
            return self._receipt(
                db,
                owner,
                body.operation_id,
                payload,
                "policy",
                allow_off=not body.enabled,
                consent_revision=row.revision,
            )

    def _validate(self, db, owner, scope, definition, *, preview=False):
        owned_scope(db, owner, scope, lock=True)
        try:
            plan = resolve_plan(definition)
        except ValueError:
            raise ServiceError(422, "schedule_calendar_invalid") from None
        expires = int(definition.expires_at.timestamp() * 1000)
        if preview and (plan[0]["at"] < self.clock() or expires > self.clock() + 366 * DAY):
            raise ServiceError(422, "schedule_window_invalid")
        if definition.kind == "curiosity_question":
            policy = db.get(CuriosityPolicy, owner)
            if (
                not policy
                or not policy.settings["enabled"]
                or not policy.settings["inbox_enabled"]
                or not self.curiosity._allowed(policy.settings, definition.topic)
            ):
                raise ServiceError(409, "schedule_question_consent_changed")
            source = (
                self.curiosity._pin(db, owner, scope, definition.source.model_dump(mode="json"))
                if definition.source
                else None
            )
            return plan, policy.revision, source
        return plan, None, None

    def preview(self, owner, scope, body, principal=None):
        payload = {"scope_id": scope, **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old.result
            plan, question_revision, source = self._validate(
                db, owner, scope, body.definition, preview=True
            )
            return self._receipt(
                db,
                owner,
                body.operation_id,
                payload,
                "preview",
                definition=body.definition.model_dump(mode="json"),
                source=source,
                _question_policy_revision=question_revision,
                occurrences=plan,
                timezone_data=TIMEZONE_DATA,
                preview_expires_at=self.clock() + 15 * 60000,
                _scope_id=scope,
            )

    @staticmethod
    def _origin(principal):
        if principal.credential_id:
            return "device", principal.credential_id
        if principal.session_id:
            return "password", principal.session_id
        return "legacy", principal.owner

    def _schedule(self, db, owner, key, *, lock=True, payload=True):
        options = (
            []
            if payload
            else [
                defer(column, raiseload=True)
                for column in (Schedule.definition, Schedule.plan, Schedule.source_snapshot)
            ]
        )
        row = db.get(Schedule, (owner, key), with_for_update=lock, options=options)
        if row is None:
            raise ServiceError(404, "schedule_not_found")
        owned_scope(db, owner, row.scope_id, lock=lock)
        return row

    def confirm(self, owner, key, body, principal):
        with self.sessions.begin() as db:
            return self.confirm_in(db, owner, key, body, principal)

    def confirm_in(self, db, owner, key, body, principal, *, work_binding=False):
        payload = {"schedule_id": key, **body.model_dump(mode="json")}
        user = self._owner(db, owner, principal)
        old = self._old(db, owner, body.operation_id, payload)
        if old:
            return old.result
        consent = db.get(ScheduleConsent, owner)
        if not consent or not consent.enabled or consent.revision != body.consent_revision:
            raise ServiceError(409, "schedule_consent_changed")
        preview = db.get(ScheduleReceipt, (owner, str(body.preview_id)))
        if not preview or preview.result["action"] != "preview":
            raise ServiceError(404, "schedule_preview_not_found")
        intent = preview.result
        from ada.work import validate_task_preview

        validate_task_preview(db, owner, intent)
        if intent.get("_work_item_id") and not work_binding:
            raise ServiceError(409, "work_reminder_confirmation_required")
        if intent["preview_expires_at"] <= self.clock() or intent["timezone_data"] != TIMEZONE_DATA:
            raise ServiceError(409, "schedule_preview_expired")
        definition = ScheduleDefinition(**intent["definition"])
        plan, question_revision, source = self._validate(
            db, owner, intent["_scope_id"], definition, preview=True
        )
        if plan != intent["occurrences"]:
            raise ServiceError(409, "schedule_preview_changed")
        if source != intent.get("source"):
            raise ServiceError(409, "schedule_source_changed")
        if question_revision != intent.get("_question_policy_revision"):
            raise ServiceError(409, "schedule_question_consent_changed")
        row = db.get(Schedule, (owner, key), with_for_update=True)
        from ada.work_models import WorkItem

        if not work_binding and db.scalar(
            select(WorkItem.id).where(WorkItem.owner_id == owner, WorkItem.schedule_id == key)
        ):
            raise ServiceError(409, "work_reminder_confirmation_required")
        if (row.generation if row else 0) != body.expected_generation:
            raise ServiceError(409, "schedule_generation_changed")
        if row and (row.scope_id != intent["_scope_id"] or row.status == "deleted"):
            raise ServiceError(409, "schedule_scope_or_state_changed")
        if row is None:
            if (
                db.scalar(
                    select(func.count()).select_from(Schedule).where(Schedule.owner_id == owner)
                )
                >= MAX_SCHEDULES
            ):
                raise ServiceError(413, "schedule_retained_limit")
            row = Schedule(
                owner_id=owner,
                id=key,
                scope_id=intent["_scope_id"],
                generation=1,
                delivered=0,
                missed=0,
                created_at=self.clock(),
            )
            db.add(row)
        else:
            self._pause(db, row, "schedule_edited")
        row.definition, row.plan, row.timezone_data = intent["definition"], plan, TIMEZONE_DATA
        row.plan_generation = row.generation
        row.cursor, row.next_at, row.snoozed_until = 0, plan[0]["at"], None
        row.expires_at = int(definition.expires_at.timestamp() * 1000)
        row.status, row.reason, row.updated_at = "active", None, self.clock()
        row.consent_revision, row.epoch = consent.revision, user.data_epoch
        row.question_policy_revision = question_revision
        row.source_snapshot = source
        row.source_version_id = (
            str(definition.source.source_version_id) if definition.source else None
        )
        row.origin_kind, row.origin_id = self._origin(principal)
        return self._receipt(
            db,
            owner,
            body.operation_id,
            payload,
            "confirm",
            schedule_id=key,
            generation=row.generation,
        )

    def _pause(self, db, row, reason):
        row.generation += 1
        row.status, row.reason, row.updated_at = "paused", reason, self.clock()
        for occurrence in db.scalars(
            select(ScheduleOccurrence).where(
                ScheduleOccurrence.owner_id == row.owner_id,
                ScheduleOccurrence.schedule_id == row.id,
                ScheduleOccurrence.status.in_(["queued", "running"]),
            )
        ):
            occurrence.status, occurrence.reason = "suppressed", reason
            occurrence.lease_until = occurrence.lease_token = None

    def action(self, owner, key, body, principal):
        payload = {"schedule_id": key, **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            user = self._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old.result
            row = self._schedule(db, owner, key)
            if row.generation != body.expected_generation or row.status == "deleted":
                raise ServiceError(409, "schedule_generation_changed")
            if body.action in ("snooze", "reauthorize"):
                from ada.work_models import WorkItem

                task = db.scalar(
                    select(WorkItem).where(WorkItem.owner_id == owner, WorkItem.schedule_id == key)
                )
                if task and (
                    task.status != "planned"
                    or task.fields["description"] != row.definition.get("text")
                ):
                    raise ServiceError(409, "work_reminder_task_changed")
            if body.action == "snooze":
                until = self._until(body.until)
                self._pause(db, row, "snoozed")
                row.status, row.snoozed_until = "active", until
                self._rewind_unpublished(db, row)
                self._finish(db, row)
            elif body.action == "reauthorize":
                if row.expires_at <= self.clock():
                    raise ServiceError(409, "schedule_new_preview_required")
                consent = db.get(ScheduleConsent, owner)
                if not consent or not consent.enabled:
                    raise ServiceError(409, "schedule_consent_changed")
                _, _, source = self._validate(
                    db, owner, row.scope_id, ScheduleDefinition(**row.definition)
                )
                if source != row.source_snapshot or row.timezone_data != TIMEZONE_DATA:
                    raise ServiceError(409, "schedule_new_preview_required")
                self._pause(db, row, "reauthorized")
                row.status, row.reason, row.epoch = "active", None, user.data_epoch
                row.origin_kind, row.origin_id = self._origin(principal)
                row.consent_revision = consent.revision
                question_policy = db.get(CuriosityPolicy, owner)
                row.question_policy_revision = question_policy.revision if question_policy else None
                self._rewind_unpublished(db, row)
                self._finish(db, row)
            else:
                self._pause(db, row, "owner_" + body.action)
                if body.action == "delete":
                    row.source_snapshot = None
                    row.status, row.definition, row.plan, row.next_at, row.source_version_id = (
                        "deleted",
                        None,
                        [],
                        None,
                        None,
                    )
            return self._receipt(
                db,
                owner,
                body.operation_id,
                payload,
                "action",
                schedule_id=key,
                generation=row.generation,
            )

    def _until(self, value):
        if value is None:
            raise ServiceError(422, "schedule_snooze_time_required")
        instant = int(value.timestamp() * 1000)
        if not self.clock() < instant <= self.clock() + 7 * DAY:
            raise ServiceError(422, "schedule_snooze_window_invalid")
        return instant

    @staticmethod
    def _rewind_unpublished(db, row):
        last = db.scalar(
            select(func.max(ScheduleOccurrence.scheduled_for)).where(
                ScheduleOccurrence.owner_id == row.owner_id,
                ScheduleOccurrence.schedule_id == row.id,
                ScheduleOccurrence.generation >= row.plan_generation,
                ScheduleOccurrence.status == "delivered",
            )
        )
        row.cursor = next(
            (i for i, value in enumerate(row.plan) if last is None or value["at"] > last),
            len(row.plan),
        )
        row.next_at = row.plan[row.cursor]["at"] if row.cursor < len(row.plan) else None

    def receipt(self, owner, key):
        with self.sessions() as db:
            row = db.get(ScheduleReceipt, (owner, key))
            if row is None:
                raise ServiceError(404, "schedule_receipt_not_found")
            return row.result

    def _authority(self, db, user, row):
        consent = db.get(ScheduleConsent, row.owner_id)
        if user.deletion_job_id or row.epoch != user.data_epoch:
            return "schedule_epoch_changed"
        if not consent or not consent.enabled or consent.revision != row.consent_revision:
            return "schedule_consent_changed"
        if row.timezone_data != TIMEZONE_DATA:
            return "schedule_timezone_rules_changed"
        if row.expires_at <= self.clock():
            return "expired"
        owned_scope(db, row.owner_id, row.scope_id, lock=True)
        if row.origin_kind == "device":
            device = db.get(DeviceCredential, row.origin_id)
            if (
                not device
                or device.owner_id != row.owner_id
                or device.revoked_at is not None
                or device.expires_at <= self.clock()
            ):
                return "schedule_device_revoked"
        if row.question_policy_revision is not None:
            revision = db.scalar(
                select(CuriosityPolicy.revision).where(CuriosityPolicy.owner_id == row.owner_id)
            )
            if revision != row.question_policy_revision:
                return "schedule_question_consent_changed"
        # Payload columns raise on accidental lazy access before these metadata fences.
        db.refresh(row, attribute_names=["definition", "plan", "source_snapshot"])
        definition = ScheduleDefinition(**row.definition)
        if int(definition.expires_at.timestamp() * 1000) != row.expires_at:
            return "schedule_definition_changed"
        try:
            _, _, source = self._validate(db, row.owner_id, row.scope_id, definition)
            if source != row.source_snapshot:
                return "schedule_source_changed"
        except ServiceError as error:
            return error.code
        return None

    @staticmethod
    def _output(row):
        return {
            "id": row.id,
            "scope_id": row.scope_id,
            "generation": row.generation,
            "state": row.status,
            "reason": row.reason,
            "definition": row.definition,
            "next_at": row.next_at,
            "snoozed_until": row.snoozed_until,
            "delivered": row.delivered,
            "missed": row.missed,
            "consent_revision": row.consent_revision,
            "origin_kind": row.origin_kind,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def detail(self, owner, key):
        with self.sessions() as db:
            return self._output(self._schedule(db, owner, key, lock=False))

    def schedules(self, owner, scope):
        with self.sessions() as db:
            owned_scope(db, owner, scope)
            return [
                self._output(row)
                for row in db.scalars(
                    select(Schedule)
                    .where(Schedule.owner_id == owner, Schedule.scope_id == scope)
                    .order_by(Schedule.created_at.desc(), Schedule.id)
                    .limit(MAX_SCHEDULES)
                )
            ]

    def occurrences(self, owner, key, limit=100, offset=0):
        with self.sessions() as db:
            self._schedule(db, owner, key, lock=False)
            return [
                {
                    "id": row.id,
                    "schedule_id": row.schedule_id,
                    "generation": row.generation,
                    "scheduled_for": row.scheduled_for,
                    "state": row.status,
                    "reason": row.reason,
                    "attempt": row.attempt,
                    "lease_until": row.lease_until,
                    "item_id": row.item_id,
                }
                for row in db.scalars(
                    select(ScheduleOccurrence)
                    .where(
                        ScheduleOccurrence.owner_id == owner, ScheduleOccurrence.schedule_id == key
                    )
                    .order_by(ScheduleOccurrence.scheduled_for.desc(), ScheduleOccurrence.id)
                    .limit(limit)
                    .offset(offset)
                )
            ]

    def _item(self, db, owner, key, *, lock=True):
        row = db.get(ScheduleInboxItem, (owner, key), with_for_update=lock)
        if row is None:
            raise ServiceError(404, "schedule_inbox_not_found")
        user = db.get(User, owner)
        if row.epoch != user.data_epoch:
            raise ServiceError(410, "schedule_epoch_changed")
        owned_scope(db, owner, row.scope_id, lock=lock)
        return row

    def _inbox_output(self, db, row):
        state, text = row.status, row.text
        if row.available_at > self.clock():
            state, text = "snoozed", None
        if row.expires_at <= self.clock():
            state, text = "expired", None
        if row.kind == "curiosity_question":
            if row.question_id is None:
                state, text = "revoked", None
            else:
                question = self.curiosity._question(db, row.owner_id, row.question_id)
                question_state, payload = self.curiosity._visible(db, question)
                if payload is None:
                    state, text = question_state, None
        return {
            "id": row.id,
            "scope_id": row.scope_id,
            "schedule_id": row.schedule_id,
            "occurrence_id": row.occurrence_id,
            "kind": row.kind,
            "text": text,
            "question_id": row.question_id,
            "state": state,
            "available_at": row.available_at,
            "expires_at": row.expires_at,
            "acknowledged_at": row.acknowledged_at,
            "opened_conversation_id": row.opened_conversation_id,
            "created_at": row.created_at,
        }

    def inbox(self, owner, limit=100, offset=0):
        with self.sessions() as db:
            return [
                self._inbox_output(db, self._item(db, owner, row.id, lock=False))
                for row in db.scalars(
                    select(ScheduleInboxItem)
                    .where(ScheduleInboxItem.owner_id == owner)
                    .order_by(ScheduleInboxItem.created_at.desc(), ScheduleInboxItem.id)
                    .limit(limit)
                    .offset(offset)
                )
            ]

    def inbox_action(self, owner, key, body, principal=None):
        payload = {"item_id": key, **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old.result
            row = self._item(db, owner, key)
            if body.action == "snooze":
                row.available_at = self._until(body.until)
            elif body.action == "dismiss":
                row.status = "dismissed"
            else:
                row.acknowledged_at = row.acknowledged_at or self.clock()
                if row.status == "unread":
                    row.status = "acknowledged"
            return self._receipt(db, owner, body.operation_id, payload, "inbox_action", item_id=key)

    def open(self, owner, key, body, principal=None):
        payload = {"item_id": key, **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old.result
            row = self._item(db, owner, key)
            if self._inbox_output(db, row)["text"] is None or row.status == "dismissed":
                raise ServiceError(409, "schedule_inbox_unavailable")
            cid = str(body.conversation_id)
            if row.opened_conversation_id and row.opened_conversation_id != cid:
                raise ServiceError(409, "schedule_inbox_already_opened")
            if not row.opened_conversation_id:
                if row.kind == "curiosity_question":
                    self.curiosity.open_in(
                        db, owner, row.question_id, CuriosityOpen(**body.model_dump())
                    )
                else:
                    profile = db.scalar(
                        select(Personality).where(
                            Personality.owner_id == owner,
                            Personality.id == str(body.personality_id),
                        )
                    )
                    if profile is None:
                        raise ServiceError(404, "personality_not_found")
                    if db.get(Conversation, cid):
                        raise ServiceError(409, "schedule_conversation_id_used")
                    scope = owned_scope(db, owner, row.scope_id)
                    snapshot = {
                        k: getattr(profile, k) for k in ("name", "style", "warmth", "detail")
                    }
                    conv = Conversation(
                        id=cid,
                        owner_id=owner,
                        personality_id=profile.id,
                        scope_id=scope.id,
                        scope_kind=scope.kind,
                        title="Reminder",
                        personality_snapshot=snapshot,
                        system_prompt=build_prompt(snapshot),
                        prompt_version=PROMPT_VERSION,
                    )
                    db.add(conv)
                    db.flush()
                    self.curiosity.chat.expression.bind_new(db, conv)
                row.opened_conversation_id, row.status = cid, "opened"
                row.acknowledged_at = row.acknowledged_at or self.clock()
            return self._receipt(
                db, owner, body.operation_id, payload, "open", item_id=key, conversation_id=cid
            )

    def _pending(self, row, instant):
        return (row.status == "queued" and row.available_at <= instant) or (
            row.status == "running" and row.lease_until <= instant
        )

    def claim(self):
        if (
            self._stop.is_set()
            or not self.settings.scheduler_enabled
            or not self.discretionary_allowed()
        ):
            return None
        instant = self.clock()
        pending = exists().where(
            ScheduleOccurrence.owner_id == Schedule.owner_id,
            ScheduleOccurrence.schedule_id == Schedule.id,
            or_(
                (ScheduleOccurrence.status == "queued")
                & (ScheduleOccurrence.available_at <= instant),
                (ScheduleOccurrence.status == "running")
                & (ScheduleOccurrence.lease_until <= instant),
            ),
        )
        with self.sessions() as db:
            candidate = db.execute(
                select(Schedule.owner_id, Schedule.id)
                .where(
                    Schedule.status == "active",
                    or_(Schedule.next_at <= instant, pending),
                    or_(Schedule.snoozed_until.is_(None), Schedule.snoozed_until <= instant),
                )
                .order_by(Schedule.updated_at, Schedule.id)
                .limit(1)
            ).first()
        if candidate is None:
            return None
        owner, key = candidate
        with self.sessions.begin() as db:
            user = self._owner(db, owner)
            row = self._schedule(db, owner, key, payload=False)
            if row.status != "active" or (row.snoozed_until and row.snoozed_until > instant):
                return None
            reason = self._authority(db, user, row)
            if reason:
                self._pause(db, row, reason)
                if reason == "expired":
                    row.status, row.next_at = "completed", None
                return {"terminal": True}
            definition = ScheduleDefinition(**row.definition)
            if int(definition.expires_at.timestamp() * 1000) <= instant:
                self._pause(db, row, "expired")
                row.status = "completed"
                return {"terminal": True}
            due = [p for p in row.plan[row.cursor :] if p["at"] <= instant]
            if due:
                count = db.scalar(
                    select(func.count())
                    .select_from(ScheduleOccurrence)
                    .where(ScheduleOccurrence.owner_id == owner)
                )
                if count + len(due) > MAX_OCCURRENCES:
                    self._pause(db, row, "occurrence_retained_limit")
                    return {"terminal": True}
                for older in db.scalars(
                    select(ScheduleOccurrence).where(
                        ScheduleOccurrence.owner_id == owner,
                        ScheduleOccurrence.schedule_id == key,
                        ScheduleOccurrence.status.in_(["queued", "running"]),
                    )
                ):
                    older.status, older.reason = "suppressed", "missed_latest_only"
                    older.lease_until = older.lease_token = None
                    row.missed += 1
                for index, plan in enumerate(due):
                    skipped = index < len(due) - 1
                    db.add(
                        ScheduleOccurrence(
                            owner_id=owner,
                            id=stable_id(owner, key, row.generation, plan["at"]),
                            schedule_id=key,
                            generation=row.generation,
                            scheduled_for=plan["at"],
                            status="suppressed" if skipped else "queued",
                            reason="missed_latest_only" if skipped else None,
                            attempt=0,
                            available_at=instant,
                        )
                    )
                    row.missed += int(skipped)
                row.cursor += len(due)
                row.next_at = row.plan[row.cursor]["at"] if row.cursor < len(row.plan) else None
                db.flush()
            occurrence = db.scalar(
                select(ScheduleOccurrence)
                .where(
                    ScheduleOccurrence.owner_id == owner,
                    ScheduleOccurrence.schedule_id == key,
                    ScheduleOccurrence.generation == row.generation,
                    or_(
                        (ScheduleOccurrence.status == "queued")
                        & (ScheduleOccurrence.available_at <= instant),
                        (ScheduleOccurrence.status == "running")
                        & (ScheduleOccurrence.lease_until <= instant),
                    ),
                )
                .order_by(ScheduleOccurrence.scheduled_for.desc())
                .limit(1)
                .with_for_update()
            )
            if occurrence is None:
                return None
            if not allowed(definition, instant):
                occurrence.status, occurrence.reason, occurrence.available_at = (
                    "queued",
                    "quiet_hours",
                    instant + 60000,
                )
                occurrence.lease_until = occurrence.lease_token = None
                return {"terminal": True}
            if occurrence.attempt >= 3:
                occurrence.status, occurrence.reason = "failed", "attempt_limit"
                occurrence.lease_until = occurrence.lease_token = None
                self._finish(db, row)
                return {"terminal": True}
            occurrence.attempt += 1
            occurrence.status, occurrence.reason = "running", None
            occurrence.lease_until, occurrence.lease_token = instant + LEASE_MS, str(uuid4())
            row.updated_at = instant
            return {
                "owner": owner,
                "schedule": key,
                "id": occurrence.id,
                "attempt": occurrence.attempt,
                "token": occurrence.lease_token,
            }

    def _finish(self, db, row):
        db.flush()
        if row.cursor == len(row.plan) and not db.scalar(
            select(ScheduleOccurrence.id)
            .where(
                ScheduleOccurrence.owner_id == row.owner_id,
                ScheduleOccurrence.schedule_id == row.id,
                ScheduleOccurrence.status.in_(["queued", "running"]),
            )
            .limit(1)
        ):
            row.status, row.reason = "completed", "finite_plan_complete"

    def publish(self, claimed):
        if claimed.get("terminal"):
            return False
        with self.sessions.begin() as db:
            user = self._owner(db, claimed["owner"])
            row = self._schedule(db, user.id, claimed["schedule"], payload=False)
            occurrence = db.get(ScheduleOccurrence, (user.id, claimed["id"]), with_for_update=True)
            if (
                not occurrence
                or occurrence.status != "running"
                or occurrence.attempt != claimed["attempt"]
                or occurrence.lease_token != claimed["token"]
                or occurrence.lease_until <= self.clock()
            ):
                return False
            if row.status != "active" or occurrence.generation != row.generation:
                occurrence.status, occurrence.reason = "suppressed", "generation_changed"
                occurrence.lease_until = occurrence.lease_token = None
                return False
            if (
                self._stop.is_set()
                or not self.settings.scheduler_enabled
                or not self.discretionary_allowed()
            ):
                occurrence.status, occurrence.reason, occurrence.available_at = (
                    "queued",
                    "global_or_host_stop",
                    self.clock() + 60000,
                )
                occurrence.lease_until = occurrence.lease_token = None
                return False
            reason = self._authority(db, user, row)
            if reason:
                self._pause(db, row, reason)
                if reason == "expired":
                    row.status, row.next_at = "completed", None
                return False
            definition = ScheduleDefinition(**row.definition)
            if self.clock() >= int(definition.expires_at.timestamp() * 1000):
                self._pause(db, row, "expired")
                row.status = "completed"
                return False
            if (
                not self.settings.scheduler_enabled
                or not allowed(definition, self.clock())
                or not self.discretionary_allowed()
            ):
                occurrence.status, occurrence.reason, occurrence.available_at = (
                    "queued",
                    "delivery_deferred",
                    self.clock() + 60000,
                )
                occurrence.lease_until = occurrence.lease_token = None
                return False
            if row.next_at is not None and row.next_at <= self.clock():
                occurrence.status, occurrence.reason = "suppressed", "missed_latest_only"
                occurrence.lease_until = occurrence.lease_token = None
                row.missed += 1
                return False
            if (
                db.scalar(
                    select(func.count())
                    .select_from(ScheduleInboxItem)
                    .where(ScheduleInboxItem.owner_id == user.id)
                )
                >= MAX_INBOX
            ):
                self._pause(db, row, "inbox_retained_limit")
                return False
            text, question_id, expiry = (
                definition.text,
                None,
                int(definition.expires_at.timestamp() * 1000),
            )
            if definition.kind == "curiosity_question":
                try:
                    with db.begin_nested():
                        result = self.curiosity.create_in(
                            db,
                            user.id,
                            row.scope_id,
                            CuriosityCreate(
                                operation_id=stable_id(occurrence.id, "question"),
                                policy_revision=row.question_policy_revision,
                                channel="inbox",
                                topic=definition.topic,
                                source=definition.source,
                            ),
                        )
                        if result["state"] == "created":
                            question = self.curiosity._question(db, user.id, result["question_id"])
                            text, question_id, expiry = (
                                question.payload["text"],
                                question.id,
                                min(expiry, question.expires_at),
                            )
                except ServiceError as error:
                    result = {"state": "not_offered", "reason": error.code}
                if not question_id:
                    occurrence.status, occurrence.reason = (
                        "suppressed",
                        result.get("reason", "question_not_offered"),
                    )
                    occurrence.lease_until = occurrence.lease_token = None
                    self._finish(db, row)
                    return False
            item_id = stable_id(occurrence.id, "inbox")
            db.add(
                ScheduleInboxItem(
                    owner_id=user.id,
                    id=item_id,
                    scope_id=row.scope_id,
                    schedule_id=row.id,
                    occurrence_id=occurrence.id,
                    epoch=user.data_epoch,
                    kind=definition.kind,
                    text=text,
                    question_id=question_id,
                    status="unread",
                    available_at=self.clock(),
                    expires_at=expiry,
                    created_at=self.clock(),
                )
            )
            occurrence.status, occurrence.item_id = "delivered", item_id
            occurrence.lease_until = occurrence.lease_token = None
            row.delivered += 1
            self._finish(db, row)
            return True

    def run_once(self):
        claimed = self.claim()
        if claimed is None:
            return (
                self.idle_dispatch()
                if self.settings.scheduler_enabled and not self._stop.is_set()
                else False
            )
        self.publish(claimed)
        return True

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()

        def work():
            while not self._stop.is_set():
                try:
                    self.run_once()
                    self.last_error_code = None
                except Exception as error:
                    # Durable leases recover; retain fixed metadata, never payload/SQL/traceback.
                    self.process_error_count = min(self.process_error_count + 1, 2147483647)
                    self.last_error_code = (
                        "dispatcher_storage_unavailable"
                        if isinstance(error, SQLAlchemyError)
                        else "dispatcher_iteration_failed"
                    )
                self._stop.wait(2)

        self._thread = threading.Thread(target=work, name="ada-schedule-dispatcher", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)

    def metadata(self):
        with self.sessions() as db:
            return {
                "globally_enabled": self.settings.scheduler_enabled,
                "worker_running": self._thread is not None and self._thread.is_alive(),
                "process_error_count": self.process_error_count,
                "last_error_code": self.last_error_code,
                "updated_at": self.clock(),
                **{
                    name: dict(
                        db.execute(select(model.status, func.count()).group_by(model.status)).all()
                    )
                    for name, model in (
                        ("schedules", Schedule),
                        ("occurrences", ScheduleOccurrence),
                        ("inbox", ScheduleInboxItem),
                    )
                },
            }
