package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.AgentController
import java.io.File
import kotlinx.coroutines.*
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

class AgentRecoveryPrepareTest {
    @Test fun prepareCommittedApprovalWithoutDelivery() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation(); assumeTrue(InstrumentationRegistry.getArguments().getString("adaAgentRecovery") == "true")
        val context = instrumentation.targetContext; val file = File(context.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val store = AndroidSessionStore(context); store.clear(); val work = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
        var prepared = false; var controller: AgentController? = null
        try {
            val token = file.readText().trim(); val conn = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val api = HttpAdaApi()
            val identity = SessionIdentity(conn.server.toString(), success(api.me(conn)).id); val caps = success(api.capabilities(conn))
            val profile = success(api.personalities(conn)).first(); val conversation = success(api.createConversation(conn, ConversationInputDto(profile.id, "Synthetic agent recovery")))
            store.saveCredential(StoredCredential(identity, token))
            val lost = object : AdaApi by api { override suspend fun agentOperation(connection: ConnectionCredential, journal: AgentJournal): ApiResult<ToolReceiptDto> { check(api.agentOperation(connection, journal) is ApiResult.Success); return ApiResult.Failure(ApiFailure.Timeout) } }
            val c = AgentController(lost, store, work, { error("Synthetic identity revoked") }); controller = c
            withContext(Dispatchers.Main) { c.setVerifiedSession(conn, identity, caps) }; await { !c.state.value.busy }
            withContext(Dispatchers.Main) { c.task("Calculate 3+4"); c.start(conversation) }; await { c.state.value.run?.status == "pending_approval" && !c.state.value.busy }
            withContext(Dispatchers.Main) { c.decide(c.state.value.run!!.steps.single(), true) }; await { !c.state.value.busy && c.state.value.fault == ApiFailure.Timeout }
            val saved = checkNotNull(store.agentJournal(identity)); assertNotNull(saved.operation); assertEquals("completed", success(api.agentRun(conn, saved.runId)).status)
            prepared = true; instrumentation.sendStatus(0, Bundle().apply { putString("recoveryAgentRun", saved.runId.toString()); putString("recoveryAgentApproval", saved.operation!!.id.toString()) })
        } finally { withContext(Dispatchers.Main) { controller?.reset() }; work.cancel(); if (!prepared) store.clear() }
    }
    private suspend fun await(check: () -> Boolean) = withTimeout(20_000) { while (!check()) delay(50) }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
