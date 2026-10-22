"""Bounded owner-reviewed work; no inference, tool write or hidden scheduling."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from ada.curiosity_contracts import CuriosityCreate
from ada.curiosity_models import CuriosityQuestion
from ada.errors import ServiceError
from ada.memory import owned_scope
from ada.models import (
    Conversation,
    DocumentUpload,
    Event,
    Request,
    Scope,
    Source,
    SourceVersion,
    User,
    now_ms,
)
from ada.proposals import fingerprint
from ada.schedule_contracts import ScheduleConfirm
from ada.schedule_models import Schedule, ScheduleReceipt
from ada.schedule_time import TIMEZONE_DATA, zone
from ada.work_contracts import VERSION, WorkFields
from ada.work_models import WorkBrief, WorkItem, WorkReceipt, WorkRevision


def local_day(instant, timezone_name):
    if instant is None:
        return None
    try:
        return (
            (datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=instant))
            .astimezone(zone(timezone_name))
            .date()
            .isoformat()
        )
    except (OverflowError, ValueError, OSError):
        raise ServiceError(422, "work_calendar_out_of_range") from None


def validate_task_preview(db, owner, intent):
    """Also called by legacy schedule confirmation: task previews cannot bypass review."""
    key = intent.get("_work_item_id")
    if key:
        row = db.get(WorkItem, (owner, key))
        if (
            not row
            or row.status != "planned"
            or row.revision != intent.get("_work_revision")
            or row.scope_id != intent.get("_scope_id")
        ):
            raise ServiceError(409, "work_reminder_task_changed")


class WorkService:
    def __init__(self, sessions, scheduler, proposals, clock=now_ms):
        self.sessions, self.scheduler, self.proposals, self.clock = (
            sessions,
            scheduler,
            proposals,
            clock,
        )
        self.curiosity = scheduler.curiosity

    def _count(self, db, model, owner, maximum):
        if (
            db.scalar(select(func.count()).select_from(model).where(model.owner_id == owner))
            >= maximum
        ):
            raise ServiceError(413, "work_retained_limit")

    def _item(self, db, owner, key):
        row = db.get(WorkItem, (owner, key))
        if row is None:
            raise ServiceError(404, "work_item_not_found")
        if row.epoch != db.get(User, owner).data_epoch:
            raise ServiceError(410, "work_item_epoch_changed")
        owned_scope(db, owner, row.scope_id, lock=True)
        return row

    def _sources(self, db, owner, scope, fields):
        for pin in fields.pins:
            metadata = db.execute(
                select(SourceVersion.created_at, Source.kind)
                .join(Source, Source.id == SourceVersion.source_id)
                .where(
                    SourceVersion.id == str(pin.source_version_id),
                    SourceVersion.owner_id == owner,
                    SourceVersion.scope_id == scope,
                )
            ).first()
            if metadata is None:
                raise ServiceError(404, "work_source_not_found")
            if metadata.created_at > self.clock():
                raise ServiceError(409, "work_source_not_available")
            if metadata.kind == "imported_document":
                available = db.scalar(
                    select(DocumentUpload.id).where(
                        DocumentUpload.owner_id == owner,
                        DocumentUpload.scope_id == scope,
                        DocumentUpload.source_version_id == str(pin.source_version_id),
                        DocumentUpload.state == "ready",
                        DocumentUpload.published_at <= self.clock(),
                        DocumentUpload.available_from <= self.clock(),
                        (
                            DocumentUpload.available_to.is_(None)
                            | (DocumentUpload.available_to > self.clock())
                        ),
                    )
                )
                if available is None:
                    raise ServiceError(409, "work_source_not_available")
        return self.proposals._support(db, owner, scope, fields.pins)

    def project(self, owner, key, body, principal):
        payload = {"scope": key, "action": "project", **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old
            if db.scalar(select(Scope.owner_id).where(Scope.id == key)) is not None:
                raise ServiceError(409, "work_project_id_reused")
            if (
                db.scalar(select(func.count()).select_from(Scope).where(Scope.owner_id == owner))
                >= 100
            ):
                raise ServiceError(413, "work_project_limit")
            db.add(
                Scope(
                    id=key, owner_id=owner, kind="project", name=body.name, created_at=self.clock()
                )
            )
            return self._receipt(db, owner, body.operation_id, payload, "project", scope_id=key)

    def _old(self, db, owner, operation, payload):
        old = db.get(WorkReceipt, (owner, str(operation)))
        if old and old.input_hash != fingerprint({"domain": VERSION, "input": payload}):
            raise ServiceError(409, "work_operation_reused")
        return old.result if old else None

    def _receipt(self, db, owner, operation, payload, action, **result):
        self._count(db, WorkReceipt, owner, 5000)
        output = {
            "version": VERSION,
            "operation_id": str(operation),
            "action": action,
            "state": "completed",
            "created_at": self.clock(),
            **result,
        }
        db.add(
            WorkReceipt(
                owner_id=owner,
                id=str(operation),
                input_hash=fingerprint({"domain": VERSION, "input": payload}),
                result=output,
                created_at=self.clock(),
            )
        )
        return output

    def receipt(self, owner, key):
        with self.sessions() as db:
            old = db.get(WorkReceipt, (owner, key))
            if old is None:
                raise ServiceError(404, "work_receipt_not_found")
            return old.result

    def _preview(self, db, owner, scope, key, body, user):
        owned_scope(db, owner, scope, lock=True)
        row = db.get(WorkItem, (owner, key))
        if row and row.epoch != user.data_epoch:
            raise ServiceError(410, "work_item_epoch_changed")
        if row and row.scope_id != scope:
            raise ServiceError(404, "work_item_not_found")
        if (row.revision if row else 0) != body.expected_revision:
            raise ServiceError(409, "work_revision_changed")
        if row and row.kind != body.fields.kind:
            raise ServiceError(409, "work_kind_immutable")
        goal_revision = None
        if body.fields.goal_id:
            parent = self._item(db, owner, str(body.fields.goal_id))
            if (
                parent.scope_id != scope
                or parent.id == key
                or parent.kind != "goal"
                or parent.status == "dismissed"
            ):
                raise ServiceError(409, "work_goal_changed")
            goal_revision = parent.revision
        if body.fields.origin_request_id:
            request = db.get(Request, (owner, str(body.fields.origin_request_id)))
            conversation = (
                db.scalar(
                    select(Conversation.id).where(
                        Conversation.owner_id == owner,
                        Conversation.scope_id == scope,
                        Conversation.id == request.conversation_id,
                    )
                )
                if request and request.status == "completed"
                else None
            )
            pins = {str(p.source_version_id) for p in body.fields.pins}
            origins = set(
                db.scalars(
                    select(SourceVersion.id)
                    .join(
                        Source,
                        (Source.id == SourceVersion.source_id)
                        & (Source.owner_id == SourceVersion.owner_id)
                        & (Source.scope_id == SourceVersion.scope_id),
                    )
                    .join(
                        Event, (Event.id == Source.event_id) & (Event.owner_id == Source.owner_id)
                    )
                    .where(
                        SourceVersion.owner_id == owner,
                        SourceVersion.scope_id == scope,
                        Event.request_id == str(body.fields.origin_request_id),
                        Event.role == "assistant",
                    )
                )
            )
            if not conversation or not pins.intersection(origins):
                raise ServiceError(409, "work_original_reply_changed")
        sources = self._sources(db, owner, scope, body.fields)
        provenance = (
            "owner_reviewed_suggestion"
            if any(s["trust_class"] != "user_explicit" for s in sources)
            else "owner_created"
        )
        due_at = body.fields.due_ms()
        data = {
            "timezone_data": TIMEZONE_DATA,
            "due_at": due_at,
            "owner": owner,
            "epoch": user.data_epoch,
            "scope": scope,
            "item": key,
            "input": body.model_dump(mode="json", exclude={"preview_hash"}),
            "sources": sources,
            "goal_revision": goal_revision,
        }
        return {
            "version": VERSION,
            "preview_hash": fingerprint(data),
            "sources": sources,
            "provenance": provenance,
            "due_at": due_at,
            "reminder": "not_scheduled",
            "reminder_choice": body.reminder_choice,
        }

    def preview(self, owner, scope, key, body, principal):
        with self.sessions.begin() as db:
            user = self.scheduler._owner(db, owner, principal)
            return self._preview(db, owner, scope, key, body, user)

    def _pause(self, db, row):
        if row.schedule_id:
            scheduled = db.get(Schedule, (row.owner_id, row.schedule_id))
            if scheduled and scheduled.status != "deleted":
                self.scheduler._pause(db, scheduled, "work_item_changed")
        if row.question_id:
            question = db.get(CuriosityQuestion, (row.owner_id, row.question_id))
            if question and question.status in ("pending", "offered", "deferred", "opened"):
                self.curiosity._scrub(question, "dismissed", self.clock())

    def _revision(self, db, row):
        self._count(db, WorkRevision, row.owner_id, 2000)
        db.flush()
        db.add(
            WorkRevision(
                owner_id=row.owner_id,
                item_id=row.id,
                revision=row.revision,
                fields=row.fields,
                created_at=self.clock(),
            )
        )

    def write(self, owner, scope, key, body, principal):
        payload = {"scope": scope, "item": key, **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            user = self.scheduler._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old
            preview = self._preview(db, owner, scope, key, body, user)
            if body.preview_hash is None or body.preview_hash != preview["preview_hash"]:
                raise ServiceError(409, "work_preview_changed")
            row = db.get(WorkItem, (owner, key))
            if row is None:
                self._count(db, WorkItem, owner, 200)
                row = WorkItem(
                    owner_id=owner,
                    id=key,
                    scope_id=scope,
                    revision=0,
                    epoch=user.data_epoch,
                    created_at=self.clock(),
                )
                db.add(row)
            else:
                self._pause(db, row)
            row.kind, row.status = body.fields.kind, body.fields.status
            row.goal_id = str(body.fields.goal_id) if body.fields.goal_id else None
            row.fields, row.due_at, row.provenance = (
                body.fields.model_dump(mode="json"),
                preview["due_at"],
                preview["provenance"],
            )
            row.revision += 1
            row.updated_at = self.clock()
            self._revision(db, row)
            return self._receipt(
                db, owner, body.operation_id, payload, "save", item_id=key, revision=row.revision
            )

    def _output(self, db, row):
        fields = WorkFields(**row.fields)
        try:
            sources, unavailable = self._sources(db, row.owner_id, row.scope_id, fields), None
        except ServiceError:
            sources, unavailable = [], "original_source_unavailable"
        origin = (
            db.get(Request, (row.owner_id, str(fields.origin_request_id)))
            if fields.origin_request_id
            else None
        )
        return {
            "version": VERSION,
            "id": row.id,
            "origin_conversation_id": origin.conversation_id if origin else None,
            "scope_id": row.scope_id,
            "revision": row.revision,
            "fields": row.fields,
            "due_at": row.due_at,
            "overdue": row.status == "planned"
            and row.due_at is not None
            and row.due_at < self.clock(),
            "provenance": row.provenance,
            "sources": sources,
            "source_unavailable": unavailable,
            "schedule_id": row.schedule_id,
            "question_id": row.question_id,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def items(self, owner, scope, offset=0):
        with self.sessions.begin() as db:
            user = self.scheduler._owner(db, owner)
            owned_scope(db, owner, scope)
            rows = db.scalars(
                select(WorkItem)
                .where(
                    WorkItem.owner_id == owner,
                    WorkItem.scope_id == scope,
                    WorkItem.epoch == user.data_epoch,
                )
                .order_by(WorkItem.created_at, WorkItem.id)
                .offset(offset)
                .limit(50)
            )
            return [self._output(db, row) for row in rows]

    def detail(self, owner, key):
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner)
            return self._output(db, self._item(db, owner, key))

    def history(self, owner, key, offset=0):
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner)
            self._item(db, owner, key)
            return [
                {"revision": r.revision, "fields": r.fields, "created_at": r.created_at}
                for r in db.scalars(
                    select(WorkRevision)
                    .where(WorkRevision.owner_id == owner, WorkRevision.item_id == key)
                    .order_by(WorkRevision.revision)
                    .offset(offset)
                    .limit(100)
                )
            ]

    def _brief_output(self, db, row):
        user = self.scheduler._owner(db, row.owner_id)
        if row.epoch != user.data_epoch:
            raise ServiceError(410, "work_brief_epoch_changed")
        value = row.snapshot
        items = []
        for i, snapshot in enumerate(value["items"]):
            owned_scope(db, row.owner_id, snapshot["scope_id"])
            # Revalidate original pins; current task status never rewrites this snapshot.
            try:
                sources = self._sources(
                    db, row.owner_id, snapshot["scope_id"], WorkFields(**snapshot["fields"])
                )
                unavailable = None
            except ServiceError:
                sources, unavailable = [], "original_source_unavailable"
            task = snapshot | {"sources": sources, "source_unavailable": unavailable}
            due_on_day = (
                value["day_flags"][i]
                if "day_flags" in value
                else local_day(snapshot["due_at"], value["timezone"]) == value["day"]
            )
            items.append(
                {
                    "label": f"T{i + 1}",
                    "task": task,
                    "overdue": task["overdue"],
                    "due_on_day": due_on_day,
                    "changes": value["changes"][i],
                }
            )
        return {
            "version": VERSION,
            "id": row.id,
            "scope_ids": value["scope_ids"],
            "day": value["day"],
            "timezone": value["timezone"],
            "items": items,
            "timezone_data": value.get("timezone_data", "unrecorded"),
            "needs_decision": sum(
                x["task"]["fields"]["status"] in ("unknown", "deferred") for x in items
            ),
            "generated_by": "deterministic_task_projection",
            "factual_evidence": False,
            "created_at": row.created_at,
        }

    def brief(self, owner, body, principal):
        payload = body.model_dump(mode="json")
        with self.sessions.begin() as db:
            user = self.scheduler._owner(db, owner, principal)
            previous = self._old(db, owner, body.operation_id, payload)
            if previous:
                return self._brief_output(db, db.get(WorkBrief, (owner, previous["brief_id"])))
            scopes = sorted(map(str, body.scope_ids))
            for scope in scopes:
                owned_scope(db, owner, scope, lock=True)
            items, changes = [], []
            for key in body.item_ids:
                row = self._item(db, owner, str(key))
                if row.scope_id not in scopes:
                    raise ServiceError(404, "work_item_not_found")
                item = self._output(db, row)
                item["sources"] = []  # Never persist duplicate source quotes in brief caches.
                items.append(item)
                previous = db.get(WorkRevision, (owner, row.id, row.revision - 1))
                changes.append(
                    [k for k, v in row.fields.items() if previous and previous.fields.get(k) != v]
                    if previous
                    else ["created"]
                )
            cache = fingerprint(
                {
                    "owner": owner,
                    "scopes": scopes,
                    "epoch": user.data_epoch,
                    "revisions": [
                        [r["id"], r["revision"], r["overdue"], r["source_unavailable"]]
                        for r in items
                    ],
                    "day": payload["day"],
                    "timezone": body.timezone,
                    "timezone_data": TIMEZONE_DATA,
                }
            )
            cached = db.scalar(
                select(WorkBrief).where(WorkBrief.owner_id == owner, WorkBrief.cache_key == cache)
            )
            if cached:
                self._receipt(db, owner, body.operation_id, payload, "brief", brief_id=cached.id)
                return self._brief_output(db, cached)
            self._count(db, WorkBrief, owner, 100)
            row = WorkBrief(
                owner_id=owner,
                id=str(body.operation_id),
                epoch=user.data_epoch,
                cache_key=cache,
                input_hash=fingerprint(payload),
                snapshot={
                    "scope_ids": scopes,
                    "items": items,
                    "changes": changes,
                    "day_flags": [
                        local_day(item["due_at"], body.timezone) == payload["day"] for item in items
                    ],
                    "timezone_data": TIMEZONE_DATA,
                    "day": payload["day"],
                    "timezone": body.timezone,
                },
                created_at=self.clock(),
            )
            db.add(row)
            self._receipt(db, owner, body.operation_id, payload, "brief", brief_id=row.id)
            return self._brief_output(db, row)

    def brief_detail(self, owner, key):
        with self.sessions.begin() as db:
            row = db.get(WorkBrief, (owner, key))
            if row is None:
                alias = db.get(WorkReceipt, (owner, key))
                row = (
                    db.get(WorkBrief, (owner, alias.result["brief_id"]))
                    if alias and alias.result.get("action") == "brief"
                    else None
                )
            if row is None:
                raise ServiceError(404, "work_brief_not_found")
            return self._brief_output(db, row)

    def followup(self, owner, key, body, principal):
        payload = {"item": key, "action": "followup", **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old
            row = self._item(db, owner, key)
            if row.revision != body.expected_revision or row.status not in ("planned", "unknown"):
                raise ServiceError(409, "work_revision_or_state_changed")
            if row.question_id:
                previous = db.get(CuriosityQuestion, (owner, row.question_id))
                if previous and previous.status in (
                    "pending",
                    "offered",
                    "deferred",
                    "opened",
                    "answering",
                ):
                    raise ServiceError(409, "work_question_already_pending")
            question = self.curiosity.create_in(
                db,
                owner,
                row.scope_id,
                CuriosityCreate(
                    operation_id=body.operation_id,
                    policy_revision=body.policy_revision,
                    channel="inbox",
                    topic=body.topic,
                ),
            )
            if question["state"] != "created":
                raise ServiceError(409, "work_question_not_offered")
            q = db.get(CuriosityQuestion, (owner, question["question_id"]))
            q.payload = q.payload | {
                "text": f"How would you like to follow up on: {row.fields['description']}?",
                "reason": "owner_requested_work_followup",
                "policy": q.payload["policy"]
                | {
                    "generator": "ada-work-question-v1",
                    "work_item_id": key,
                    "work_revision": row.revision,
                },
            }
            row.question_id = q.id
            row.revision += 1
            row.updated_at = self.clock()
            self._revision(db, row)
            return self._receipt(
                db,
                owner,
                body.operation_id,
                payload,
                "followup",
                item_id=key,
                revision=row.revision,
                question_id=q.id,
            )

    def reminder_preview(self, owner, key, body, principal):
        payload = {"item": key, "action": "reminder_preview", **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old
            row = self._item(db, owner, key)
            if (
                row.revision != body.expected_revision
                or row.status != "planned"
                or body.definition.kind != "reminder"
                or body.definition.text != row.fields["description"]
            ):
                raise ServiceError(409, "work_reminder_preview_changed")
            plan, question_revision, source = self.scheduler._validate(
                db, owner, row.scope_id, body.definition, preview=True
            )
            preview = self.scheduler._receipt(
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
                preview_expires_at=self.clock() + 900000,
                _scope_id=row.scope_id,
                _work_item_id=key,
                _work_revision=row.revision,
            )
            return self._receipt(
                db,
                owner,
                body.operation_id,
                payload,
                "reminder_preview",
                item_id=key,
                revision=row.revision,
                schedule_preview=preview,
            )

    def reminder_confirm(self, owner, key, body, principal):
        payload = {"item": key, "action": "reminder_confirm", **body.model_dump(mode="json")}
        with self.sessions.begin() as db:
            self.scheduler._owner(db, owner, principal)
            old = self._old(db, owner, body.operation_id, payload)
            if old:
                return old
            row = self._item(db, owner, key)
            preview = db.get(ScheduleReceipt, (owner, str(body.preview_id)))
            if not preview or preview.result.get("_work_item_id") != key:
                raise ServiceError(404, "work_reminder_preview_not_found")
            validate_task_preview(db, owner, preview.result)
            if (
                row.revision != body.expected_revision
                or (row.schedule_id and row.schedule_id != str(body.schedule_id))
                or (not row.schedule_id and db.get(Schedule, (owner, str(body.schedule_id))))
            ):
                raise ServiceError(409, "work_reminder_binding_changed")
            self.scheduler.confirm_in(
                db,
                owner,
                str(body.schedule_id),
                ScheduleConfirm(
                    operation_id=body.operation_id,
                    preview_id=body.preview_id,
                    expected_generation=body.expected_generation,
                    consent_revision=body.consent_revision,
                ),
                principal,
                work_binding=True,
            )
            row.schedule_id = str(body.schedule_id)
            row.revision += 1
            row.updated_at = self.clock()
            self._revision(db, row)
            return self._receipt(
                db,
                owner,
                body.operation_id,
                payload,
                "reminder_confirm",
                item_id=key,
                revision=row.revision,
                schedule_id=row.schedule_id,
            )
