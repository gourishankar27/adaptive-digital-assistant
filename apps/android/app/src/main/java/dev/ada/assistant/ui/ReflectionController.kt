package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.encodeToString

data class ReflectionState(val supported: Boolean = false, val busy: Boolean = false, val policy: ReflectionPolicyDto? = null,
    val artifacts: List<ReflectionArtifactDto> = emptyList(), val runs: List<ReflectionRunDto> = emptyList(),
    val offset: Int = 0, val pending: List<ReflectionPending> = emptyList(), val notice: String? = null) {
    override fun toString() = "ReflectionState(redacted)"
}

/** Exact encrypted mutations; restoration only consults their original GET receipts. */
class ReflectionController(private val api: AdaApi, private val store: SessionStore, private val scope: CoroutineScope,
    private val unauthorized: () -> Unit) {
    private val mutable = MutableStateFlow(ReflectionState())
    val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private var sequence = 0L
    private var foreground = true
    private var cooldown = 0L
    private val jobs = mutableSetOf<Job>()
    private fun update(f: (ReflectionState) -> ReflectionState) { mutable.value = f(mutable.value) }
    private fun current(epoch: Long) = generation == epoch && identity != null
    fun reset() { generation++; sequence++; jobs.toList().forEach { it.cancel() }; jobs.clear(); connection = null; identity = null; cooldown = 0; mutable.value = ReflectionState() }
    fun observeForeground(visible: Boolean) { foreground = visible; sequence++; if (visible) refresh() else update { it.copy(busy = false) } }
    private fun work(block: suspend (ConnectionCredential, SessionIdentity, Long) -> Unit) {
        val c = connection ?: return; val owner = identity ?: return; val epoch = generation
        scope.launch(start = CoroutineStart.UNDISPATCHED) {
            try { if (current(epoch)) block(c, owner, epoch) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(epoch)) update { it.copy(busy = false, notice = "Result unconfirmed. Check the saved operation before retrying.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accept(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        if (result is ApiResult.Success) return result.value
        val error = (result as ApiResult.Failure).reason
        if (error == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (error is ApiFailure.Busy) cooldown = System.currentTimeMillis() + (error.retryAfterSeconds ?: 3).coerceIn(0, 300) * 1000L
        if (error is ApiFailure.Http && error.status == 429) cooldown = System.currentTimeMillis() + 60000
        update { it.copy(busy = false, notice = when (error) {
            ApiFailure.Validation -> "Check the selected scopes, source consent, timezone, hours and budgets."
            ApiFailure.Conflict -> "Consent, sources or revision changed. Refresh and review before making a new change."
            ApiFailure.TooLarge -> "The retained job or receipt limit is reached. Turning reflection off remains available."
            else -> "Reflection is unavailable or this change is unconfirmed. Saved operations have not been retried."
        }) }
        return null
    }
    fun setVerifiedSession(c: ConnectionCredential, who: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = c; identity = who; update { it.copy(supported = caps.reflection_protocol == "ada-reflection-v1") }
        if (!state.value.supported) return
        work { conn, owner, epoch ->
            val journal = store.reflectionJournal(owner)
            if (!current(epoch)) return@work
            update { it.copy(pending = journal?.operations.orEmpty()) }
            journal?.operations?.forEach { check(conn, owner, it, epoch) }
            load(conn, epoch)
        }
    }
    fun refresh() { if (foreground && state.value.supported && System.currentTimeMillis() >= cooldown) work { c, _, e -> load(c, e) } }
    private suspend fun load(c: ConnectionCredential, epoch: Long) {
        val page = state.value.offset; val read = ++sequence
        fun visible() = current(epoch) && foreground && sequence == read && page == state.value.offset
        update { it.copy(busy = true) }
        val p = api.reflectionPolicy(c); if (!visible()) return
        val policy = accept(p, epoch) ?: return
        require(policy.version == "ada-reflection-v1" && policy.revision >= 0)
        if (policy.revision < (state.value.policy?.revision ?: 0)) return
        update { it.copy(policy = policy) }
        val a = api.reflectionArtifacts(c, page); if (!visible()) return
        val artifacts = accept(a, epoch) ?: return
        require(artifacts.size <= 100 && artifacts.map { it.id }.distinct().size == artifacts.size && artifacts.all { it.version == "ada-reflection-v1" })
        val r = api.reflectionRuns(c, page); if (!visible()) return
        val runs = accept(r, epoch) ?: return
        require(runs.size <= 100)
        update { it.copy(artifacts = artifacts, runs = runs, busy = false) }
    }
    private suspend fun pending(owner: SessionIdentity, e: Long) { val rows = store.reflectionJournal(owner)?.operations.orEmpty(); if (current(e)) update { it.copy(pending = rows) } }
    private suspend fun acknowledge(c: ConnectionCredential, owner: SessionIdentity, op: ReflectionPending, r: ReflectionReceiptDto, e: Long) {
        require(r.version == "ada-reflection-v1" && r.operation_id == op.operationId && r.state == "completed")
        if (op.kind == "policy") require(r.action == "policy" && r.revision != null)
        else {
            val b = adaJson.decodeFromString<ReflectionActionDto>(op.body)
            require(r.action == b.action && r.artifact_id == op.artifactId)
            if (b.action == "open_question") require(r.conversation_id == b.conversation_id && r.question_id != null)
        }
        if (!current(e)) return
        store.removeReflectionOperation(owner, op.operationId)
        if (!current(e)) return
        pending(owner, e); load(c, e)
    }
    private suspend fun check(c: ConnectionCredential, owner: SessionIdentity, op: ReflectionPending, e: Long) {
        val r = api.reflectionReceipt(c, op.operationId); if (!current(e)) return
        if (r is ApiResult.Success) acknowledge(c, owner, op, r.value, e)
        else if (r is ApiResult.Failure && r.reason == ApiFailure.NotFound) update { it.copy(busy = false, notice = "No saved result yet. Retry only when ready; the original operation will be reused.") }
        else accept(r, e)
    }
    private suspend fun submit(c: ConnectionCredential, owner: SessionIdentity, op: ReflectionPending, e: Long) {
        val r = api.reflectionWrite(c, op); if (!current(e)) return
        if (r is ApiResult.Success) acknowledge(c, owner, op, r.value, e)
        else {
            accept(r, e)
            if (r is ApiResult.Failure && r.reason in setOf(ApiFailure.Validation, ApiFailure.Conflict, ApiFailure.TooLarge)) {
                val saved = api.reflectionReceipt(c, op.operationId); if (!current(e)) return
                if (saved is ApiResult.Success) acknowledge(c, owner, op, saved.value, e)
                else if (saved is ApiResult.Failure && saved.reason == ApiFailure.NotFound) { store.removeReflectionOperation(owner, op.operationId); pending(owner, e); load(c, e) }
            }
        }
    }
    private fun queue(op: ReflectionPending) {
        if (!state.value.supported || ((state.value.busy || System.currentTimeMillis() < cooldown) && !op.turnsReflectionOff())) return
        val who = identity ?: return; validateReflectionJournal(ReflectionJournal(who, listOf(op)))
        update { it.copy(busy = true, notice = null) }
        work { c, owner, e -> store.saveReflectionOperation(owner, op); if (current(e)) { pending(owner, e); submit(c, owner, op, e) } }
    }
    fun save(settings: ReflectionSettingsDto) { val p = state.value.policy ?: return; val b = ReflectionPolicyWriteDto(UUID.randomUUID(), p.revision, settings); queue(ReflectionPending(b.operation_id, "policy", adaJson.encodeToString(b))) }
    fun action(row: ReflectionArtifactDto, action: String, profile: UUID? = null) {
        val b = ReflectionActionDto(UUID.randomUUID(), action, if (action == "open_question") row.conversation_id ?: UUID.randomUUID() else null, if (action == "open_question") profile else null)
        queue(ReflectionPending(b.operation_id, "action", adaJson.encodeToString(b), row.id))
    }
    fun check(op: ReflectionPending) { if (op in state.value.pending) work { c, o, e -> check(c, o, op, e) } }
    fun retry(op: ReflectionPending) { if (op in state.value.pending && !state.value.busy && (System.currentTimeMillis() >= cooldown || op.turnsReflectionOff())) work { c, o, e -> submit(c, o, op, e) } }
    fun page(next: Boolean) { if (state.value.busy) return; val offset = (state.value.offset + if (next) 100 else -100).coerceIn(0, 900); if (offset == state.value.offset) return; sequence++; update { it.copy(offset = offset, artifacts = emptyList(), runs = emptyList()) }; refresh() }
}
