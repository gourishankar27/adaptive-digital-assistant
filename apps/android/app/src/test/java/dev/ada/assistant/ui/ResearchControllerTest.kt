package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

private val researchOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val researchConn = ConnectionCredential.parse(researchOwner.server, "synthetic-research-token", false)!!
private val researchCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(web_research = "ada-web-research-v1", web_search = "wikimedia-rest-v1")
private val researchConversation = ConversationDto(UUID.randomUUID(), "Synthetic", UUID.randomUUID(), "project", PersonalitySnapshotDto("ADA", "conversational", "warm", "balanced"), "ada-baseline-v4", 0, 1)
private class ResearchStore : SessionStore {
    var journal: ResearchJournal? = null
    var fail = false
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { journal = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) {}
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
    override suspend fun researchJournal(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun saveResearchJournal(journal: ResearchJournal) { if (fail) throw SessionStorageException(); validateResearchJournal(journal); this.journal = journal }
    override suspend fun removeResearchJournal(identity: SessionIdentity, runId: UUID) { journal = null }
}
private fun unusedResearchApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected ${method.name}") } as AdaApi
private class ResearchApi(private val store: ResearchStore) : AdaApi by unusedResearchApi() {
    var posts = 0; var gets = 0
    var run: ResearchRunDto? = null
    var approvalWait: CompletableDeferred<Unit>? = null
    override suspend fun createResearch(connection: ConnectionCredential, conversation: UUID, body: String): ApiResult<ResearchRunDto> {
        assertEquals(store.journal!!.createBody, body); posts++
        val p = store.journal!!
        val preview = ResearchPreviewDto(p.runId, "fetch", "https://docs.python.org/3/index.html", "docs.python.org", "GET", "Exact disclosure", "a".repeat(64), Long.MAX_VALUE, 1048576, 15, 0, false, mapOf("User-Agent" to "Public fixture", "Accept" to "text/html", "Accept-Encoding" to "identity"))
        run = ResearchRunDto("ada-web-research-v1", p.runId, p.scopeId, p.conversationId, "Public synthetic", "pending_approval", calls = listOf(ResearchCallDto(preview, "pending_approval")), citations = emptyList(), citation_warnings = emptyList(), created_at = 1, remaining_calls = 2)
        return ApiResult.Success(run!!)
    }
    override suspend fun researchRun(connection: ConnectionCredential, id: UUID): ApiResult<ResearchRunDto> { gets++; return ApiResult.Success(run!!) }
    override suspend fun researchOperation(connection: ConnectionCredential, id: UUID, operation: ResearchOperation): ApiResult<ResearchRunDto> {
        posts++
        if (operation.kind == "approve") {
            assertEquals(operation, store.journal!!.operation)
            val stale = run!!.copy(state = "ready")
            approvalWait?.let { withContext(NonCancellable) { it.await() } }
            return ApiResult.Success(stale)
        }
        assertEquals("cancel", operation.kind); assertTrue(store.journal!!.cancelRequested)
        run = run!!.copy(state = "cancelled")
        return ApiResult.Success(run!!)
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
class ResearchControllerTest {
    @Test fun creationIsJournalingFirstAndRestoreUsesGetOnly() = runTest {
        val store = ResearchStore(); val api = ResearchApi(store)
        val controller = ResearchController(api, store, backgroundScope) { fail("Unexpected expiry") }
        controller.setVerifiedSession(researchConn, researchOwner, researchCaps)
        controller.edit("Public synthetic", "https://docs.python.org/3/index.html", "fetch")
        controller.start(researchConversation); advanceUntilIdle()
        assertEquals(1, api.posts)
        val restored = ResearchController(api, store, backgroundScope) {}
        restored.setVerifiedSession(researchConn, researchOwner, researchCaps); advanceUntilIdle()
        assertEquals(1, api.posts); assertEquals(1, api.gets)
        assertEquals(store.journal!!.runId, restored.state.value.run!!.id)
    }
    @Test fun diskFailurePreventsPostAndResetDropsLateResult() = runTest {
        val store = ResearchStore(); val api = ResearchApi(store); store.fail = true
        val controller = ResearchController(api, store, backgroundScope) {}
        controller.setVerifiedSession(researchConn, researchOwner, researchCaps)
        controller.edit("Public synthetic", "https://docs.python.org/3/index.html", "fetch")
        controller.start(researchConversation); advanceUntilIdle()
        assertEquals(0, api.posts)
        controller.reset(); assertNull(controller.state.value.journal)
    }
    @Test fun cancellingInFlightApprovalIsDurableAndLateReplyCannotRestoreReadyState() = runTest {
        val store = ResearchStore(); val api = ResearchApi(store)
        val controller = ResearchController(api, store, backgroundScope) {}
        controller.setVerifiedSession(researchConn, researchOwner, researchCaps)
        controller.edit("Public synthetic", "https://docs.python.org/3/index.html", "fetch")
        controller.start(researchConversation)
        api.approvalWait = CompletableDeferred()
        controller.approve(); assertNotNull(store.journal!!.operation)
        controller.cancel(); assertEquals("cancelled", controller.state.value.run!!.state)
        assertTrue(store.journal!!.cancelRequested)
        api.approvalWait!!.complete(Unit); runCurrent()
        assertEquals("cancelled", controller.state.value.run!!.state)
        assertTrue(store.journal!!.cancelRequested)
    }
}
