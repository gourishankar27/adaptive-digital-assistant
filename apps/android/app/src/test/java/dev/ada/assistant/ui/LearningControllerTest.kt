package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import org.junit.Assert.*
import org.junit.Test

private val learningOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val learningConnection = ConnectionCredential.parse(learningOwner.server, "synthetic-learning-token", false)!!
private val learningScope = UUID.randomUUID()
private val learningCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(interaction_learning = "ada-learning-v1")
private class LearningStore : SessionStore {
    var journal: LearningJournal? = null; var failSave = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun learningJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveLearningJournal(journal: LearningJournal) { if(failSave) throw SessionStorageException(); validateLearningJournal(journal); this.journal = journal }
    override suspend fun removeLearningJournal(identity: SessionIdentity, operationId: UUID) { if(journal?.identity == identity && journal?.operationId == operationId) journal = null }
}
private fun unusedLearningApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected: ${method.name}") } as AdaApi
private class LearningApi(private val store: LearningStore) : AdaApi by unusedLearningApi() {
    var posts = 0; var reads = 0; var lost = false; var foreign = false
    var data = LearningStateDto(LearningConfigDto(learningScope, 0, 0, "off", false, "ada-learning-v1", 3), emptyList(), emptyList(), emptyList())
    var receipt: LearningReceiptDto? = null
    var gate: CompletableDeferred<ApiResult<LearningStateDto>>? = null
    override suspend fun learning(connection: ConnectionCredential, scope: UUID): ApiResult<LearningStateDto> = gate?.let { withContext(NonCancellable) { it.await() } } ?: ApiResult.Success(data.copy(config = data.config.copy(scope_id = scope)))
    override suspend fun learningOperation(connection: ConnectionCredential, journal: LearningJournal): ApiResult<LearningReceiptDto> {
        assertEquals(journal, store.journal); posts++
        val input = adaJson.decodeFromString<LearningConfigWriteDto>(journal.body)
        data = data.copy(config = data.config.copy(revision = input.expected_revision + 1, status = input.status))
        receipt = LearningReceiptDto(journal.operationId, journal.scopeId, journal.action, data.config.revision, 0, created_at = 1)
        return if(lost) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(if(foreign) receipt!!.copy(scope_id = UUID.randomUUID()) else receipt!!)
    }
    override suspend fun learningReceipt(connection: ConnectionCredential, operation: UUID): ApiResult<LearningReceiptDto> { reads++; return ApiResult.Success(receipt!!) }
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class LearningControllerTest {
    private fun TestScope.ready(): Triple<LearningController, LearningApi, LearningStore> {
        val store = LearningStore(); val api = LearningApi(store); val c = LearningController(api, store, this, {})
        c.setVerifiedSession(learningConnection, learningOwner, learningCaps); advanceUntilIdle()
        c.activate(learningScope); advanceUntilIdle(); return Triple(c, api, store)
    }
    @Test fun reservationPrecedesPostAndDoubleTapCannotDuplicate() = runTest {
        val (c, api, store) = ready(); c.configure("enrolled"); c.configure("enrolled"); advanceUntilIdle()
        assertEquals(1, api.posts); assertNull(store.journal); assertEquals("enrolled", c.state.value.data!!.config.status)
    }
    @Test fun lostDeliveryRestartsByGetOnlyAndPreservesKey() = runTest {
        val (c, api, store) = ready(); api.lost = true; c.configure("enrolled"); advanceUntilIdle()
        val original = store.journal!!; c.reset()
        val restarted = LearningController(api, store, this, {}); restarted.setVerifiedSession(learningConnection, learningOwner, learningCaps); advanceUntilIdle()
        assertEquals(original.operationId, api.receipt!!.operation_id); assertEquals(1, api.posts); assertEquals(1, api.reads); assertNull(store.journal)
    }
    @Test fun failedDurableWritePreventsHttp() = runTest {
        val (c, api, store) = ready(); store.failSave = true; c.configure("enrolled"); advanceUntilIdle()
        assertEquals(0, api.posts); assertNull(store.journal); assertNotNull(c.state.value.fault)
    }
    @Test fun foreignReceiptCannotClearJournal() = runTest {
        val (c, api, store) = ready(); api.foreign = true; c.configure("enrolled"); advanceUntilIdle()
        assertNotNull(store.journal); assertEquals(ApiFailure.IncompatibleContract, c.state.value.fault)
    }
    @Test fun lateScopeReadCannotReplaceCurrentData() = runTest {
        val (c, api, _) = ready(); val pending = CompletableDeferred<ApiResult<LearningStateDto>>(); api.gate = pending
        c.refresh(); runCurrent(); api.gate = null; val other = UUID.randomUUID(); c.activate(other); runCurrent()
        pending.complete(ApiResult.Success(api.data)); advanceUntilIdle()
        assertEquals(other, c.state.value.data!!.config.scope_id)
    }
    @Test fun lateAccountReadCannotExposePriorProfile() = runTest {
        val (c, api, _) = ready(); val pending = CompletableDeferred<ApiResult<LearningStateDto>>(); api.gate = pending
        c.refresh(); runCurrent(); c.reset(); pending.complete(ApiResult.Success(api.data)); advanceUntilIdle()
        assertNull(c.state.value.data); assertNull(c.state.value.source)
    }
    @Test fun unknownPolicyDisablesWrites() = runTest {
        val (c, api, _) = ready(); c.setVerifiedSession(learningConnection, learningOwner, learningCaps.copy(interaction_learning = "future")); advanceUntilIdle()
        c.activate(learningScope); c.configure("enrolled"); advanceUntilIdle(); assertEquals(0, api.posts); assertFalse(c.state.value.enabled)
    }
}
