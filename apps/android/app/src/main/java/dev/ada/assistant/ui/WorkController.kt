package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.encodeToString

data class WorkDraft(val scope: UUID, val item: UUID, val body: WorkWriteDto) { override fun toString() = "WorkDraft(redacted)" }
data class WorkState(val supported: Boolean = false, val busy: Boolean = false,
    val scopes: List<ScopeDto> = emptyList(), val scope: UUID? = null, val offset: Int = 0,
    val items: List<WorkItemDto> = emptyList(), val draft: WorkDraft? = null, val preview: WorkPreviewDto? = null,
    val selected: Map<UUID, UUID> = emptyMap(), val brief: WorkBriefDto? = null,
    val history: List<WorkRevisionDto> = emptyList(), val historyItem: UUID? = null,
    val questionPolicy: CuriosityPolicyDto? = null, val schedulePolicy: SchedulePolicyDto? = null,
    val schedules: List<ScheduleDto> = emptyList(), val reminder: WorkReceiptDto? = null,
    val pending: List<WorkPending> = emptyList(), val notice: String? = null) { override fun toString() = "WorkState(redacted)" }

/** Every confirmed write is encrypted before HTTP. Reopening performs only original GETs. */
class WorkController(private val api: AdaApi, private val store: SessionStore, private val scope: CoroutineScope,
    private val unauthorized: () -> Unit) {
    private val mutable = MutableStateFlow(WorkState()); val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null; private var owner: SessionIdentity? = null
    private var epoch = 0L; private var sequence = 0L; private var foreground = true; private var visible = false
    private var cooldown = 0L; private val jobs = mutableSetOf<Job>()
    private fun update(f: (WorkState) -> WorkState) { mutable.value = f(state.value) }
    private fun current(e: Long) = e == epoch && owner != null
    fun reset() { epoch++; sequence++; jobs.toList().forEach { it.cancel() }; jobs.clear(); connection = null; owner = null; cooldown = 0; mutable.value = WorkState() }
    fun observeForeground(active: Boolean) { foreground = active; sequence++; update { it.copy(busy = false) }; if (active && visible) refresh() }
    fun observeVisible(active: Boolean) { if (visible == active) return; visible = active; sequence++; update { it.copy(busy = false) }; if (active) refresh() }
    private fun launch(block: suspend (ConnectionCredential, SessionIdentity, Long) -> Unit) {
        val c = connection ?: return; val who = owner ?: return; val e = epoch
        scope.launch(start = CoroutineStart.UNDISPATCHED) {
            try { if (current(e)) block(c,who,e) }
            catch (cancel: CancellationException) { throw cancel }
            catch (_: Exception) { if (current(e)) update { it.copy(busy = false, notice = "Result unconfirmed. Check the saved operation before retrying.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accept(r: ApiResult<T>, e: Long): T? {
        if (!current(e)) return null
        if (r is ApiResult.Success) return r.value
        val error = (r as ApiResult.Failure).reason
        if (error == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (error is ApiFailure.Busy) cooldown = System.currentTimeMillis() + (error.retryAfterSeconds ?: 3).coerceIn(0,300) * 1000L
        if (error is ApiFailure.Http && error.status == 429) cooldown = System.currentTimeMillis() + 60000
        update { it.copy(busy = false, notice = when (error) {
            ApiFailure.Validation -> "Check description, due time, IANA timezone and ambiguous-time choice. Nothing was silently scheduled."
            ApiFailure.Conflict -> "Revision, source, consent or preview changed. Keep the original operation until its result is checked."
            ApiFailure.TooLarge -> "The retained work or operation limit was reached."
            else -> "Work is unavailable or this result is unconfirmed. Text chat remains available."
        }) }; return null
    }
    fun setVerifiedSession(c: ConnectionCredential, who: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = c; owner = who; update { it.copy(supported = caps.work_protocol == WORK_PROTOCOL) }
        if (!state.value.supported) return
        launch { conn, identity, e ->
            val saved = store.workJournal(identity)?.operations.orEmpty(); if (!current(e)) return@launch
            update { it.copy(pending = saved) }
            saved.forEach { check(conn, identity, it, e) }
        }
    }
    private fun validate(row: WorkItemDto, selectedScope: UUID? = null) {
        require(row.version == WORK_PROTOCOL && row.revision > 0 && (selectedScope == null || row.scope_id == selectedScope))
        require(row.fields.kind in setOf("goal","task") && row.fields.status in setOf("planned","done","deferred","unknown","dismissed"))
        row.sources.forEach { require(it.trust_class in setOf("user_explicit","model_generated","imported_untrusted") && it.evidence.content_hash.matches(Regex("[a-f0-9]{64}")) && it.evidence.span_start >= 0 && it.evidence.span_end-it.evidence.span_start == it.evidence.quote.codePointCount(0,it.evidence.quote.length)) }

    }
    fun refresh() {
        if (!visible || !foreground || !state.value.supported || System.currentTimeMillis() < cooldown) return
        launch { c, _, e ->
            val query = ++sequence; val selected = state.value.scope; val offset = state.value.offset
            fun live() = current(e) && foreground && visible && sequence == query && state.value.scope == selected
            update { it.copy(busy = true) }
            val scopes = accept(api.scopes(c,100,0), e) ?: return@launch; if (!live()) return@launch
            update { it.copy(scopes = scopes) }
            if (selected == null) { update { it.copy(busy = false) }; return@launch }
            val rows = accept(api.workItems(c, selected, offset),e) ?: return@launch; if (!live()) return@launch
            require(rows.size <= 50 && rows.map { it.id }.distinct().size == rows.size); rows.forEach { validate(it,selected) }
            val q = accept(api.curiosityPolicy(c),e); if (!live()) return@launch
            val p = accept(api.schedulePolicy(c),e); if (!live()) return@launch
            val schedules = if (p != null) accept(api.schedules(c,selected),e).orEmpty() else emptyList(); if (!live()) return@launch
            update { it.copy(items = rows, questionPolicy = q, schedulePolicy = p, schedules = schedules, busy = false) }
        }
    }
    fun selectScope(id: UUID) { if (state.value.scopes.none { it.id == id }) return; sequence++; update { it.copy(scope = id, offset = 0, items = emptyList(), draft = null, preview = null, brief = null, history = emptyList(), historyItem = null, reminder = null, busy = false) }; refresh() }
    fun page(next: Boolean) { val offset = (state.value.offset + if (next) 50 else -50).coerceIn(0,150); sequence++; update { it.copy(offset = offset, items = emptyList(), busy = false) }; refresh() }
    fun begin(kind: String = "task") { val selected = state.value.scope ?: return; sequence++; update { it.copy(draft = WorkDraft(selected, UUID.randomUUID(), WorkWriteDto(UUID.randomUUID(),0,WorkFieldsDto(kind,""))), preview = null, busy = false) } }
    fun edit(row: WorkItemDto) { sequence++; update { it.copy(draft = WorkDraft(row.scope_id,row.id,WorkWriteDto(UUID.randomUUID(),row.revision,row.fields)), preview = null, busy = false) } }
    fun fields(value: WorkFieldsDto) { val draft = state.value.draft ?: return; if (state.value.pending.any { it.operationId == draft.body.operation_id }) return; sequence++; update { it.copy(draft = draft.copy(body = draft.body.copy(fields = value, preview_hash = null)), preview = null, busy = false) } }
    fun reminderChoice(value: String) { val d = state.value.draft ?: return; if (value !in setOf("none","review_after_save") || state.value.pending.any { it.operationId == d.body.operation_id }) return; sequence++; update { it.copy(draft=d.copy(body=d.body.copy(reminder_choice=value)),preview=null,busy=false) } }
    fun closeDraft() { sequence++; update { it.copy(draft = null, preview = null, busy = false) } }
    fun fromReply(event: EventDto, selectedScope: UUID) {
        if (event.role != "assistant" || event.request_status != "completed" || !state.value.supported) return
        sequence++; val query = sequence
        update { it.copy(scope = selectedScope, items = emptyList(), draft = null, preview = null, busy = true) }
        launch { c, _, e ->
            val source = accept(api.source(c,event.source_version_id),e) ?: return@launch
            if (!current(e) || sequence != query || !foreground) return@launch
            require(source.scope_id == selectedScope && source.id == event.source_version_id && source.content_hash == voiceHash(source.content) && source.content == event.content && source.trust_class == "model_generated")
            val count = source.content.codePointCount(0,source.content.length).coerceAtMost(400)
            val pin = SourcePinDto(source.id,source.version,source.content_hash,0,count)
            update { it.copy(draft = WorkDraft(selectedScope, UUID.randomUUID(), WorkWriteDto(UUID.randomUUID(),0,WorkFieldsDto("task","",origin_request_id=event.request_id,pins=listOf(pin)))), busy = false,
                notice = "Write your next action. The selected original excerpt is the first $count characters of this generated reply; review it before Save. It is not factual evidence.") }
        }
    }
    fun prepare() { val draft = state.value.draft ?: return
        if (!foreground || !visible || state.value.busy) return
        val query = ++sequence; update { it.copy(busy = true, preview = null) }
        launch { c, _, e ->
            val preview = accept(api.workPreview(c,draft.scope,draft.item,draft.body),e) ?: return@launch
            if (current(e) && visible && foreground && query == sequence && state.value.draft == draft) {
                require(preview.version == WORK_PROTOCOL && preview.preview_hash.matches(Regex("[a-f0-9]{64}")) && preview.reminder == "not_scheduled" && preview.reminder_choice == draft.body.reminder_choice)
                update { it.copy(preview = preview, busy = false) }
            }
        }
    }
    private suspend fun pending(who: SessionIdentity, e: Long) { val rows = store.workJournal(who)?.operations.orEmpty(); if (current(e)) update { it.copy(pending = rows) } }
    private suspend fun ack(who: SessionIdentity, op: WorkPending, receipt: WorkReceiptDto, e: Long) {
        require(receipt.version == WORK_PROTOCOL && receipt.operation_id == op.operationId && receipt.state == "completed")
        require(receipt.action == if (op.kind == "save") "save" else op.kind)
        if (op.kind == "project") require(receipt.scope_id == op.scopeId) else require(receipt.item_id == op.itemId)
        when (op.kind) {
            "save" -> require(receipt.revision == adaJson.decodeFromString<WorkWriteDto>(op.body).expected_revision + 1)
            "followup" -> require(receipt.revision == adaJson.decodeFromString<WorkFollowupDto>(op.body).expected_revision + 1 && receipt.question_id != null)
            "reminder_confirm" -> {
                val input = adaJson.decodeFromString<WorkReminderConfirmDto>(op.body)
                require(receipt.revision == input.expected_revision + 1 && receipt.schedule_id == input.schedule_id)
            }
            "reminder_preview" -> {
                val input = adaJson.decodeFromString<WorkReminderPreviewDto>(op.body)
                val preview = requireNotNull(receipt.schedule_preview)
                val returned = requireNotNull(preview.definition)
                require(receipt.revision == input.expected_revision && preview.version == "ada-scheduling-v1" && preview.operation_id == op.operationId && preview.action == "preview" && preview.state == "completed")
                require(returned.copy(expires_at=input.definition.expires_at) == input.definition && java.time.OffsetDateTime.parse(returned.expires_at).toInstant() == java.time.OffsetDateTime.parse(input.definition.expires_at).toInstant())
                require(preview.occurrences?.size in 1..100 && preview.preview_expires_at != null && preview.timezone_data != null)
            }
        }
        if (!current(e)) return
        if (op.kind == "reminder_preview") { if (state.value.scope == op.scopeId && visible && foreground) update { it.copy(reminder = receipt) } }
        else {
            if (op.kind == "reminder_confirm") store.removeWorkOperation(who,adaJson.decodeFromString<WorkReminderConfirmDto>(op.body).preview_id)
            store.removeWorkOperation(who,op.operationId)
        }
        if (!current(e)) return
        pending(who,e); update { it.copy(busy = false, draft = if (op.kind == "save" && it.draft?.item == op.itemId) null else it.draft, preview = if (it.draft?.item == op.itemId) null else it.preview, reminder = if (op.kind == "reminder_confirm" && it.reminder?.item_id == op.itemId) null else it.reminder, notice = "Saved result confirmed. A task due date alone does not schedule a reminder.") }; refresh()
    }
    private suspend fun ackBrief(who: SessionIdentity, op: WorkPending, result: WorkBriefDto, e: Long, explicit: Boolean = false) {
        val input = adaJson.decodeFromString<WorkBriefInputDto>(op.body)
        require(result.version == WORK_PROTOCOL && !result.factual_evidence && result.generated_by == "deterministic_task_projection" && result.scope_ids.toSet() == input.scope_ids.toSet() && result.day == input.day && result.timezone == input.timezone)
        require(result.items.map { it.task.id }.toSet() == input.item_ids.toSet()); result.items.forEach { validate(it.task); require(it.task.scope_id in input.scope_ids) }
        if (!current(e)) return
        if (!visible || !foreground || (!explicit && state.value.selected.keys.toSet() != input.item_ids.toSet())) return
        store.removeWorkOperation(who,op.operationId); if (!current(e)) return
        pending(who,e); if (visible && foreground) update { it.copy(brief = result, busy = false) }
    }
    private suspend fun check(c: ConnectionCredential, who: SessionIdentity, op: WorkPending, e: Long) {
        if (op.kind == "brief") { when(val r = api.workBrief(c,op.operationId)) { is ApiResult.Success -> ackBrief(who,op,r.value,e,explicit=true); is ApiResult.Failure -> if (r.reason != ApiFailure.NotFound) accept(r,e) }; return }
        when(val r = api.workReceipt(c,op.operationId)) { is ApiResult.Success -> ack(who,op,r.value,e); is ApiResult.Failure -> if (r.reason != ApiFailure.NotFound) accept(r,e) else if (current(e)) update { it.copy(busy = false, notice = "No saved receipt. Retry explicitly with the original operation or discard only its local recovery record.") } }
    }
    private suspend fun submit(c: ConnectionCredential, who: SessionIdentity, op: WorkPending, e: Long) {
        if (op.kind == "brief") { when(val r = api.workCreateBrief(c,op)) { is ApiResult.Success -> ackBrief(who,op,r.value,e); is ApiResult.Failure -> accept(r,e) }; return }
        when(val r = api.workWrite(c,op)) { is ApiResult.Success -> ack(who,op,r.value,e); is ApiResult.Failure -> accept(r,e) }
    }
    private fun queue(op: WorkPending) {
        if (!visible || !foreground || !state.value.supported || state.value.busy || System.currentTimeMillis() < cooldown) return
        val who = owner ?: return; validateWorkJournal(WorkJournal(who,listOf(op))); update { it.copy(busy = true) }
        launch { c, identity, e -> store.saveWorkOperation(identity,op); if (current(e)) { pending(identity,e); submit(c,identity,op,e) } }
    }
    fun save() { val d = state.value.draft ?: return; val preview = state.value.preview ?: return; val b = d.body.copy(preview_hash=preview.preview_hash); queue(WorkPending(b.operation_id,"save",adaJson.encodeToString(b),d.scope,d.item)) }
    fun project(name: String) { val b = WorkProjectDto(UUID.randomUUID(),name); queue(WorkPending(b.operation_id,"project",adaJson.encodeToString(b),UUID.randomUUID())) }
    fun selectForBrief(row: WorkItemDto, selected: Boolean) { if (selected && (state.value.selected.size >= 30 || (state.value.selected.values.toSet()+row.scope_id).size > 4)) return; update { it.copy(selected = if (selected) it.selected + (row.id to row.scope_id) else it.selected-row.id) } }
    fun brief(day: String, timezone: String) { val rows = state.value.selected; if (rows.isEmpty()) return; val b = WorkBriefInputDto(UUID.randomUUID(),rows.values.distinct(),rows.keys.toList(),day,timezone); queue(WorkPending(b.operation_id,"brief",adaJson.encodeToString(b))) }
    fun history(row: WorkItemDto, offset: Int = 0) { val query = ++sequence; update { it.copy(historyItem = row.id, history = emptyList()) }; launch { c, _, e -> val rows = accept(api.workHistory(c,row.id,offset),e) ?: return@launch; if (current(e) && visible && foreground && query == sequence) update { it.copy(history = rows) } } }
    fun followup(row: WorkItemDto, topic: String) { val p = state.value.questionPolicy ?: return; val b = WorkFollowupDto(UUID.randomUUID(),row.revision,p.revision,topic); queue(WorkPending(b.operation_id,"followup",adaJson.encodeToString(b),row.scope_id,row.id)) }
    fun reminder(row: WorkItemDto, definition: ScheduleDefinitionDto) { val b = WorkReminderPreviewDto(UUID.randomUUID(),row.revision,definition); queue(WorkPending(b.operation_id,"reminder_preview",adaJson.encodeToString(b),row.scope_id,row.id)) }
    fun confirmReminder() {
        val r = state.value.reminder ?: return; val row = state.value.items.firstOrNull { it.id == r.item_id } ?: return
        val p = state.value.schedulePolicy ?: return; val old = state.value.schedules.firstOrNull { it.id == row.schedule_id }
        val b = WorkReminderConfirmDto(UUID.randomUUID(),row.revision,r.operation_id,p.revision,row.schedule_id ?: UUID.randomUUID(),old?.generation ?: 0)
        queue(WorkPending(b.operation_id,"reminder_confirm",adaJson.encodeToString(b),row.scope_id,row.id))
    }
    fun check(op: WorkPending) { if (op in state.value.pending) launch { c,o,e -> check(c,o,op,e) } }
    fun retry(op: WorkPending) { if (!state.value.busy && visible && foreground && System.currentTimeMillis() >= cooldown && op in state.value.pending) { update { it.copy(busy=true) }; launch { c,o,e -> submit(c,o,op,e) } } }
    fun forget(op: WorkPending) { if (op in state.value.pending) launch { _,o,e -> store.removeWorkOperation(o,op.operationId); if (current(e)) { pending(o,e); update { it.copy(notice="Only the local recovery record was discarded. Server tasks or reminders were not deleted.", reminder=null) } } } }
}
