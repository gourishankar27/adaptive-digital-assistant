package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.security.MessageDigest
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.encodeToString

data class ResearchState(val enabled: Boolean = false, val searchEnabled: Boolean = false, val busy: Boolean = false, val cancelling: Boolean = false,
    val question: String = "", val target: String = "", val kind: String = "fetch",
    val journal: ResearchJournal? = null, val run: ResearchRunDto? = null, val source: WebSnapshotDto? = null,
    val notice: String? = null) {
    override fun toString() = "ResearchState(redacted)"
}

class ResearchController(private val api: AdaApi, private val store: SessionStore,
    private val scope: CoroutineScope, private val unauthorized: () -> Unit) {
    private val mutable = MutableStateFlow(ResearchState())
    val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private var delivery = 0L
    private var cooldown = 0L
    private val jobs = mutableSetOf<Job>()
    private fun update(block: (ResearchState) -> ResearchState) { mutable.value = block(mutable.value) }
    fun reset() {
        generation++; jobs.toList().forEach { it.cancel() }; jobs.clear()
        connection = null; identity = null; cooldown = 0; mutable.value = ResearchState()
    }
    private fun current(epoch: Long) = epoch == generation && identity != null
    private fun work(block: suspend (ConnectionCredential, Long) -> Unit) {
        val conn = connection ?: return
        val epoch = generation
        scope.launch(start = CoroutineStart.UNDISPATCHED) {
            try { if (current(epoch)) block(conn, epoch) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(epoch)) update { it.copy(busy = false, notice = "Research could not be confirmed. Check the saved run; nothing is resubmitted automatically.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accepted(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        if (result is ApiResult.Success) return result.value
        val fault = (result as ApiResult.Failure).reason
        if (fault == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (fault is ApiFailure.Busy) cooldown = System.currentTimeMillis() + (fault.retryAfterSeconds ?: 3).coerceIn(0, 300) * 1000L
        update { it.copy(busy = false, notice = "The operation is unconfirmed or blocked. Check the saved run. Expired or changed requests require a new preview.") }
        return null
    }
    private fun validate(run: ResearchRunDto, journal: ResearchJournal) {
        require(run.version == "ada-web-research-v1" && run.id == journal.runId && run.scope_id == journal.scopeId && run.conversation_id == journal.conversationId)
        require(run.calls.size <= 3 && run.calls.map { it.preview.id }.distinct().size == run.calls.size && run.remaining_calls == 3 - run.calls.size)
        run.calls.forEach { call ->
            val preview = call.preview
            require(preview.kind in setOf("fetch", "search") && preview.method == "GET" && !preview.external_writes && preview.automatic_redirects == 0)
            require(preview.preview_hash.matches(Regex("[a-f0-9]{64}")) && preview.max_bytes in 1..1048576 && preview.deadline_seconds in 1..15)
            require(preview.recipient in setOf("docs.python.org", "en.wikipedia.org") && preview.url.startsWith("https://${preview.recipient}/"))
            require(preview.headers.keys == setOf("User-Agent", "Accept-Encoding", "Accept"))
            call.receipt?.let { require(it.call_id == preview.id) }
        }
        run.citations.forEach { card ->
            require(card.version == "ada-web-citation-v1" && card.label.matches(Regex("W[1-3]")))
            require(card.source_origin == "public_web" && card.trust_class == "untrusted_web" && card.parser_version == "ada-static-text-v1")
            require(card.evidence.content_hash.matches(Regex("[a-f0-9]{64}")) && card.evidence.span_start >= 0 && card.evidence.span_end > card.evidence.span_start)
            require(run.calls.any { it.receipt?.id == card.receipt_id && it.receipt.citation == card })
        }
    }
    fun setVerifiedSession(conn: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = conn; identity = owner
        update { it.copy(enabled = caps.web_research == "ada-web-research-v1", searchEnabled = caps.web_search == "wikimedia-rest-v1") }
        work { c, epoch ->
            val saved = store.researchJournal(owner)
            if (!current(epoch)) return@work
            update { it.copy(journal = saved, notice = if (saved != null) "Saved research restored. Recovery checks the original run without submitting an operation." else null) }
            if (saved != null) load(c, saved, epoch)
        }
    }
    fun edit(question: String, target: String, kind: String) {
        if (state.value.journal == null && !state.value.busy && kind in setOf("fetch", "search") && (kind != "search" || state.value.searchEnabled)) update { it.copy(question = question, target = target, kind = kind) }
    }
    fun start(conversation: ConversationDto) {
        val owner = identity ?: return
        val s = state.value
        if (!s.enabled || s.busy || s.journal != null || System.currentTimeMillis() < cooldown) return
        val id = UUID.randomUUID()
        val journal = try { ResearchJournal(owner, conversation.scope_id, conversation.id, id,
            adaJson.encodeToString(ResearchCreateDto(id, s.question, s.kind, s.target))).also(::validateResearchJournal) }
        catch (_: Exception) { update { it.copy(notice = "Enter a public question and the exact URL or search query.") }; return }
        update { it.copy(busy = true) }
        work { c, epoch -> store.saveResearchJournal(journal); if (!current(epoch)) return@work
            update { it.copy(journal = journal) }; create(c, journal, epoch) }
    }
    private suspend fun create(c: ConnectionCredential, p: ResearchJournal, epoch: Long) {
        val sequence = ++delivery
        val result = accepted(api.createResearch(c, p.conversationId, p.createBody), epoch) ?: return
        validate(result, p); if (current(epoch) && sequence == delivery) update { it.copy(run = result, busy = false, notice = null) }
    }
    private suspend fun load(c: ConnectionCredential, p: ResearchJournal, epoch: Long) {
        val sequence = delivery
        val result = accepted(api.researchRun(c, p.runId), epoch) ?: return
        validate(result, p)
        if (!current(epoch) || sequence != delivery) return
        val clear = if (p.cancelRequested && result.state in setOf("cancelled", "completed")) p.copy(operation = null) else p
        if (clear != p) store.saveResearchJournal(clear)
        if (current(epoch)) update { it.copy(run = result, journal = clear, busy = false, source = null) }
    }
    fun refresh() {
        val p = state.value.journal ?: return
        if (state.value.busy) return
        update { it.copy(busy = true) }; work { c, epoch -> load(c, p, epoch) }
    }
    fun retry() {
        val p = state.value.journal ?: return
        if (p.cancelRequested) { cancel(); return }
        if (state.value.busy || System.currentTimeMillis() < cooldown) return
        update { it.copy(busy = true) }
        work { c, epoch -> if (p.operation == null) create(c, p, epoch) else submit(c, p, epoch) }
    }
    private fun operation(kind: String, body: String) {
        val p = state.value.journal ?: return
        if (state.value.busy || p.operation != null || p.cancelRequested || System.currentTimeMillis() < cooldown) return
        val next = p.copy(operation = ResearchOperation(kind, body))
        validateResearchJournal(next); update { it.copy(busy = true) }
        work { c, epoch -> store.saveResearchJournal(next); if (!current(epoch)) return@work
            update { it.copy(journal = next) }; submit(c, next, epoch) }
    }
    private suspend fun submit(c: ConnectionCredential, p: ResearchJournal, epoch: Long) {
        val op = p.operation ?: return
        val sequence = ++delivery
        var updated: ResearchRunDto? = null
        if (op.kind == "save-note") {
            val saved = accepted(api.saveResearchNote(c, p.runId, op.body), epoch) ?: return
            val body = adaJson.decodeFromString<ResearchNoteDto>(op.body)
            require(saved.id == body.upload_id && saved.source_id == body.source_id && saved.scope_id == p.scopeId && saved.trust_class == "imported_untrusted")
        } else {
            updated = accepted(api.researchOperation(c, p.runId, op), epoch) ?: return
            validate(updated, p)
        }
        if (!current(epoch) || sequence != delivery) return
        val clear = (state.value.journal ?: p).copy(operation = null)
        store.saveResearchJournal(clear)
        if (current(epoch)) update { it.copy(journal = clear, run = updated ?: it.run, busy = false, notice = if (op.kind == "save-note") "Saved as an imported, untrusted research note. No personal factual claim was created." else null) }
    }
    fun approve() {
        val call = state.value.run?.calls?.lastOrNull()?.takeIf { it.status == "pending_approval" } ?: return
        if (call.preview.expires_at <= System.currentTimeMillis()) { update { it.copy(notice = "The preview expired. Cancel and create a new preview.") }; return }
        operation("approve", adaJson.encodeToString(ResearchApprovalDto(UUID.randomUUID(), call.preview.id, call.preview.preview_hash)))
    }
    fun cancel() {
        val p = state.value.journal ?: return
        if (state.value.cancelling || state.value.run == null) return
        val sequence = ++delivery
        val next = p.copy(cancelRequested = true)
        update { it.copy(cancelling = true) }
        work { c, epoch ->
            try {
                store.saveResearchJournal(next)
                if (!current(epoch)) return@work
                update { it.copy(journal = next) }
                val result = accepted(api.researchOperation(c, p.runId, ResearchOperation("cancel", "{}")), epoch) ?: return@work
                validate(result, next)
                require(result.state == "cancelled")
                if (!current(epoch) || sequence != delivery) return@work
                val clear = next.copy(operation = null)
                store.saveResearchJournal(clear)
                if (current(epoch)) update { it.copy(run = result, journal = clear, busy = false, source = null) }
            } finally { if (current(epoch)) update { it.copy(cancelling = false) } }
        }
    }
    fun answer() = operation("answer", "{}")
    fun next(url: String) = operation("calls", adaJson.encodeToString(ResearchActionDto(UUID.randomUUID(), "fetch", url)))
    fun saveNote() = operation("save-note", adaJson.encodeToString(ResearchNoteDto(UUID.randomUUID(), UUID.randomUUID())))
    fun close() {
        val p = state.value.journal ?: return
        if (state.value.busy || p.operation != null || state.value.run?.state !in setOf("completed", "cancelled")) return
        work { _, epoch -> store.removeResearchJournal(p.identity, p.runId)
            if (current(epoch)) update { it.copy(journal = null, run = null, source = null, notice = "Local view closed. This did not delete or cancel server research.") } }
    }
    fun source(card: WebCitationDto) {
        val p = state.value.journal ?: return
        if (state.value.busy) return
        update { it.copy(busy = true, source = null) }
        work { c, epoch ->
            val snapshot = accepted(api.researchSource(c, p.runId, card.receipt_id), epoch) ?: return@work
            require(snapshot.citation == card)
            val hash = MessageDigest.getInstance("SHA-256").digest(snapshot.text.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
            val ev = card.evidence
            require(hash == ev.content_hash && snapshot.text.substring(snapshot.text.offsetByCodePoints(0, ev.span_start), snapshot.text.offsetByCodePoints(0, ev.span_end)) == ev.quote)
            if (current(epoch)) update { it.copy(source = snapshot, busy = false) }
        }
    }
}
