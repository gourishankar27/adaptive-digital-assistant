package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ProposalController
import java.io.File
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

class ProposalRecoveryPrepareTest {
    @Test fun prepareCommittedReviewWithoutDelivery() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation(); assumeTrue(InstrumentationRegistry.getArguments().getString("adaProposalRecovery") == "true")
        val context = instrumentation.targetContext; val file = File(context.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val store = AndroidSessionStore(context); store.clear(); val work = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
        var prepared = false; var controller: ProposalController? = null
        try {
            val token = file.readText().trim(); val conn = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val actual = HttpAdaApi()
            val identity = SessionIdentity(conn.server.toString(), success(actual.me(conn)).id); val caps = success(actual.capabilities(conn)); val scope = success(actual.createScope(conn, ScopeInputDto("Synthetic proposal recovery")))
            val text = "Android verification project uses Oxford Blue. 😀"
            val source = success(actual.createNote(conn, scope.id, NoteInputDto(UUID.randomUUID(), text))); val key = UUID.randomUUID()
            val extraction = success(actual.extractProposals(conn, PendingProposal(identity, scope.id, key, kind = "extract", body = adaJson.encodeToString(ExtractionInputDto(key, listOf(SourcePinDto(source.id, source.version, source.content_hash, 0, text.codePointCount(0, text.length))))))))
            val p = success(actual.proposal(conn, extraction.proposal_ids.single())); store.saveCredential(StoredCredential(identity, token))
            val lost = object : AdaApi by actual { override suspend fun reviewProposal(connection: ConnectionCredential, pending: PendingProposal): ApiResult<ReviewReceiptDto> { check(actual.reviewProposal(connection, pending) is ApiResult.Success); return ApiResult.Failure(ApiFailure.Timeout) } }
            val c = ProposalController(lost, store, work, { error("Synthetic identity revoked") }); controller = c
            withContext(Dispatchers.Main) { c.setVerifiedSession(conn, identity, caps) }; await { !c.state.value.busy }
            withContext(Dispatchers.Main) { c.activate() }; await { c.state.value.scopes.items.any { it.id == scope.id } }
            withContext(Dispatchers.Main) { c.selectScope(scope.id) }; await { c.state.value.inbox.items.any { it.id == p.id } }
            withContext(Dispatchers.Main) { c.open(p) }; await { c.state.value.draft != null && !c.state.value.busy }
            withContext(Dispatchers.Main) { c.draft(annotation = "Synthetic explicit review recovery.") }; await { c.state.value.draftSaved }
            withContext(Dispatchers.Main) { c.decide("accept") }; await { !c.state.value.busy && c.state.value.fault == ApiFailure.Timeout }
            val pending = checkNotNull(store.proposalPending(identity)); assertEquals(1, success(actual.claims(conn, scope.id)).size)
            assertNotNull(success(actual.reviewReceipt(conn, pending.operationId)).claim_id); prepared = true
            instrumentation.sendStatus(0, Bundle().apply { putString("recoveryProposalReview", pending.operationId.toString()) })
        } finally { withContext(Dispatchers.Main) { controller?.reset() }; work.cancel(); if (!prepared) store.clear() }
    }
    private suspend fun await(check: () -> Boolean) = withTimeout(20_000) { while (!check()) delay(50) }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
