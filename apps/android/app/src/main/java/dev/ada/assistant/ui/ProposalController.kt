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

data class ProposalState(
    val enabled: Boolean = false, val scopes: ChatPage<ScopeDto> = ChatPage(), val scopeId: UUID? = null,
    val inbox: ChatPage<ProposalDto> = ChatPage(), val sources: List<SourceVersionDto> = emptyList(),
    val uploads: List<DocumentUploadDto> = emptyList(), val chunks: List<DocumentChunkDto> = emptyList(),
    val document: DocumentVersionDto? = null, val selectedPin: SourcePinDto? = null, val selectedQuote: String? = null,
    val entities: List<EntityDto> = emptyList(),
    val draft: ProposalDraft? = null, val pending: PendingProposal? = null, val busy: Boolean = false,
    val fault: ApiFailure? = null, val notice: String? = null, val draftSaved: Boolean = true,
) { override fun toString() = "ProposalState(redacted)" }

class ProposalController(private val api: AdaApi, private val store: SessionStore,
    private val workScope: CoroutineScope, private val unauthorized: () -> Unit,
    private val now: () -> Long = System::currentTimeMillis) {
    private val mutableState = MutableStateFlow(ProposalState()); val state = mutableState.asStateFlow()
    private var connection: ConnectionCredential? = null; private var identity: SessionIdentity? = null
    private var generation = 0L; private var choice = 0L; private var cooldown = 0L
    private val jobs = mutableSetOf<Job>(); private var draftJob: Job? = null
    private fun update(change: (ProposalState) -> ProposalState) { mutableState.value = change(state.value) }
    fun reset() { generation++; choice++; jobs.toList().forEach { it.cancel() }; jobs.clear(); connection = null; identity = null; cooldown = 0; draftJob = null; mutableState.value = ProposalState() }
    private fun current(epoch: Long) = epoch == generation && connection != null && identity != null
    private fun work(task: suspend (ConnectionCredential, Long) -> Unit): Job? {
        val conn = connection ?: return null; val epoch = generation
        return workScope.launch { try { if (current(epoch)) task(conn, epoch) }
            catch (e: CancellationException) { throw e }
            catch (_: Exception) { if (current(epoch)) update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract, notice = "The operation could not be confirmed safely. Keep the saved input and check its receipt.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accepted(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        if (result is ApiResult.Success) return result.value
        val failure = result as ApiResult.Failure
        if (failure.reason == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (failure.reason is ApiFailure.Busy) { val instant = now(); val wait = failure.reason.retryAfterSeconds ?: 3; cooldown = if (wait > (Long.MAX_VALUE - instant) / 1000) Long.MAX_VALUE else instant + wait.coerceAtLeast(0) * 1000 }
        update { it.copy(busy = false, fault = failure.reason, notice = when (failure.reason) {
            ApiFailure.Conflict -> "The source, revision or conflicting memory changed. Check the saved operation before refreshing and reviewing again."
            ApiFailure.Validation, ApiFailure.TooLarge -> "Check the selected excerpt, fields and effective dates. The server could not accept this input."
            else -> "The outcome is not confirmed. Check the receipt or explicitly retry the same saved input."
        }) }; return null
    }
    fun setVerifiedSession(conn: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = conn; identity = owner
        update { it.copy(enabled = caps.memory_proposals == "selected_sources_v1" && caps.memory_review && caps.memory_provenance == "review-v1", busy = true) }
        work { _, epoch -> val pending = store.proposalPending(owner); val draft = store.proposalDraft(owner)
            if (current(epoch)) update { it.copy(busy = false, pending = pending, draft = draft, scopeId = pending?.scopeId ?: draft?.proposal?.scope_id,
                notice = if (pending != null || draft != null) "A private review draft was restored. Nothing has been submitted automatically." else null) }
        }
    }
    fun activate() { if (state.value.enabled && !state.value.busy) loadScopes(false) }
    fun moreScopes() = loadScopes(true)
    private fun loadScopes(more: Boolean) {
        val old = state.value.scopes; if (old.loading || (more && !old.hasMore)) return
        val offset = if (more) old.nextOffset else 0; update { it.copy(scopes = old.copy(loading = true)) }
        work { conn, epoch -> val rows = accepted(api.scopes(conn, 50, offset), epoch)
            if (!current(epoch)) return@work
            update { it.copy(scopes = if (rows == null) old.copy(loading = false) else ChatPage((if (more) old.items else emptyList()) + rows, false, rows.size == 50, offset + rows.size)) }
            if (rows != null) { if (state.value.scopeId == null) rows.firstOrNull()?.let { selectScope(it.id) } else refresh() }
        }
    }
    fun selectScope(scope: UUID) {
        if (state.value.busy || state.value.scopes.items.none { it.id == scope } || state.value.pending != null) return
        choice++; update { it.copy(scopeId = scope, inbox = ChatPage(), entities = emptyList(), sources = emptyList(), uploads = emptyList(), chunks = emptyList(), document = null, selectedPin = null, selectedQuote = null, fault = null) }; refresh()
    }
    fun refresh() = loadInbox(false)
    fun moreProposals() = loadInbox(true)
    private fun loadInbox(more: Boolean) {
        val scope = state.value.scopeId ?: return; val selected = choice; val old = state.value.inbox
        if (!state.value.enabled || old.loading || (more && !old.hasMore)) return
        val offset = if (more) old.nextOffset else 0; update { it.copy(inbox = old.copy(loading = true)) }
        work { conn, epoch -> val rows = accepted(api.proposals(conn, scope, 25, offset), epoch)
            if (!current(epoch) || selected != choice) return@work
            update { it.copy(inbox = if (rows == null) old.copy(loading = false) else ChatPage((if (more) old.items else emptyList()) + rows, false, rows.size == 25, offset + rows.size)) }
            if (!more) { val sources = accepted(api.sources(conn, scope, 50), epoch); if (current(epoch) && selected == choice && sources != null) update { it.copy(sources = sources) }
                val docs = accepted(api.documentUploads(conn, scope, 50), epoch); if (current(epoch) && selected == choice && docs != null) update { it.copy(uploads = docs.filter { row -> row.state == "ready" }) }
                val entities = accepted(api.entities(conn, scope, 50), epoch); if (current(epoch) && selected == choice && entities != null) update { it.copy(entities = entities) } }
        }
    }
    fun selectSource(source: SourceVersionDto) {
        if (state.value.busy || state.value.pending != null || source.scope_id != state.value.scopeId || state.value.sources.none { it.id == source.id }) return
        if (source.content.toByteArray(Charsets.UTF_8).size > 4000) { update { it.copy(notice = "Choose a shorter source or a document excerpt.") }; return }
        update { it.copy(selectedPin = SourcePinDto(source.id, source.version, source.content_hash, 0, source.content.codePointCount(0, source.content.length)), selectedQuote = source.content) }
    }
    fun selectDocument(upload: DocumentUploadDto) {
        if (state.value.busy || state.value.pending != null || upload.scope_id != state.value.scopeId) return
        val selected = choice; update { it.copy(busy = true) }
        work { conn, epoch -> val version = accepted(api.documentVersion(conn, upload.source_version_id), epoch) ?: return@work
            val chunks = accepted(api.documentChunks(conn, version.id, 50), epoch) ?: return@work
            if (current(epoch) && selected == choice) update { it.copy(busy = false, document = version, chunks = chunks) }
        }
    }
    fun selectChunk(chunk: DocumentChunkDto) {
        val doc = state.value.document ?: return
        if (state.value.busy || state.value.pending != null || chunk.scope_id != state.value.scopeId || chunk.source_version_id != doc.id || state.value.chunks.none { it.id == chunk.id }) return
        update { it.copy(selectedPin = SourcePinDto(doc.id, doc.version, chunk.content_hash, chunk.span_start, chunk.span_end), selectedQuote = chunk.quote) }
    }
    fun extractSelected() {
        val pin = state.value.selectedPin ?: return; val scope = state.value.scopeId ?: return; val owner = identity ?: return
        val key = UUID.randomUUID(); reserve(PendingProposal(owner, scope, key, kind = "extract", body = adaJson.encodeToString(ExtractionInputDto(key, listOf(pin)))))
    }
    fun open(proposal: ProposalDto) {
        if (state.value.busy || state.value.pending != null || proposal.scope_id != state.value.scopeId) return
        update { it.copy(busy = true) }; val selected = choice
        work { conn, epoch -> val p = accepted(api.proposal(conn, proposal.id), epoch) ?: return@work
            if (current(epoch) && selected == choice && p.scope_id == state.value.scopeId && p.status == "pending") {
                update { it.copy(busy = false, draft = ProposalDraft(identity!!, p, p.candidate), fault = null) }; saveDraft()
            }
        }
    }
    fun draft(candidate: ProposalCandidateDto? = null, annotation: String? = null, replacement: UUID? = null, setReplacement: Boolean = false) {
        val d = state.value.draft ?: return; if (state.value.busy || state.value.pending != null) return
        update { it.copy(draft = d.copy(candidate = candidate ?: d.candidate, annotation = annotation ?: d.annotation, replaceClaimId = if (setReplacement) replacement else d.replaceClaimId), draftSaved = false) }; saveDraft()
    }
    private fun saveDraft() {
        val d = state.value.draft ?: return; val previous = draftJob
        draftJob = work { _, epoch -> previous?.join(); if (!current(epoch) || state.value.draft != d) return@work
            store.saveProposalDraft(d); if (current(epoch) && state.value.draft == d) update { it.copy(draftSaved = true) }
        }
    }
    fun previewEdits() {
        val d = state.value.draft ?: return
        try { validateCandidate(d.candidate) } catch (_: Exception) { update { it.copy(fault = ApiFailure.Validation, notice = "Check the annotation and effective interval.") }; return }
        reserve(PendingProposal(d.identity, d.proposal.scope_id, UUID.randomUUID(), d.proposal.id, "edit", adaJson.encodeToString(ProposalEditDto(d.proposal.revision, d.proposal.review_hash, d.candidate))))
    }
    fun decide(decision: String) {
        val d = state.value.draft ?: return
        if (d.candidate != d.proposal.candidate || decision !in setOf("accept", "reject")) { update { it.copy(notice = "Preview your edited fields before reviewing this exact revision.") }; return }
        val key = UUID.randomUUID(); reserve(PendingProposal(d.identity, d.proposal.scope_id, key, d.proposal.id, "review", adaJson.encodeToString(ProposalReviewDto(key, d.proposal.revision, d.proposal.review_hash, decision, d.annotation, d.candidate, if (decision == "accept") d.replaceClaimId else null))))
    }
    private fun reserve(p: PendingProposal) {
        if (!state.value.enabled || state.value.busy || state.value.pending != null || now() < cooldown || p.identity != identity) return
        try { validateProposalPending(p) } catch (_: Exception) { update { it.copy(fault = ApiFailure.Validation, notice = "Complete the fields, dates and your decision annotation.") }; return }
        update { it.copy(busy = true) }
        work { conn, epoch -> draftJob?.join(); store.saveProposalPending(p)
            if (!current(epoch)) return@work
            update { it.copy(pending = p) }; submit(conn, p, epoch)
        }
    }
    private suspend fun finish(p: PendingProposal, epoch: Long, revised: ProposalDto? = null) {
        if (!current(epoch) || identity != p.identity) return
        store.removeProposalPending(p.identity, p.operationId)
        if (p.kind == "review") store.removeProposalDraft(p.identity)
        if (!current(epoch)) return
        update { it.copy(pending = null, busy = false, fault = null,
            draft = if (p.kind == "review") null else revised?.let { row -> it.draft?.copy(proposal = row, candidate = row.candidate) } ?: it.draft,
            notice = if (p.kind == "review") "Your explicit decision is saved. The receipt preserves its exact provenance." else "The operation is saved. Suggestions still need explicit review.") }
        if (revised != null) saveDraft(); refresh()
    }
    private suspend fun submit(conn: ConnectionCredential, p: PendingProposal, epoch: Long) {
        when (p.kind) {
            "extract" -> { val result = accepted(api.extractProposals(conn, p), epoch) ?: return
                if (result.id != p.operationId || result.scope_id != p.scopeId) { unconfirmed(); return }
                if (result.state in setOf("completed", "failed")) { finish(p, epoch); if (result.state == "failed") update { it.copy(notice = "Extraction produced no saved proposal. Review the source and server/model validation before starting a new extraction.") } } else update { it.copy(busy = false, notice = "Extraction is still processing. Check its original receipt.") } }
            "edit" -> { val result = accepted(api.editProposal(conn, p), epoch) ?: return; if (result.id == p.proposalId && result.scope_id == p.scopeId) finish(p, epoch, result) else unconfirmed() }
            "review" -> { val result = accepted(api.reviewProposal(conn, p), epoch) ?: return; if (validReceipt(p, result)) finish(p, epoch) else unconfirmed() }
        }
    }
    private fun unconfirmed() { update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract, notice = "The response does not match the saved operation. Keep the original key and check its receipt.") } }
    private fun validReceipt(p: PendingProposal, r: ReviewReceiptDto): Boolean {
        val b = adaJson.decodeFromString<ProposalReviewDto>(p.body)
        return r.id == p.operationId && r.proposal_id == p.proposalId && r.scope_id == p.scopeId && r.principal_id == p.identity.owner && r.decision == b.decision && r.revision == b.revision && r.review_hash == b.review_hash &&
            ((r.decision == "accept" && r.claim_id != null && r.endorsement_source_version_id != null) || (r.decision == "reject" && r.claim_id == null && r.endorsement_source_version_id == null))
    }
    fun retry() {
        val p = state.value.pending ?: return; if (!state.value.enabled || state.value.busy || now() < cooldown) return
        update { it.copy(busy = true) }; work { conn, epoch -> val me = accepted(api.me(conn), epoch) ?: return@work
            if (me.id != p.identity.owner) { reset(); unauthorized(); return@work }; store.saveProposalPending(p); submit(conn, p, epoch) }
    }
    fun check() {
        val p = state.value.pending ?: return; if (state.value.busy) return; update { it.copy(busy = true) }
        work { conn, epoch -> when (p.kind) {
            "extract" -> { val r = accepted(api.extraction(conn, p.operationId), epoch) ?: return@work; if (r.id == p.operationId && r.scope_id == p.scopeId && r.state in setOf("completed", "failed")) finish(p, epoch) else update { it.copy(busy = false) } }
            "review" -> { val r = accepted(api.reviewReceipt(conn, p.operationId), epoch) ?: return@work; if (validReceipt(p, r)) finish(p, epoch) else unconfirmed() }
            "edit" -> { val r = accepted(api.proposal(conn, p.proposalId!!), epoch) ?: return@work; val b = adaJson.decodeFromString<ProposalEditDto>(p.body)
                if (r.scope_id == p.scopeId && r.status == "pending" && r.revision == b.revision + 1 && sameProposalCandidate(r.candidate, b.candidate)) finish(p, epoch, r) else update { it.copy(busy = false, notice = "The saved edit is not confirmed. Retry identical input or keep the draft for a fresh review.") } }
        } }
    }
    fun discard() {
        val owner = identity ?: return; if (state.value.busy) return; val p = state.value.pending
        update { it.copy(busy = true) }; work { _, epoch -> if (p != null) store.removeProposalPending(owner, p.operationId); store.removeProposalDraft(owner)
            if (current(epoch)) update { it.copy(busy = false, pending = null, draft = null, notice = "Local recovery was discarded. Existing server proposals, claims and receipts are retained.") }
        }
    }
}
