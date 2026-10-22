package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

private val reflectionOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val reflectionConnection = ConnectionCredential.parse(reflectionOwner.server, "public-synthetic-reflection-credential", false)!!
private val reflectionCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(reflection_protocol = "ada-reflection-v1")
private class ReflectionTestStore : SessionStore {
    var journal: ReflectionJournal? = null; var fail = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun reflectionJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveReflectionOperation(identity: SessionIdentity, operation: ReflectionPending) {
        if (fail) throw SessionStorageException()
        journal = ReflectionJournal(identity, journal?.operations.orEmpty() + operation).also(::validateReflectionJournal)
    }
    override suspend fun removeReflectionOperation(identity: SessionIdentity, operationId: UUID) { journal = journal?.copy(operations = journal!!.operations.filter { it.operationId != operationId }) }
}
private fun unusedReflectionApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected ${method.name}") } as AdaApi
private class ReflectionTestApi(val store: ReflectionTestStore) : AdaApi by unusedReflectionApi() {
    var posts = 0; var unknown = false; var wait: CompletableDeferred<Unit>? = null; var wrongReceipt = false
    var policy = ReflectionPolicyDto("ada-reflection-v1", 1, ReflectionSettingsDto(), true, true, false, foreground_idle_seconds = 0)
    val saved = mutableMapOf<UUID, ReflectionReceiptDto>(); val posted = mutableListOf<ReflectionPending>()
    override suspend fun reflectionPolicy(connection: ConnectionCredential): ApiResult<ReflectionPolicyDto> = ApiResult.Success(policy)
    override suspend fun reflectionArtifacts(connection: ConnectionCredential, offset: Int): ApiResult<List<ReflectionArtifactDto>> { wait?.let { withContext(NonCancellable) { it.await() } }; return ApiResult.Success(emptyList()) }
    override suspend fun reflectionRuns(connection: ConnectionCredential, offset: Int): ApiResult<List<ReflectionRunDto>> = ApiResult.Success(emptyList())
    override suspend fun reflectionReceipt(connection: ConnectionCredential, operation: UUID): ApiResult<ReflectionReceiptDto> = saved[operation]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun reflectionWrite(connection: ConnectionCredential, operation: ReflectionPending): ApiResult<ReflectionReceiptDto> {
        assertTrue(store.journal!!.operations.contains(operation)); posts++; posted += operation
        if (unknown) return ApiResult.Failure(ApiFailure.Unreachable)
        val b = adaJson.decodeFromString<ReflectionPolicyWriteDto>(operation.body)
        policy = policy.copy(revision = policy.revision + 1, settings = b.settings)
        val r = ReflectionReceiptDto("ada-reflection-v1", if (wrongReceipt) UUID.randomUUID() else operation.operationId, "policy", "completed", revision = policy.revision, created_at = 1)
        saved[operation.operationId] = r
        return ApiResult.Success(r)
    }
}
@OptIn(ExperimentalCoroutinesApi::class)
class ReflectionControllerTest {
    @Test fun unknownOutcomeRestartReadsOnlyAndRetryUsesExactOriginalInput() = runTest {
        val store = ReflectionTestStore(); val api = ReflectionTestApi(store); api.unknown = true
        val c = ReflectionController(api, store, backgroundScope) {}
        c.setVerifiedSession(reflectionConnection, reflectionOwner, reflectionCaps); runCurrent()
        c.save(ReflectionSettingsDto(enabled = true, scope_ids = listOf(UUID.randomUUID()))); runCurrent()
        val original = c.state.value.pending.single(); assertEquals(1, api.posts); c.reset()
        val restored = ReflectionController(api, store, backgroundScope) {}
        restored.setVerifiedSession(reflectionConnection, reflectionOwner, reflectionCaps); runCurrent()
        assertEquals(1, api.posts); assertEquals(original, restored.state.value.pending.single())
        api.unknown = false; restored.retry(original); runCurrent()
        assertEquals(listOf(original, original), api.posted); assertTrue(restored.state.value.pending.isEmpty())
    }
    @Test fun diskFailurePreventsPost() = runTest {
        val store = ReflectionTestStore(); val api = ReflectionTestApi(store); val c = ReflectionController(api, store, backgroundScope) {}
        c.setVerifiedSession(reflectionConnection, reflectionOwner, reflectionCaps); runCurrent(); store.fail = true
        c.save(ReflectionSettingsDto()); runCurrent(); assertEquals(0, api.posts); assertNotNull(c.state.value.notice)
    }
    @Test fun mismatchedReceiptCannotClearExactJournal() = runTest {
        val store = ReflectionTestStore(); val api = ReflectionTestApi(store); val c = ReflectionController(api, store, backgroundScope) {}
        c.setVerifiedSession(reflectionConnection, reflectionOwner, reflectionCaps); runCurrent(); api.wrongReceipt = true
        c.save(ReflectionSettingsDto()); runCurrent(); assertEquals(1, c.state.value.pending.size); assertNotNull(c.state.value.notice)
    }
    @Test fun resetFencesLatePrivateRead() = runTest {
        val store = ReflectionTestStore(); val api = ReflectionTestApi(store); val c = ReflectionController(api, store, backgroundScope) {}
        api.wait = CompletableDeferred(); c.setVerifiedSession(reflectionConnection, reflectionOwner, reflectionCaps); runCurrent()
        c.reset(); api.wait!!.complete(Unit); runCurrent(); assertNull(c.state.value.policy); assertTrue(c.state.value.artifacts.isEmpty())
    }
    @Test fun unsupportedServerDoesNotReadOrWrite() = runTest {
        val store = ReflectionTestStore(); val c = ReflectionController(unusedReflectionApi(), store, backgroundScope) {}
        c.setVerifiedSession(reflectionConnection, reflectionOwner, reflectionCaps.copy(reflection_protocol = "disabled")); runCurrent()
        c.refresh(); c.save(ReflectionSettingsDto()); runCurrent(); assertFalse(c.state.value.supported)
    }
}
