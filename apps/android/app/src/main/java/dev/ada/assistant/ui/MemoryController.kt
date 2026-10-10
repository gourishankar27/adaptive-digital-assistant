package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.time.OffsetDateTime
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** Owned by ChatViewModel: credentials enter only after /me and capabilities verification. */
class MemoryController(
    private val api: AdaApi, private val store: SessionStore, private val workScope: CoroutineScope,
    private val onUnauthorized: () -> Unit,
) {
    private val mutableState = MutableStateFlow(MemoryState())
    val state = mutableState.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private var query = 0L
    private var detailSelection = 0L
    private var retryNotBefore = 0L
    private val jobs = mutableSetOf<Job>()
    private fun update(block: (MemoryState) -> MemoryState) { mutableState.value = block(mutableState.value) }
    fun reset() {
        generation++; query++; detailSelection++
        jobs.toList().forEach { it.cancel() }; jobs.clear()
        connection = null; identity = null; retryNotBefore = 0
        mutableState.value = MemoryState()
    }
    fun setVerifiedSession(connection: ConnectionCredential, identity: SessionIdentity, features: CapabilitiesDto) {
        reset(); this.connection = connection; this.identity = identity
        update { it.copy(enabled = features.structured_memory,
            historicalEnabled = features.historical_memory_queries,
            writesEnabled = features.structured_memory && features.memory_writes == "explicit_user_assertions") }
        work { _, epoch ->
            val pending = store.memoryPending(identity)
            if (!current(epoch)) return@work
            if (pending != null && pending.reservation.identity == identity) update { it.copy(
                pending = pending, scopeId = pending.reservation.scopeId,
                notice = "A saved memory write needs review. Check its original ID or resume the exact saved input. The raw note may already exist.") }
        }
    }
    private fun current(epoch: Long) = generation == epoch && connection != null && identity != null
    private fun work(block: suspend (ConnectionCredential, Long) -> Unit) {
        val verified = connection ?: return; val epoch = generation
        workScope.launch {
            try { if (current(epoch)) block(verified, epoch) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) {
                if (current(epoch)) update { it.copy(saving = false, detailLoading = false,
                    scopes = it.scopes.copy(loading = false), claims = it.claims.copy(loading = false),
                    sourceChoices = it.sourceChoices.copy(loading = false), fault = ApiFailure.IncompatibleContract,
                    notice = "The operation could not be confirmed safely. Keep the saved input and check recovery or refresh.") }
            }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun failed(failure: ApiResult.Failure, epoch: Long) {
        if (!current(epoch)) return
        if (failure.reason == ApiFailure.Unauthorized) { reset(); onUnauthorized(); return }
        if (failure.reason is ApiFailure.Busy) {
            val now = System.currentTimeMillis()
            val seconds = failure.reason.retryAfterSeconds ?: 1
            retryNotBefore = if (seconds > (Long.MAX_VALUE - now) / 1000) Long.MAX_VALUE else now + seconds.coerceAtLeast(0) * 1000
        }
        update { it.copy(fault = failure.reason, notice = when (failure.code) {
            "claim_duplicate" -> "An identical assertion already exists. Review owned history before discarding this reservation or making a conscious new assertion."
            "claim_already_superseded" -> "Another correction has already replaced this assertion. Refresh its detail and history; the reserved replacement is kept for review."
            "source_id_reused", "source_conflict", "claim_id_reused", "claim_conflict" -> "The saved ID conflicts with different input. Check the original ID and review owned history. Resuming keeps the exact input; it never allocates a new ID."
            "source_not_user_evidence" -> "This source cannot support an explicit user assertion. Keep the input for review and choose an owned user statement for a consciously new assertion."
            "invalid_validity_interval", "correction_outside_validity_interval" -> "The effective interval was rejected. Keep the reserved input, review history and explicitly discard the reservation before editing a new write."
            "evidence_content_changed", "invalid_evidence_span", "empty_evidence_span" -> "The exact evidence could not be verified. Refresh its source and review the saved selection."
            else -> if (mutableState.value.pending != null) "The memory outcome is not confirmed. The raw note may exist. Check the original ID or explicitly resume the same saved input." else null
        }) }
    }
    private fun <T> value(result: ApiResult<T>, epoch: Long): T? = when {
        !current(epoch) -> null
        result is ApiResult.Success -> result.value
        result is ApiResult.Failure -> { failed(result, epoch); null }
        else -> null
    }
    private fun acceptSessionResult(result: ApiResult<*>, epoch: Long): Boolean {
        if (!current(epoch)) return false
        // Authentication belongs to the session, even when its originating view is stale.
        if (result is ApiResult.Failure && result.reason == ApiFailure.Unauthorized) {
            failed(result, epoch); return false
        }
        return true
    }
    private fun <T> page(previous: ChatPage<T>, rows: List<T>, offset: Int, id: (T) -> UUID): ChatPage<T> {
        val byId = linkedMapOf<UUID, T>()
        if (offset != 0) previous.items.forEach { byId[id(it)] = it }
        rows.forEach { byId[id(it)] = it }
        return ChatPage(byId.values.toList(), false, rows.size == PAGE_SIZE, offset + rows.size)
    }
    fun activate() { if (state.value.enabled) { refreshScopes(); if (state.value.scopeId != null) refreshClaims() } }
    fun refreshScopes() = scopes(true)
    fun loadMoreScopes() = scopes(false)
    private fun scopes(refresh: Boolean) {
        val prior = state.value.scopes
        if (!state.value.enabled || prior.loading || (!refresh && !prior.hasMore)) return
        val offset = if (refresh) 0 else prior.nextOffset
        update { it.copy(scopes = prior.copy(loading = true), fault = null) }
        work { conn, epoch ->
            val rows = value(api.scopes(conn, PAGE_SIZE, offset), epoch)
            if (!current(epoch)) return@work
            update { it.copy(scopes = if (rows == null) it.scopes.copy(loading = false) else page(it.scopes, rows, offset) { row -> row.id }) }
            if (state.value.scopeId == null) rows?.firstOrNull()?.let { selectScope(it.id) }
        }
    }
    fun selectScope(id: UUID) {
        if (state.value.saving || state.value.scopes.items.none { it.id == id }) return
        query++; detailSelection++
        update { it.copy(scopeId = id, screen = MemoryScreen.Browse, claims = ChatPage(), detail = null,
            detailSource = null, sourceChoices = ChatPage(), draft = MemoryDraft(), preview = null, fault = null, validation = null) }
        refreshClaims()
    }
    fun setMode(mode: MemoryMode) {
        if (mode != MemoryMode.Current && !state.value.historicalEnabled) return
        if (mode == state.value.mode) return
        query++
        update { it.copy(mode = mode, claims = ChatPage(), fault = null, validation = null) }
        if (mode != MemoryMode.AsOf) applyQuery()
    }
    fun updateAsOf(text: String) { query++; update { it.copy(asOf = text, claims = ChatPage(), validation = null) } }
    fun applyQuery() {
        if (state.value.mode == MemoryMode.AsOf) try {
            require(normalizeUtcMillis(state.value.asOf) != null)
        } catch (_: Exception) { invalid("Enter a timestamp with a timezone and at most millisecond precision."); return }
        query++; update { it.copy(claims = ChatPage(), validation = null) }; refreshClaims()
    }
    fun refreshClaims() = claims(true)
    fun loadMoreClaims() = claims(false)
    private fun claims(refresh: Boolean) {
        val s = state.value; val scope = s.scopeId ?: return
        if (!s.enabled || s.claims.loading || (!refresh && !s.claims.hasMore)) return
        val at = if (s.mode == MemoryMode.AsOf) try { normalizeUtcMillis(s.asOf) ?: return } catch (_: Exception) { invalid("Enter a timestamp with a timezone and at most millisecond precision."); return } else null
        val offset = if (refresh) 0 else s.claims.nextOffset; val selectedQuery = query
        update { it.copy(claims = s.claims.copy(loading = true), fault = null) }
        work { conn, epoch ->
            val result = api.claims(conn, scope, PAGE_SIZE, offset, s.mode == MemoryMode.History, at)
            if (!acceptSessionResult(result, epoch) || query != selectedQuery) return@work
            val rows = value(result, epoch)
            if (!current(epoch)) return@work
            if (rows?.any { it.scope_id != scope } == true) { invalid("The server returned an incompatible scope. Refresh before continuing."); update { it.copy(claims = ChatPage(), fault = ApiFailure.IncompatibleContract) }; return@work }
            update { it.copy(claims = if (rows == null) it.claims.copy(loading = false) else page(it.claims, rows, offset) { row -> row.id }) }
        }
    }
    fun openClaim(id: UUID) {
        val scope = state.value.scopeId ?: return; val selected = ++detailSelection
        update { it.copy(screen = MemoryScreen.Detail, detail = null, detailSource = null,
            detailLoading = true, evidenceVerified = false, fault = null, validation = null) }
        work { conn, epoch ->
            val result = api.claim(conn, id)
            if (!acceptSessionResult(result, epoch) || detailSelection != selected) return@work
            val claim = value(result, epoch)
            if (!current(epoch)) return@work
            if (claim == null || claim.id != id || claim.scope_id != scope) {
                update { it.copy(detailLoading = false, detail = null, detailSource = null,
                    fault = if (claim != null) ApiFailure.IncompatibleContract else it.fault) }; return@work
            }
            update { it.copy(detail = claim) }
            val sourceResult = api.source(conn, claim.evidence.source_version_id)
            if (!acceptSessionResult(sourceResult, epoch) || detailSelection != selected) return@work
            val source = value(sourceResult, epoch)
            if (!current(epoch)) return@work
            val verified = source != null && verifyClaimEvidence(claim, source)
            update { it.copy(detailLoading = false, detailSource = source?.takeIf { verified }, evidenceVerified = verified,
                notice = if (source != null && !verified) "Exact evidence does not match the returned source version. Refresh before using it." else it.notice) }
        }
    }
    fun openReplacement() { state.value.detail?.superseded_by?.let(::openClaim) }
    fun beginRemember() {
        if (!state.value.writesEnabled || state.value.pending != null || state.value.saving || state.value.scopeId == null) return
        update { it.copy(screen = MemoryScreen.Edit, draft = MemoryDraft(), preview = null, sourceChoices = ChatPage(), validation = null, fault = null, notice = null) }
    }
    fun beginCorrection() {
        val old = state.value.detail ?: return
        if (!state.value.writesEnabled || state.value.pending != null || state.value.saving || old.status != "active" || old.superseded_by != null) return
        update { it.copy(screen = MemoryScreen.Edit,
            draft = MemoryDraft(subject = old.subject, predicate = old.predicate, value = "", kind = old.kind, corrects = old),
            preview = null, sourceChoices = ChatPage(), validation = null, fault = null, notice = null) }
    }
    fun updateDraft(draft: MemoryDraft) {
        if (state.value.screen != MemoryScreen.Edit || state.value.saving) return
        val original = state.value.draft.corrects
        update { it.copy(draft = if (original == null) draft.copy(corrects = null) else draft.copy(
            corrects = original, subject = original.subject, predicate = original.predicate, kind = original.kind), preview = null, validation = null) }
    }
    fun loadSources() = sources(true)
    fun loadMoreSources() = sources(false)
    private fun sources(refresh: Boolean) {
        val s = state.value; val scope = s.scopeId ?: return; val selectedQuery = query
        if (s.sourceChoices.loading || (!refresh && !s.sourceChoices.hasMore)) return
        val offset = if (refresh) 0 else s.sourceChoices.nextOffset
        update { it.copy(sourceChoices = s.sourceChoices.copy(loading = true), fault = null) }
        work { conn, epoch ->
            val result = api.sources(conn, scope, PAGE_SIZE, offset)
            if (!acceptSessionResult(result, epoch) || query != selectedQuery) return@work
            val rows = value(result, epoch)
            if (!current(epoch)) return@work
            val owned = rows?.filter { it.scope_id == scope }
            update { it.copy(sourceChoices = if (owned == null) it.sourceChoices.copy(loading = false) else page(it.sourceChoices, owned, offset) { row -> row.id }.copy(
                hasMore = rows.size == PAGE_SIZE, nextOffset = offset + rows.size)) }
        }
    }
    fun selectSource(source: SourceVersionDto) {
        val scope = state.value.scopeId ?: return
        if (state.value.screen != MemoryScreen.Edit) return
        try { exactEvidenceSelection(source, scope, 0, source.content.length) }
        catch (_: Exception) { invalid("Choose an intact user statement in this scope. Model output cannot become user evidence."); return }
        update { it.copy(draft = it.draft.copy(selectedSource = source, startUtf16 = 0, endUtf16 = source.content.length), validation = null) }
    }
    fun selectNote() = updateDraft(state.value.draft.copy(selectedSource = null, startUtf16 = 0, endUtf16 = 0))
    fun updateSelection(start: Int, end: Int) = updateDraft(state.value.draft.copy(startUtf16 = minOf(start, end), endUtf16 = maxOf(start, end)))
    private fun invalid(message: String) { update { it.copy(validation = message, preview = null) } }
    private fun validateText(text: String, max: Int): String {
        require(text.isNotBlank() && text.codePointCount(0, text.length) <= max && !text.contains('\u0000'))
        var i = 0
        while (i < text.length) { val c = text[i++]; require(!c.isLowSurrogate()); if (c.isHighSurrogate()) require(i < text.length && text[i++].isLowSurrogate()) }
        return text
    }
    fun preview() {
        val s = state.value; val owner = identity ?: return; val scope = s.scopeId ?: return
        if (!s.writesEnabled || s.pending != null || s.saving || s.screen != MemoryScreen.Edit) return
        val d = s.draft
        try {
            // Python's annotation strip also includes NEXT LINE; exact source text is untouched.
            fun annotation(text: String, max: Int) = validateText(text, max).trim { it.isWhitespace() || it == '\u0085' }.also { require(it.isNotEmpty()) }
            val subject = annotation(d.subject, 160); val predicate = annotation(d.predicate, 160)
            val annotation = annotation(d.value, 1000); require(d.kind in listOf("fact", "preference", "decision"))
            val from = normalizeUtcMillis(d.validFrom); val to = normalizeUtcMillis(d.validTo)
            val start = from?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() }
            val end = to?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() }
            val selected = d.selectedSource
            val evidence = selected?.let { exactEvidenceSelection(it, scope, d.startUtf16, d.endUtf16) }
            val note = if (selected == null) NoteInputDto(UUID.randomUUID(), validateText(d.note, 4000)) else null
            val effective = start ?: selected?.created_at
            if (end != null && effective != null) require(end > effective)
            d.corrects?.let { old ->
                require(old.scope_id == scope && old.status == "active" && old.superseded_by == null)
                if (effective != null) require(effective > old.valid_from && (old.valid_to == null || effective <= old.valid_to))
            }
            val reservation = MemoryReservation(owner, scope, UUID.randomUUID(), note, evidence, subject, predicate,
                annotation, d.kind, from, to, d.corrects)
            update { it.copy(screen = MemoryScreen.Preview, preview = PendingMemory(reservation, selected), validation = null, fault = null) }
        } catch (_: Exception) { invalid("Check the required fields, exact nonblank selection and timestamps. Use a timezone and millisecond precision; end must follow start. A correction must start after the old start and at or before its existing end.") }
    }
    fun editPreview() {
        if (!state.value.saving && state.value.pending == null) update { it.copy(screen = MemoryScreen.Edit, preview = null) }
    }
    private fun allowedWrite(): Boolean {
        if (!state.value.writesEnabled || state.value.saving) return false
        if (System.currentTimeMillis() < retryNotBefore) { invalid("ADA asked you to wait before retrying this saved write."); return false }
        return true
    }
    fun savePreview() {
        val preview = state.value.preview ?: return
        if (!allowedWrite() || state.value.pending != null) return
        update { it.copy(saving = true, fault = null, validation = null) }
        work { conn, epoch ->
            try { store.saveMemoryPending(preview) }
            catch (_: Exception) { if (current(epoch)) update { it.copy(saving = false, fault = ApiFailure.IncompatibleContract, notice = "Secure storage could not commit the write. Nothing was submitted; keep this preview and resolve device storage before saving.") }; return@work }
            if (!current(epoch)) return@work
            update { it.copy(pending = preview) }; submit(conn, epoch, preview)
        }
    }
    fun resumePending() {
        val pending = state.value.pending ?: return
        if (!allowedWrite()) return
        update { it.copy(saving = true, fault = null, validation = null) }
        work { conn, epoch ->
            // Check first: a previous claim may have committed even if the response disappeared.
            val existing = api.claim(conn, pending.reservation.claimId)
            if (!current(epoch)) return@work
            when (existing) {
                // Resume is an explicit identical replay. The server verifies its stored write
                // fingerprint even if another client subsequently narrowed the claim interval.
                is ApiResult.Success -> submit(conn, epoch, pending)
                is ApiResult.Failure -> if (existing.reason == ApiFailure.NotFound) submit(conn, epoch, pending)
                    else { failed(existing, epoch); if (current(epoch)) update { it.copy(saving = false) } }
            }
        }
    }
    private suspend fun submit(conn: ConnectionCredential, epoch: Long, original: PendingMemory) {
        val r = original.reservation
        if (!current(epoch) || r.identity != identity) return
        val owned = value(api.scope(conn, r.scopeId), epoch)
        if (!current(epoch)) return
        if (owned == null || owned.id != r.scopeId) { update { it.copy(saving = false) }; return }
        var pending = original
        if (pending.source == null) {
            val result = api.createNote(conn, r.scopeId, r.note ?: return)
            if (!current(epoch)) return
            val source = value(result, epoch)
            if (!current(epoch)) return
            if (source == null) { update { it.copy(saving = false) }; return }
            if (source.source_id != r.note.source_id || source.content != r.note.content || source.scope_id != r.scopeId) {
                update { it.copy(saving = false, fault = ApiFailure.IncompatibleContract, notice = "The note response does not match the reserved input. Check recovery before continuing.") }; return
            }
            pending = pending.copy(source = source)
            try { exactEvidenceSelection(source, r.scopeId, 0, source.content.length); validateInterval(pending); store.saveMemoryPending(pending) }
            catch (_: Exception) { if (current(epoch)) update { it.copy(saving = false, fault = ApiFailure.Validation, notice = "The note may exist, but its evidence, interval or secure checkpoint could not be confirmed. The original reservation is kept; no claim was submitted.") }; return }
            if (!current(epoch)) return
            update { it.copy(pending = pending) }
        } else {
            val source = value(api.source(conn, pending.source!!.id), epoch)
            if (!current(epoch)) return
            if (source == null) { update { it.copy(saving = false) }; return }
            try {
                require(source == pending.source)
                val evidence = r.evidence ?: exactEvidenceSelection(source, r.scopeId, 0, source.content.length)
                require(exactEvidenceSelection(source, r.scopeId, codePointToUtf16Offset(source.content, evidence.span_start), codePointToUtf16Offset(source.content, evidence.span_end)) == evidence)
                validateInterval(pending)
            } catch (_: Exception) { update { it.copy(saving = false, fault = ApiFailure.Conflict, notice = "The reserved source or interval no longer matches. Review exact evidence and history before a conscious new write.") }; return }
        }
        val result = if (r.corrects == null) api.createClaim(conn, r.scopeId, pending.claimInput())
            else api.supersede(conn, r.corrects.id, pending.correctionInput())
        if (!current(epoch)) return
        when (result) {
            is ApiResult.Success -> reconcile(conn, epoch, pending, result.value, boundReplay = true)
            is ApiResult.Failure -> { failed(result, epoch); if (current(epoch)) update { it.copy(saving = false) } }
        }
    }
    private fun validateInterval(pending: PendingMemory) {
        val r = pending.reservation
        val start = r.validFrom?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() } ?: pending.source!!.created_at
        val end = r.validTo?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() }
        require(end == null || end > start)
        r.corrects?.let { require(start > it.valid_from && (it.valid_to == null || start <= it.valid_to)) }
    }
    fun checkPending() {
        val pending = state.value.pending ?: return
        if (state.value.saving) return
        update { it.copy(saving = true, fault = null) }
        work { conn, epoch ->
            when (val result = api.claim(conn, pending.reservation.claimId)) {
                is ApiResult.Success -> if (current(epoch)) reconcile(conn, epoch, pending, result.value)
                is ApiResult.Failure -> {
                    if (!current(epoch)) return@work
                    if (result.reason == ApiFailure.NotFound) update { it.copy(saving = false,
                        notice = "No claim is available at the saved ID. The note may already exist. Resume uses the same IDs and exact payload.") }
                    else { failed(result, epoch); if (current(epoch)) update { it.copy(saving = false) } }
                }
            }
        }
    }
    private suspend fun reconcile(conn: ConnectionCredential, epoch: Long, pending: PendingMemory, claim: ClaimDto, boundReplay: Boolean = false) {
        val r = pending.reservation
        val source = value(api.source(conn, claim.evidence.source_version_id), epoch)
        if (!current(epoch)) return
        val matches = try {
            require(source != null && source.scope_id == r.scopeId && source.trust_class == "user_explicit")
            val reservedEvidence = r.evidence ?: exactEvidenceSelection(source, r.scopeId, 0, source.content.length)
            val start = r.validFrom?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() } ?: source.created_at
            val end = r.validTo?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() }
            val endMatches = claim.valid_to == end || (boundReplay && claim.status == "superseded" &&
                claim.superseded_by != null && claim.valid_to != null && claim.valid_to > start &&
                (end == null || claim.valid_to <= end))
            claim.id == r.claimId && claim.scope_id == r.scopeId && claim.subject == r.subject && claim.predicate == r.predicate &&
                claim.value == r.value && claim.kind == r.kind && claim.origin == "user_asserted" &&
                claim.valid_from == start && endMatches && claim.evidence == reservedEvidence && verifyClaimEvidence(claim, source) &&
                (pending.source == null || pending.source == source) &&
                (r.note == null || (source.source_id == r.note.source_id && source.content == r.note.content))
        } catch (_: Exception) { false }
        if (source == null) { update { it.copy(saving = false) }; return }
        if (!matches) { update { it.copy(saving = false, fault = ApiFailure.Conflict,
            notice = "The returned claim differs from the reserved annotation, evidence or interval. Review history. Resume original write verifies the identical payload with the server; the saved input is retained.") }; return }
        if (r.corrects != null) {
            val old = value(api.claim(conn, r.corrects.id), epoch)
            if (!current(epoch)) return
            if (old == null || old.scope_id != r.scopeId || old.superseded_by != claim.id || old.valid_to != claim.valid_from) {
                update { it.copy(saving = false, fault = ApiFailure.Conflict, notice = "The correction link could not be verified. Refresh history and keep the reservation for recovery.") }; return
            }
        }
        try { store.removeMemoryPending(r.identity, r.claimId) }
        catch (_: Exception) { if (current(epoch)) update { it.copy(saving = false, fault = ApiFailure.IncompatibleContract,
            notice = "The claim is confirmed, but its encrypted recovery journal could not be cleared. Check the same ID after resolving device storage; a new save stays blocked.") }; return }
        if (!current(epoch)) return
        query++; detailSelection++
        update { it.copy(pending = null, preview = null, saving = false, screen = MemoryScreen.Detail,
            scopeId = r.scopeId, detail = claim, detailSource = source, evidenceVerified = true, detailLoading = false,
            claims = ChatPage(), draft = MemoryDraft(), fault = null, validation = null,
            notice = "Memory saved. Existing chat replies retain their original citation snapshots.") }
        refreshClaims()
    }
    /** Explicit UI confirmation is required. This only removes local recovery, never server history. */
    fun discardPending() {
        val pending = state.value.pending ?: return
        if (state.value.saving) return
        update { it.copy(saving = true) }
        work { _, epoch ->
            store.removeMemoryPending(pending.reservation.identity, pending.reservation.claimId)
            if (!current(epoch)) return@work
            val r = pending.reservation
            update { it.copy(pending = null, saving = false, preview = null, screen = MemoryScreen.Edit,
                draft = MemoryDraft(r.note?.content ?: "", r.subject, r.predicate, r.value, r.kind,
                    r.validFrom ?: "", r.validTo ?: "", pending.source?.takeIf { r.evidence != null },
                    r.evidence?.let { e -> pending.source?.let { codePointToUtf16Offset(it.content, e.span_start) } } ?: 0,
                    r.evidence?.let { e -> pending.source?.let { codePointToUtf16Offset(it.content, e.span_end) } } ?: 0, r.corrects),
                notice = "Local recovery was discarded. The note or claim may still exist on the server. Review owned history before explicitly previewing a new write.") }
        }
    }
    fun back(): Boolean {
        if (state.value.screen == MemoryScreen.Browse) return false
        detailSelection++
        update { it.copy(screen = MemoryScreen.Browse, detailLoading = false, validation = null) }
        return true
    }
    companion object { const val PAGE_SIZE = 50 }
}
