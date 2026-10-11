package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.security.MessageDigest
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString

data class EpisodeState(val enabled: Boolean = false, val canGenerate: Boolean = false,
    val scopeId: UUID? = null, val events: List<EventDto> = emptyList(), val selected: Set<UUID> = emptySet(),
    val preview: List<SourceVersionDto>? = null, val previewKind: String? = null,
    val journal: ConsolidationJournal? = null, val job: ConsolidationJobDto? = null,
    val jobs: List<ConsolidationJobDto> = emptyList(), val episodes: List<EpisodeDto> = emptyList(),
    val episode: EpisodeDto? = null, val original: SourceVersionDto? = null, val offset: Int = 0,
    val busy: Boolean = false, val fault: ApiFailure? = null, val notice: String? = null) {
    override fun toString() = "EpisodeState(redacted)"
}

/** Every job is an explicit exact encrypted submission; restart only reads. */
class EpisodeController(private val api: AdaApi, private val store: SessionStore,
    private val scope: CoroutineScope, private val unauthorized: () -> Unit,
    private val now: () -> Long = System::currentTimeMillis) {
    private val mutable = MutableStateFlow(EpisodeState()); val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null; private var identity: SessionIdentity? = null
    private var activeConversation: ConversationDto? = null
    private var epoch = 0L; private var selection = 0L; private var cooldown = 0L
    private val tasks = mutableSetOf<Job>()
    private fun update(f: (EpisodeState) -> EpisodeState) { mutable.value = f(state.value) }
    fun reset() { epoch++; selection++; tasks.toList().forEach { it.cancel() }; tasks.clear(); connection = null; identity = null; activeConversation = null; cooldown = 0; mutable.value = EpisodeState() }
    private fun current(e: Long, s: Long) = e == epoch && s == selection && identity != null
    private fun work(block: suspend (ConnectionCredential, Long, Long) -> Unit) {
        val conn = connection ?: return; val e = epoch; val s = selection
        scope.launch {
            try { block(conn, e, s) }
            catch (c: CancellationException) { throw c }
            catch (_: Exception) { if (current(e, s)) update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract, notice = "The outcome is unconfirmed. Check the saved submission before retrying.") } }
        }.also { j -> tasks += j; j.invokeOnCompletion { tasks -= j } }
    }
    private fun <T> accepted(result: ApiResult<T>, e: Long, s: Long): T? {
        if (e != epoch) return null
        if (result is ApiResult.Failure && result.reason == ApiFailure.Unauthorized) { unauthorized(); return null }
        if (!current(e, s)) return null
        return when (result) {
            is ApiResult.Success -> result.value
            is ApiResult.Failure -> {
                if (result.reason is ApiFailure.Busy) cooldown = now() + (result.reason.retryAfterSeconds ?: 3).coerceIn(1, 120) * 1000
                update { it.copy(busy = false, fault = result.reason, notice = "Refresh or check the original submission. A timeout does not prove failure.") }; null
            }
        }
    }
    fun setVerifiedSession(conn: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = conn; identity = owner
        update { it.copy(enabled = caps.hasEpisodes(), canGenerate = caps.hasEpisodes() && caps.consolidation_generation && caps.consolidation_worker, busy = true) }
        work { c, e, s ->
            val saved = store.consolidationJournal(owner)
            if (saved != null && current(e, s)) { validateConsolidationJournal(saved); require(saved.identity == owner)
                update { it.copy(journal = saved, scopeId = saved.scopeId) }; loadJob(c, saved, e, s)
                if (current(e, s) && state.value.fault == null) { update { it.copy(busy = true) }; loadLists(c, saved.scopeId, e, s) }
            } else if (current(e, s)) update { it.copy(busy = false) }
        }
    }
    fun activate(conversation: ConversationDto?) {
        if (!state.value.enabled || state.value.busy) return
        activeConversation = conversation
        selection++
        val active = state.value.journal?.scopeId ?: conversation?.scope_id ?: return
        update { it.copy(scopeId = active, events = emptyList(), selected = emptySet(), preview = null,
            previewKind = null, episodes = emptyList(), jobs = emptyList(), episode = null, original = null, offset = 0, fault = null, busy = true) }
        work { conn, e, s ->
            if (conversation?.scope_id == active && state.value.journal == null) {
                val events = accepted(api.events(conn, conversation.id, 50, 0), e, s) ?: return@work
                if (current(e, s)) update { it.copy(events = events.filter { row -> row.request_status == "completed" }) }
            }
            loadLists(conn, active, e, s)
        }
    }
    private suspend fun loadLists(conn: ConnectionCredential, id: UUID, e: Long, s: Long) {
        val rows = accepted(api.episodes(conn, id, state.value.offset), e, s) ?: return
        require(rows.size <= 25); rows.forEach { validateEpisode(it, id) }
        val jobs = accepted(api.consolidationJobs(conn, id, state.value.offset), e, s) ?: return
        require(jobs.size <= 25 && jobs.all { it.owner_id == identity?.owner && it.scope_id == id })
        if (current(e, s)) update { it.copy(episodes = rows, jobs = jobs, busy = false, fault = null) }
    }
    fun page(delta: Int) {
        val id = state.value.scopeId ?: return; if (state.value.busy) return
        selection++; update { it.copy(offset = (it.offset + delta * 25).coerceIn(0, 10000), busy = true, episode = null, original = null) }
        work { c, e, s -> loadLists(c, id, e, s) }
    }
    fun refresh() {
        val id = state.value.scopeId ?: return; if (state.value.busy || now() < cooldown) return
        update { it.copy(busy = true) }
        work { c, e, s -> state.value.journal?.let { loadJob(c, it, e, s); if (!current(e, s) || state.value.fault != null) return@work }; loadLists(c, id, e, s) }
    }
    fun toggle(id: UUID) { if (!state.value.busy && state.value.journal == null && state.value.events.any { it.id == id }) update { it.copy(selected = if (id in it.selected) it.selected - id else if (it.selected.size < 4) it.selected + id else it.selected, preview = null, previewKind = null) } }
    fun preview(kind: String) {
        val s0 = state.value; val id = s0.scopeId ?: return
        if (!s0.enabled || s0.busy || s0.journal != null || now() < cooldown || kind !in setOf("episode", "proposals", "lexical_rebuild")) return
        if (kind != "lexical_rebuild" && (!s0.canGenerate || s0.selected.isEmpty())) return
        update { it.copy(busy = true, fault = null) }
        work { conn, e, s ->
            val sources = mutableListOf<SourceVersionDto>()
            if (kind != "lexical_rebuild") for (event in s0.events.filter { it.id in s0.selected }) {
                val source = accepted(api.source(conn, event.source_version_id), e, s) ?: return@work
                require(source.scope_id == id && source.id == event.source_version_id && source.content == event.content && source.trust_class == event.trust_class)
                require(source.content_hash == hash(source.content)); sources += source
            }
            if (sources.sumOf { it.content.toByteArray(Charsets.UTF_8).size } > 6000) { if (current(e, s)) update { it.copy(busy = false, fault = ApiFailure.TooLarge, notice = "Select fewer or shorter complete messages (6,000 UTF-8 bytes maximum).") }; return@work }
            if (current(e, s)) update { it.copy(preview = sources, previewKind = kind, busy = false) }
        }
    }
    fun dismissPreview() { if (!state.value.busy) update { it.copy(preview = null, previewKind = null) } }
    fun queue() {
        val s0 = state.value; val owner = identity ?: return; val id = s0.scopeId ?: return
        val selected = s0.preview ?: return; val kind = s0.previewKind ?: return
        if (s0.busy || s0.journal != null || now() < cooldown) return
        val key = UUID.randomUUID()
        val body = ConsolidationInputDto(key, kind, selected.map { SourcePinDto(it.id, it.version, it.content_hash, 0, it.content.codePointCount(0, it.content.length)) })
        val saved = ConsolidationJournal(owner, id, key, adaJson.encodeToString(body)).also(::validateConsolidationJournal)
        update { it.copy(busy = true) }
        work { conn, e, s ->
            store.saveConsolidationJournal(saved)
            if (!current(e, s)) return@work
            update { it.copy(journal = saved, preview = null, previewKind = null) }
            submit(conn, saved, e, s)
        }
    }
    private fun validateJob(j: ConsolidationJobDto, p: ConsolidationJournal) {
        val b = adaJson.decodeFromString<ConsolidationInputDto>(p.body)
        require(j.id == p.jobId && j.owner_id == p.identity.owner && j.scope_id == p.scopeId && j.kind == b.kind && j.version == "consolidation-v1")
        require(j.attempt in 0..3 && j.status in setOf("queued", "running", "completed", "failed", "stale"))
        if (j.status in setOf("completed", "failed", "stale")) { val r = j.receipt ?: error("Missing receipt"); require(r.job_id == j.id && r.outcome == j.status && r.attempt == j.attempt && j.finished_at != null && j.lease_until == null) }
        else require(j.receipt == null && j.finished_at == null)
    }
    private suspend fun loadJob(conn: ConnectionCredential, p: ConsolidationJournal, e: Long, s: Long) {
        val j = accepted(api.consolidationJob(conn, p.jobId), e, s) ?: return
        validateJob(j, p); if (current(e, s)) update { it.copy(job = j, busy = false, fault = null) }
    }
    private suspend fun submit(conn: ConnectionCredential, p: ConsolidationJournal, e: Long, s: Long) {
        val j = accepted(api.createConsolidationJob(conn, p), e, s) ?: return
        validateJob(j, p); if (current(e, s)) update { it.copy(job = j, busy = false, fault = null) }
    }
    fun retry() { val p = state.value.journal ?: return; if (state.value.busy || now() < cooldown || !state.value.enabled) return
        update { it.copy(busy = true) }; work { c, e, s -> submit(c, p, e, s) } }
    fun discard() { val p = state.value.journal ?: return; if (state.value.busy) return
        update { it.copy(busy = true) }; work { _, e, s -> store.removeConsolidationJournal(p.identity, p.jobId)
            if (current(e, s)) { update { it.copy(journal = null, job = null, busy = false, notice = "Local reservation removed. Server jobs and evidence are retained.") }; activate(activeConversation) } } }
    private fun validateEpisode(ep: EpisodeDto, scopeId: UUID) {
        require(ep.owner_id == identity?.owner && ep.scope_id == scopeId && ep.trust_class == "model_generated" && ep.summary_version == "episode-summary-v1" && ep.range_end > ep.range_start)
        require(ep.sections.size in 1..8 && ep.sources.size in 1..4 && ep.sources.sumOf { it.evidence.quote.toByteArray(Charsets.UTF_8).size } <= 6000)
        ep.sections.forEach { section -> require(section.support.size in 1..4 && section.support.all { p -> ep.sources.any { src -> src.source_version == p.version && src.evidence.source_version_id == p.source_version_id && src.evidence.content_hash == p.content_hash && src.evidence.span_start <= p.span_start && p.span_start < p.span_end && p.span_end <= src.evidence.span_end } }) }
    }
    fun open(ep: EpisodeDto) { val id = state.value.scopeId ?: return; if (state.value.busy) return
        update { it.copy(busy = true, original = null) }; work { conn, e, s -> val row = accepted(api.episode(conn, ep.id), e, s) ?: return@work
            validateEpisode(row, id); if (current(e, s)) update { it.copy(episode = row, busy = false, fault = null) } } }
    fun original(source: EpisodeSourceDto) { val id = state.value.scopeId ?: return; if (state.value.busy || state.value.episode?.sources?.contains(source) != true) return
        update { it.copy(busy = true, original = null) }; work { conn, e, s -> val row = if (source.source_origin == "imported_document") {
                val doc = accepted(api.documentVersion(conn, source.evidence.source_version_id), e, s) ?: return@work
                require(verifyDocumentVersion(doc, doc.upload))
                SourceVersionDto(doc.id, doc.source_id, doc.scope_id, doc.version, doc.content, doc.content_hash, doc.trust_class, doc.created_at)
            } else accepted(api.source(conn, source.evidence.source_version_id), e, s) ?: return@work
            require(row.scope_id == id && row.id == source.evidence.source_version_id && row.version == source.source_version && row.content_hash == source.evidence.content_hash && hash(row.content) == row.content_hash)
            val ev = source.evidence; require(row.trust_class == source.trust_class && ev.span_start >= 0 && ev.span_end <= row.content.codePointCount(0, row.content.length) && row.content.substring(row.content.offsetByCodePoints(0, ev.span_start), row.content.offsetByCodePoints(0, ev.span_end)) == ev.quote)
            if (current(e, s)) update { it.copy(original = row, busy = false) } } }
    private fun hash(text: String) = MessageDigest.getInstance("SHA-256").digest(text.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
}
