package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.time.Instant
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.encodeToString

data class ScheduleState(val supported: Boolean = false, val busy: Boolean = false,
    val policy: SchedulePolicyDto? = null, val scopeId: UUID? = null,
    val schedules: List<ScheduleDto> = emptyList(), val inbox: List<ScheduleInboxDto> = emptyList(),
    val inboxOffset: Int = 0, val occurrenceOffset: Int = 0, val inspectedSchedule: UUID? = null,
    val occurrences: List<ScheduleOccurrenceDto> = emptyList(), val pending: List<SchedulePending> = emptyList(),
    val preview: ScheduleReceiptDto? = null, val previewSchedule: UUID? = null, val previewGeneration: Int = 0,
    val receipts: Map<UUID, ScheduleReceiptDto> = emptyMap(), val notice: String? = null) {
    override fun toString() = "ScheduleState(redacted)"
}

/** GET-only restart and visible-only polling. Every POST has an encrypted exact reservation. */
class ScheduleController(private val api: AdaApi, private val store: SessionStore,
    private val scope: CoroutineScope, private val unauthorized: () -> Unit) {
    private val mutable = MutableStateFlow(ScheduleState())
    val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private var selection = 0L
    private var readSequence = 0L
    private var foreground = true
    private var poll: Job? = null
    private var cooldown = 0L
    private val jobs = mutableSetOf<Job>()
    private fun update(block: (ScheduleState) -> ScheduleState) { mutable.value = block(mutable.value) }
    private fun current(epoch: Long) = generation == epoch && identity != null
    fun reset() { generation++; selection++; poll?.cancel(); poll = null
        jobs.toList().forEach { it.cancel() }; jobs.clear(); connection = null; identity = null; cooldown = 0
        mutable.value = ScheduleState() }
    private fun work(block: suspend (ConnectionCredential, SessionIdentity, Long) -> Unit) {
        val c = connection ?: return
        val who = identity ?: return
        val epoch = generation
        scope.launch(start = CoroutineStart.UNDISPATCHED) {
            try { if (current(epoch)) block(c, who, epoch) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(epoch)) update { it.copy(busy = false, notice = "This change is unconfirmed. Check its saved result before retrying.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accept(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        if (result is ApiResult.Success) return result.value
        val fault = (result as ApiResult.Failure).reason
        if (fault == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (fault is ApiFailure.Busy) cooldown = System.currentTimeMillis() + (fault.retryAfterSeconds ?: 3).coerceIn(0, 300) * 1000L
        if (fault is ApiFailure.Http && fault.status == 429) cooldown = System.currentTimeMillis() + 60000
        val message = when (fault) {
            ApiFailure.Validation -> "Check the local date/time, IANA timezone, DST choice, allowed hours and expiry. Past or ambiguous times need a new preview."
            ApiFailure.Conflict -> "This schedule or its consent changed. Refresh, review the current state and preview edits again."
            ApiFailure.TooLarge -> "The retained schedule or receipt limit was reached. You can still turn scheduling off; saved content follows owner deletion controls."
            ApiFailure.NotFound -> "This schedule, inbox item or saved result is unavailable to this account."
            else -> "Reminders are unavailable or this change needs review. Saved operations have not been retried."
        }
        update { it.copy(busy = false, notice = message) }
        return null
    }
    fun setVerifiedSession(c: ConnectionCredential, who: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = c; identity = who
        update { it.copy(supported = caps.scheduling_protocol == "ada-scheduling-v1" && !caps.scheduling_background_push) }
        if (!state.value.supported) return
        work { conn, owner, epoch ->
            val journal = store.scheduleJournal(owner)
            if (!current(epoch)) return@work
            update { it.copy(pending = journal?.operations ?: emptyList()) }
            journal?.operations?.forEach { check(conn, owner, it, epoch) }
            load(conn, epoch)
        }
        startPolling()
    }
    fun observeForeground(visible: Boolean) { foreground = visible; poll?.cancel(); poll = null; if (visible) startPolling() }
    private fun startPolling() {
        if (!foreground || !state.value.supported || poll?.isActive == true) return
        val epoch = generation
        poll = scope.launch {
            while (current(epoch) && foreground) {
                delay(30000)
                if (current(epoch) && foreground && System.currentTimeMillis() >= cooldown) refresh()
            }
        }
    }
    fun activate(id: UUID?) { selection++; update { it.copy(scopeId = id, schedules = emptyList(), occurrences = emptyList(), occurrenceOffset = 0, inspectedSchedule = null, inboxOffset = 0, inbox = emptyList(), preview = null) }; refresh() }
    fun clearPreview() { update { it.copy(preview = null) } }
    fun refresh() {
        if (!state.value.supported || !foreground || System.currentTimeMillis() < cooldown) return
        work { c, _, epoch -> load(c, epoch) }
    }
    private suspend fun load(c: ConnectionCredential, epoch: Long) {
        val selected = state.value.scopeId
        val sequence = selection
        val page = state.value.inboxOffset
        val request = ++readSequence
        fun visible() = current(epoch) && request == readSequence && page == state.value.inboxOffset
        update { it.copy(busy = true) }
        val policyResult = api.schedulePolicy(c)
        if (!visible()) return
        val policy = accept(policyResult, epoch) ?: return
        require(policy.version == "ada-scheduling-v1" && policy.revision >= 0 && policy.notice_channel == "foreground_in_app" && !policy.background_push)
        if (!visible() || policy.revision < (state.value.policy?.revision ?: 0)) return
        update { it.copy(policy = policy) }
        val inboxResult = api.scheduleInbox(c, page)
        if (!visible()) return
        val inbox = accept(inboxResult, epoch) ?: return
        require(inbox.size <= 100 && inbox.map { it.id }.distinct().size == inbox.size && inbox.all { it.version == "ada-scheduling-v1" })
        if (visible()) update { it.copy(inbox = inbox.sortedByDescending { row -> row.created_at }, busy = false) }
        if (selected != null) {
            val rows = accept(api.schedules(c, selected), epoch) ?: return
            require(rows.size <= 100 && rows.all { it.version == "ada-scheduling-v1" && it.scope_id == selected && it.generation > 0 })
            if (visible() && sequence == selection) update { it.copy(schedules = rows, busy = false) }
        }
    }
    private suspend fun pending(owner: SessionIdentity, epoch: Long) {
        val rows = store.scheduleJournal(owner)?.operations ?: emptyList()
        if (current(epoch)) update { it.copy(pending = rows) }
    }
    private fun queue(op: SchedulePending) {
        if (!state.value.supported || (System.currentTimeMillis() < cooldown && !op.turnsSchedulingOff())) return
        val who = identity ?: return
        validateScheduleJournal(ScheduleJournal(who, listOf(op)))
        update { it.copy(busy = true, notice = null) }
        work { c, owner, epoch ->
            store.saveScheduleOperation(owner, op)
            if (!current(epoch)) return@work
            pending(owner, epoch); submit(c, owner, op, epoch)
        }
    }
    private suspend fun acknowledge(c: ConnectionCredential, owner: SessionIdentity, op: SchedulePending, receipt: ScheduleReceiptDto, epoch: Long) {
        require(receipt.version == "ada-scheduling-v1" && receipt.operation_id == op.operationId && receipt.action == op.kind && receipt.state == "completed")
        if (op.kind == "confirm" || op.kind == "action") require(receipt.schedule_id == op.scheduleId)
        if (op.itemId != null) require(receipt.item_id == op.itemId)
        if (op.kind == "open") require(receipt.conversation_id == adaJson.decodeFromString<ScheduleOpenDto>(op.body).conversation_id)
        if (op.kind == "preview") {
            val requested = adaJson.decodeFromString<SchedulePreviewDto>(op.body).definition
            val returned = requireNotNull(receipt.definition)
            require(returned.copy(expires_at = requested.expires_at) == requested && java.time.OffsetDateTime.parse(returned.expires_at).toInstant() == java.time.OffsetDateTime.parse(requested.expires_at).toInstant())
            val pin = requested.source
            val original = receipt.source
            if (pin == null) require(original == null)
            else require(original != null && original.source_version_id == pin.source_version_id && original.scope_id == op.scopeId && original.span_start == pin.span_start && original.span_end == pin.span_end && original.trust_class == "user_explicit" && original.content_hash.matches(Regex("[a-f0-9]{64}")) && original.quote.codePointCount(0, original.quote.length) == pin.span_end - pin.span_start)
            require(receipt.occurrences?.size in 1..100 && receipt.preview_expires_at != null && receipt.timezone_data != null)
            if (current(epoch) && state.value.scopeId != op.scopeId) {
                update { it.copy(receipts = it.receipts + (op.operationId to receipt), busy = false, notice = "A saved preview is ready. Use Review saved preview to open its original scope.") }
                return // Keep its exact encrypted intent until explicit scope review.
            }
            if (current(epoch) && state.value.scopeId == op.scopeId) update { it.copy(preview = receipt, previewSchedule = op.scheduleId, previewGeneration = op.expectedGeneration) }
        }
        if (!current(epoch)) return
        update { it.copy(receipts = (it.receipts + (op.operationId to receipt)).entries.toList().takeLast(32).associate { entry -> entry.toPair() }, busy = false) }
        store.removeScheduleOperation(owner, op.operationId)
        if (!current(epoch)) return
        pending(owner, epoch)
        load(c, epoch)
    }
    private suspend fun submit(c: ConnectionCredential, owner: SessionIdentity, op: SchedulePending, epoch: Long) {
        val result = api.scheduleWrite(c, op)
        if (!current(epoch)) return
        if (result is ApiResult.Success) acknowledge(c, owner, op, result.value, epoch)
        else {
            accept(result, epoch)
            if (current(epoch) && result is ApiResult.Failure && result.reason in setOf(ApiFailure.Validation, ApiFailure.Conflict, ApiFailure.TooLarge)) {
                // A definitive rejection has no committed write; still consult the exact receipt first.
                val saved = api.scheduleReceipt(c, op.operationId)
                if (saved is ApiResult.Success) acknowledge(c, owner, op, saved.value, epoch)
                else if (current(epoch) && saved is ApiResult.Failure && saved.reason == ApiFailure.NotFound) {
                    store.removeScheduleOperation(owner, op.operationId); pending(owner, epoch); load(c, epoch)
                }
            }
        }
    }
    private suspend fun check(c: ConnectionCredential, owner: SessionIdentity, op: SchedulePending, epoch: Long) {
        val result = api.scheduleReceipt(c, op.operationId)
        if (!current(epoch)) return
        if (result is ApiResult.Success) acknowledge(c, owner, op, result.value, epoch)
        else if (result is ApiResult.Failure && result.reason == ApiFailure.NotFound) update { it.copy(busy = false, notice = "No saved result yet. An explicit retry will reuse the original operation.") }
        else accept(result, epoch)
    }
    fun check(op: SchedulePending) { if (op in state.value.pending) work { c, owner, epoch -> check(c, owner, op, epoch) } }
    fun reviewPreview(op: SchedulePending) { if (op.kind == "preview" && op in state.value.pending && op.scopeId != null) { activate(op.scopeId); check(op) } }
    fun retry(op: SchedulePending) { if (op in state.value.pending && (System.currentTimeMillis() >= cooldown || op.turnsSchedulingOff())) work { c, owner, epoch -> submit(c, owner, op, epoch) } }
    fun setEnabled(enabled: Boolean) {
        val policy = state.value.policy ?: return
        val body = SchedulePolicyWriteDto(UUID.randomUUID(), policy.revision, enabled)
        queue(SchedulePending(body.operation_id, "policy", adaJson.encodeToString(body)))
    }
    fun preview(definition: ScheduleDefinitionDto, editing: ScheduleDto? = null) {
        val selected = state.value.scopeId ?: return
        val body = SchedulePreviewDto(UUID.randomUUID(), definition)
        queue(SchedulePending(body.operation_id, "preview", adaJson.encodeToString(body), scopeId = selected,
            scheduleId = editing?.id, expectedGeneration = editing?.generation ?: 0))
    }
    fun confirm() {
        val preview = state.value.preview ?: return
        val policy = state.value.policy ?: return
        if (!policy.enabled) return
        if ((preview.preview_expires_at ?: 0) <= System.currentTimeMillis()) { update { it.copy(notice = "This preview expired. Review its saved text and create a fresh preview before confirming.") }; return }
        val body = ScheduleConfirmDto(UUID.randomUUID(), preview.operation_id, state.value.previewGeneration, policy.revision)
        val key = state.value.previewSchedule ?: UUID.randomUUID()
        queue(SchedulePending(body.operation_id, "confirm", adaJson.encodeToString(body), scopeId = state.value.scopeId, scheduleId = key))
        clearPreview()
    }
    fun action(row: ScheduleDto, action: String) {
        val body = ScheduleActionDto(UUID.randomUUID(), row.generation, action, if (action == "snooze") Instant.ofEpochMilli(System.currentTimeMillis() + 3600000L).toString() else null)
        queue(SchedulePending(body.operation_id, "action", adaJson.encodeToString(body), scopeId = row.scope_id, scheduleId = row.id))
    }
    fun inboxAction(row: ScheduleInboxDto, action: String) {
        val body = ScheduleInboxActionDto(UUID.randomUUID(), action, if (action == "snooze") Instant.ofEpochMilli(System.currentTimeMillis() + 3600000L).toString() else null)
        queue(SchedulePending(body.operation_id, "inbox_action", adaJson.encodeToString(body), scopeId = row.scope_id, itemId = row.id))
    }
    fun open(row: ScheduleInboxDto, profile: UUID) {
        val body = ScheduleOpenDto(UUID.randomUUID(), row.opened_conversation_id ?: UUID.randomUUID(), profile)
        queue(SchedulePending(body.operation_id, "open", adaJson.encodeToString(body), scopeId = row.scope_id, itemId = row.id))
    }
    fun inboxPage(next: Boolean) {
        if (state.value.busy || (next && state.value.inbox.size < 100)) return
        val offset = (state.value.inboxOffset + if (next) 100 else -100).coerceIn(0, 900)
        if (offset == state.value.inboxOffset) return
        selection++; update { it.copy(inboxOffset = offset, inbox = emptyList()) }; refresh()
    }
    fun inspect(row: ScheduleDto, offset: Int = 0) { update { it.copy(inspectedSchedule = row.id, occurrenceOffset = offset, occurrences = emptyList()) }; work { c, _, epoch ->
        val rows = accept(api.scheduleOccurrences(c, row.id, offset), epoch) ?: return@work
        require(rows.size <= 100 && rows.all { it.schedule_id == row.id })
        if (current(epoch) && state.value.scopeId == row.scope_id && state.value.inspectedSchedule == row.id && state.value.occurrenceOffset == offset) update { it.copy(occurrences = rows) }
    } }
    fun occurrencePage(next: Boolean) {
        val row = state.value.schedules.firstOrNull { it.id == state.value.inspectedSchedule } ?: return
        inspect(row, (state.value.occurrenceOffset + if (next) 100 else -100).coerceIn(0, 900))
    }
}
