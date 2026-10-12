package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import org.junit.Assert.*
import org.junit.Test

private val expressionOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val expressionConnection = ConnectionCredential.parse(expressionOwner.server, "synthetic-expression-token", false)!!
private val expressionCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(interaction_preferences = "explicit_settings_v1", session_expression = "ada-expression-v1")
private class ExpressionStore : SessionStore {
    var journal: ExpressionJournal? = null; var failSave = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun expressionJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveExpressionJournal(journal: ExpressionJournal) { if (failSave) throw SessionStorageException(); validateExpressionJournal(journal); this.journal = journal }
    override suspend fun removeExpressionJournal(identity: SessionIdentity, operationId: UUID) { if (journal?.identity == identity && journal?.operationId == operationId) journal = null }
}
private fun unusedExpressionApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected: ${method.name}") } as AdaApi
private class ExpressionApi(private val store: ExpressionStore) : AdaApi by unusedExpressionApi() {
    var posts = 0; var reads = 0; var lost = false; var foreign = false
    var pref = PreferenceDto("account", expressionOwner.owner, 0, PreferenceValuesDto())
    var receipt: ExpressionReceiptDto? = null
    var gate: CompletableDeferred<ApiResult<PreferenceDto>>? = null
    override suspend fun preference(connection: ConnectionCredential, kind: String, target: UUID): ApiResult<PreferenceDto> = gate?.let { withContext(NonCancellable) { it.await() } } ?: ApiResult.Success(pref)
    override suspend fun expressionOperation(connection: ConnectionCredential, journal: ExpressionJournal): ApiResult<ExpressionReceiptDto> {
        assertEquals(journal, store.journal); posts++
        val input = adaJson.decodeFromString<PreferenceWriteDto>(journal.body)
        pref = pref.copy(revision = input.expected_revision + 1, values = input.values, receipt_id = journal.operationId)
        receipt = ExpressionReceiptDto(journal.operationId, journal.action, journal.targetKind, journal.targetId, 1, preference = pref)
        return if (lost) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(if (foreign) receipt!!.copy(target_id = UUID.randomUUID()) else receipt!!)
    }
    override suspend fun expressionReceipt(connection: ConnectionCredential, operation: UUID): ApiResult<ExpressionReceiptDto> { reads++; return ApiResult.Success(receipt!!) }
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class ExpressionControllerTest {
    private fun TestScope.ready(): Triple<ExpressionController, ExpressionApi, ExpressionStore> {
        val store = ExpressionStore(); val api = ExpressionApi(store); val c = ExpressionController(api, store, this, {})
        c.setVerifiedSession(expressionConnection, expressionOwner, expressionCaps); advanceUntilIdle()
        c.edit(PreferenceValuesDto(verbosity = "concise", humor = "none"))
        return Triple(c, api, store)
    }
    @Test fun exactReservationPrecedesPostAndDoubleTapCreatesOneReceipt() = runTest {
        val (c, api, store) = ready(); c.save(); c.save(); advanceUntilIdle()
        assertEquals(1, api.posts); assertNull(store.journal); assertEquals("concise", c.state.value.preference?.values?.verbosity)
    }
    @Test fun lostDeliveryRestartUsesGetOnlyAndRetainsExactSettings() = runTest {
        val (c, api, store) = ready(); api.lost = true; c.save(); advanceUntilIdle()
        assertNotNull(store.journal)
        val restarted = ExpressionController(api, store, this, {})
        restarted.setVerifiedSession(expressionConnection, expressionOwner, expressionCaps); advanceUntilIdle()
        assertEquals(1, api.posts); assertEquals(1, api.reads); assertNull(store.journal)
        assertEquals("concise", restarted.state.value.preference?.values?.verbosity)
    }
    @Test fun storageFailurePreventsWrite() = runTest {
        val (c, api, store) = ready(); store.failSave = true; c.save(); advanceUntilIdle()
        assertEquals(0, api.posts); assertNull(store.journal); assertNotNull(c.state.value.fault)
    }
    @Test fun foreignReceiptCannotClearSavedChange() = runTest {
        val (c, api, store) = ready(); api.foreign = true; c.save(); advanceUntilIdle()
        assertNotNull(store.journal); assertEquals(ApiFailure.IncompatibleContract, c.state.value.fault)
    }
    @Test fun lateAccountReadCannotPopulateDisconnectedSettings() = runTest {
        val (c, api, _) = ready(); api.gate = CompletableDeferred(); c.refresh(); runCurrent(); c.reset()
        api.gate!!.complete(ApiResult.Success(api.pref)); advanceUntilIdle()
        assertNull(c.state.value.preference); assertFalse(c.state.value.enabled)
    }
    @Test fun unknownCapabilityDoesNotOfferWorkingSettings() = runTest {
        val (c, api, _) = ready(); c.setVerifiedSession(expressionConnection, expressionOwner, expressionCaps.copy(session_expression = "future-policy")); advanceUntilIdle()
        c.save(); advanceUntilIdle(); assertEquals(0, api.posts); assertFalse(c.state.value.enabled)
    }
}
