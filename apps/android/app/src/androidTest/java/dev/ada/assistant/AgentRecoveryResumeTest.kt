package dev.ada.assistant

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatViewModel
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class AgentRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun exactReceiptIsRestoredByGetAfterActualForceStop() {
        val args = InstrumentationRegistry.getArguments(); assumeTrue(args.getString("adaAgentRecovery") == "true")
        val run = UUID.fromString(args.getString("expectedAgentRun")); val approval = UUID.fromString(args.getString("expectedAgentApproval"))
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null && vm.agents.state.value.run?.id == run && vm.agents.state.value.receipt?.approval_id == approval && !vm.agents.state.value.busy }
        val s = vm.agents.state.value; assertEquals("completed", s.run!!.status); assertEquals("completed", s.receipt!!.outcome); assertNull(s.journal!!.operation)
        val store = AndroidSessionStore(compose.activity.applicationContext); val credential = runBlocking { store.readCredential() }!!
        val conn = ConnectionCredential.parse(credential.identity.server, credential.token, true)!!; val api = HttpAdaApi()
        assertEquals(s.receipt, runBlocking { success(api.toolReceipt(conn, s.receipt.id)) }); assertEquals(1, s.run.steps.count { it.receipt != null })
        assertNull(runBlocking { store.agentJournal(credential.identity) }!!.operation); assertTrue(runBlocking { success(api.claims(conn, s.run.scope_id)) }.isEmpty())
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
