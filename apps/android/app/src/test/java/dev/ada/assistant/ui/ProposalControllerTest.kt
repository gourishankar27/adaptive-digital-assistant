package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.JsonObject
import org.junit.Assert.*
import org.junit.Test

private val reviewScope = UUID.randomUUID()
private val reviewIdentity = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val reviewConnection = ConnectionCredential.parse(reviewIdentity.server, "synthetic-review-token", false)!!
private val reviewCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(memory_proposals = "selected_sources_v1", memory_review = true, memory_provenance = "review-v1")
private fun suggestion(): ProposalDto {
    val pin = SourcePinDto(UUID.randomUUID(), 1, "a".repeat(64), 0, 3)
    val candidate = ProposalCandidateDto("Mira", "drink", "tea", "preference", "2026-10-01T00:00:00Z", support = listOf(pin))
    return ProposalDto(UUID.randomUUID(), reviewScope, UUID.randomUUID(), "pending", 1, candidate, candidate, "synthetic", "selected-sources-v1", JsonObject(emptyMap()), emptyList(), emptyList(), "a".repeat(64), created_at = 1)
}
private class ReviewStore : SessionStore {
    var saved: PendingProposal? = null; var draft: ProposalDraft? = null; var failSave = false; var failRemove = false
    val events = mutableListOf<String>()
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { saved = null; draft = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun proposalPending(identity: SessionIdentity) = saved?.takeIf { it.identity == identity }
    override suspend fun proposalDraft(identity: SessionIdentity) = draft?.takeIf { it.identity == identity }
    override suspend fun saveProposalDraft(draft: ProposalDraft) { this.draft = draft }
    override suspend fun removeProposalDraft(identity: SessionIdentity) { draft = null }
    override suspend fun saveProposalPending(pending: PendingProposal) { if (failSave) throw SessionStorageException(); require(saved == null || saved == pending); saved = pending; events += "reserve" }
    override suspend fun removeProposalPending(identity: SessionIdentity, operationId: UUID) { if (failRemove) throw SessionStorageException(); if (saved?.identity == identity && saved?.operationId == operationId) saved = null; events += "remove" }
}
private fun unexpectedReviewApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected call: ${method.name}") } as AdaApi
private class ReviewApi(val store: ReviewStore) : AdaApi by unexpectedReviewApi() {
    val p = suggestion(); val posts = mutableListOf<PendingProposal>(); val receipts = mutableMapOf<UUID, ReviewReceiptDto>()
    var lost = false; var mismatch = false
    var listCall: suspend () -> ApiResult<List<ProposalDto>> = { ApiResult.Success(listOf(p)) }
    override suspend fun me(connection: ConnectionCredential) = ApiResult.Success(MeDto(reviewIdentity.owner, "Synthetic"))
    override suspend fun scopes(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(ScopeDto(reviewScope, "Synthetic", "project", 1)))
    override suspend fun proposals(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int) = listCall()
    override suspend fun proposal(connection: ConnectionCredential, id: UUID) = ApiResult.Success(p)
    override suspend fun sources(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int) = ApiResult.Success(emptyList<SourceVersionDto>())
    override suspend fun documentUploads(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int) = ApiResult.Success(emptyList<DocumentUploadDto>())
    override suspend fun entities(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int) = ApiResult.Success(emptyList<EntityDto>())
    override suspend fun reviewReceipt(connection: ConnectionCredential, id: UUID): ApiResult<ReviewReceiptDto> = receipts[id]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun reviewProposal(connection: ConnectionCredential, pending: PendingProposal): ApiResult<ReviewReceiptDto> {
        assertEquals(pending, store.saved); posts += pending; store.events += "post"
        val b = adaJson.decodeFromString<ProposalReviewDto>(pending.body)
        val r = receipts.getOrPut(pending.operationId) { ReviewReceiptDto(pending.operationId, p.id, reviewScope, reviewIdentity.owner, b.decision, b.revision, b.review_hash, UUID.randomUUID(), UUID.randomUUID(), 1) }
        return if (lost) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(if (mismatch) r.copy(scope_id = UUID.randomUUID()) else r)
    }
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class ProposalControllerTest {
    private fun TestScope.ready(store: ReviewStore = ReviewStore()): Triple<ProposalController, ReviewApi, ReviewStore> {
        val api = ReviewApi(store); val c = ProposalController(api, store, this, {})
        c.setVerifiedSession(reviewConnection, reviewIdentity, reviewCaps); advanceUntilIdle(); c.activate(); advanceUntilIdle(); c.open(api.p); advanceUntilIdle(); c.draft(annotation = "I reviewed this synthetic annotation."); advanceUntilIdle()
        return Triple(c, api, store)
    }
    @Test fun doubleAcceptReservesBeforePostAndCreatesOneReceipt() = runTest {
        val (c, api, store) = ready(); c.decide("accept"); c.decide("accept"); advanceUntilIdle()
        assertEquals(listOf("reserve", "post", "remove"), store.events); assertEquals(1, api.receipts.size); assertNull(store.saved)
    }
    @Test fun lossRestoresDraftAndExactKeyWithoutAutomaticPost() = runTest {
        val (c, api, store) = ready(); api.lost = true; c.decide("accept"); advanceUntilIdle(); val pending = store.saved!!; val draft = store.draft!!
        c.reset(); val restored = ProposalController(api, store, this, {}); restored.setVerifiedSession(reviewConnection, reviewIdentity, reviewCaps); advanceUntilIdle()
        assertEquals(pending, restored.state.value.pending); assertEquals(draft, restored.state.value.draft); assertEquals(1, api.posts.size)
        api.lost = false; restored.retry(); advanceUntilIdle(); assertEquals(listOf(pending, pending), api.posts); assertEquals(1, api.receipts.size); assertNull(store.saved)
    }
    @Test fun storageFailureAndUnpreviewedEditsNeverSubmitApproval() = runTest {
        val (c, api, store) = ready(); c.draft(candidate = api.p.candidate.copy(value = "coffee")); advanceUntilIdle(); c.decide("accept"); advanceUntilIdle(); assertTrue(api.posts.isEmpty())
        c.draft(candidate = api.p.candidate); advanceUntilIdle(); store.failSave = true; c.decide("accept"); advanceUntilIdle(); assertTrue(api.posts.isEmpty()); assertNull(store.saved)
    }
    @Test fun invalidReceiptAndFailedCleanupRetainExactReservation() = runTest {
        val (c, api, store) = ready(); api.mismatch = true; c.decide("accept"); advanceUntilIdle(); assertNotNull(store.saved)
        store.failRemove = true; c.check(); advanceUntilIdle(); assertNotNull(store.saved); c.decide("accept"); advanceUntilIdle(); assertEquals(1, api.posts.size)
        store.failRemove = false; c.check(); advanceUntilIdle(); assertNull(store.saved)
    }
    @Test fun oldOwnersLate401CannotEraseNewSession() = runTest {
        val (c, api, store) = ready(); var expired = false
        val late = CompletableDeferred<ApiResult<List<ProposalDto>>>(); api.listCall = { withContext(NonCancellable) { late.await() } }
        c.refresh(); runCurrent(); api.listCall = { ApiResult.Success(emptyList()) }
        c.setVerifiedSession(reviewConnection, reviewIdentity.copy(owner = UUID.randomUUID()), reviewCaps); runCurrent(); late.complete(ApiResult.Failure(ApiFailure.Unauthorized)); advanceUntilIdle(); assertTrue(c.state.value.enabled)
        val current = ProposalController(api, store, this, { expired = true }); current.setVerifiedSession(reviewConnection, reviewIdentity, reviewCaps); advanceUntilIdle(); api.listCall = { ApiResult.Failure(ApiFailure.Unauthorized) }; current.activate(); advanceUntilIdle(); assertTrue(expired); assertNull(current.state.value.draft)
    }
    @Test fun legacyCapabilitiesKeepReviewDisabled() = runTest {
        val store = ReviewStore(); val api = ReviewApi(store); val c = ProposalController(api, store, this, {})
        c.setVerifiedSession(reviewConnection, reviewIdentity, reviewCaps.copy(memory_proposals = "unsupported")); advanceUntilIdle(); c.activate(); advanceUntilIdle(); assertFalse(c.state.value.enabled); assertTrue(c.state.value.inbox.items.isEmpty())
    }
}
