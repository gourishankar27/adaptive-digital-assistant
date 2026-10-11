package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test

private val agentOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val agentConn = ConnectionCredential.parse(agentOwner.server, "synthetic-agent-token", false)!!
private val agentCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(agent_tools = "approval_read_only_v1", agent_protocol = "ada-agent-v1", agent_registry = selectedAgentTools.toList())
private val agentConversation = ConversationDto(UUID.randomUUID(), "Synthetic", UUID.randomUUID(), "project", PersonalitySnapshotDto("ADA", "conversational", "warm", "balanced"), "ada-baseline-v4", 0, 1)
private class AgentStore : SessionStore {
    var journal: AgentJournal? = null; var failSave = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun agentJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveAgentJournal(journal: AgentJournal) { if (failSave) throw SessionStorageException(); validateAgentJournal(journal); this.journal = journal }
    override suspend fun removeAgentJournal(identity: SessionIdentity, runId: UUID) { if (journal?.identity == identity && journal?.runId == runId) journal = null }
}
private fun unusedAgentApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected: ${method.name}") } as AdaApi
private class AgentApi(val store: AgentStore) : AdaApi by unusedAgentApi() {
    var run: AgentRunDto? = null; var lost = false; var mismatch = false
    val posts = mutableListOf<AgentJournal>(); val receipts = mutableMapOf<UUID, ToolReceiptDto>()
    var read: suspend () -> ApiResult<AgentRunDto> = { ApiResult.Success(checkNotNull(run)) }
    override suspend fun createAgentRun(connection: ConnectionCredential, journal: AgentJournal): ApiResult<AgentRunDto> {
        assertEquals(journal, store.journal); posts += journal
        if (run == null) {
            val step = AgentStepDto(UUID.randomUUID(), 1, 1, "pending_approval", "calculator", "calculator-v1", buildJsonObject { put("expression", "3+4") }, "a".repeat(64), "b".repeat(64), 120000)
            run = AgentRunDto(journal.runId, journal.identity.owner, journal.scopeId, journal.conversationId, "ada-agent-v1", "pending_approval", provider = "fixture", model = "synthetic", generation = 1, created_at = 0, as_of = 0, steps = listOf(step))
        }
        return if (lost) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(run!!)
    }
    override suspend fun agentRun(connection: ConnectionCredential, id: UUID) = read()
    override suspend fun agentOperation(connection: ConnectionCredential, journal: AgentJournal): ApiResult<ToolReceiptDto> {
        assertEquals(journal, store.journal); posts += journal
        val op = journal.operation!!; val a = adaJson.decodeFromString<AgentApprovalDto>(op.body); val s = run!!.steps.single()
        val r = receipts.getOrPut(op.id) { ToolReceiptDto(UUID.randomUUID(), op.id, journal.identity.owner, journal.runId, journal.scopeId, s.id, s.tool, s.tool_version, a.argument_hash, a.preview_hash, if (op.kind == "approve") "completed" else "revoked", "tool_result", "untrusted_tool_output", if (op.kind == "approve") buildJsonObject { put("value", "7") } else null, created_at = 1) }
        run = run!!.copy(status = if (op.kind == "approve") "completed" else "failed", response = if (op.kind == "approve") "Recorded result: 7" else null, steps = listOf(s.copy(status = r.outcome, receipt = r)))
        return if (lost) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(if (mismatch) r.copy(scope_id = UUID.randomUUID()) else r)
    }
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class AgentControllerTest {
    private fun TestScope.ready(): Triple<AgentController, AgentApi, AgentStore> {
        val store = AgentStore(); val api = AgentApi(store); val c = AgentController(api, store, this, {})
        c.setVerifiedSession(agentConn, agentOwner, agentCaps); advanceUntilIdle(); c.task("Calculate 3+4"); return Triple(c, api, store)
    }
    @Test fun exactApprovalIsJournaledAndDoubleTapCannotExecuteTwice() = runTest {
        val (c, api, store) = ready(); c.start(agentConversation); c.start(agentConversation); advanceUntilIdle()
        val step = c.state.value.run!!.steps.single(); c.decide(step, true); c.decide(step, true); advanceUntilIdle()
        assertEquals(2, api.posts.size); assertEquals(1, api.receipts.size); assertNull(store.journal!!.operation)
        assertEquals("completed", c.state.value.run!!.status); assertEquals("7", c.state.value.receipt!!.result!!["value"]!!.jsonPrimitive.content)
    }
    @Test fun lostApprovalRestoresByGetWithOriginalNonceAndNoAutomaticPost() = runTest {
        val (c, api, store) = ready(); c.start(agentConversation); advanceUntilIdle(); api.lost = true
        c.decide(c.state.value.run!!.steps.single(), true); advanceUntilIdle(); val saved = store.journal!!; assertNotNull(saved.operation)
        c.reset(); val restored = AgentController(api, store, this, {}); restored.setVerifiedSession(agentConn, agentOwner, agentCaps); advanceUntilIdle()
        assertEquals(2, api.posts.size); assertEquals(saved.runId, restored.state.value.run!!.id); assertEquals(saved.operation!!.id, restored.state.value.receipt!!.approval_id); assertNull(store.journal!!.operation)
    }
    @Test fun lostCreationOnlyChecksAndExplicitRetryUsesTheExactSavedBody() = runTest {
        val (c, api, store) = ready(); api.lost = true; c.start(agentConversation); advanceUntilIdle(); val saved = store.journal!!
        c.reset(); val restored = AgentController(api, store, this, {}); restored.setVerifiedSession(agentConn, agentOwner, agentCaps); advanceUntilIdle()
        assertEquals(1, api.posts.size); assertEquals(saved, restored.state.value.journal)
        api.lost = false; restored.retry(); advanceUntilIdle(); assertEquals(listOf(saved, saved), api.posts)
    }
    @Test fun storageFailureAndUnsupportedProtocolPreventEveryPost() = runTest {
        val (c, api, store) = ready(); store.failSave = true; c.start(agentConversation); advanceUntilIdle(); assertTrue(api.posts.isEmpty())
        store.failSave = false; c.setVerifiedSession(agentConn, agentOwner, agentCaps.copy(agent_tools = "unsupported")); advanceUntilIdle(); c.task("Calculate"); c.start(agentConversation); advanceUntilIdle(); assertTrue(api.posts.isEmpty())
    }
    @Test fun mismatchedReceiptCannotConfirmSuccessAndDenialReturnsOnlyRevocation() = runTest {
        val (c, api, store) = ready(); c.start(agentConversation); advanceUntilIdle(); api.mismatch = true
        c.decide(c.state.value.run!!.steps.single(), true); advanceUntilIdle(); assertNotNull(store.journal!!.operation); assertNull(c.state.value.receipt)
        c.check(); advanceUntilIdle(); assertNull(store.journal!!.operation); assertNotNull(c.state.value.receipt)
        c.closeCompleted(); advanceUntilIdle(); c.task("Calculate again"); api.run = null; api.mismatch = false; c.start(agentConversation); advanceUntilIdle()
        c.decide(c.state.value.run!!.steps.single(), false); advanceUntilIdle(); assertEquals("revoked", c.state.value.receipt!!.outcome); assertNull(c.state.value.receipt!!.result)
    }
    @Test fun oldOwnersLateUnauthorizedReplyCannotExpireTheNewSession() = runTest {
        val (c, api, _) = ready(); c.start(agentConversation); advanceUntilIdle()
        val late = CompletableDeferred<ApiResult<AgentRunDto>>(); api.read = { withContext(NonCancellable) { late.await() } }
        c.check(); runCurrent(); c.setVerifiedSession(agentConn, agentOwner.copy(owner = UUID.randomUUID()), agentCaps); runCurrent()
        late.complete(ApiResult.Failure(ApiFailure.Unauthorized)); advanceUntilIdle(); assertTrue(c.state.value.enabled); assertNull(c.state.value.run)
    }
    @Test fun authoritativeExpiredPreviewCanCloseWithoutInventingReceipt() = runTest {
        val (c, api, store) = ready(); c.start(agentConversation); advanceUntilIdle(); api.lost = true
        c.decide(c.state.value.run!!.steps.single(), true); advanceUntilIdle(); assertNotNull(store.journal!!.operation)
        api.run = api.run!!.copy(status = "failed", response = null, error_code = "agent_approval_expired", steps = api.run!!.steps.map { it.copy(status = "failed", receipt = null) })
        c.check(); advanceUntilIdle(); assertNull(store.journal!!.operation); assertNull(c.state.value.receipt)
        c.closeCompleted(); advanceUntilIdle(); assertNull(store.journal); assertEquals(2, api.posts.size)
    }
}
