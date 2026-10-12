package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString

data class ExpressionSettingsState(val enabled: Boolean = false, val targetKind: String = "account",
    val targetId: UUID? = null, val preference: PreferenceDto? = null, val draft: PreferenceValuesDto = PreferenceValuesDto(),
    val expression: ExpressionDto? = null, val dynamic: Boolean = false, val busy: Boolean = false,
    val journal: ExpressionJournal? = null, val fault: ApiFailure? = null, val notice: String? = null) {
    override fun toString() = "ExpressionSettingsState(redacted)"
}

/** Explicit encrypted updates; restore reads an exact receipt and never resubmits. */
class ExpressionController(private val api: AdaApi, private val store: SessionStore,
    private val scope: CoroutineScope, private val unauthorized: () -> Unit,
    private val now: () -> Long = System::currentTimeMillis) {
    private val mutable = MutableStateFlow(ExpressionSettingsState()); val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null; private var identity: SessionIdentity? = null
    private var conversationId: UUID? = null; private var epoch = 0L; private var selection = 0L
    private var cooldown = 0L; private val jobs = mutableSetOf<Job>()
    private fun update(f: (ExpressionSettingsState) -> ExpressionSettingsState) { mutable.value = f(state.value) }
    fun reset() { epoch++; selection++; jobs.toList().forEach { it.cancel() }; jobs.clear(); connection = null; identity = null; conversationId = null; cooldown = 0; mutable.value = ExpressionSettingsState() }
    private fun current(e: Long, s: Long) = e == epoch && s == selection && identity != null
    private fun work(block: suspend (ConnectionCredential, Long, Long) -> Unit) {
        val c = connection ?: return; val e = epoch; val s = selection
        scope.launch {
            try { block(c, e, s) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(e, s)) update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract, notice = "The change is unconfirmed. Check its saved receipt before retrying.") } }
        }.also { j -> jobs += j; j.invokeOnCompletion { jobs -= j } }
    }
    private fun <T> value(result: ApiResult<T>, e: Long, s: Long): T? {
        if (e != epoch) return null
        if (result is ApiResult.Failure && result.reason == ApiFailure.Unauthorized) { unauthorized(); return null }
        if (!current(e, s)) return null
        return when (result) {
            is ApiResult.Success -> result.value
            is ApiResult.Failure -> {
                if (result.reason is ApiFailure.Busy) cooldown = now() + (result.reason.retryAfterSeconds ?: 3).coerceIn(1, 120) * 1000
                update { it.copy(busy = false, fault = result.reason, notice = when (result.code) {
                    "conversation_busy" -> "Wait for the current reply before changing its expression."
                    "preference_revision_changed" -> "Settings changed elsewhere. Discard this local reservation and refresh before reviewing a new change."
                    "expression_requires_prompt_upgrade" -> "Explicitly upgrade this conversation's saved prompt first."
                    else -> "The outcome is unconfirmed. Check the receipt or retry the identical change."
                }) }; null
            }
        }
    }
    fun setVerifiedSession(c: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = c; identity = owner
        update { it.copy(enabled = caps.interaction_preferences == "explicit_settings_v1" && caps.session_expression == "ada-expression-v1", targetId = owner.owner) }
        if (!state.value.enabled) return
        update { it.copy(busy = true) }
        work { conn, e, s ->
            val saved = store.expressionJournal(owner)
            if (!current(e, s)) return@work
            if (saved != null) { validateExpressionJournal(saved); require(saved.identity == owner)
                update { it.copy(journal = saved, targetKind = saved.targetKind, targetId = saved.targetId) }
                check(conn, saved, e, s)
            } else load(conn, e, s)
        }
    }
    fun activateConversation(id: UUID?) {
        if (!state.value.enabled || id == conversationId || state.value.journal != null) return
        conversationId = id
        selection++; update { it.copy(expression = null, preference = null, draft = PreferenceValuesDto(), targetKind = if (id != null) "conversation" else "account", targetId = id ?: identity?.owner, busy = true) }
        work { c, e, s -> load(c, e, s) }
    }
    fun select(kind: String) {
        if (state.value.busy || state.value.journal != null || kind !in setOf("account", "profile", "scope", "conversation")) return
        val target = when (kind) { "account" -> identity?.owner; "conversation" -> conversationId; "profile" -> state.value.expression?.profile_id; else -> state.value.expression?.scope_id } ?: return
        selection++; update { it.copy(targetKind = kind, targetId = target, preference = null, draft = PreferenceValuesDto(), busy = true, fault = null, notice = null) }
        work { c, e, s -> load(c, e, s) }
    }
    private suspend fun load(c: ConnectionCredential, e: Long, s: Long) {
        conversationId?.let { id ->
            val expression = value(api.expression(c, id), e, s) ?: return
            validateExpression(expression); require(expression.conversation_id == id)
            if (current(e, s)) update { it.copy(expression = expression, dynamic = expression.dynamic_enabled) }
        }
        val before = state.value; val target = before.targetId ?: return
        val p = value(api.preference(c, before.targetKind, target), e, s) ?: return
        require(p.target_kind == before.targetKind && p.target_id == target && p.revision >= 0); validatePreferences(p.values)
        if (current(e, s)) update { it.copy(preference = p, draft = p.values, busy = false, fault = null) }
    }
    fun refresh() { if (state.value.enabled && !state.value.busy && state.value.journal == null && now() >= cooldown) { update { it.copy(busy = true) }; work { c, e, s -> load(c, e, s) } } }
    fun edit(values: PreferenceValuesDto) { if (!state.value.busy && state.value.journal == null) { validatePreferences(values); update { it.copy(draft = values) } } }
    fun dynamic(enabled: Boolean) { if (!state.value.busy && state.value.journal == null && state.value.targetKind == "conversation") update { it.copy(dynamic = enabled) } }
    fun save(reset: Boolean = false) {
        val owner = identity ?: return; val s = state.value; val pref = s.preference ?: return
        if (s.busy || s.journal != null || now() < cooldown) return
        val key = UUID.randomUUID()
        val input = PreferenceWriteDto(key, pref.revision, if (reset) PreferenceValuesDto() else s.draft, if (s.targetKind == "conversation") s.dynamic else null)
        reserve(ExpressionJournal(owner, key, "preferences", s.targetKind, pref.target_id, adaJson.encodeToString(input)))
    }
    fun resetSession() {
        val owner = identity ?: return; val x = state.value.expression ?: return; val session = x.session_id ?: return
        if (state.value.busy || state.value.journal != null || now() < cooldown) return
        val key = UUID.randomUUID()
        reserve(ExpressionJournal(owner, key, "reset", "conversation", x.conversation_id, adaJson.encodeToString(ExpressionResetDto(key, session))))
    }
    fun signal(dimension: String) {
        val owner = identity ?: return; val x = state.value.expression ?: return
        val session = x.session_id ?: return; val source = x.last_request_id ?: return
        if (!x.dynamic_enabled || x.expired || dimension !in setOf("warmth", "focus") || state.value.busy || state.value.journal != null || now() < cooldown) return
        val key = UUID.randomUUID(); val desired = if (dimension == "warmth") x.vector.warmth + 10 else x.vector.focus + 10
        reserve(ExpressionJournal(owner, key, "signal", "conversation", x.conversation_id, adaJson.encodeToString(ExpressionSignalDto(key, session, source, vector = mapOf(dimension to desired)))))
    }
    private fun reserve(journal: ExpressionJournal) {
        update { it.copy(busy = true, fault = null, notice = null) }
        work { c, e, s ->
            store.saveExpressionJournal(journal)
            if (!current(e, s)) return@work
            update { it.copy(journal = journal) }; submit(c, journal, e, s)
        }
    }
    private suspend fun finish(receipt: ExpressionReceiptDto, journal: ExpressionJournal, c: ConnectionCredential, e: Long, s: Long) {
        require(receipt.operation_id == journal.operationId && receipt.action == journal.action && receipt.target_kind == journal.targetKind && receipt.target_id == journal.targetId)
        receipt.expression?.let { validateExpression(it); require(it.conversation_id == journal.targetId) }
        receipt.preference?.let { require(it.target_kind == journal.targetKind && it.target_id == journal.targetId); validatePreferences(it.values) }
        if (journal.action == "preferences") { val input = adaJson.decodeFromString<PreferenceWriteDto>(journal.body); val pref = requireNotNull(receipt.preference); require(pref.revision == input.expected_revision + 1 && pref.values == input.values && pref.receipt_id == journal.operationId) }
        else {
            val expression = requireNotNull(receipt.expression)
            if (journal.action == "reset") { val input = adaJson.decodeFromString<ExpressionResetDto>(journal.body); require(receipt.reason == "user_reset" && expression.session_id != input.session_id) }
            else { val input = adaJson.decodeFromString<ExpressionSignalDto>(journal.body); require(receipt.reason == input.reason && receipt.source_request_id == input.source_request_id && expression.session_id == input.session_id) }
        }
        store.removeExpressionJournal(journal.identity, journal.operationId)
        if (!current(e, s)) return
        update { it.copy(journal = null, busy = true, notice = "Confirmed. Preferences apply to future replies; existing request snapshots stay saved.") }
        load(c, e, s)
    }
    private suspend fun submit(c: ConnectionCredential, j: ExpressionJournal, e: Long, s: Long) { value(api.expressionOperation(c, j), e, s)?.let { finish(it, j, c, e, s) } }
    private suspend fun check(c: ConnectionCredential, j: ExpressionJournal, e: Long, s: Long) { value(api.expressionReceipt(c, j.operationId), e, s)?.let { finish(it, j, c, e, s) } }
    fun checkPending() { val j = state.value.journal ?: return; if (state.value.busy || now() < cooldown) return; update { it.copy(busy = true) }; work { c, e, s -> check(c, j, e, s) } }
    fun retry() { val j = state.value.journal ?: return; if (state.value.busy || now() < cooldown) return; update { it.copy(busy = true) }; work { c, e, s -> submit(c, j, e, s) } }
    fun discard() {
        val j = state.value.journal ?: return; if (state.value.busy) return
        update { it.copy(busy = true) }
        work { c, e, s -> store.removeExpressionJournal(j.identity, j.operationId); if (current(e, s)) { update { it.copy(journal = null, notice = "Local reservation discarded. Server settings were not undone.") }; load(c, e, s) } }
    }
}
