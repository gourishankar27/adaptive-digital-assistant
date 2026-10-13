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

class VoiceRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private fun setup(): Triple<ChatViewModel, HttpAdaApi, ConnectionCredential> {
        assumeTrue(InstrumentationRegistry.getArguments().getString("adaVoiceRecovery") == "true")
        val token = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token").readText().trim()
        val c = ConnectionCredential.parse("http://10.0.2.2:18765", token, true)!!
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null }
        return Triple(vm, HttpAdaApi(), c)
    }
    @Test fun editedDraftRestoresForReviewWithoutAutomaticSubmission() {
        val (vm, api, c) = setup()
        val key = UUID.fromString(InstrumentationRegistry.getArguments().getString("expectedVoiceKey"))
        val store = AndroidSessionStore(compose.activity.applicationContext)
        val identity = SessionIdentity(c.server.toString(), vm.state.value.account!!.owner)
        val saved = runBlocking { store.voiceDraft(identity) }!!
        assertEquals(key, saved.transcript.transcript_id); assertFalse(saved.approved)
        compose.runOnIdle { vm.openConversation(saved.conversationId) }
        compose.waitUntil(5000) { vm.voice.state.value.draft != null }
        assertEquals(saved, vm.voice.state.value.draft)
        assertTrue(runBlocking { (api.events(c, saved.conversationId) as ApiResult.Success).value }.isEmpty())
        compose.runOnIdle { vm.voice.approve(true) }; compose.waitUntil(5000) { vm.voice.approvedDraft() != null }
        compose.runOnIdle { vm.sendReviewedVoice(); vm.sendReviewedVoice() }
        compose.waitUntil(20_000) { vm.state.value.submittedMessages.isNotEmpty() && vm.state.value.pending == null }
        val request = vm.state.value.submittedMessages.keys.single()
        val lineage = runBlocking { (api.voiceInput(c, request) as ApiResult.Success).value }
        assertEquals(saved.transcript.original_text, lineage.original_text); assertEquals(saved.reviewedText, lineage.reviewed_text)
        compose.runOnIdle { vm.logout() }
    }
    @Test fun originalReviewedRequestRestoresByGetAndDoesNotAllocateANewTurn() {
        val (vm, api, c) = setup()
        val key = UUID.fromString(InstrumentationRegistry.getArguments().getString("expectedVoiceKey"))
        val request = runBlocking { (api.request(c, key) as ApiResult.Success).value }
        compose.runOnIdle { vm.openConversation(request.conversation_id) }
        compose.waitUntil(20_000) { vm.state.value.pending == null }
        val terminal = runBlocking { (api.streamStatus(c, key) as ApiResult.Success).value }
        assertEquals("completed", terminal.stream_state); assertEquals(1, terminal.attempt)
        val lineage = runBlocking { (api.voiceInput(c, key) as ApiResult.Success).value }
        assertEquals("Original generated recovery cattle", lineage.original_text)
        assertEquals("Synthetic streaming reviewed recovery kettle", lineage.reviewed_text)
        assertEquals(2, runBlocking { (api.events(c, request.conversation_id) as ApiResult.Success).value }.count { it.request_id == key })
        assertEquals(1, runBlocking { (api.voiceInputs(c, request.conversation_id) as ApiResult.Success).value }.size)
        assertTrue(vm.state.value.submittedMessages.keys.all { it == key })
        compose.runOnIdle { vm.logout() }
    }
}
