package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

private val curiousOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val curiousConn = ConnectionCredential.parse(curiousOwner.server, "synthetic-curiosity-token", false)!!
private val curiousCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(curiosity_protocol = "ada-curiosity-v1")
private class CuriousStore : SessionStore {
    var journal: CuriosityJournal? = null; var fail = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun curiosityJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveCuriosityOperation(identity: SessionIdentity, operation: CuriosityPending) {
        if (fail) throw SessionStorageException()
        val old = journal?.operations ?: emptyList()
        journal = CuriosityJournal(identity, old + operation).also(::validateCuriosityJournal)
    }
    override suspend fun removeCuriosityOperation(identity: SessionIdentity, operationId: UUID) { journal = journal?.copy(operations = journal!!.operations.filter { it.operationId != operationId }) }
}
private fun unusedCuriosityApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected ${method.name}") } as AdaApi
private class CuriousApi(val store: CuriousStore) : AdaApi by unusedCuriosityApi() {
    var original: SourceVersionDto? = null; var sourceWait: CompletableDeferred<Unit>? = null
    override suspend fun source(connection: ConnectionCredential, id: UUID): ApiResult<SourceVersionDto> { sourceWait?.let { withContext(NonCancellable) { it.await() } }; return ApiResult.Success(original!!) }
    var policy = CuriosityPolicyDto("ada-curiosity-v1", 1, CuriositySettingsDto(enabled = true), "UTC", 2, 10, 30, 0)
    var posts = 0; var gets = 0; var wait: CompletableDeferred<Unit>? = null
    var rateLimitCreate = false
    var answerReceiptState = "unknown"
    override suspend fun curiosityPolicy(connection: ConnectionCredential): ApiResult<CuriosityPolicyDto> { gets++; return ApiResult.Success(policy) }
    override suspend fun curiosityQuestions(connection: ConnectionCredential, scope: UUID): ApiResult<List<CuriosityQuestionDto>> { gets++; return ApiResult.Success(emptyList()) }
    override suspend fun curiosityConversation(connection: ConnectionCredential, conversation: UUID): ApiResult<List<CuriosityQuestionDto>> { gets++; return ApiResult.Success(emptyList()) }
    override suspend fun curiosityReceipt(connection: ConnectionCredential, operation: UUID): ApiResult<CuriosityReceiptDto> {
        gets++
        val op = store.journal!!.operations.single { it.operationId == operation }
        val answer = if (op.kind == "answer") adaJson.decodeFromString<CuriosityAnswerDto>(op.body) else null
        return ApiResult.Success(CuriosityReceiptDto("ada-curiosity-v1", operation, op.kind, if (answer != null) answerReceiptState else "unknown", question_id = op.questionId, request_id = answer?.request_id, created_at = 1))
    }
    override suspend fun curiosityWrite(connection: ConnectionCredential, operation: CuriosityPending): ApiResult<CuriosityReceiptDto> {
        assertTrue(store.journal!!.operations.contains(operation)); posts++
        if (operation.kind == "answer") return ApiResult.Failure(ApiFailure.TooLarge, "prompt_too_large")
        if (operation.kind == "create" && rateLimitCreate) return ApiResult.Failure(ApiFailure.Http(429), "curiosity_owner_daily_limit")
        if (operation.kind == "create") wait?.let { withContext(NonCancellable) { it.await() } }
        if (operation.kind == "policy") policy = policy.copy(revision = policy.revision + 1, settings = adaJson.decodeFromString<CuriosityPolicyWriteDto>(operation.body).settings)
        return ApiResult.Success(CuriosityReceiptDto("ada-curiosity-v1", operation.operationId, operation.kind, if (operation.kind == "policy") "completed" else "created", created_at = 1))
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
class CuriosityControllerTest {
    @Test fun oversizedUnicodeAnswerIsActionableWithoutThrowingOrPosting() = runTest {
        val store = CuriousStore(); val api = CuriousApi(store)
        val controller = CuriosityController(api, store, backgroundScope) {}
        val scopeId = UUID.randomUUID()
        val q = CuriosityQuestionDto("ada-curiosity-v1", UUID.randomUUID(), scopeId, channel = "inbox", topic = "interests", state = "opened", created_at = 1, expires_at = Long.MAX_VALUE, available_at = 1)
        controller.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); controller.activate(scopeId); runCurrent()
        controller.answer(q, "😀".repeat(4001)); runCurrent()
        assertEquals(0, api.posts); assertNull(store.journal)
        assertTrue(controller.state.value.notice!!.contains("4000"))
    }
    @Test fun answerAdmissionErrorChecksDurableReceiptAndRetainsExactIntentUntilRejected() = runTest {
        val store = CuriousStore(); val api = CuriousApi(store)
        val controller = CuriosityController(api, store, backgroundScope) {}
        val scopeId = UUID.randomUUID()
        val q = CuriosityQuestionDto("ada-curiosity-v1", UUID.randomUUID(), scopeId, conversation_id = UUID.randomUUID(), channel = "chat", topic = "interests", state = "opened", created_at = 1, expires_at = Long.MAX_VALUE, available_at = 1)
        controller.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); controller.activate(scopeId); runCurrent()
        controller.answer(q, "Public answer"); runCurrent()
        val saved = controller.state.value.pending.single()
        assertEquals("unknown", controller.state.value.receipts[saved.operationId]!!.state)
        controller.answer(q, "Another answer"); runCurrent(); assertEquals(1, api.posts)
        api.answerReceiptState = "failed"; controller.check(saved); runCurrent()
        assertEquals(saved, controller.state.value.pending.single())
        api.answerReceiptState = "rejected"; controller.check(saved); runCurrent()
        assertTrue(controller.state.value.pending.isEmpty()); assertTrue(store.journal!!.operations.isEmpty())
        assertTrue(controller.state.value.notice!!.contains("not recorded"))
        controller.answer(q, "Reviewed shorter answer"); runCurrent(); assertEquals(2, api.posts)
    }
    @Test fun questionQuotaCooldownDoesNotDelayGlobalOff() = runTest {
        val store = CuriousStore(); val api = CuriousApi(store); api.rateLimitCreate = true
        val controller = CuriosityController(api, store, backgroundScope) {}
        controller.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); controller.activate(UUID.randomUUID()); runCurrent()
        controller.create(UUID.randomUUID(), "interests"); runCurrent(); assertEquals(1, api.posts)
        controller.off(); runCurrent()
        assertEquals(2, api.posts); assertFalse(controller.state.value.policy!!.settings.enabled)
    }
    @Test fun lateOriginalCannotReturnAfterScopeChange() = runTest {
        val store = CuriousStore(); val api = CuriousApi(store); val scopeId = UUID.randomUUID(); val sourceId = UUID.randomUUID()
        val text = "😀 I enjoy books."
        val hash = java.security.MessageDigest.getInstance("SHA-256").digest(text.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
        api.original = SourceVersionDto(sourceId, sourceId, scopeId, 1, text, hash, "user_explicit", 1)
        api.sourceWait = CompletableDeferred()
        val controller = CuriosityController(api, store, backgroundScope) {}
        controller.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); controller.activate(scopeId); runCurrent()
        val source = CuriositySourceDto(sourceId, scopeId, hash, 0, text.codePointCount(0, text.length), text, "user_explicit", 1)
        controller.inspect(CuriosityQuestionDto("ada-curiosity-v1", UUID.randomUUID(), scopeId, channel = "inbox", topic = "interests", state = "pending", source = source, created_at = 1, expires_at = Long.MAX_VALUE, available_at = 1)); runCurrent()
        controller.activate(UUID.randomUUID()); api.sourceWait!!.complete(Unit); runCurrent()
        assertNull(controller.state.value.inspected)
    }
    @Test fun storageFailureSendsNothingAndRestoreOnlyChecksReceipts() = runTest {
        val store = CuriousStore(); val api = CuriousApi(store); val scopeId = UUID.randomUUID()
        val controller = CuriosityController(api, store, backgroundScope) {}
        controller.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); controller.activate(scopeId); runCurrent()
        store.fail = true; controller.create(scopeId, "interests"); runCurrent(); assertEquals(0, api.posts)
        store.fail = false; api.wait = CompletableDeferred()
        controller.create(scopeId, "interests"); runCurrent(); assertEquals(1, api.posts)
        val saved = store.journal!!.operations.single()
        val restored = CuriosityController(api, store, backgroundScope) {}
        restored.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); restored.activate(scopeId); runCurrent()
        assertEquals(1, api.posts); assertEquals(saved, restored.state.value.pending.single())
        api.wait!!.complete(Unit); runCurrent()
    }
    @Test fun globalOffQueuesAlongsideUnknownCreateAndLateCompletionCannotReenable() = runTest {
        val store = CuriousStore(); val api = CuriousApi(store); api.wait = CompletableDeferred()
        val controller = CuriosityController(api, store, backgroundScope) {}
        controller.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); controller.activate(UUID.randomUUID()); runCurrent()
        controller.create(UUID.randomUUID(), "interests"); runCurrent()
        assertEquals(1, store.journal!!.operations.size)
        controller.off(); runCurrent()
        assertEquals(2, api.posts); assertFalse(controller.state.value.policy!!.settings.enabled)
        assertEquals("create", store.journal!!.operations.single().kind)
        api.wait!!.complete(Unit); runCurrent()
        assertFalse(controller.state.value.policy!!.settings.enabled); assertTrue(controller.state.value.questions.isEmpty())
    }
    @Test fun uncancellableLatePostCannotRestoreAfterLogout() = runTest {
        val store = CuriousStore(); val api = CuriousApi(store); api.wait = CompletableDeferred()
        val controller = CuriosityController(api, store, backgroundScope) {}
        controller.setVerifiedSession(curiousConn, curiousOwner, curiousCaps); controller.activate(UUID.randomUUID()); runCurrent()
        controller.create(UUID.randomUUID(), "interests"); runCurrent()
        controller.reset(); api.wait!!.complete(Unit); runCurrent()
        assertNull(controller.state.value.policy); assertTrue(controller.state.value.questions.isEmpty())
        assertEquals(1, store.journal!!.operations.size)
    }
}
