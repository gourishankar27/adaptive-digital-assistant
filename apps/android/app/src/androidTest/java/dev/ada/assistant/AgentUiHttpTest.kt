package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatViewModel
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class AgentUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun exactCalculatorApprovalAndDenialUseRealHttpReceipts() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val conn = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val api = HttpAdaApi()
        val profile = runBlocking { success(api.personalities(conn)) }.first()
        val conversation = runBlocking { success(api.createConversation(conn, ConversationInputDto(profile.id, "Synthetic tool UI"))) }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]; compose.runOnIdle { vm.connect(conn.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null && !vm.agents.state.value.busy }
        compose.runOnIdle { vm.openConversation(conversation.id) }; compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id }
        compose.onNodeWithTag("open-tools").performClick(); compose.onNodeWithTag("agent-task").performTextInput("Calculate 3+4")
        closeSoftKeyboard(); compose.onNodeWithTag("agent-start").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.agents.state.value.run?.status == "pending_approval" && !vm.agents.state.value.busy }
        assertNull(vm.agents.state.value.run!!.steps.single().receipt); compose.onNodeWithTag("agent-preview").performScrollTo().performClick()
        compose.onNodeWithText("Approve this exact read-only request?").assertIsDisplayed(); compose.onNodeWithTag("agent-approve").performClick()
        compose.waitUntil(20_000) { vm.agents.state.value.run?.status == "completed" && !vm.agents.state.value.busy }
        val receipt = vm.agents.state.value.receipt!!; assertEquals("completed", receipt.outcome); assertEquals("calculator", receipt.tool)
        assertEquals(receipt, runBlocking { success(api.toolReceipt(conn, receipt.id)) }); assertTrue(runBlocking { success(api.claims(conn, conversation.scope_id)) }.isEmpty())
        compose.runOnIdle { vm.agents.closeCompleted() }; compose.waitUntil(20_000) { vm.agents.state.value.journal == null && !vm.agents.state.value.busy }
        compose.onNodeWithTag("agent-task").performScrollTo().performTextInput("Another calculation"); closeSoftKeyboard(); compose.onNodeWithTag("agent-start").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.agents.state.value.run?.status == "pending_approval" && !vm.agents.state.value.busy }
        compose.onNodeWithTag("agent-deny").performScrollTo().performClick(); compose.waitUntil(20_000) { vm.agents.state.value.receipt?.outcome == "revoked" && !vm.agents.state.value.busy }
        assertNull(vm.agents.state.value.receipt!!.result); assertNull(vm.agents.state.value.run!!.response)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
