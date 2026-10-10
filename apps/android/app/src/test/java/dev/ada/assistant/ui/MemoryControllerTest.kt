package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.security.MessageDigest
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import org.junit.Assert.*
import org.junit.After
import org.junit.Before
import org.junit.Test

private val memoryScope = UUID.randomUUID()
private val memoryIdentity = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val memoryConnection = ConnectionCredential.parse("https://ada.test", "synthetic-token", false)!!
private val memoryFeatures = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json"))
private fun memorySource(note: NoteInputDto, scope: UUID = memoryScope) = SourceVersionDto(
    UUID.randomUUID(), note.source_id, scope, 1, note.content,
    MessageDigest.getInstance("SHA-256").digest(note.content.toByteArray()).joinToString("") { "%02x".format(it) },
    "user_explicit", 1791500000123L,
)
private fun memoryClaim(p: PendingMemory): ClaimDto {
    val r = p.reservation; val source = p.source!!
    val e = r.evidence ?: exactEvidenceSelection(source, r.scopeId, 0, source.content.length)
    return ClaimDto(r.claimId, r.scopeId, r.subject, r.predicate, r.value, r.kind, "active",
        r.validFrom?.let { java.time.OffsetDateTime.parse(it).toInstant().toEpochMilli() } ?: source.created_at,
        r.validTo?.let { java.time.OffsetDateTime.parse(it).toInstant().toEpochMilli() }, null, source.created_at,
        "user_asserted", e)
}
private class MemoryWriteStore : SessionStore {
    var saved: PendingMemory? = null
    var failSave = false; var failRemove = false; var failCheckpoint = false
    val operations = mutableListOf<String>()
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) = Unit
    override suspend fun clear() { saved = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) = Unit
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) = Unit
    override suspend fun memoryPending(identity: SessionIdentity) = saved?.takeIf { it.reservation.identity == identity }
    override suspend fun saveMemoryPending(pending: PendingMemory) {
        if (failSave || (failCheckpoint && pending.source != null)) throw SessionStorageException()
        assertTrue(saved == null || saved!!.reservation == pending.reservation)
        saved = pending; operations += if (pending.source == null) "reserve" else "checkpoint"
    }
    override suspend fun removeMemoryPending(identity: SessionIdentity, claimId: UUID) {
        if (failRemove) throw SessionStorageException()
        if (saved?.reservation?.identity == identity && saved?.reservation?.claimId == claimId) saved = null
        operations += "remove"
    }
}
private fun unsupportedMemoryApi(): AdaApi = java.lang.reflect.Proxy.newProxyInstance(
    AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java),
) { _, method, _ -> error("Unexpected test call: ${method.name}") } as AdaApi
private class MemoryWriteApi(val store: MemoryWriteStore) : AdaApi by unsupportedMemoryApi() {
    val notes = mutableListOf<NoteInputDto>(); val writes = mutableListOf<ClaimInputDto>()
    val corrections = mutableListOf<SupersedeInputDto>()
    val rows = mutableMapOf<UUID, ClaimDto>(); val sourceRows = mutableMapOf<UUID, SourceVersionDto>()
    var claimFailure: ApiResult.Failure? = null
    var noteFailure: ApiResult.Failure? = null
    var lostClaimDelivery = false
    var listCall: suspend (UUID, Int, Boolean, String?) -> ApiResult<List<ClaimDto>> = { _, _, _, _ -> ApiResult.Success(rows.values.toList()) }
    override suspend fun scopes(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(ScopeDto(memoryScope, "Test scope", "project", 1)))
    override suspend fun scope(connection: ConnectionCredential, id: UUID) = ApiResult.Success(ScopeDto(id, "Test scope", "project", 1))
    override suspend fun claims(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int, history: Boolean, asOf: String?) = listCall(scope, offset, history, asOf)
    override suspend fun claim(connection: ConnectionCredential, id: UUID): ApiResult<ClaimDto> = rows[id]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun source(connection: ConnectionCredential, id: UUID): ApiResult<SourceVersionDto> = sourceRows[id]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun createNote(connection: ConnectionCredential, scope: UUID, body: NoteInputDto): ApiResult<SourceVersionDto> {
        assertEquals(body, store.saved!!.reservation.note); notes += body; store.operations += "note"
        noteFailure?.let { return it }
        val source = sourceRows.values.firstOrNull { it.source_id == body.source_id } ?: memorySource(body, scope)
        sourceRows[source.id] = source; return ApiResult.Success(source)
    }
    override suspend fun createClaim(connection: ConnectionCredential, scope: UUID, body: ClaimInputDto): ApiResult<ClaimDto> {
        assertEquals(body, store.saved!!.claimInput()); writes += body; store.operations += "claim"
        claimFailure?.let { return it }
        val row = rows[body.claim_id] ?: memoryClaim(store.saved!!); rows[row.id] = row
        return if (lostClaimDelivery) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(row)
    }
    override suspend fun supersede(connection: ConnectionCredential, id: UUID, body: SupersedeInputDto): ApiResult<ClaimDto> {
        assertEquals(body, store.saved!!.correctionInput()); corrections += body
        claimFailure?.let { return it }
        val row = memoryClaim(store.saved!!); rows[row.id] = row
        rows[id]?.let { rows[id] = it.copy(status = "superseded", valid_to = row.valid_from, superseded_by = row.id) }
        return ApiResult.Success(row)
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
class MemoryControllerTest {
    @Before fun setup() { Dispatchers.setMain(StandardTestDispatcher()) }
    @After fun cleanup() { Dispatchers.resetMain() }
    private fun TestScope.ready(store: MemoryWriteStore = MemoryWriteStore()): Triple<MemoryController, MemoryWriteApi, MemoryWriteStore> {
        val api = MemoryWriteApi(store)
        val controller = MemoryController(api, store, this) {}
        controller.setVerifiedSession(memoryConnection, memoryIdentity, memoryFeatures)
        advanceUntilIdle(); controller.activate(); advanceUntilIdle()
        return Triple(controller, api, store)
    }
    private fun draft(c: MemoryController) {
        c.beginRemember(); c.updateDraft(MemoryDraft(note = "Exact 😀 é\r\n日本語", subject = "Project", predicate = "color", value = "Blue"))
        c.preview(); assertNotNull(c.state.value.preview)
    }
    @Test fun reservationAndCheckpointPrecedeWritesAndDoubleSaveCannotDuplicate() = runTest {
        val (c, api, store) = ready(); draft(c); c.savePreview(); c.savePreview(); advanceUntilIdle()
        assertEquals(listOf("reserve", "note", "checkpoint", "claim", "remove"), store.operations)
        assertEquals(1, api.writes.size); assertNull(store.saved)
        assertEquals("Exact 😀 é\r\n日本語", c.state.value.detail!!.evidence.quote)
    }
    @Test fun noteSuccessClaimFailureRestoresExactIdsAndPayloadWithoutAutomaticPost() = runTest {
        val (c, api, store) = ready(); api.claimFailure = ApiResult.Failure(ApiFailure.Timeout)
        draft(c); c.savePreview(); advanceUntilIdle(); val reserved = store.saved!!; val input = api.writes.single()
        c.reset(); api.claimFailure = null
        val restored = MemoryController(api, store, this) {}; restored.setVerifiedSession(memoryConnection, memoryIdentity, memoryFeatures)
        advanceUntilIdle(); assertEquals(1, api.writes.size); assertEquals(reserved, restored.state.value.pending)
        restored.resumePending(); advanceUntilIdle()
        assertEquals(listOf(input, input), api.writes); assertEquals(1, api.notes.size); assertEquals(1, api.rows.size); assertNull(store.saved)
    }
    @Test fun missingSourceCheckpointReplaysSameNoteAndClaimIds() = runTest {
        val (c, api, store) = ready(); store.failCheckpoint = true
        draft(c); c.savePreview(); advanceUntilIdle(); assertTrue(api.writes.isEmpty()); val note = api.notes.single()
        assertNull(store.saved!!.source); store.failCheckpoint = false
        c.resumePending(); advanceUntilIdle()
        assertEquals(listOf(note, note), api.notes); assertEquals(1, api.sourceRows.size); assertEquals(1, api.rows.size)
    }
    @Test fun failedReservationMakesNoNetworkWrite() = runTest {
        val (c, api, store) = ready(); store.failSave = true; draft(c); c.savePreview(); advanceUntilIdle()
        assertTrue(api.notes.isEmpty()); assertTrue(api.writes.isEmpty()); assertNotNull(c.state.value.preview)
    }
    @Test fun lostDeliveryAndFailedCleanupBlockNewWriteUntilSameIdReconciliation() = runTest {
        val (c, api, store) = ready(); api.lostClaimDelivery = true; draft(c); c.savePreview(); advanceUntilIdle()
        store.failRemove = true; c.checkPending(); advanceUntilIdle(); assertNotNull(c.state.value.pending)
        c.beginRemember(); assertNotEquals(MemoryScreen.Edit, c.state.value.screen)
        store.failRemove = false; c.checkPending(); advanceUntilIdle(); assertNull(c.state.value.pending)
        assertEquals(1, api.writes.size)
    }
    @Test fun mismatchedIdInputNeverReportsSuccessAndConflictPreservesPayload() = runTest {
        val (c, api, store) = ready(); api.claimFailure = ApiResult.Failure(ApiFailure.Conflict, "claim_id_reused")
        draft(c); c.savePreview(); advanceUntilIdle(); val saved = store.saved!!
        api.rows[saved.reservation.claimId] = memoryClaim(saved).copy(predicate = "different")
        c.checkPending(); advanceUntilIdle(); assertEquals(saved, store.saved); assertEquals(ApiFailure.Conflict, c.state.value.fault)
        assertNotNull(c.state.value.pending)
    }
    @Test fun explicitIdenticalReplayCanRecoverAfterAnotherClientCorrectedCommittedClaim() = runTest {
        val (c, api, store) = ready(); api.lostClaimDelivery = true
        draft(c); c.savePreview(); advanceUntilIdle(); val saved = store.saved!!
        val committed = api.rows[saved.reservation.claimId]!!
        api.rows[committed.id] = committed.copy(status = "superseded", valid_to = committed.valid_from + 1000, superseded_by = UUID.randomUUID())
        c.checkPending(); advanceUntilIdle(); assertNotNull(store.saved)
        api.lostClaimDelivery = false; c.resumePending(); advanceUntilIdle()
        assertNull(store.saved); assertEquals(2, api.writes.size); assertEquals(api.writes[0], api.writes[1])
        assertEquals("superseded", c.state.value.detail!!.status)
    }
    @Test fun invalidTimesAndCorrectionBoundariesStopBeforeReservation() = runTest {
        val (c, api, _) = ready(); draft(c)
        c.editPreview(); c.updateDraft(c.state.value.draft.copy(validFrom = "2026-10-09T10:00:00.000001Z")); c.preview()
        assertNull(c.state.value.preview); assertNotNull(c.state.value.validation)
        val src = memorySource(NoteInputDto(UUID.randomUUID(), "Old")); api.sourceRows[src.id] = src
        val old = ClaimDto(UUID.randomUUID(), memoryScope, "Project", "color", "Old", "fact", "active", 1000, 3000, null, 1, "user_asserted", exactEvidenceSelection(src, memoryScope, 0, 3))
        api.rows[old.id] = old; c.openClaim(old.id); advanceUntilIdle(); c.beginCorrection()
        for (time in listOf("1970-01-01T00:00:01.000Z", "1970-01-01T00:00:03.001Z")) {
            c.updateDraft(c.state.value.draft.copy(note = "New", value = "New", validFrom = time)); c.preview(); assertNull(c.state.value.preview)
        }
        c.updateDraft(c.state.value.draft.copy(validFrom = "1970-01-01T00:00:03.000Z", validTo = "1970-01-01T00:00:03.000Z")); c.preview(); assertNull(c.state.value.preview)
        c.updateDraft(c.state.value.draft.copy(validTo = "")); c.preview(); assertNotNull(c.state.value.preview)
    }
    @Test fun existingEvidenceRejectsModelScopeHashAndSplitSurrogate() = runTest {
        val (c, api, _) = ready(); c.beginRemember()
        val source = memorySource(NoteInputDto(UUID.randomUUID(), "😀 é\r\n日本語")); api.sourceRows[source.id] = source
        for (bad in listOf(source.copy(trust_class = "model_generated"), source.copy(scope_id = UUID.randomUUID()), source.copy(content_hash = "0".repeat(64)))) {
            c.selectSource(bad); assertNull(c.state.value.draft.selectedSource)
        }
        c.selectSource(source); c.updateDraft(c.state.value.draft.copy(subject = "A", predicate = "B", value = "C", startUtf16 = 1, endUtf16 = 2)); c.preview(); assertNull(c.state.value.preview)
        c.updateSelection(0, source.content.length); c.preview(); c.savePreview(); advanceUntilIdle()
        assertTrue(api.notes.isEmpty()); assertEquals(source.content.codePointCount(0, source.content.length), api.writes.single().span_end)
    }
    @Test fun annotationWhitespaceMatchesServerWhileEvidenceIsNeverNormalized() = runTest {
        val (c, _, _) = ready(); c.beginRemember()
        c.updateDraft(MemoryDraft(note = "\u0085 Exact 😀 \r\n", subject = "\u0085 Project \u0085", predicate = " color ", value = "\u0085 Blue \u0085"))
        c.preview(); val r = c.state.value.preview!!.reservation
        assertEquals("Project", r.subject); assertEquals("Blue", r.value); assertEquals("\u0085 Exact 😀 \r\n", r.note!!.content)
    }
    @Test fun unauthorizedHaltsAndHidesPrivateState() = runTest {
        var expired = 0; val store = MemoryWriteStore(); val api = MemoryWriteApi(store)
        val c = MemoryController(api, store, this) { expired++; cNotUsed() }
        c.setVerifiedSession(memoryConnection, memoryIdentity, memoryFeatures); advanceUntilIdle(); c.activate(); advanceUntilIdle()
        api.noteFailure = ApiResult.Failure(ApiFailure.Unauthorized); draft(c); c.savePreview(); advanceUntilIdle()
        assertEquals(1, expired); assertNull(c.state.value.pending); assertFalse(c.state.value.enabled); assertTrue(api.writes.isEmpty())
    }
    @Test fun queryModesAndLateScopeResponsesAreFenced() = runTest {
        val (c, api, _) = ready(); val old = CompletableDeferred<ApiResult<List<ClaimDto>>>()
        api.listCall = { _, _, history, at -> assertFalse(history && at != null); withContext(NonCancellable) { old.await() } }
        c.refreshClaims(); runCurrent(); c.setMode(MemoryMode.History)
        api.listCall = { _, _, history, at -> assertTrue(history); assertNull(at); ApiResult.Success(emptyList()) }
        c.applyQuery(); runCurrent(); old.complete(ApiResult.Success(listOf(memoryClaim(PendingMemory(MemoryReservation(memoryIdentity, memoryScope, UUID.randomUUID(), NoteInputDto(UUID.randomUUID(), "old"), null, "s", "p", "v", "fact"), memorySource(NoteInputDto(UUID.randomUUID(), "old")))))))
        advanceUntilIdle(); assertTrue(c.state.value.claims.items.isEmpty())
        c.setMode(MemoryMode.AsOf); c.updateAsOf("2026-10-09T10:00:00.123+02:00")
        api.listCall = { _, _, history, at -> assertFalse(history); assertEquals("2026-10-09T08:00:00.123Z", at); ApiResult.Success(emptyList()) }
        c.applyQuery(); advanceUntilIdle()
    }
    @Test fun overlapWarningsRespectHalfOpenIntervalsWithoutRanking() {
        val source = memorySource(NoteInputDto(UUID.randomUUID(), "a"))
        val a = ClaimDto(UUID.randomUUID(), memoryScope, "s", "p", "a", "fact", "superseded", 1, 10, UUID.randomUUID(), 1, "user_asserted", exactEvidenceSelection(source, memoryScope, 0, 1))
        val b = a.copy(id = UUID.randomUUID(), value = "b", valid_from = 10, valid_to = null)
        assertTrue(competingAssertions(listOf(a, b)).isEmpty()); assertEquals(setOf(a.id, b.id), competingAssertions(listOf(a, b.copy(valid_from = 9))))
    }
    @Test fun futureCorrectionRefreshNeverChangesCachedOriginalChatCitationOrFrozenProfile() = runTest {
        val store = MemoryWriteStore(); val memoryApi = MemoryWriteApi(store)
        val source = memorySource(NoteInputDto(UUID.randomUUID(), "Old color")); memoryApi.sourceRows[source.id] = source
        val old = memoryClaim(PendingMemory(MemoryReservation(memoryIdentity, memoryScope, UUID.randomUUID(),
            NoteInputDto(source.source_id, source.content), null, "Project", "color", "Old", "fact", "2026-10-01T00:00:00Z"), source))
        memoryApi.rows[old.id] = old
        val conversation = adaJson.decodeFromString<ConversationDto>(fixture("conversation-current.json")).copy(scope_id = memoryScope)
        val template = adaJson.decodeFromString<RequestDto>(fixture("request-current.json"))
        val original = template.copy(conversation_id = conversation.id, citations = listOf(template.citations.first().copy(
            claim_id = old.id, scope_id = memoryScope, valid_from = old.valid_from, valid_to = null, evidence = old.evidence)))
        val profile = PersonalityDto(UUID.randomUUID(), "New style", "formal", "reserved", "detailed")
        val api = object : AdaApi by memoryApi {
            override suspend fun me(connection: ConnectionCredential) = ApiResult.Success(MeDto(memoryIdentity.owner, "Test owner"))
            override suspend fun capabilities(connection: ConnectionCredential) = ApiResult.Success(memoryFeatures)
            override suspend fun personalities(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(profile))
            override suspend fun conversations(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(conversation))
            override suspend fun conversation(connection: ConnectionCredential, id: UUID) = ApiResult.Success(conversation)
            override suspend fun events(connection: ConnectionCredential, id: UUID, limit: Int, offset: Int) = ApiResult.Success(emptyList<EventDto>())
            override suspend fun request(connection: ConnectionCredential, id: UUID) = ApiResult.Success(original)
        }
        val vm = ChatViewModel(api, store, false)
        vm.connect("https://ada.test", "synthetic-token"); advanceUntilIdle()
        vm.openConversation(conversation.id); advanceUntilIdle(); vm.openSources(original.request_id); advanceUntilIdle()
        val cached = vm.state.value.sources[original.request_id]!!
        vm.memory.activate(); advanceUntilIdle(); vm.memory.openClaim(old.id); advanceUntilIdle(); vm.memory.beginCorrection()
        vm.memory.updateDraft(vm.memory.state.value.draft.copy(note = "New color", value = "New", validFrom = "2030-01-01T00:00:00.123Z"))
        vm.memory.preview(); vm.memory.savePreview(); advanceUntilIdle()
        assertEquals("superseded", memoryApi.rows[old.id]!!.status)
        assertEquals(1893456000123L, memoryApi.rows[old.id]!!.valid_to)
        assertSame(cached, vm.state.value.sources[original.request_id]); assertNull(cached.citations.single().valid_to)
        vm.selectProfile(profile.id); vm.beginCreate(); advanceUntilIdle()
        assertEquals(profile.id, vm.state.value.createProfileId); assertEquals(conversation.personality, vm.state.value.conversation!!.personality)
        vm.logout(); advanceUntilIdle(); assertTrue(vm.state.value.sources.isEmpty()); assertFalse(vm.memory.state.value.enabled)
    }
    @Test fun resetFencesUncancellableLateOwnerResultsAndValidationRetainsReservedInput() = runTest {
        val (c, api, store) = ready(); api.claimFailure = ApiResult.Failure(ApiFailure.Validation, "invalid_validity_interval")
        draft(c); c.savePreview(); advanceUntilIdle(); val saved = store.saved!!
        assertEquals(saved, c.state.value.pending); assertEquals(ApiFailure.Validation, c.state.value.fault)
        val late = CompletableDeferred<ApiResult<List<ClaimDto>>>()
        api.listCall = { _, _, _, _ -> withContext(NonCancellable) { late.await() } }
        c.refreshClaims(); runCurrent(); c.reset(); late.complete(ApiResult.Success(listOf(memoryClaim(saved)))); advanceUntilIdle()
        assertTrue(c.state.value.claims.items.isEmpty()); assertNull(c.state.value.pending); assertFalse(c.state.value.enabled)
    }
    @Test fun lateSameSessionUnauthorizedReadExpiresEvenAfterChangingView() = runTest {
        var expired = 0; val store = MemoryWriteStore(); val api = MemoryWriteApi(store)
        val c = MemoryController(api, store, this) { expired++ }
        c.setVerifiedSession(memoryConnection, memoryIdentity, memoryFeatures); advanceUntilIdle(); c.activate(); advanceUntilIdle()
        val late = CompletableDeferred<ApiResult<List<ClaimDto>>>()
        api.listCall = { _, _, _, _ -> withContext(NonCancellable) { late.await() } }
        c.refreshClaims(); runCurrent()
        api.listCall = { _, _, _, _ -> ApiResult.Success(emptyList()) }; c.setMode(MemoryMode.History); runCurrent()
        late.complete(ApiResult.Failure(ApiFailure.Unauthorized)); advanceUntilIdle()
        assertEquals(1, expired); assertFalse(c.state.value.enabled); assertNull(c.state.value.pending)
    }
    @Test fun serverPaginationUsesActualOffsetsMergesStableIdsAndResetsForHistory() = runTest {
        val (c, api, _) = ready()
        val source = memorySource(NoteInputDto(UUID.randomUUID(), "Synthetic evidence"))
        val template = memoryClaim(PendingMemory(MemoryReservation(memoryIdentity, memoryScope, UUID.randomUUID(),
            NoteInputDto(source.source_id, source.content), null, "Project", "color", "Blue", "fact"), source))
        val rows = List(51) { template.copy(id = UUID.randomUUID()) }; val offsets = mutableListOf<Int>()
        api.listCall = { _, offset, _, _ -> offsets += offset; ApiResult.Success(rows.drop(offset).take(50)) }
        c.refreshClaims(); advanceUntilIdle(); assertTrue(c.state.value.claims.hasMore)
        c.loadMoreClaims(); c.loadMoreClaims(); advanceUntilIdle()
        assertEquals(listOf(0, 50), offsets); assertEquals(rows, c.state.value.claims.items); assertFalse(c.state.value.claims.hasMore)
        c.setMode(MemoryMode.History); advanceUntilIdle()
        assertEquals(0, offsets.last()); assertEquals(rows.take(50), c.state.value.claims.items)
    }
    private fun cNotUsed() = Unit
}
