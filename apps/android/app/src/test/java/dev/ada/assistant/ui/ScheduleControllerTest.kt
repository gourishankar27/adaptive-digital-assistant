package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

private val scheduleOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val scheduleConn = ConnectionCredential.parse(scheduleOwner.server, "synthetic-scheduling-credential", false)!!
private val scheduleCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(scheduling_protocol = "ada-scheduling-v1")
private class ScheduleTestStore : SessionStore {
    var journal: ScheduleJournal? = null; var fail = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun scheduleJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveScheduleOperation(identity: SessionIdentity, operation: SchedulePending) {
        if (fail) throw SessionStorageException()
        val old = journal?.operations ?: emptyList()
        journal = ScheduleJournal(identity, old + operation).also(::validateScheduleJournal)
    }
    override suspend fun removeScheduleOperation(identity: SessionIdentity, operationId: UUID) { journal = journal?.copy(operations = journal!!.operations.filter { it.operationId != operationId }) }
}
private fun unusedScheduleApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected ${method.name}") } as AdaApi
private class ScheduleTestApi(val store: ScheduleTestStore) : AdaApi by unusedScheduleApi() {
    var posts = 0; var gets = 0; var unknown = false; var busy = false
    var inboxWait: CompletableDeferred<Unit>? = null
    var policy = SchedulePolicyDto("ada-scheduling-v1",1,false,true,"foreground_in_app",false)
    var rows = emptyList<ScheduleInboxDto>()
    val saved = mutableMapOf<UUID, ScheduleReceiptDto>()
    val posted = mutableListOf<SchedulePending>()
    override suspend fun schedulePolicy(connection: ConnectionCredential): ApiResult<SchedulePolicyDto> { gets++; return ApiResult.Success(policy) }
    override suspend fun scheduleInbox(connection: ConnectionCredential, offset: Int): ApiResult<List<ScheduleInboxDto>> {
        gets++; val snapshot = rows.drop(offset).take(100)
        inboxWait?.let { withContext(NonCancellable) { it.await() } }
        return ApiResult.Success(snapshot)
    }
    override suspend fun schedules(connection: ConnectionCredential, scope: UUID): ApiResult<List<ScheduleDto>> { gets++; return ApiResult.Success(emptyList()) }
    override suspend fun scheduleReceipt(connection: ConnectionCredential, operation: UUID): ApiResult<ScheduleReceiptDto> { gets++; return saved[operation]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound) }
    override suspend fun scheduleWrite(connection: ConnectionCredential, operation: SchedulePending): ApiResult<ScheduleReceiptDto> {
        assertTrue(store.journal!!.operations.contains(operation)); posts++; posted += operation
        if (busy) return ApiResult.Failure(ApiFailure.Busy(60))
        if (unknown) return ApiResult.Failure(ApiFailure.Unreachable)
        if (operation.kind == "preview") {
            val requested = adaJson.decodeFromString<SchedulePreviewDto>(operation.body).definition
            return ApiResult.Success(ScheduleReceiptDto("ada-scheduling-v1",operation.operationId,"preview","completed",
                definition=requested.copy(expires_at="2030-01-02T00:00:00.123000Z"), occurrences=listOf(SchedulePlanDto(1,"2030-01-01T08:00")), timezone_data="tzdata-test",preview_expires_at=Long.MAX_VALUE,created_at=1))
        }
        if (operation.kind == "policy") policy = policy.copy(revision = policy.revision + 1, enabled = adaJson.decodeFromString<SchedulePolicyWriteDto>(operation.body).enabled)
        return ApiResult.Success(ScheduleReceiptDto("ada-scheduling-v1", operation.operationId, operation.kind, "completed", created_at = 1))
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
class ScheduleControllerTest {
    @Test fun recoveredPreviewKeepsItsExactDraftUntilExplicitScopeReview() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store)
        val id = UUID.randomUUID(); val scopeId = UUID.randomUUID()
        val definition = ScheduleDefinitionDto(text="Original public draft.",timezone="Etc/UTC",start_local="2030-01-01T08:00",expires_at="2030-01-02T00:00:00.123Z")
        val op = SchedulePending(id,"preview",adaJson.encodeToString(SchedulePreviewDto(id,definition)),scopeId=scopeId)
        store.journal = ScheduleJournal(scheduleOwner,listOf(op))
        api.saved[id] = ScheduleReceiptDto("ada-scheduling-v1",id,"preview","completed",definition=definition.copy(expires_at="2030-01-02T00:00:00.123000Z"),occurrences=listOf(SchedulePlanDto(1,"2030-01-01T08:00")),timezone_data="tzdata-test",preview_expires_at=Long.MAX_VALUE,created_at=1)
        val controller = ScheduleController(api,store,backgroundScope) {}
        controller.setVerifiedSession(scheduleConn,scheduleOwner,scheduleCaps); runCurrent()
        assertEquals(0,api.posts); assertEquals(op,controller.state.value.pending.single()); assertNull(controller.state.value.preview)
        controller.reviewPreview(op); runCurrent()
        assertEquals(0,api.posts); assertEquals(scopeId,controller.state.value.scopeId)
        assertEquals(definition.text,controller.state.value.preview!!.definition!!.text)
        assertTrue(controller.state.value.pending.isEmpty())
    }
    @Test fun inboxPagesStayBoundedAndDoNotMixDifferentPages() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store)
        api.rows = (1..201).map { ScheduleInboxDto("ada-scheduling-v1",UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),"reminder","Public page sample.",state="unread",available_at=1,expires_at=Long.MAX_VALUE,created_at=it.toLong()) }.sortedByDescending { it.created_at }
        val controller = ScheduleController(api,store,backgroundScope) {}
        controller.setVerifiedSession(scheduleConn,scheduleOwner,scheduleCaps); runCurrent()
        val first = controller.state.value.inbox.map { it.id }.toSet(); assertEquals(100,first.size)
        controller.inboxPage(true); runCurrent()
        assertEquals(100,controller.state.value.inboxOffset); assertEquals(100,controller.state.value.inbox.size)
        assertTrue(controller.state.value.inbox.none { it.id in first })
        controller.inboxPage(true); runCurrent(); assertEquals(1,controller.state.value.inbox.size)
        controller.inboxPage(true); runCurrent(); assertEquals(200,controller.state.value.inboxOffset)
        controller.inboxPage(false); runCurrent(); assertEquals(100,controller.state.value.inboxOffset)
        assertEquals(0,api.posts)
    }
    @Test fun previewAcceptsEquivalentTimestampEncodingWithoutChangingReservedInput() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store)
        val controller = ScheduleController(api, store, backgroundScope) {}
        controller.setVerifiedSession(scheduleConn, scheduleOwner, scheduleCaps); controller.activate(UUID.randomUUID()); runCurrent()
        controller.preview(ScheduleDefinitionDto(text="Public sample.",timezone="Etc/UTC",start_local="2030-01-01T08:00",expires_at="2030-01-02T00:00:00.123Z")); runCurrent()
        assertNotNull(controller.state.value.preview)
        assertTrue(api.posted.single().body.contains("00:00:00.123Z"))
        assertTrue(controller.state.value.pending.isEmpty())
    }
    @Test fun diskFailurePreventsAnySchedulePost() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store)
        val controller = ScheduleController(api, store, backgroundScope) {}
        controller.setVerifiedSession(scheduleConn, scheduleOwner, scheduleCaps); runCurrent()
        store.fail = true; controller.setEnabled(true); runCurrent()
        assertEquals(0, api.posts); assertNull(store.journal); assertNotNull(controller.state.value.notice)
    }
    @Test fun unknownOutcomeRestoresByGetOnlyAndExplicitRetryKeepsExactPayload() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store); api.unknown = true
        val controller = ScheduleController(api, store, backgroundScope) {}
        controller.setVerifiedSession(scheduleConn, scheduleOwner, scheduleCaps); runCurrent()
        controller.setEnabled(true); runCurrent()
        val op = controller.state.value.pending.single()
        controller.reset()
        val restored = ScheduleController(api, store, backgroundScope) {}
        restored.setVerifiedSession(scheduleConn, scheduleOwner, scheduleCaps); runCurrent()
        assertEquals(1, api.posts); assertEquals(op, restored.state.value.pending.single())
        api.unknown = false; restored.retry(op); runCurrent()
        assertEquals(listOf(op,op), api.posted); assertTrue(restored.state.value.pending.isEmpty())
    }
    @Test fun latePrivateInboxCannotReturnAfterReset() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store)
        api.rows = listOf(ScheduleInboxDto("ada-scheduling-v1",UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),"reminder","Public test reminder",state="unread",available_at=1,expires_at=Long.MAX_VALUE,created_at=1))
        api.inboxWait = CompletableDeferred()
        val controller = ScheduleController(api, store, backgroundScope) {}
        controller.setVerifiedSession(scheduleConn, scheduleOwner, scheduleCaps); runCurrent()
        controller.reset(); api.inboxWait!!.complete(Unit); runCurrent()
        assertFalse(controller.state.value.supported); assertTrue(controller.state.value.inbox.isEmpty())
    }
    @Test fun pollingStopsInBackgroundAndResumesWithoutPosting() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store)
        val controller = ScheduleController(api, store, backgroundScope) {}
        controller.setVerifiedSession(scheduleConn, scheduleOwner, scheduleCaps); runCurrent()
        controller.observeForeground(false); val before = api.gets
        advanceTimeBy(61000); runCurrent(); assertEquals(before, api.gets)
        controller.observeForeground(true); advanceTimeBy(31000); runCurrent()
        assertTrue(api.gets > before); assertEquals(0, api.posts)
    }
    @Test fun quotaCooldownStillAllowsGlobalOffIntent() = runTest {
        val store = ScheduleTestStore(); val api = ScheduleTestApi(store)
        val controller = ScheduleController(api, store, backgroundScope) {}
        controller.setVerifiedSession(scheduleConn, scheduleOwner, scheduleCaps); runCurrent()
        api.busy = true; controller.setEnabled(true); runCurrent(); assertEquals(1, api.posts)
        api.busy = false; controller.setEnabled(false); runCurrent()
        assertEquals(2, api.posts); assertFalse(controller.state.value.policy!!.enabled)
    }
    @Test fun forgedUnsupportedKindNeverConstructsAWriteRoute() {
        assertThrows(IllegalStateException::class.java) { schedulePath(SchedulePending(UUID.randomUUID(),"reflection_shell","{}")) }
    }
}
