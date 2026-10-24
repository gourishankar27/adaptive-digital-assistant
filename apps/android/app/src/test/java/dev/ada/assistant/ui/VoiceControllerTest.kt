package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import org.junit.Assert.*
import org.junit.Test

private val voiceConversation = adaJson.decodeFromString<ConversationDto>(fixture("conversation-current.json"))
private val voiceOwner = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val voiceConnection = ConnectionCredential.parse(voiceOwner.server, "synthetic-voice-test-token", false)!!
private val voiceFeatures = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(
    streaming = true, generation_cancellation = true, stream_protocol = "ada-stream-v1", voice_input = VOICE_PROTOCOL)
private class VoiceReviewStore : SessionStore {
    var draft: VoiceDraft? = null; var fail = false
    var gate: CompletableDeferred<Unit>? = null
    override suspend fun voiceDraft(identity: SessionIdentity) = draft?.takeIf { it.identity == identity }
    override suspend fun saveVoiceDraft(draft: VoiceDraft) { gate?.let { withContext(NonCancellable) { it.await() } }; if (fail) throw SessionStorageException(); validateVoiceDraft(draft); this.draft = draft }
    override suspend fun removeVoiceDraft(identity: SessionIdentity, transcript: UUID) { if (draft?.identity == identity && draft?.transcript?.transcript_id == transcript) draft = null }
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) {}
    override suspend fun clear() { draft = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) = error("Controller must not submit")
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {}
}
private fun noVoiceApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected: ${method.name}") } as AdaApi
private class VoiceReviewApi : AdaApi by noVoiceApi() {
    var response = adaJson.decodeFromString<RequestDto>(fixture("request-current.json")).copy(conversation_id = voiceConversation.id)
    var gate: CompletableDeferred<ApiResult<RequestDto>>? = null
    override suspend fun voiceInputs(connection: ConnectionCredential, conversation: UUID) = ApiResult.Success(emptyList<VoiceLineageDto>())
    override suspend fun request(connection: ConnectionCredential, id: UUID): ApiResult<RequestDto> = gate?.let { withContext(NonCancellable) { it.await() } } ?: ApiResult.Success(response.copy(request_id = id))
}
private class Recorder(private val continuous: Boolean=false) : SpeechCapture {
    override val longForm get()=continuous
    override val longFormAvailable get()=continuous
    override val modelSha256 get()=if(continuous) "a".repeat(64) else null
    var rows=emptyList<TranscriptSegmentDto>()
    override fun transcriptSegments()=rows
    override var availability = SpeechAvailability.Available
    override val version get()=if(continuous) "sherpa-onnx-1.13.8" else "Android synthetic test engine"
    var callback: CaptureListener? = null; var starts = 0; var stops = 0; var cancels = 0
    override fun start(language: String, listener: CaptureListener) { starts++; callback = listener }
    override fun stop() { stops++ }
    override fun cancel() { cancels++ }
    override fun close() { cancel() }
}
private class Player : SpeechPlayback {
    var text: String? = null; var stops = 0; var done: ((String?) -> Unit)? = null
    override fun initialize(ready: (List<SpeechVoice>) -> Unit) = ready(listOf(SpeechVoice("offline-en", "Offline English", "en-US")))
    override fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit) { this.text = text; done = finished }
    override fun stop() { stops++ }
    override fun close() { stop() }
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class VoiceControllerTest {
    @Test fun holdReleaseShowsPartialThenEncryptedEditableDraftWithoutApproval() = runTest {
        val (c, _, store, input) = ready()
        val key = c.requestHoldRecording("Typed introduction:")!!
        c.permissionResult(true); input.callback!!.ready()
        input.callback!!.partial("Generated partial")
        assertEquals("Typed introduction: Generated partial", c.state.value.partialText)
        assertNull(store.draft); assertNull(c.composerDraftForSend())
        c.releaseHoldRecording(key); assertEquals(1, input.stops)
        input.callback!!.result("Generated cattle 🫖"); runCurrent()
        assertNull(c.state.value.partialText)
        assertEquals("Typed introduction: Generated cattle 🫖", store.draft!!.reviewedText)
        assertFalse(store.draft!!.approved); assertNull(c.approvedDraft())
        c.edit("Typed introduction: Reviewed kettle 🫖"); runCurrent()
        assertEquals("Reviewed kettle 🫖", c.composerDraftForSend()!!.reviewedText.substringAfter(": "))
        assertEquals("Generated cattle 🫖", store.draft!!.transcript.original_text)
        c.reset()
    }
    @Test fun holdReleasedBeforePermissionOrReadyCannotStartLateCapture() = runTest {
        for (permission in listOf(false, true)) {
            val (c, _, store, input) = ready()
            val key = c.requestHoldRecording()!!
            if (permission) c.permissionResult(true)
            val late = input.callback
            c.releaseHoldRecording(key)
            c.permissionResult(true); late?.ready(); late?.result("Late generated words"); runCurrent()
            assertFalse(c.captureActive); assertNull(store.draft); assertNull(c.state.value.draft)
            assertEquals(if (permission) 1 else 0, input.starts)
            c.reset()
        }
    }
    @Test fun cancelledHoldAndOldReleaseCannotAffectNewCaptureOrKeepPartialWords() = runTest {
        val (c, _, store, input) = ready()
        val old = c.requestHoldRecording()!!; c.permissionResult(true); input.callback!!.ready()
        val late = input.callback!!; late.partial("Private synthetic partial")
        c.releaseHoldRecording(old, cancelled = true)
        assertNull(c.state.value.partialText)
        val next = c.requestHoldRecording()!!; c.permissionResult(true); input.callback!!.ready()
        c.releaseHoldRecording(old); late.result("Old generated result")
        assertEquals(VoicePhase.Recording, c.state.value.phase); assertEquals(0, input.stops)
        c.releaseHoldRecording(next); input.callback!!.result("Current generated result"); runCurrent()
        assertEquals("Current generated result", store.draft!!.reviewedText)
        c.reset()
    }
    @Test fun combinedOverLimitDraftIsEditableButCannotBeSentOrSavedUntilShortened() = runTest {
        val (c, _, store, input) = ready()
        c.requestHoldRecording("a".repeat(3999)); c.permissionResult(true); input.callback!!.result("word"); runCurrent()
        assertNotNull(c.state.value.draft); assertNull(store.draft); assertNull(c.composerDraftForSend())
        c.edit("Short reviewed wording"); runCurrent()
        assertNotNull(c.composerDraftForSend()); assertNotNull(store.draft)
        c.reset()
    }
    private data class Rig(val c: VoiceController, val api: VoiceReviewApi, val store: VoiceReviewStore, val input: Recorder, val output: Player)
    private fun TestScope.ready(continuous:Boolean=false): Rig {
        val store = VoiceReviewStore(); val api = VoiceReviewApi(); val recorder = Recorder(continuous); val player = Player()
        val c = VoiceController(api, store, this, {}, { testScheduler.currentTime })
        c.attachAudio(recorder, player); c.setVerifiedSession(voiceConnection, voiceOwner, voiceFeatures.copy(long_voice_input=if(continuous) LONG_VOICE_PROTOCOL else "unsupported"))
        c.context(voiceConversation, true, false); runCurrent()
        return Rig(c, api, store, recorder, player)
    }
    @Test fun continuousInputSurvivesSixtySecondsAndRecoversCompletedCheckpointAfterPause() = runTest {
        val(c,_,store,input)=ready(true)
        assertTrue(c.requestRecording()); c.permissionResult(true); input.callback!!.ready()
        advanceTimeBy(80000); runCurrent()
        assertEquals(0,input.stops); assertEquals(VoicePhase.Recording,c.state.value.phase)
        val row=TranscriptSegmentDto(UUID.randomUUID(),0,80000,"Public completed segment",voiceHash("Public completed segment"))
        input.rows=listOf(row)
        var committed=false
        input.callback!!.checkpoint(input.rows,80000) { committed=it }; runCurrent()
        assertTrue(committed); assertNotNull(store.draft); assertNull(c.state.value.draft)
        c.observeForeground(false); c.observeForeground(true); runCurrent()
        assertEquals("Public completed segment",c.state.value.draft!!.transcript.original_text)
        assertFalse(c.state.value.draft!!.approved); assertNull(c.approvedDraft()); c.reset()
    }
    @Test fun explicitDiscardRemovesContinuousCheckpointsAndRejectsLateSaving() = runTest {
        val(c,_,store,input)=ready(true)
        c.requestRecording(); c.permissionResult(true); input.callback!!.ready()
        val row=TranscriptSegmentDto(UUID.randomUUID(),0,5000,"Public checkpoint",voiceHash("Public checkpoint"))
        val old=input.callback!!
        old.checkpoint(listOf(row),5000) {}; runCurrent(); assertNotNull(store.draft)
        c.discard(); runCurrent(); assertNull(store.draft)
        var late=true; old.checkpoint(listOf(row),5000) {late=it}; runCurrent()
        assertFalse(late); assertNull(store.draft); c.reset()
    }
    @Test fun publicPreviewDoesNotReadOrWriteServerDataAndLateCompletionIsFenced() = runTest {
        val (c, api, store, input, output) = ready()
        api.gate = CompletableDeferred() // Preview must not wait for an HTTP reply.
        c.previewVoice()
        assertTrue(c.state.value.playing)
        assertEquals(VOICE_PREVIEW_TEXT, output.text)
        assertNull(store.draft); assertEquals(0, input.starts)
        val late = output.done!!
        c.stopPlayback(); c.previewVoice(); late("old error")
        assertTrue(c.state.value.playing)
        c.observeForeground(false)
        assertFalse(c.state.value.playing)
        val previous = output.text; c.previewVoice(); assertEquals(previous, output.text)
        c.reset()
    }
    @Test fun previewCannotInterruptRecordingOrSurviveIdentityOrNavigationChanges() = runTest {
        val (c, _, _, input, output) = ready()
        c.requestRecording(); c.permissionResult(true); input.callback!!.ready()
        c.previewVoice(); assertNull(output.text)
        c.discard(); c.previewVoice(); assertTrue(c.state.value.playing)
        c.context(voiceConversation, false, false); assertFalse(c.state.value.playing)
        c.context(voiceConversation, true, false); c.previewVoice()
        val late = output.done!!; c.reset(); late(null)
        assertFalse(c.state.value.playing); c.previewVoice(); assertFalse(c.state.value.playing)
    }
    @Test fun missingMatchingLanguageRequiresExplicitVoiceChoiceAndNeverSwitchesSilently() = runTest {
        val (c, _, _, input) = ready()
        val player = object : SpeechPlayback {
            var plays = 0
            override fun initialize(ready: (List<SpeechVoice>) -> Unit) = ready(listOf(SpeechVoice("fr", "French", "fr-FR")))
            override fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit) { plays++ }
            override fun stop() = Unit
            override fun close() = Unit
        }
        c.attachAudio(input, player); assertNull(c.state.value.voiceId)
        c.previewVoice(); assertEquals(0, player.plays)
        c.selectVoice("fr"); c.previewVoice(); assertEquals(1, player.plays)
        c.reset()
    }
    @Test fun ownPermissionDialogDefersGrantUntilTheSameHostResumes() = runTest {
        val (c, _, store, input) = ready()
        assertTrue(c.requestRecording()); c.permissionDialogLaunched()
        c.observeForeground(false); c.permissionResult(true)
        assertEquals(VoicePhase.Permission,c.state.value.phase)
        assertEquals(0,input.starts); assertNull(store.draft)
        c.observeForeground(true)
        assertEquals(1,input.starts); assertEquals(VoicePhase.Checking,c.state.value.phase)
        c.reset()
    }
    @Test fun ownDialogDenialAndPermanentDenialAreNotLostOnPause() = runTest {
        for (permanent in listOf(false,true)) {
            val (c, _, store, input) = ready()
            c.requestRecording(); c.permissionDialogLaunched(); c.observeForeground(false)
            c.permissionResult(false,permanent); c.observeForeground(true)
            assertEquals(VoicePhase.Denied,c.state.value.phase)
            assertEquals(permanent,c.state.value.permissionPermanent)
            assertEquals(0,input.starts); assertNull(store.draft); c.reset()
        }
    }
    @Test fun stoppedHostAndChangedOwnerFencePermissionResults() = runTest {
        val (c, _, _, input) = ready()
        c.requestRecording(); c.permissionDialogLaunched(); c.observeForeground(false)
        c.permissionHostStopped(); c.permissionResult(true); c.observeForeground(true)
        assertEquals(VoicePhase.Interrupted,c.state.value.phase); assertEquals(0,input.starts)
        c.requestRecording(); c.permissionDialogLaunched(); c.reset()
        c.permissionResult(true); c.observeForeground(true); assertEquals(0,input.starts)
        c.reset()
    }
    @Test fun navigationAndPendingTurnFencePermissionWithoutStartingCapture() = runTest {
        val (c, _, _, input) = ready()
        c.requestRecording(); c.permissionDialogLaunched(); c.observeForeground(false)
        c.context(voiceConversation,false,false); c.permissionResult(true); c.observeForeground(true)
        assertEquals(0,input.starts); assertEquals(VoicePhase.Interrupted,c.state.value.phase)
        c.context(voiceConversation,true,false); c.requestRecording(); c.permissionDialogLaunched()
        c.context(voiceConversation,true,true); c.permissionResult(true)
        assertEquals(0,input.starts); c.reset()
    }
    @Test fun ordinaryPauseWithoutOwnDialogStillCancelsPermissionIntent() = runTest {
        val (c, _, _, input) = ready()
        c.requestRecording(); c.observeForeground(false); c.permissionResult(true); c.observeForeground(true)
        assertEquals(VoicePhase.Interrupted,c.state.value.phase); assertEquals(0,input.starts); c.reset()
    }
    @Test fun savedDraftInAnotherConversationBlocksCaptureUntilOpenedOrDiscarded() = runTest {
        val (c, _, store, input) = ready()
        c.requestRecording(); c.permissionResult(true); input.callback!!.result("Generated owned draft"); runCurrent()
        val original = store.draft!!
        c.context(voiceConversation.copy(id = UUID.randomUUID()), true, false)
        assertFalse(c.requestRecording()); runCurrent()
        assertEquals(original.conversationId, c.state.value.savedDraftConversation); assertFalse(c.requestRecording())
        c.discard(); runCurrent(); assertNull(store.draft); assertNull(c.state.value.savedDraftConversation)
        assertTrue(c.requestRecording()); c.reset()
    }
    @Test fun saveInterruptedByBackgroundChecksCommittedDraftOnResumeWithoutSending() = runTest {
        val (c, _, store, input) = ready()
        store.gate = CompletableDeferred()
        c.requestRecording(); c.permissionResult(true); input.callback!!.result("Generated delayed draft"); runCurrent()
        assertTrue(c.state.value.saving); c.observeForeground(false); assertNull(c.state.value.draft)
        store.gate!!.complete(Unit); runCurrent(); assertNotNull(store.draft)
        c.observeForeground(true); runCurrent(); assertEquals(store.draft,c.state.value.draft)
        assertFalse(c.state.value.draftLoading); assertNull(c.approvedDraft()); c.reset()
    }
    @Test fun permissionDenialHardwareAndLanguageDoNotCaptureOrPost() = runTest {
        val (c, _, store, input) = ready()
        assertEquals("en-US", c.state.value.language)
        assertTrue(c.requestRecording()); c.permissionResult(false, true)
        assertEquals(VoicePhase.Denied, c.state.value.phase); assertTrue(c.state.value.permissionPermanent)
        assertEquals(0, input.starts); assertNull(store.draft)
        input.availability = SpeechAvailability.NoMicrophone
        assertFalse(c.requestRecording()); assertEquals(VoicePhase.Unavailable, c.state.value.phase)
        input.availability = SpeechAvailability.Available; c.language("invalid_tag")
        assertFalse(c.requestRecording()); c.reset()
    }
    @Test fun recordingReviewAndEditInvalidateApprovalAndNeverSendAutomatically() = runTest {
        val (c, _, store, input) = ready()
        assertTrue(c.requestRecording()); c.permissionResult(true); input.callback!!.ready()
        advanceTimeBy(1500); c.stopCapture(); assertEquals(1, input.stops)
        input.callback!!.result("Generated cattle 🫖"); runCurrent()
        assertNull(c.approvedDraft()); assertEquals("Generated cattle 🫖", store.draft!!.transcript.original_text)
        c.edit("Reviewed kettle 🫖"); runCurrent(); c.approve(true); runCurrent()
        assertEquals("Reviewed kettle 🫖", c.approvedDraft()!!.reviewedText)
        assertEquals(1500, c.approvedDraft()!!.transcript.duration_ms)
        c.edit("Edited again"); runCurrent(); assertNull(c.approvedDraft())
        assertEquals("Generated cattle 🫖", store.draft!!.transcript.original_text)
        c.discard(); runCurrent(); assertNull(store.draft); assertNull(c.state.value.draft); c.reset()
    }
    @Test fun maxDurationAndTimeoutStopCaptureAndLateCallbacksAreIgnored() = runTest {
        val (c, _, store, input) = ready()
        c.requestRecording(); c.permissionResult(true); input.callback!!.ready(); val late = input.callback!!
        advanceTimeBy(60_001); runCurrent(); assertEquals(1, input.stops); assertEquals(VoicePhase.Transcribing, c.state.value.phase)
        advanceTimeBy(15_001); runCurrent(); assertEquals(VoicePhase.Error, c.state.value.phase)
        late.result("Late generated text"); runCurrent(); assertNull(store.draft)
        c.requestRecording(); c.permissionResult(true); val background = input.callback!!
        c.observeForeground(false); background.result("Background generated text"); runCurrent()
        assertNull(c.state.value.draft); assertNull(store.draft); c.reset()
    }
    @Test fun encryptedSaveFailureApprovalRecoveryAndScopeSwitchFailClosed() = runTest {
        val (c, _, store, input) = ready(); store.fail = true
        c.requestRecording(); c.permissionResult(true); input.callback!!.result("Generated review"); runCurrent()
        assertNotNull(c.state.value.fault); c.approve(true); runCurrent(); assertNull(c.approvedDraft())
        store.fail = false; c.saveAgain(); runCurrent(); c.approve(true); runCurrent(); assertNotNull(c.approvedDraft())
        c.context(voiceConversation.copy(id = UUID.randomUUID()), true, false); runCurrent(); assertNull(c.state.value.draft)
        c.context(voiceConversation, true, false); runCurrent(); assertNotNull(c.state.value.draft)
        c.reset(); assertNull(c.state.value.draft); input.callback!!.result("Old owner callback"); runCurrent(); assertNull(c.state.value.draft)
    }
    @Test fun playbackRequiresOwnedCompletedSafeTextAndStopNeverCancelsGeneration() = runTest {
        val (c, api, store, _, player) = ready(); val rid = UUID.randomUUID()
        api.response = api.response.copy(status = "running", response = "Partial")
        c.play(rid); runCurrent(); assertNull(player.text)
        api.response = api.response.copy(status = "completed", response = "<think>hidden</think>Hello [M1] ```debug``` https://private.test/quote")
        c.play(rid); runCurrent(); assertEquals("Hello", player.text); assertTrue(c.state.value.playing)
        player.done!!.invoke("Focus interrupted"); assertFalse(c.state.value.playing)
        c.play(rid); runCurrent(); c.stopPlayback(); assertFalse(c.state.value.playing)
        c.play(rid); runCurrent(); c.observeForeground(false); assertFalse(c.state.value.playing); c.reset()
    }
    @Test fun delayedPlaybackCannotCrossOwnerOrConversationAndOldVoiceCapabilitiesAreOptional() = runTest {
        val (c, api, store, _, player) = ready(); val rid = UUID.randomUUID()
        api.gate = CompletableDeferred(); c.play(rid); runCurrent()
        c.reset(); api.gate!!.complete(ApiResult.Success(api.response.copy(request_id = rid))); runCurrent()
        assertNull(player.text); assertFalse(c.state.value.playing)
        c.setVerifiedSession(voiceConnection, voiceOwner, voiceFeatures.copy(voice_input = "unsupported"))
        store.draft = VoiceDraft(voiceOwner, voiceConversation.id, voiceConversation.scope_id,
            TranscriptInputDto(UUID.randomUUID(), "android_on_device", "Synthetic old-server test", "en-US", 1, "Generated old draft"), "Reviewed old draft", true)
        c.context(voiceConversation, true, false); runCurrent(); assertFalse(c.requestRecording())
        assertNotNull(c.state.value.draft); assertNull(c.approvedDraft()); c.reset()
    }
}
