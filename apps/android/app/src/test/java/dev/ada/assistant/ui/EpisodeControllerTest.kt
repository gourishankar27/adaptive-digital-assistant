package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.security.MessageDigest
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import org.junit.Assert.*
import org.junit.Test

private val episodeIdentity = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val episodeConnection = ConnectionCredential.parse(episodeIdentity.server, "synthetic-episode-token", false)!!
private val episodeCapabilities = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(episodes = "source_linked_v1", consolidation_jobs = "bounded_jobs_v1", consolidation_generation = true, consolidation_worker = true)
private val episodeConversation = ConversationDto(UUID.randomUUID(), "Synthetic", UUID.randomUUID(), "project", PersonalitySnapshotDto("ADA", "conversational", "warm", "balanced"), "ada-baseline-v4", 0, 1)
private val syntheticEpisodeText = "Synthetic message 😀 e\u0301"
private val episodeSource = SourceVersionDto(UUID.randomUUID(), UUID.randomUUID(), episodeConversation.scope_id, 1, syntheticEpisodeText, MessageDigest.getInstance("SHA-256").digest(syntheticEpisodeText.toByteArray()).joinToString("") { "%02x".format(it) }, "user_explicit", 1)
private val episodeEvent = EventDto(episodeSource.id, "user", syntheticEpisodeText, "user_explicit", UUID.randomUUID(), "completed", 1, episodeSource.id)
private class EpisodeStore : SessionStore {
    var journal: ConsolidationJournal? = null; var failSave = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun consolidationJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveConsolidationJournal(journal: ConsolidationJournal) { if (failSave) throw SessionStorageException(); validateConsolidationJournal(journal); this.journal = journal }
    override suspend fun removeConsolidationJournal(identity: SessionIdentity, jobId: UUID) { if (journal?.identity == identity && journal?.jobId == jobId) journal = null }
}
private fun unusedEpisodeApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected: ${method.name}") } as AdaApi
private class EpisodeApi(val store: EpisodeStore) : AdaApi by unusedEpisodeApi() {
    var posts = 0; var reads = 0; var lost = false; var foreign = false
    var gate: CompletableDeferred<ApiResult<ConsolidationJobDto>>? = null
    var job: ConsolidationJobDto? = null
    override suspend fun events(connection: ConnectionCredential, id: UUID, limit: Int, offset: Int) = ApiResult.Success(listOf(episodeEvent))
    override suspend fun source(connection: ConnectionCredential, id: UUID) = ApiResult.Success(episodeSource)
    override suspend fun episodes(connection: ConnectionCredential, scope: UUID, offset: Int) = ApiResult.Success(emptyList<EpisodeDto>())
    override suspend fun consolidationJobs(connection: ConnectionCredential, scope: UUID, offset: Int) = ApiResult.Success(emptyList<ConsolidationJobDto>())
    override suspend fun createConsolidationJob(connection: ConnectionCredential, journal: ConsolidationJournal): ApiResult<ConsolidationJobDto> {
        assertEquals(journal, store.journal); posts++
        val b = adaJson.decodeFromString<ConsolidationInputDto>(journal.body)
        job = ConsolidationJobDto(journal.jobId, journal.identity.owner, journal.scopeId, b.kind, "consolidation-v1", "queued", "reserved", 0, "fixture", created_at = 1)
        return if (lost) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(if (foreign) job!!.copy(owner_id = UUID.randomUUID()) else job!!)
    }
    override suspend fun consolidationJob(connection: ConnectionCredential, id: UUID): ApiResult<ConsolidationJobDto> { reads++; return gate?.let { withContext(NonCancellable) { it.await() } } ?: ApiResult.Success(job!!) }
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class EpisodeControllerTest {
    private fun TestScope.ready(): Triple<EpisodeController, EpisodeApi, EpisodeStore> {
        val store = EpisodeStore(); val api = EpisodeApi(store); val c = EpisodeController(api, store, this, {})
        c.setVerifiedSession(episodeConnection, episodeIdentity, episodeCapabilities); advanceUntilIdle()
        c.activate(episodeConversation); advanceUntilIdle(); c.toggle(episodeEvent.id); c.preview("episode"); advanceUntilIdle()
        assertEquals(syntheticEpisodeText, c.state.value.preview!!.single().content)
        return Triple(c, api, store)
    }
    @Test fun reservationPrecedesPostDuplicateTapAndUnicodeUsesCodePoints() = runTest {
        val (c, api, store) = ready(); c.queue(); c.queue(); advanceUntilIdle()
        assertEquals(1, api.posts); assertEquals("queued", c.state.value.job!!.status)
        val b = adaJson.decodeFromString<ConsolidationInputDto>(store.journal!!.body)
        assertEquals(syntheticEpisodeText.codePointCount(0, syntheticEpisodeText.length), b.sources.single().span_end)
    }
    @Test fun lostDeliveryRestartReadsOriginalJobWithoutPost() = runTest {
        val (c, api, store) = ready(); api.lost = true; c.queue(); advanceUntilIdle()
        assertEquals(ApiFailure.Timeout, c.state.value.fault); val original = store.journal
        c.reset(); val restored = EpisodeController(api, store, this, {})
        restored.setVerifiedSession(episodeConnection, episodeIdentity, episodeCapabilities); advanceUntilIdle()
        assertEquals(1, api.posts); assertEquals(1, api.reads); assertEquals(original, restored.state.value.journal)
        assertEquals("queued", restored.state.value.job!!.status)
    }
    @Test fun immediateHistoryNavigationCannotHideReservationWhileStoreRestores() = runTest {
        val (c, api, store) = ready(); api.lost = true; c.queue(); advanceUntilIdle()
        val original = store.journal; c.reset(); val restored = EpisodeController(api, store, this, {})
        restored.setVerifiedSession(episodeConnection, episodeIdentity, episodeCapabilities)
        restored.activate(episodeConversation)
        advanceUntilIdle()
        assertEquals(original, restored.state.value.journal)
        assertEquals(original!!.jobId, restored.state.value.job!!.id)
        assertEquals(1, api.posts); assertEquals(1, api.reads)
    }
    @Test fun discardingLocalRecoveryRestoresConversationSelectionWithoutServerWrite() = runTest {
        val (c, api, store) = ready(); c.queue(); advanceUntilIdle(); c.reset()
        val restored = EpisodeController(api, store, this, {})
        restored.setVerifiedSession(episodeConnection, episodeIdentity, episodeCapabilities); advanceUntilIdle()
        restored.activate(episodeConversation); advanceUntilIdle(); assertTrue(restored.state.value.events.isEmpty())
        restored.discard(); advanceUntilIdle()
        assertNull(store.journal); assertEquals(listOf(episodeEvent), restored.state.value.events)
        assertEquals(1, api.posts); assertNotNull(api.job)
    }
    @Test fun encryptionFailurePreventsSubmissionAndForeignAcknowledgmentCannotConfirm() = runTest {
        val (c, api, store) = ready(); store.failSave = true; c.queue(); advanceUntilIdle(); assertEquals(0, api.posts)
        store.failSave = false; api.foreign = true; c.queue(); advanceUntilIdle()
        assertNotNull(store.journal); assertNull(c.state.value.job); assertEquals(ApiFailure.IncompatibleContract, c.state.value.fault)
    }
    @Test fun unsupportedServerCannotQueueAndResetClearsPrivateViews() = runTest {
        val (c, api, store) = ready(); c.setVerifiedSession(episodeConnection, episodeIdentity, episodeCapabilities.copy(episodes = "unsupported")); advanceUntilIdle()
        c.activate(episodeConversation); c.preview("episode"); c.queue(); advanceUntilIdle()
        assertEquals(0, api.posts); assertTrue(c.state.value.events.isEmpty()); assertNull(c.state.value.preview)
    }
    @Test fun lateOldOwner401DoesNotExpireNewVerifiedSession() = runTest {
        val (c, api, store) = ready(); c.queue(); advanceUntilIdle(); val delayed = CompletableDeferred<ApiResult<ConsolidationJobDto>>()
        api.gate = delayed; c.refresh(); runCurrent()
        c.setVerifiedSession(episodeConnection, episodeIdentity.copy(owner = UUID.randomUUID()), episodeCapabilities); runCurrent()
        delayed.complete(ApiResult.Failure(ApiFailure.Unauthorized)); advanceUntilIdle()
        assertTrue(c.state.value.enabled); assertNull(c.state.value.journal); assertNull(c.state.value.job)
    }
}
