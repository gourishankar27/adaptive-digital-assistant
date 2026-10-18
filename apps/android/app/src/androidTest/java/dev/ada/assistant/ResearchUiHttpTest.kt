package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Real ADA/session/PG HTTP; explicitly synthetic broker/provider; separate emulator application. */
class ResearchUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private fun <T> success(result: ApiResult<T>): T {
        assertTrue("Synthetic HTTP operation must succeed", result is ApiResult.Success)
        return (result as ApiResult.Success).value
    }
    @Test fun researchApprovalBeforeProcessStop() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.phase24.debug")
        val origin = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
        val api = HttpAdaApi()
        val login = runBlocking { success(api.passwordLogin(origin, "synthetic-admin", "Public synthetic Android passphrase 123", true)) }
        val connection = ConnectionCredential.parse(origin, login.access_token, true)!!
        val conversation = runBlocking {
            val profile = success(api.createPersonality(connection, PersonalityInputDto()))
            success(api.createConversation(connection, ConversationInputDto(profile.id, "Public research validation")))
        }
        runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() }
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.passwordLogin(origin, "synthetic-admin", "Public synthetic Android passphrase 123") }
        compose.waitUntil(30000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(10000) { vm.state.value.conversation?.id == conversation.id }
        compose.onNodeWithTag("open-research").performClick()
        compose.onNodeWithTag("research-question").performTextInput("What data does ZoneInfo use?")
        compose.onNodeWithTag("research-target").performTextInput("https://docs.python.org/3/library/zoneinfo.html")
        closeSoftKeyboard()
        compose.onNodeWithTag("research-preview").performScrollTo().performClick()
        compose.waitUntil(15000) { vm.research.state.value.run?.state == "pending_approval" }
        assertTrue(vm.research.state.value.run!!.citations.isEmpty())
        val saved = vm.research.state.value.journal!!
        assertEquals(saved.runId, runBlocking { AndroidSessionStore(compose.activity.applicationContext).researchJournal(saved.identity) }!!.runId)
        compose.onNodeWithTag("research-approve").performScrollTo().performClick()
        compose.onNodeWithText("Approve this request only").performClick()
        compose.waitUntil(15000) { vm.research.state.value.run?.state == "ready" && !vm.research.state.value.busy }
        compose.onNodeWithText("Inspect exact saved source").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.research.state.value.source != null }
        assertTrue(vm.research.state.value.source!!.text.startsWith("😀"))
        compose.onNodeWithTag("research-answer").performScrollTo().performClick()
        compose.waitUntil(15000) { vm.research.state.value.run?.state == "completed" && !vm.research.state.value.busy }
        assertEquals(1, vm.research.state.value.run!!.citations.size)
        assertNull(vm.research.state.value.journal!!.operation)
    }
    @Test fun researchRestoreAfterProcessStop() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.phase24.debug")
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(30000) { vm.state.value.account != null && vm.research.state.value.run?.state == "completed" }
        val saved = vm.research.state.value.journal!!
        val run = vm.research.state.value.run!!
        assertEquals(saved.runId, run.id)
        assertEquals(1, run.calls.size)
        assertTrue(run.response!!.contains("[W1]"))
        compose.runOnIdle { vm.navigate(ChatDestination.Research) }
        compose.onNodeWithTag("research-state").assertTextEquals("State: completed")
        compose.onNodeWithText("Inspect exact saved source").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.research.state.value.source != null }
        assertEquals(run.citations.single(), vm.research.state.value.source!!.citation)
    }
}
