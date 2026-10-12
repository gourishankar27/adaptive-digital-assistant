package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.encodeToString

data class LearningSettingsState(val enabled: Boolean = false, val scopeId: UUID? = null,
    val data: LearningStateDto? = null, val busy: Boolean = false, val journal: LearningJournal? = null,
    val source: SourceVersionDto? = null, val fault: ApiFailure? = null, val notice: String? = null) {
    override fun toString() = "LearningSettingsState(redacted)"
}

/** One exact encrypted operation; restart reads receipts, never submits. */
class LearningController(private val api: AdaApi, private val store: SessionStore,
    private val scope: CoroutineScope, private val unauthorized: () -> Unit,
    private val now: () -> Long = System::currentTimeMillis) {
    private val mutable = MutableStateFlow(LearningSettingsState()); val state = mutable.asStateFlow()
    private var credential: ConnectionCredential? = null; private var identity: SessionIdentity? = null
    private var epoch = 0L; private var selection = 0L; private var cooldown = 0L
    private var restoring = false
    private val jobs = mutableSetOf<Job>()
    fun reset() { epoch++; selection++; jobs.toList().forEach { it.cancel() }; jobs.clear(); credential = null; identity = null; cooldown = 0; restoring = false; mutable.value = LearningSettingsState() }
    private fun update(f: (LearningSettingsState) -> LearningSettingsState) { mutable.value = f(state.value) }
    private fun current(e: Long, s: Long) = epoch == e && selection == s && identity != null
    private fun work(block: suspend (ConnectionCredential, Long, Long) -> Unit) {
        val c = credential ?: return; val e = epoch; val s = selection
        scope.launch {
            try { block(c, e, s) } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(e, s)) update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract, notice = "The change is unconfirmed. Check its saved receipt before retrying.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> value(r: ApiResult<T>, e: Long, s: Long): T? {
        if (e != epoch) return null
        if (r is ApiResult.Failure && r.reason == ApiFailure.Unauthorized) { unauthorized(); return null }
        if (!current(e, s)) return null
        return when(r) {
            is ApiResult.Success -> r.value
            is ApiResult.Failure -> { if (r.reason is ApiFailure.Busy) cooldown = now() + (r.reason.retryAfterSeconds ?: 3).coerceIn(1, 120) * 1000
                update { it.copy(busy = false, fault = r.reason, notice = when(r.code) {
                    "learning_proposal_changed", "learning_revision_changed" -> "The preview is stale. Check the saved receipt, then discard the local reservation and refresh before reviewing again."
                    "learning_insufficient_independent_evidence" -> "More independent interactions are required. A threshold is a review gate, not proof."
                    else -> "The change is unconfirmed. Check its receipt or retry identical input."
                }) }; null }
        }
    }
    fun setVerifiedSession(c: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); credential = c; identity = owner; update { it.copy(enabled = caps.interaction_learning == "ada-learning-v1") }
        if (!state.value.enabled) return
        restoring = true
        update { it.copy(busy = true) }
        work { conn, e, s ->
            val saved = store.learningJournal(owner)
            if (!current(e, s)) return@work
            restoring = false
            if (saved != null) { validateLearningJournal(saved); require(saved.identity == owner)
                update { it.copy(journal = saved, scopeId = saved.scopeId) }; check(conn, saved, e, s)
            } else update { it.copy(busy = false) }
        }
    }
    fun activate(scopeId: UUID?) {
        if (!state.value.enabled || scopeId == state.value.scopeId || state.value.journal != null || restoring) return
        selection++; update { it.copy(scopeId = scopeId, data = null, source = null, fault = null, busy = scopeId != null) }
        if (scopeId != null) work { c, e, s -> load(c, scopeId, e, s) }
    }
    private suspend fun load(c: ConnectionCredential, id: UUID, e: Long, s: Long) {
        val data = value(api.learning(c, id), e, s) ?: return
        validateLearningState(data, requireNotNull(identity), id)
        if (current(e, s)) update { it.copy(data = data, busy = false, fault = null) }
    }
    fun refresh() { val id = state.value.scopeId ?: return; if (state.value.busy || state.value.journal != null || now() < cooldown) return
        update { it.copy(busy = true, source = null) }; work { c, e, s -> load(c, id, e, s) } }
    fun chooseSource(event: EventDto) {
        val id = state.value.scopeId ?: return
        if (state.value.busy || state.value.journal != null || event.role != "user" || event.request_status != "completed" || state.value.data?.config?.status != "enrolled") return
        update { it.copy(busy = true) }
        work { c, e, s ->
            val source = value(api.source(c, event.source_version_id), e, s) ?: return@work
            require(source.id == event.source_version_id && source.scope_id == id && source.trust_class == "user_explicit" && source.content == event.content)
            exactEvidenceSelection(source, id, 0, source.content.length)
            if (current(e, s)) update { it.copy(source = source, busy = false) }
        }
    }
    private fun ready() = state.value.enabled && !state.value.busy && state.value.journal == null && now() >= cooldown
    fun configure(status: String, continuity: Boolean = false) {
        val owner = identity ?: return; val config = state.value.data?.config ?: return; if (!ready()) return
        val key = UUID.randomUUID(); reserve(LearningJournal(owner, config.scope_id, key, "config", adaJson.encodeToString(LearningConfigWriteDto(key, config.revision, status, continuity))))
    }
    fun resetLearned() {
        val owner = identity ?: return; val config = state.value.data?.config ?: return; if (!ready()) return
        val key = UUID.randomUUID(); reserve(LearningJournal(owner, config.scope_id, key, "reset", adaJson.encodeToString(LearningResetWriteDto(key, config.revision))))
    }
    fun observe(values: PreferenceValuesDto, confidence: String) {
        val owner = identity ?: return; val source = state.value.source ?: return; val id = state.value.scopeId ?: return; if (!ready()) return
        val key = UUID.randomUUID(); val pin = SourcePinDto(source.id, source.version, source.content_hash, 0, source.content.codePointCount(0, source.content.length))
        reserve(LearningJournal(owner, id, key, "observe", adaJson.encodeToString(LearningObservationWriteDto(key, pin, values, confidence))))
    }
    fun review(proposal: InteractionProposalDto, decision: String, accountWide: Boolean, values: PreferenceValuesDto? = null) {
        val owner = identity ?: return; val id = state.value.scopeId ?: return; if (!ready() || proposal.status != "pending" || (decision == "approve" && !proposal.eligible)) return
        val key = UUID.randomUUID(); reserve(LearningJournal(owner, id, key, "review", adaJson.encodeToString(LearningReviewWriteDto(key, proposal.id, proposal.revision, decision, accountWide, values = values))))
    }
    private fun reserve(j: LearningJournal) {
        validateLearningJournal(j); update { it.copy(busy = true, fault = null, notice = null) }
        work { c, e, s -> store.saveLearningJournal(j); if (!current(e, s)) return@work
            update { it.copy(journal = j) }; submit(c, j, e, s) }
    }
    private suspend fun finish(c: ConnectionCredential, j: LearningJournal, r: LearningReceiptDto, e: Long, s: Long) {
        require(r.operation_id == j.operationId && r.scope_id == j.scopeId && r.action == j.action && r.revision > 0 && r.epoch >= 0)
        when(j.action) {
            "review" -> { val b = adaJson.decodeFromString<LearningReviewWriteDto>(j.body); require(r.proposal_id == b.proposal_id && r.decision == b.decision && r.proposal_revision == b.expected_revision) }
            "observe" -> require(r.observation_id != null && r.proposal_id != null)
            "config" -> require(r.revision == adaJson.decodeFromString<LearningConfigWriteDto>(j.body).expected_revision + 1)
            "reset" -> require(r.revision == adaJson.decodeFromString<LearningResetWriteDto>(j.body).expected_revision + 1)
        }
        store.removeLearningJournal(j.identity, j.operationId)
        if (!current(e, s)) return
        update { it.copy(journal = null, source = null, busy = true, notice = "Confirmed. Future replies use current consent. Historical request snapshots remain for replay.") }
        load(c, j.scopeId, e, s)
    }
    private suspend fun submit(c: ConnectionCredential, j: LearningJournal, e: Long, s: Long) { value(api.learningOperation(c, j), e, s)?.let { finish(c, j, it, e, s) } }
    private suspend fun check(c: ConnectionCredential, j: LearningJournal, e: Long, s: Long) { value(api.learningReceipt(c, j.operationId), e, s)?.let { finish(c, j, it, e, s) } }
    fun checkPending() { val j = state.value.journal ?: return; if (state.value.busy || now() < cooldown) return; update { it.copy(busy = true) }; work { c, e, s -> check(c, j, e, s) } }
    fun retry() { val j = state.value.journal ?: return; if (state.value.busy || now() < cooldown) return; update { it.copy(busy = true) }; work { c, e, s -> submit(c, j, e, s) } }
    fun discard() { val j = state.value.journal ?: return; if (state.value.busy) return; update { it.copy(busy = true) }
        work { c, e, s -> store.removeLearningJournal(j.identity, j.operationId); if (current(e, s)) { update { it.copy(journal = null, notice = "Local reservation discarded; server state is unchanged.") }; load(c, j.scopeId, e, s) } } }
}
