package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatViewModel
import dev.ada.assistant.ui.ChatDestination
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class StreamingUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun provisionalObserverDetachStopAndExactCancelledRetryOverHttp() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val c = ConnectionCredential.parse(dev.ada.assistant.fixtureOrigin(), token, true)!!; val api = HttpAdaApi()
        val profile = runBlocking { success(api.personalities(c)).first() }
        val conversation = runBlocking { success(api.createConversation(c, ConversationInputDto(profile.id, "Synthetic stream UI"))) }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(c.server.toString(), token) }; compose.waitUntil(20_000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }; compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id && !vm.state.value.events.loading }
        compose.runOnIdle { vm.updateDraft("Synthetic streaming UI turn"); vm.send() }
        compose.waitUntil(20_000) { vm.state.value.stream?.provisional?.isNotEmpty() == true }
        val id = vm.state.value.pending!!.message.body.request_id
        compose.onNodeWithText("Provisional reply").performScrollTo().assertIsDisplayed()
        assertTrue(vm.state.value.sources.isEmpty())
        compose.runOnIdle { vm.navigate(ChatDestination.Settings) }
        compose.waitUntil(5_000) { !vm.state.value.streamConnected }
        assertEquals("running", runBlocking { success(api.streamStatus(c, id)) }.stream_state)
        compose.runOnIdle { vm.navigate(ChatDestination.Chat) }
        compose.waitUntil(20_000) { vm.state.value.streamConnected }
        compose.onNodeWithTag("stop-generation").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.state.value.pending?.response?.error_code == "request_cancelled" }
        val terminal = runBlocking { success(api.streamStatus(c, id)) }
        assertEquals("cancelled", terminal.stream_state); assertEquals(1, terminal.attempt)
        assertNull(terminal.result.response); assertTrue(terminal.provisional.isNotEmpty())
        assertEquals(1, runBlocking { success(api.events(c, conversation.id)) }.count { it.request_id == id })
        val receipt = runBlocking { success(api.cancelGeneration(c, id, 1)) }
        assertEquals(receipt, runBlocking { success(api.cancelGeneration(c, id, 1)) })
        compose.onNodeWithText("Incomplete reply").performScrollTo().assertIsDisplayed()
        compose.runOnIdle { vm.retry() }
        compose.waitUntil(20_000) { vm.state.value.stream?.attempt == 2 }
        compose.waitUntil(20_000) { vm.state.value.pending == null }
        val saved = runBlocking { success(api.request(c, id)) }
        assertEquals("completed", saved.status); assertEquals(2, saved.attempt)
        assertEquals(2, runBlocking { success(api.events(c, conversation.id)) }.count { it.request_id == id })
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
