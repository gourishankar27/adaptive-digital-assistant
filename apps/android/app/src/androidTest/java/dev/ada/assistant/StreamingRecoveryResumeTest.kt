package dev.ada.assistant

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatViewModel
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class StreamingRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    @Test fun originalRequestRestoresByGetWithoutDuplicateSubmission() {
        assumeTrue(InstrumentationRegistry.getArguments().getString("adaStreamingRecovery") == "true")
        val key = UUID.fromString(InstrumentationRegistry.getArguments().getString("expectedStreamKey"))
        val token = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token").readText().trim()
        val c = ConnectionCredential.parse("http://10.0.2.2:18765", token, true)!!; val api = HttpAdaApi()
        val request = runBlocking { (api.request(c, key) as ApiResult.Success).value }
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(request.conversation_id) }
        compose.waitUntil(20_000) { vm.state.value.pending == null || vm.state.value.stream?.request_id == key }
        compose.waitUntil(20_000) { vm.state.value.pending == null }
        val terminal = runBlocking { (api.streamStatus(c, key) as ApiResult.Success).value }
        assertEquals("completed", terminal.stream_state); assertEquals(1, terminal.attempt)
        assertEquals(2, runBlocking { (api.events(c, request.conversation_id) as ApiResult.Success).value }.count { it.request_id == key })
        runBlocking { assertNull(AndroidSessionStore(compose.activity.applicationContext).pending(SessionIdentity(c.server.toString(), vm.state.value.account!!.owner))) }
        compose.runOnIdle { vm.logout() }
    }
}
