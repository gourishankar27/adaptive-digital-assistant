package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Synthetic capture/playback adapters; actual HTTP, owner checks, Compose and Keystore. */
class VoiceUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    private val input = InstrumentedVoiceCapture()
    private val output = InstrumentedVoicePlayback()
    private fun connect(): Pair<HttpAdaApi, ConnectionCredential> {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val c = ConnectionCredential.parse(dev.ada.assistant.fixtureOrigin(), token, true)!!
        val api = HttpAdaApi(); val profile = runBlocking { (api.personalities(c) as ApiResult.Success).value.first() }
        val conversation = runBlocking { (api.createConversation(c, ConversationInputDto(profile.id, "Synthetic voice UI")) as ApiResult.Success).value }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.voice.attachAudio(input, output); vm.connect(c.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null }
        assertTrue("Disposable fixture must enable reviewed streaming voice", vm.voice.state.value.enabled)
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id && !vm.state.value.events.loading && !vm.voice.state.value.draftLoading }
        return api to c
    }
    private fun waitForStableMicrophone() {
        var previous: androidx.compose.ui.geometry.Rect? = null
        var changedAt = android.os.SystemClock.uptimeMillis()
        compose.waitUntil(5000) {
            val bounds = compose.onNodeWithTag("voice-toggle").fetchSemanticsNode().boundsInRoot
            if (bounds != previous) { previous = bounds; changedAt = android.os.SystemClock.uptimeMillis() }
            android.os.SystemClock.uptimeMillis() - changedAt >= 300
        }
    }
    private fun grantSyntheticMicrophone() {
        InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand("pm grant ${compose.activity.packageName} android.permission.RECORD_AUDIO").close()
    }
    @Test fun heldMicrophonePartialEditAndComposerSendPreserveRealHttpLineage() {
        val (api, c) = connect(); grantSyntheticMicrophone()
        compose.runOnIdle { vm.updateDraft("Public typed prefix:") }
        compose.onNodeWithTag("composer").performClick() // Keep the IME open under the held control.
        waitForStableMicrophone()
        compose.onNodeWithTag("voice-toggle").performTouchInput { down(center) }
        compose.waitUntil(5000) { input.callback != null }
        val partial = "Generated partial line one\nPublic partial line two\nPublic partial line three\nPublic partial line four"
        compose.runOnIdle { input.callback!!.ready(); input.callback!!.partial(partial) }
        compose.onNodeWithTag("composer").assertTextContains("Public typed prefix: $partial")
        compose.onNodeWithTag("send").assertIsNotEnabled()
        compose.onNodeWithTag("voice-controls-dialog").assertDoesNotExist()
        compose.onNodeWithTag("voice-toggle").performTouchInput { up() }
        compose.waitUntil(5000) { input.stops == 1 }
        compose.runOnIdle { input.callback!!.result("Generated synthetic cattle 🫖") }
        compose.waitUntil(5000) { vm.voice.state.value.draft != null && !vm.voice.state.value.saving }
        compose.onNodeWithTag("composer").assertTextContains("Public typed prefix: Generated synthetic cattle 🫖")
        assertFalse(vm.voice.state.value.draft!!.approved)
        assertTrue(runBlocking { (api.events(c, vm.state.value.conversation!!.id) as ApiResult.Success).value }.isEmpty())
        compose.onNodeWithTag("composer").performTextReplacement("Edited synthetic kettle 🫖 from composer")
        androidx.test.espresso.Espresso.closeSoftKeyboard()
        compose.waitUntil(5000) { !vm.voice.state.value.saving }
        compose.onNodeWithTag("send").assertIsEnabled().performClick()
        compose.waitUntil(20_000) { vm.state.value.submittedMessages.isNotEmpty() && vm.state.value.pending == null }
        val request = vm.state.value.submittedMessages.keys.single()
        val lineage = runBlocking { (api.voiceInput(c, request) as ApiResult.Success).value }
        assertEquals("Generated synthetic cattle 🫖", lineage.original_text)
        assertEquals("Edited synthetic kettle 🫖 from composer", lineage.reviewed_text)
        assertEquals("generated_interpretation", lineage.original_trust)
        assertEquals("user_reviewed", lineage.reviewed_origin)
        assertEquals("", vm.state.value.draft); assertNull(lineage.audio_sha256)
    }
    @Test fun cancelledHoldAndReleaseBeforeReadyDiscardLateResultsWithoutHttp() {
        val (api, c) = connect(); grantSyntheticMicrophone()
        for (cancelled in listOf(true, false)) {
            compose.runOnIdle { input.callback = null; vm.updateDraft("Preserved typed draft") }
            waitForStableMicrophone()
            compose.onNodeWithTag("voice-toggle").performTouchInput { down(center) }
            compose.waitUntil(5000) { input.callback != null }
            val late = input.callback!!
            if (cancelled) compose.runOnIdle { late.ready(); late.partial("Unfinished synthetic words") }
            compose.onNodeWithTag("voice-toggle").performTouchInput { if (cancelled) cancel() else up() }
            compose.waitUntil(5000) { !vm.voice.captureActive }
            compose.runOnIdle { late.ready(); late.partial("Late partial"); late.result("Late result") }
            assertNull(vm.voice.state.value.partialText); assertNull(vm.voice.state.value.draft)
            compose.onNodeWithTag("composer").assertTextContains("Preserved typed draft")
        }
        assertNull(vm.state.value.pending)
        assertTrue(runBlocking { (api.events(c, vm.state.value.conversation!!.id) as ApiResult.Success).value }.isEmpty())
    }
    @Test fun publicVoicePreviewAndEngineStatusNeverCaptureOrSubmit() {
        val (api, c) = connect()
        waitForStableMicrophone()
        compose.onNodeWithTag("voice-toggle").performTouchInput { click() }
        compose.onNodeWithTag("voice-controls-dialog").assertIsDisplayed()
        assertNull(input.callback)
        compose.onNodeWithTag("voice-controls-close").performClick()
        compose.onNodeWithTag("voice-toggle").performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.OnLongClick) { it() }
        compose.onNodeWithTag("voice-controls-dialog").assertIsDisplayed()
        assertNull(input.callback) // Accessibility has no held finger/Up event.
        compose.onNodeWithTag("voice-engine-details-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("voice-engine-status").performScrollTo().assertTextContains("Android on-device service", substring = true)
        compose.onNodeWithTag("voice-preview").performScrollTo().performClick()
        compose.waitUntil(5000) { vm.voice.state.value.playing }
        assertEquals(VOICE_PREVIEW_TEXT, output.text)
        assertNull(input.callback); assertNull(vm.voice.state.value.draft); assertNull(vm.state.value.pending)
        compose.onNodeWithTag("voice-stop-playback").performScrollTo().performClick()
        assertFalse(vm.voice.state.value.playing)
        assertTrue(runBlocking { (api.events(c, vm.state.value.conversation!!.id) as ApiResult.Success).value }.isEmpty())
        compose.runOnIdle { vm.voice.previewVoice(); vm.voice.observeForeground(false) }
        assertFalse(vm.voice.state.value.playing)
    }
    @Test fun explicitRecordReviewSendLineageAndPlaybackStopAreIndependentOfGeneration() {
        val (api, c) = connect()
        // Explicit test setup only. Production permission is requested by Record.
        InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand("pm grant ${compose.activity.packageName} android.permission.RECORD_AUDIO").close()
        compose.runOnIdle { vm.updateDraft("Independent typed draft") }
        compose.onNodeWithTag("voice-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("voice-controls-dialog").assertIsDisplayed()
        compose.onNodeWithTag("voice-record").performScrollTo().performClick()
        compose.waitUntil(5000) { input.callback != null }
        compose.runOnIdle { input.callback!!.ready() }
        compose.onNodeWithTag("voice-controls-close").assertIsNotEnabled()
        compose.onNodeWithTag("send").assertIsNotEnabled()
        compose.onNodeWithTag("voice-stop-recording").performScrollTo().performClick()
        assertEquals(1, input.stops)
        compose.runOnIdle { input.callback!!.result("Generated synthetic cattle 🫖 wording") }
        compose.waitUntil(5000) { vm.voice.state.value.draft != null && !vm.voice.state.value.saving }
        compose.onNodeWithTag("composer").assertTextContains("Generated synthetic cattle 🫖 wording", substring = true)
        compose.onNodeWithTag("voice-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("voice-send").performScrollTo().assertIsNotEnabled()
        compose.onNodeWithTag("voice-review").performScrollTo().performTextReplacement("Reviewed synthetic kettle 🫖 wording")
        // Finish the IME/edit journal before interacting with a relocated approval control.
        androidx.test.espresso.Espresso.closeSoftKeyboard()
        compose.waitUntil(10_000) { vm.voice.state.value.draft?.reviewedText == "Reviewed synthetic kettle 🫖 wording" && !vm.voice.state.value.saving }
        compose.runOnIdle { compose.activity.window.decorView.clearFocus() }
        compose.onNodeWithTag("voice-approve").performScrollTo().performClick()
        compose.onNodeWithTag("voice-approve").assertIsOn()
        compose.waitUntil(5000) { vm.voice.approvedDraft() != null }
        val original = vm.voice.state.value.draft!!.transcript
        compose.onNodeWithTag("voice-controls-close").assertIsDisplayed().performClick()
        compose.onNodeWithTag("voice-controls-dialog").assertDoesNotExist()
        assertNotNull(vm.voice.approvedDraft())
        assertEquals("Independent typed draft", vm.state.value.draft)
        assertTrue(runBlocking { (api.events(c, vm.state.value.conversation!!.id) as ApiResult.Success).value }.isEmpty())
        compose.onNodeWithTag("voice-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("voice-review").performScrollTo().assertTextContains("Reviewed synthetic kettle 🫖 wording")
        compose.onNodeWithTag("voice-approve").assertIsOn()
        compose.onNodeWithTag("voice-send").performScrollTo().assertIsEnabled().performClick()
        try {
            compose.waitUntil(20_000) { vm.state.value.submittedMessages.isNotEmpty() && vm.state.value.pending == null }
        } catch (_: androidx.compose.ui.test.ComposeTimeoutException) {
            val chat = vm.state.value; val voice = vm.voice.state.value
            fail("Reviewed Send state: pending=${chat.pending?.phase}, failure=${chat.pending?.failure?.javaClass?.simpleName}, fault=${chat.fault?.javaClass?.simpleName}, reserved=${chat.submittedMessages.size}, voice=${voice.phase}, approved=${voice.draft?.approved}, saving=${voice.saving}")
        }
        val id = vm.state.value.submittedMessages.keys.last()
        val lineage = runBlocking { (api.voiceInput(c, id) as ApiResult.Success).value }
        assertEquals(original.original_text, lineage.original_text); assertEquals("generated_interpretation", lineage.original_trust)
        assertEquals("Reviewed synthetic kettle 🫖 wording", lineage.reviewed_text); assertEquals("user_reviewed", lineage.reviewed_origin)
        assertNull(lineage.audio_sha256)
        val source = runBlocking { (api.source(c, lineage.endorsement_source_version_id) as ApiResult.Success).value }
        assertEquals("user_explicit", source.trust_class); assertEquals(lineage.reviewed_text, source.content)
        compose.runOnIdle { vm.updateDraft("Synthetic streaming alongside voice playback"); vm.send() }
        compose.waitUntil(20_000) { vm.state.value.stream?.provisional?.isNotEmpty() == true }
        val running = vm.state.value.pending!!.message.body.request_id
        compose.runOnIdle { vm.voice.play(id) }
        compose.waitUntil(5000) { vm.voice.state.value.playing }
        assertNotNull(output.text); assertFalse(output.text!!.contains(original.original_text))
        if (compose.onAllNodesWithTag("voice-controls-dialog").fetchSemanticsNodes().isEmpty()) {
            compose.onNodeWithTag("voice-toggle").performScrollTo().performClick()
        }
        compose.onNodeWithTag("voice-stop-playback").performScrollTo().performClick()
        assertEquals("running", runBlocking { (api.streamStatus(c, running) as ApiResult.Success).value }.stream_state)
        compose.runOnIdle { vm.stopGeneration() }
        compose.waitUntil(20_000) { vm.state.value.pending?.response?.error_code == "request_cancelled" }
        compose.runOnIdle { vm.openSources(id) }
        compose.waitUntil(5000) { vm.voice.state.value.lineage?.request_id == id }
        compose.onNodeWithTag("sources-list").performScrollToNode(hasTestTag("voice-lineage-$id"))
        compose.onNodeWithTag("voice-lineage-$id").assertIsDisplayed()
    }
    @Test fun reviewedDraftDiscardRequiresConfirmationAndNeverSends() {
        val (api, c) = connect()
        compose.runOnIdle { vm.voice.requestRecording(); vm.voice.permissionResult(true); input.callback!!.result("Public discard validation transcript") }
        compose.waitUntil(5000) { vm.voice.state.value.draft != null && !vm.voice.state.value.saving }
        val identity = SessionIdentity(c.server.toString(), vm.state.value.account!!.owner)
        val store = AndroidSessionStore(compose.activity.applicationContext)
        compose.onNodeWithTag("voice-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("voice-discard").performScrollTo().performClick()
        compose.onNodeWithTag("voice-discard-cancel").assertIsFocused().performClick()
        assertNotNull(vm.voice.state.value.draft)
        assertNotNull(runBlocking { store.voiceDraft(identity) })
        compose.onNodeWithTag("voice-discard").performScrollTo().performClick()
        compose.onNodeWithTag("voice-discard-confirm").performClick()
        compose.waitUntil(5000) { vm.voice.state.value.draft == null && !vm.voice.state.value.saving }
        assertNull(runBlocking { store.voiceDraft(identity) })
        assertNull(vm.state.value.pending)
        assertTrue(runBlocking { (api.events(c, vm.state.value.conversation!!.id) as ApiResult.Success).value }.isEmpty())
    }
    @Test fun denialBackgroundLateResultsAndEncryptedDraftRecoveryDoNotSend() {
        val (api, c) = connect()
        compose.runOnIdle { assertTrue(vm.voice.requestRecording()); vm.voice.permissionResult(false, true) }
        assertEquals(VoicePhase.Denied, vm.voice.state.value.phase)
        compose.runOnIdle { vm.voice.requestRecording(); vm.voice.permissionResult(true); input.callback!!.ready() }
        val late = input.callback!!
        compose.runOnIdle { vm.navigate(ChatDestination.Settings); late.result("Discarded late ASR") }
        assertNull(vm.voice.state.value.draft)
        compose.runOnIdle { vm.navigate(ChatDestination.Chat); vm.voice.requestRecording(); vm.voice.permissionResult(true); input.callback!!.ready() }
        val paused = input.callback!!
        compose.activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.STARTED)
        compose.activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.RESUMED)
        compose.runOnIdle { paused.result("Late result after actual activity pause") }
        assertNull(vm.voice.state.value.draft)
        compose.runOnIdle { vm.navigate(ChatDestination.Chat); vm.voice.requestRecording(); vm.voice.permissionResult(true); input.callback!!.result("Saved generated transcript") }
        compose.waitUntil(5000) { !vm.voice.state.value.saving && vm.voice.state.value.draft != null }
        compose.runOnIdle { vm.voice.edit("Saved reviewed wording"); vm.voice.approve(true) }
        compose.waitUntil(5000) { !vm.voice.state.value.saving }
        val identity = SessionIdentity(c.server.toString(), vm.state.value.account!!.owner)
        val store = AndroidSessionStore(compose.activity.applicationContext)
        assertNotNull(runBlocking { store.voiceDraft(identity) })
        assertTrue(runBlocking { (api.events(c, vm.state.value.conversation!!.id) as ApiResult.Success).value }.isEmpty())
        compose.runOnIdle { vm.voice.observeForeground(false) }
        assertFalse(vm.voice.state.value.playing)
        compose.runOnIdle { vm.logout() }; compose.waitUntil(5000) { vm.state.value.account == null }
        assertNull(vm.voice.state.value.draft); assertNull(runBlocking { store.voiceDraft(identity) })
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() } }
}

internal class InstrumentedVoiceCapture : SpeechCapture {
    override val availability = SpeechAvailability.Available
    override val version = "Explicit instrumented synthetic ASR adapter"
    var callback: CaptureListener? = null; var stops = 0
    override fun start(language: String, listener: CaptureListener) { callback = listener }
    override fun stop() { stops++ }
    override fun cancel() {}
    override fun close() {}
}
internal class InstrumentedVoicePlayback : SpeechPlayback {
    var text: String? = null
    override fun initialize(ready: (List<SpeechVoice>) -> Unit) = ready(listOf(SpeechVoice("synthetic-offline", "Synthetic offline voice", "en-US")))
    override fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit) { this.text = text }
    override fun stop() {}
    override fun close() {}
}
