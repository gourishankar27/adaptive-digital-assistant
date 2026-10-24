package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Synthetic ASR input, actual HTTP/PostgreSQL, actual Compose/Keystore/process restart. */
class LongVoiceUiHttpTest {
    @get:Rule val compose=createAndroidComposeRule<MainActivity>()
    private val context get()=InstrumentationRegistry.getInstrumentation().targetContext
    private val locator get()=File(context.noBackupFilesDir,"public-long-voice-locator")
    private fun connection(): Pair<HttpAdaApi,ConnectionCredential> {
        val token=File(context.filesDir,"foundation-test-token"); assumeTrue(token.isFile)
        return HttpAdaApi() to requireNotNull(ConnectionCredential.parse(fixtureOrigin(),token.readText().trim(),true))
    }
    private fun connect(c:ConnectionCredential):ChatViewModel {
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(c.server.toString(),c.token) }
        compose.waitUntil(20000) { vm.state.value.account!=null }
        assertTrue(vm.state.value.capabilities!!.hasLongVoice())
        return vm
    }
    @Test fun checkpointPersistsExactGeneratedSegmentsWithoutSending() {
        val(api,c)=connection()
        val profile=runBlocking { (api.personalities(c) as ApiResult.Success).value.first() }
        val conversation=runBlocking { (api.createConversation(c,ConversationInputDto(profile.id,"Public long voice recovery")) as ApiResult.Success).value }
        val vm=connect(c)
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(20000) { vm.state.value.conversation?.id==conversation.id && !vm.voice.state.value.draftLoading }
        val words="Public generated story words. ".repeat(200)
        val row=TranscriptSegmentDto(UUID.randomUUID(),0,125000,words,voiceHash(words))
        val input=object:SpeechCapture {
            override val longForm=true
            override val availability=SpeechAvailability.Available
            override val version="sherpa-onnx-1.13.8"
            override val modelSha256="a".repeat(64)
            var callback:CaptureListener?=null
            override fun transcriptSegments()=listOf(row)
            override fun capturedDurationMs()=125000L
            override fun start(language:String,listener:CaptureListener) { callback=listener }
            override fun stop()=Unit
            override fun cancel()=Unit
            override fun close()=Unit
        }
        compose.runOnIdle { vm.voice.attachAudio(input,InstrumentedVoicePlayback()); assertTrue(vm.requestVoiceRecording()); vm.voice.permissionResult(true); input.callback!!.ready() }
        var committed=false
        compose.runOnIdle { input.callback!!.checkpoint(listOf(row),125000) { committed=it } }
        compose.waitUntil(5000) { committed }
        val identity=SessionIdentity(c.server.toString(),vm.state.value.account!!.owner)
        val saved=runBlocking { AndroidSessionStore(context).voiceDraft(identity) }!!
        assertFalse(saved.approved); assertEquals(words,saved.transcript.original_text)
        assertTrue(runBlocking { (api.events(c,conversation.id) as ApiResult.Success).value }.isEmpty())
        locator.writeText("${conversation.id}\n${saved.transcript.transcript_id}")
        // The runner force-stops this validation package. No POST/resume is allowed on restart.
    }
    @Test fun recoveredStoryNeedsContextAndExplicitSendThenPreservesLineage() {
        assumeTrue(locator.isFile)
        val ids=locator.readLines(); val cid=UUID.fromString(ids[0]); val tid=UUID.fromString(ids[1])
        val(api,c)=connection()
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        // Explicit Connect intentionally clears old journals. Exercise the real
        // identity-verified Restore path after the runner's actual force-stop.
        compose.runOnIdle { vm.restore() }
        compose.waitUntil(20000) { vm.state.value.account!=null }
        compose.runOnIdle { vm.openConversation(cid) }
        compose.waitUntil(20000) { vm.voice.state.value.draft?.transcript?.transcript_id==tid && !vm.voice.state.value.saving }
        val original=vm.voice.state.value.draft!!.transcript
        assertNull(vm.voice.composerDraftForSend())
        assertTrue(runBlocking { (api.events(c,cid) as ApiResult.Success).value }.isEmpty())
        val reviewed="Public reviewed story words. ".repeat(200)
        compose.runOnIdle { vm.updateComposerDraft(reviewed) }
        compose.waitUntil(5000) { !vm.voice.state.value.saving }
        compose.runOnIdle { vm.voice.chooseContext(0,2000) }
        compose.waitUntil(5000) { !vm.voice.state.value.saving }
        compose.onNodeWithTag("send").assertIsEnabled().performClick()
        compose.waitUntil(20000) { vm.state.value.submittedMessages.isNotEmpty() && vm.state.value.pending==null }
        val id=vm.state.value.submittedMessages.keys.single()
        val lineage=runBlocking { (api.longVoiceInput(c,id) as ApiResult.Success).value }
        lineage.validate(cid,vm.state.value.conversation!!.scope_id)
        assertEquals(original.segments,lineage.transcript.segments); assertEquals(reviewed,lineage.reviewed_text)
        assertEquals(125000L,lineage.transcript.duration_ms)
        assertEquals(2000,lineage.context_end)
        compose.runOnIdle { vm.openSources(id) }
        compose.waitUntil(5000) { vm.voice.state.value.longLineage?.request_id==id }
        compose.onNodeWithTag("sources-list").performScrollToNode(hasTestTag("long-voice-lineage-$id"))
        compose.onNodeWithTag("long-voice-lineage-$id").assertIsDisplayed()
        assertEquals(2,runBlocking { (api.events(c,cid) as ApiResult.Success).value }.size)
    }
}
