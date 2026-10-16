package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

private class SecurityStore : SessionStore {
    var journal: SecurityJournal? = null
    var fail = false
    override suspend fun securityJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveSecurityJournal(journal: SecurityJournal) { if (fail) throw SessionStorageException(); this.journal = journal }
    override suspend fun removeSecurityJournal(identity: SessionIdentity, operation: UUID) { if (journal?.identity == identity && journal?.operation == operation) journal = null }
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) = Unit
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) = Unit
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) = Unit
}

class SecurityControllerTest {
    private val identity = SessionIdentity("http://localhost:8000/", UUID.randomUUID())
    private val connection = ConnectionCredential.parse(identity.server, "synthetic-security", true)!!
    private val features = adaJson.decodeFromString<CapabilitiesDto>(javaClass.classLoader!!.getResource("capabilities-current.json")!!.readText())
        .copy(device_credentials = "ada-device-credentials-v1", private_deletion = "ada-private-deletion-v1")
    private fun status(owner: UUID = identity.owner) = SecurityStatusDto(owner, null, true, true, true, 0, "until_explicit_owner_deletion")
    private var issueCalls = 0
    private var deleteCalls = 0
    private var readCalls = 0
    private var result: ApiResult<CredentialIssueDto> = ApiResult.Failure(ApiFailure.Timeout)
    private var gate: CompletableDeferred<Unit>? = null
    private var recovered = "queued"
    private val api = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, args ->
        when (method.name) {
            "securityStatus" -> ApiResult.Success(status())
            "credentials" -> ApiResult.Success(emptyList<DeviceCredentialDto>())
            "deletions" -> ApiResult.Success(emptyList<DeletionDto>())
            "issueCredential" -> { issueCalls++; result }
            "deletion" -> { readCalls++; ApiResult.Success(DeletionDto(args[1] as UUID, recovered, 1, 1, null, null, emptyMap(), true, true)) }
            "deleteContent" -> { deleteCalls++; ApiResult.Failure(ApiFailure.Timeout) }
            else -> error("Unexpected security test API call")
        }
    } as AdaApi
    @Test fun failedReservationNeverIssuesAndUnknownResultRetainsExactOperation() = runTest {
        val store = SecurityStore(); val controller = SecurityController(api, store, this, {}, { _, _ -> }, {})
        controller.setVerifiedSession(connection, identity, features); advanceUntilIdle()
        store.fail = true; controller.enroll("Synthetic phone"); advanceUntilIdle()
        assertEquals(0, issueCalls); assertNull(store.journal)
        store.fail = false; controller.enroll("Synthetic phone"); controller.enroll("Another tap"); advanceUntilIdle()
        assertEquals(1, issueCalls)
        val original = store.journal!!
        controller.refresh(); advanceUntilIdle(); assertEquals(original, controller.state.value.pending)
        assertEquals(1, issueCalls)
        controller.retrySaved(); advanceUntilIdle(); assertEquals(2, issueCalls); assertEquals(original, store.journal)
    }
    @Test fun savedDeletionRestoresByGetAndCompletionClearsThroughOwnerCallback() = runTest {
        val store = SecurityStore(); store.journal = SecurityJournal(identity, "delete", UUID.randomUUID(), preview = UUID.randomUUID())
        var erased = 0
        val controller = SecurityController(api, store, this, {}, { _, _ -> }, { erased++ })
        controller.setVerifiedSession(connection, identity, features); advanceUntilIdle()
        assertEquals(1, readCalls); assertEquals(0, deleteCalls); assertEquals(0, erased)
        recovered = "completed"; controller.refresh(); advanceUntilIdle()
        assertEquals(1, erased); assertEquals(0, deleteCalls)
    }
    @Test fun foreignOwnerStatusDoesNotLoadDeviceList() = runTest {
        var reads = 0; var expired = 0
        val foreign = object : AdaApi by api {
            override suspend fun securityStatus(connection: ConnectionCredential) = ApiResult.Success(status(UUID.randomUUID()))
            override suspend fun credentials(connection: ConnectionCredential): ApiResult<List<DeviceCredentialDto>> { reads++; return ApiResult.Success(emptyList()) }
        }
        val controller = SecurityController(foreign, SecurityStore(), this, { expired++ }, { _, _ -> }, {})
        controller.setVerifiedSession(connection, identity, features); advanceUntilIdle()
        assertEquals(1, expired); assertEquals(0, reads)
    }
    @Test fun lateOldAccountIssueCannotRepopulatePrivateState() = runTest {
        val wait = CompletableDeferred<Unit>()
        val late = object : AdaApi by api {
            override suspend fun issueCredential(connection: ConnectionCredential, journal: SecurityJournal): ApiResult<CredentialIssueDto> = withContext(NonCancellable) {
                wait.await(); ApiResult.Success(CredentialIssueDto(DeviceCredentialDto(journal.operation, journal.label, 1, 2, null, null, null), "synthetic-late-secret"))
            }
        }
        val controller = SecurityController(late, SecurityStore(), this, {}, { _, _ -> fail("Late token installed") }, {})
        controller.setVerifiedSession(connection, identity, features); advanceUntilIdle()
        controller.enroll("Synthetic phone"); runCurrent(); controller.reset(); wait.complete(Unit); advanceUntilIdle()
        assertNull(controller.state.value.issued); assertFalse(controller.state.value.enabled)
    }
}
