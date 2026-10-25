package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.flow
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

private val owner = UUID.fromString("00000000-0000-4000-8000-000000000001")
private val conversation = adaJson.decodeFromString<ConversationDto>(fixture("conversation-current.json"))
private val capabilities = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json"))

private class MemorySessionStore : SessionStore {
    var voice: VoiceDraft? = null
    override suspend fun voiceDraft(identity: SessionIdentity) = voice?.takeIf { it.identity == identity }
    override suspend fun saveVoiceDraft(draft: VoiceDraft) { if (failJournal) throw SessionStorageException(); voice = draft }
    override suspend fun removeVoiceDraft(identity: SessionIdentity, transcript: UUID) { if (voice?.identity == identity && voice?.transcript?.transcript_id == transcript) voice = null }
    var credential: StoredCredential? = null
    var journal: PendingMessage? = null
    var failJournal = false
    var failClear = false
    var failRemove = false
    var journalGate: CompletableDeferred<Unit>? = null
    val writes = mutableListOf<String>()
    override suspend fun readCredential() = credential
    override suspend fun saveCredential(credential: StoredCredential) {
        if (this.credential?.identity != credential.identity) journal = null
        this.credential = credential
    }
    override suspend fun clear() {
        if (failClear) error("Synthetic cleanup failure")
        credential = null; journal = null; writes += "clear"
    }
    override suspend fun pending(identity: SessionIdentity) = journal?.takeIf { it.identity == identity }
    override suspend fun savePending(message: PendingMessage) {
        journalGate?.await()
        if (failJournal) error("Synthetic storage failure")
        if (message.voiceTranscript != null && journal == null) {
            check(voice?.approved == true && voice?.reviewedText == message.body.content && voice?.transcript == message.voiceTranscript)
            voice = null
        }
        journal = message; writes += "journal"
    }
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) {
        if (failRemove) error("Synthetic journal cleanup failure")
        if (journal?.identity == identity && journal?.body?.request_id == requestId) journal = null
        writes += "remove"
    }
}

private fun unsupportedChatApi(): AdaApi = java.lang.reflect.Proxy.newProxyInstance(
    AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java),
) { _, method, _ -> error("Unexpected test call: ${method.name}") } as AdaApi

private class ContinuousChatRecorder:SpeechCapture {
    override val availability=SpeechAvailability.Available
    override val version="sherpa-onnx-1.13.8"
    override val longFormAvailable=true
    override var longForm=false
    override val modelSha256="a".repeat(64)
    var callback:CaptureListener?=null; var cancels=0; var stops=0
    override fun selectLongForm(enabled:Boolean):Boolean {longForm=enabled;return true}
    override fun start(language:String,listener:CaptureListener) {callback=listener}
    override fun stop() {stops++}
    override fun cancel() {cancels++}
    override fun close() {cancel()}
}
private class ContinuousChatPlayer:SpeechPlayback {
    override fun initialize(ready:(List<SpeechVoice>)->Unit)=ready(emptyList())
    override fun play(text:String,voice:String,speed:Float,finished:(String?)->Unit)=Unit
    override fun stop()=Unit
    override fun close()=Unit
}

private class ChatApiMock(val store: MemorySessionStore) : AdaApi by unsupportedChatApi() {
    var passwordLifetimeMs = 900000L
    var passwordRenewals = 0
    var passwordLogouts = 0
    var passwordRefreshGate:CompletableDeferred<Unit>?=null
    var passwordRefreshUnavailable=false
    private val passwordFamily=UUID.randomUUID()
    override suspend fun passwordLogin(server: String, username: String, password: String, allowDebugHttp: Boolean) = ApiResult.Success(PasswordSessionDto("synthetic-password-access", "synthetic-password-refresh"+(if(passwordRenewals==0) "" else "-$passwordRenewals"), passwordFamily, System.currentTimeMillis() + passwordLifetimeMs, System.currentTimeMillis() + 1000000))
    override suspend fun refreshLogin(server: String, refresh: String, allowDebugHttp: Boolean): ApiResult<PasswordSessionDto> {
        passwordRenewals++
        passwordRefreshGate?.await()
        if(passwordRefreshUnavailable) return ApiResult.Failure(ApiFailure.Unreachable)
        return passwordLogin(server, "", "", allowDebugHttp)
    }
    override suspend fun logoutSession(connection: ConnectionCredential, all: Boolean): ApiResult<AuthAcknowledgementDto> { passwordLogouts++; return ApiResult.Success(AuthAcknowledgementDto("signed_out")) }

    val voicePosts = mutableListOf<ReviewedVoiceInputDto>()
    var voiceReject = false
    override suspend fun voiceInputs(connection: ConnectionCredential, conversation: UUID) = ApiResult.Success(emptyList<VoiceLineageDto>())
    override suspend fun submitVoice(connection: ConnectionCredential, conversation: UUID, body: ReviewedVoiceInputDto): ApiResult<StreamStatusDto> {
        assertEquals(body, ReviewedVoiceInputDto.from(store.journal!!)); assertNull(store.voice)
        voicePosts += body
        if (voiceReject) return ApiResult.Failure(ApiFailure.Validation)
        val result = completed(body.request_id).copy(status = "running", response = null)
        streamSnapshot = StreamStatusDto(body.request_id, conversation, result.attempt, true, "running", 1, 0, "", result)
        return ApiResult.Success(streamSnapshot!!)
    }
    var streamSnapshot: StreamStatusDto? = null
    val streamChannel = Channel<ApiResult<StreamEventDto>>(Channel.UNLIMITED)
    var detached = 0
    var streamPosts = 0
    val stops = mutableListOf<Pair<UUID, Int>>()
    override suspend fun submitStream(connection: ConnectionCredential, conversation: UUID, body: ChatInputDto): ApiResult<StreamStatusDto> {
        assertEquals(body, store.journal!!.body); store.writes += "stream-post"; streamPosts++
        val result = completed(body.request_id).copy(status = "running", response = null)
        streamSnapshot = StreamStatusDto(body.request_id, conversation, result.attempt, true, "running", 1, 0, "", result)
        return ApiResult.Success(streamSnapshot!!)
    }
    override suspend fun streamStatus(connection: ConnectionCredential, id: UUID): ApiResult<StreamStatusDto> = streamSnapshot?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override fun streamEvents(connection: ConnectionCredential, id: UUID, attempt: Int, after: Int) = flow {
        try { for (event in streamChannel) emit(event) } finally { detached++ }
    }
    override suspend fun cancelGeneration(connection: ConnectionCredential, id: UUID, attempt: Int): ApiResult<CancelReceiptDto> {
        stops += id to attempt
        return ApiResult.Success(CancelReceiptDto(id, attempt, "requested", "running", 1))
    }
    var user = owner
    var meCall: suspend () -> ApiResult<MeDto> = { ApiResult.Success(MeDto(user, "Synthetic account")) }
    var sendCall: suspend (ChatInputDto) -> ApiResult<RequestDto> = { body -> ApiResult.Success(completed(body.request_id)) }
    var requestCall: suspend (UUID) -> ApiResult<RequestDto> = { id -> ApiResult.Success(completed(id)) }
    var createCall: suspend () -> ApiResult<ConversationDto> = { ApiResult.Success(conversation) }
    var profileCall: suspend () -> ApiResult<PersonalityDto> = { ApiResult.Failure(ApiFailure.Timeout) }
    var conversationRow = conversation
    var upgradeCall: suspend (UUID) -> ApiResult<PromptUpgradeDto> = { ApiResult.Failure(ApiFailure.Conflict) }
    val upgraded = mutableListOf<UUID>()
    var features = capabilities
    var profileRows = emptyList<PersonalityDto>()
    val sent = mutableListOf<ChatInputDto>()
    val queried = mutableListOf<UUID>()
    var created = 0
    var profilesCreated = 0
    var conversationReads = 0
    var eventPages = mutableListOf<List<EventDto>>(emptyList())
    val eventOffsets = mutableListOf<Int>()
    override suspend fun me(connection: ConnectionCredential) = meCall()
    override suspend fun capabilities(connection: ConnectionCredential) = ApiResult.Success(features)
    override suspend fun personalities(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(profileRows)
    override suspend fun scopes(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(emptyList<ScopeDto>())
    override suspend fun conversations(connection: ConnectionCredential, limit: Int, offset: Int): ApiResult<List<ConversationDto>> {
        conversationReads++; return ApiResult.Success(listOf(conversationRow))
    }
    override suspend fun conversation(connection: ConnectionCredential, id: UUID) = ApiResult.Success(conversationRow)
    override suspend fun upgradePrompt(connection: ConnectionCredential, id: UUID): ApiResult<PromptUpgradeDto> {
        upgraded += id; return upgradeCall(id)
    }
    override suspend fun events(connection: ConnectionCredential, id: UUID, limit: Int, offset: Int): ApiResult<List<EventDto>> {
        eventOffsets += offset
        return ApiResult.Success(if (eventPages.size > 1) eventPages.removeAt(0) else eventPages[0])
    }
    override suspend fun send(connection: ConnectionCredential, conversation: UUID, body: ChatInputDto): ApiResult<RequestDto> {
        assertNotNull("Journal must exist before POST", store.journal)
        assertEquals(body, store.journal!!.body)
        sent += body; store.writes += "post"; return sendCall(body)
    }
    override suspend fun request(connection: ConnectionCredential, id: UUID): ApiResult<RequestDto> {
        queried += id; return requestCall(id)
    }
    override suspend fun createConversation(connection: ConnectionCredential, body: ConversationInputDto): ApiResult<ConversationDto> {
        created++; return createCall()
    }
    override suspend fun createPersonality(connection: ConnectionCredential, body: PersonalityInputDto): ApiResult<PersonalityDto> {
        profilesCreated++; return profileCall()
    }
    override suspend fun trace(connection: ConnectionCredential, id: UUID) = ApiResult.Failure(ApiFailure.NotFound)
}

private fun completed(id: UUID) = adaJson.decodeFromString<RequestDto>(fixture("request-current.json"))
    .copy(request_id = id, conversation_id = conversation.id)
private fun journal(identity: SessionIdentity) = PendingMessage(identity, conversation.id,
    ChatInputDto(UUID.randomUUID(), "Exact synthetic \uD83D\uDE00 text\n", "2026-10-08T00:00:00.000Z", false))

@OptIn(ExperimentalCoroutinesApi::class)
class ChatViewModelTest {
    @Test fun heldComposerAppendsTypedPrefixDiscardRestoresItAndSendClearsOnlyIncludedText() = runTest {
        val (vm, api, _) = ready(streaming = true)
        var callback: CaptureListener? = null
        val recorder = object : SpeechCapture {
            override val availability = SpeechAvailability.Available
            override val version = "Synthetic held composer capture"
            override fun start(language: String, listener: CaptureListener) { callback = listener }
            override fun stop() {}
            override fun cancel() {}
            override fun close() {}
        }
        val player = object : SpeechPlayback {
            override fun initialize(ready: (List<SpeechVoice>) -> Unit) = ready(emptyList())
            override fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit) {}
            override fun stop() {}
            override fun close() {}
        }
        vm.voice.attachAudio(recorder, player); vm.updateDraft("Typed introduction:")
        var key = vm.requestHeldVoiceRecording()!!; vm.voice.permissionResult(true); callback!!.ready()
        vm.updateComposerDraft("Ignored during capture")
        vm.voice.releaseHoldRecording(key); callback!!.result("Generated first attempt"); runCurrent()
        assertEquals("Typed introduction: Generated first attempt", vm.voice.state.value.draft!!.reviewedText)
        vm.voice.discard(); runCurrent(); assertEquals("Typed introduction:", vm.state.value.draft)
        key = vm.requestHeldVoiceRecording()!!; vm.voice.permissionResult(true); callback!!.ready()
        vm.voice.releaseHoldRecording(key); callback!!.result("Generated final words"); runCurrent()
        vm.updateMemory(false); vm.send(); runCurrent()
        assertEquals("Typed introduction: Generated final words", api.voicePosts.single().content)
        assertFalse(api.voicePosts.single().use_memory); assertEquals("", vm.state.value.draft)
        vm.observeForeground(false)
    }
    @Test fun composerSendApprovesEditedVoicePersistsBeforeHttpAndNeverUsesPlainFallback() = runTest {
        val (vm, api, store) = voiceReady()
        vm.voice.approve(false); runCurrent()
        vm.updateComposerDraft("Edited in the ordinary composer 🫖"); runCurrent()
        assertFalse(store.voice!!.approved); assertTrue(api.voicePosts.isEmpty())
        vm.send(); vm.send(); runCurrent()
        assertEquals(1, api.voicePosts.size); assertTrue(api.sent.isEmpty()); assertEquals(0, api.streamPosts)
        assertEquals("Edited in the ordinary composer 🫖", api.voicePosts.single().content)
        assertEquals("Original generated cattle", api.voicePosts.single().transcript.original_text)
        assertEquals("approve", api.voicePosts.single().review)
        vm.observeForeground(false)
    }
    @Test fun composerVoiceSaveFailureAndInFlightEditNeverLoseOrSubmitTheDraft() = runTest {
        val (vm, api, store) = voiceReady()
        vm.voice.approve(false); runCurrent()
        vm.updateComposerDraft("Exact composer review"); vm.send()
        assertNull(vm.state.value.pending) // Edit must finish encrypting first.
        runCurrent(); store.failJournal = true; vm.send(); runCurrent()
        assertNull(vm.state.value.pending); assertNotNull(vm.voice.state.value.draft)
        assertTrue(api.voicePosts.isEmpty()); assertEquals(0, api.streamPosts); assertTrue(api.sent.isEmpty())
        store.failJournal = false; vm.send(); runCurrent()
        assertEquals(1, api.voicePosts.size); assertEquals("Exact composer review", api.voicePosts.single().content)
        vm.observeForeground(false)
    }
    @Before fun setup() { Dispatchers.setMain(StandardTestDispatcher()) }
    @After fun cleanup() { Dispatchers.resetMain() }
    private suspend fun TestScope.voiceReady(): Triple<ChatViewModel, ChatApiMock, MemorySessionStore> {
        val (vm, api, store) = ready(streaming = true)
        val features = api.features.copy(voice_input = VOICE_PROTOCOL)
        api.features = features
        vm.voice.setVerifiedSession(ConnectionCredential.parse("http://localhost:8000", "synthetic-test-token", true)!!, store.credential!!.identity, features)
        vm.voice.context(conversation, true, false); runCurrent()
        val transcript = TranscriptInputDto(UUID.randomUUID(), "android_on_device", "Android synthetic test", "en-US", 2000, "Original generated cattle")
        vm.voice.rejected(PendingMessage(store.credential!!.identity, conversation.id, ChatInputDto(UUID.randomUUID(), "Reviewed kettle"), transcript, conversation.scope_id))
        runCurrent(); vm.voice.approve(true); runCurrent()
        return Triple(vm, api, store)
    }
    @Test fun shortAccessLifetimeDoesNotCauseARefreshLoop() = runTest {
        val store = MemorySessionStore(); val api = ChatApiMock(store); api.passwordLifetimeMs = 60000
        val vm = ChatViewModel(api, store, true)
        vm.passwordLogin("http://localhost:8000", "synthetic-user", "Public synthetic passphrase"); runCurrent()
        advanceTimeBy(5000); runCurrent()
        assertEquals(0, api.passwordRenewals)
        vm.logout(); runCurrent()
    }
    @Test fun passwordLoginReopenRenewLogoutNeverStoresAccessOrReplaysMessages() = runTest {
        val store = MemorySessionStore(); val api = ChatApiMock(store); val vm = ChatViewModel(api, store, true)
        vm.passwordLogin("http://localhost:8000", "synthetic-user", "Public synthetic passphrase"); runCurrent()
        assertNotNull(vm.state.value.account); assertTrue(store.credential!!.passwordSession)
        assertEquals("synthetic-password-refresh", store.credential!!.token)
        assertTrue(api.sent.isEmpty())
        vm.restore(); runCurrent()
        assertNotNull(vm.state.value.account); assertEquals(0, api.passwordRenewals)
        vm.renewSession(); runCurrent()
        assertNotNull(vm.state.value.account); assertEquals(1, api.passwordRenewals)
        assertTrue(api.sent.isEmpty())
        vm.logout(); runCurrent()
        assertNull(store.credential); assertNull(vm.state.value.account); assertEquals(1, api.passwordLogouts)
    }
    @Test fun passwordRenewalWithWrongOwnerClearsAllRecoveryWithoutPost() = runTest {
        val store = MemorySessionStore(); val api = ChatApiMock(store); val vm = ChatViewModel(api, store, true)
        vm.passwordLogin("http://localhost:8000", "synthetic-user", "Public synthetic passphrase"); runCurrent()
        api.user = UUID.randomUUID(); vm.restore(); runCurrent()
        assertNull(store.credential); assertNull(vm.state.value.account); assertTrue(api.sent.isEmpty())
    }
    private suspend fun TestScope.continuousPasswordCapture(lifetime:Long=900000):Triple<ChatViewModel,ChatApiMock,ContinuousChatRecorder> {
        val store=MemorySessionStore(); val api=ChatApiMock(store)
        api.passwordLifetimeMs=lifetime
        api.features=api.features.copy(streaming=true,generation_cancellation=true,stream_protocol="ada-stream-v1",voice_input=VOICE_PROTOCOL,long_voice_input=LONG_VOICE_PROTOCOL)
        val vm=ChatViewModel(api,store,true)
        vm.passwordLogin("http://localhost:8000","synthetic-user","Public synthetic passphrase");runCurrent()
        vm.openConversation(conversation.id);runCurrent()
        val recorder=ContinuousChatRecorder()
        vm.voice.attachAudio(recorder,ContinuousChatPlayer());vm.voice.longForm(true);runCurrent()
        return Triple(vm,api,recorder)
    }
    @Test fun passwordRenewalPreservesContinuousCaptureAndItsOriginalHoldRelease()=runTest {
        val(vm,api,recorder)=continuousPasswordCapture()
        val lease=vm.requestHeldVoiceRecording()!!;vm.voice.permissionResult(true);runCurrent()
        recorder.callback!!.ready();runCurrent();val cancelled=recorder.cancels
        vm.renewSession();runCurrent()
        assertEquals(1,api.passwordRenewals);assertNotNull(vm.state.value.account)
        assertFalse(vm.state.value.connecting);assertEquals(VoicePhase.Recording,vm.voice.state.value.phase)
        assertEquals(cancelled,recorder.cancels);assertTrue(vm.voice.state.value.longFormEnabled)
        vm.voice.releaseHoldRecording(lease);assertEquals(1,recorder.stops)
        vm.logout();runCurrent()
    }
    @Test fun explicitContinuousModeSurvivesIdleRenewalButLogoutClearsIt()=runTest {
        val(vm,_,_)=continuousPasswordCapture()
        assertTrue(vm.voice.state.value.longFormEnabled)
        vm.renewSession();runCurrent()
        assertNotNull(vm.state.value.account);assertTrue(vm.voice.state.value.longFormEnabled)
        vm.logout();runCurrent();assertFalse(vm.voice.state.value.longFormEnabled)
    }
    @Test fun lostContinuousCapabilityRequiresExplicitShortModeInsteadOfHiddenFallback()=runTest {
        val(vm,api,_)=continuousPasswordCapture()
        api.features=api.features.copy(long_voice_input="unsupported")
        vm.renewSession();runCurrent()
        assertNotNull(vm.state.value.account);assertFalse(vm.voice.state.value.enabled)
        assertFalse(vm.requestVoiceRecording())
        vm.voice.longForm(false)
        assertTrue(vm.voice.state.value.enabled);assertFalse(vm.voice.state.value.longFormEnabled)
        vm.logout();runCurrent()
    }
    @Test fun wrongOwnerDuringContinuousRenewalStopsCaptureAndNeverSends()=runTest {
        val(vm,api,recorder)=continuousPasswordCapture()
        assertTrue(vm.requestVoiceRecording());vm.voice.permissionResult(true);runCurrent();recorder.callback!!.ready();runCurrent()
        val cancelled=recorder.cancels;api.user=UUID.randomUUID()
        vm.renewSession();runCurrent()
        assertTrue(recorder.cancels>cancelled);assertNull(vm.state.value.account)
        assertTrue(api.sent.isEmpty());assertTrue(api.voicePosts.isEmpty())
    }
    @Test fun releaseDuringBlockedRenewalStillStopsOnceWithoutCancellingCapture()=runTest {
        val(vm,api,recorder)=continuousPasswordCapture()
        val lease=vm.requestHeldVoiceRecording()!!;vm.voice.permissionResult(true);runCurrent();recorder.callback!!.ready();runCurrent()
        val cancelled=recorder.cancels;api.passwordRefreshGate=CompletableDeferred()
        vm.renewSession();runCurrent();assertTrue(vm.state.value.connecting)
        vm.voice.releaseHoldRecording(lease);assertEquals(1,recorder.stops)
        vm.send();assertTrue(api.sent.isEmpty());assertTrue(api.voicePosts.isEmpty())
        api.passwordRefreshGate!!.complete(Unit);runCurrent()
        assertEquals(cancelled,recorder.cancels);assertEquals(VoicePhase.Transcribing,vm.voice.state.value.phase)
        assertFalse(vm.state.value.connecting);vm.logout();runCurrent()
    }
    @Test fun unavailableRenewalStopsRecordingWithoutAWriteOrConsumedRefreshRetry()=runTest {
        val(vm,api,recorder)=continuousPasswordCapture()
        assertTrue(vm.requestVoiceRecording());vm.voice.permissionResult(true);runCurrent();recorder.callback!!.ready();runCurrent()
        val cancelled=recorder.cancels;api.passwordRefreshUnavailable=true
        vm.renewSession();runCurrent()
        assertEquals(1,api.passwordRenewals);assertTrue(recorder.cancels>cancelled);assertNull(vm.state.value.account)
        assertTrue(api.sent.isEmpty());assertTrue(api.voicePosts.isEmpty())
    }
    @Test fun stalledRenewalStopsAtExpiryAndLateResponseCannotRestoreCapture()=runTest {
        val(vm,api,recorder)=continuousPasswordCapture(2500)
        assertTrue(vm.requestVoiceRecording());vm.voice.permissionResult(true);runCurrent();recorder.callback!!.ready();runCurrent()
        val cancelled=recorder.cancels;api.passwordRefreshGate=CompletableDeferred()
        vm.renewSession();runCurrent();advanceTimeBy(3000);runCurrent()
        assertTrue(recorder.cancels>cancelled);assertNull(vm.state.value.account)
        api.passwordRefreshGate!!.complete(Unit);runCurrent()
        assertNull(vm.state.value.account);assertFalse(vm.voice.captureActive);assertTrue(api.sent.isEmpty())
    }
    @Test fun reviewedVoiceJournalPrecedesPostAndDuplicateSendUsesOneRequest() = runTest {
        val (vm, api, store) = voiceReady()
        vm.sendReviewedVoice(); vm.sendReviewedVoice(); runCurrent()
        assertEquals(1, api.voicePosts.size); assertTrue(api.sent.isEmpty()); assertEquals(0, api.streamPosts)
        val saved = store.journal!!; assertEquals(saved.body.request_id, api.voicePosts.single().request_id)
        assertEquals("Original generated cattle", api.voicePosts.single().transcript.original_text)
        assertEquals("Reviewed kettle", api.voicePosts.single().content); assertNull(store.voice)
        vm.voice.stopPlayback(); assertTrue(api.stops.isEmpty()); assertNotNull(vm.state.value.pending)
        vm.observeForeground(false); runCurrent()
    }
    @Test fun reviewedVoiceStorageFailureAndMissingCapabilityNeverUseTextFallback() = runTest {
        val (vm, api, store) = voiceReady(); store.failJournal = true
        vm.sendReviewedVoice(); runCurrent(); assertTrue(api.voicePosts.isEmpty()); assertNotNull(vm.voice.state.value.draft)
        store.failJournal = false
        val reserved = PendingMessage(store.credential!!.identity, conversation.id, ChatInputDto(UUID.randomUUID(), "Reviewed kettle"), store.voice!!.transcript, conversation.scope_id)
        vm.disconnect(); runCurrent()
        store.credential = StoredCredential(reserved.identity, "synthetic-test-token"); store.journal = reserved
        api.features = api.features.copy(voice_input = "unsupported", streaming = false)
        vm.restore(); runCurrent(); vm.openConversation(conversation.id); runCurrent()
        assertTrue(api.voicePosts.isEmpty()); assertTrue(api.sent.isEmpty()); assertEquals(0, api.streamPosts)
        vm.observeForeground(false)
    }
    @Test fun rejectedVoiceReturnsToSeparateUnapprovedReviewInsteadOfPlainComposer() = runTest {
        val (vm, api, store) = voiceReady(); api.voiceReject = true
        vm.updateDraft("Independent typed draft"); vm.sendReviewedVoice(); runCurrent()
        assertNull(store.journal); assertNotNull(store.voice); assertFalse(store.voice!!.approved)
        assertEquals("Independent typed draft", vm.state.value.draft)
        assertEquals("Original generated cattle", vm.voice.state.value.draft!!.transcript.original_text)
        assertNull(vm.voice.approvedDraft()); vm.observeForeground(false)
    }
    private suspend fun TestScope.ready(store: MemorySessionStore = MemorySessionStore(), streaming: Boolean = false): Triple<ChatViewModel, ChatApiMock, MemorySessionStore> {
        val api = ChatApiMock(store)
        if (streaming) api.features = api.features.copy(streaming = true, generation_cancellation = true, stream_protocol = "ada-stream-v1", voice_input = VOICE_PROTOCOL)
        val vm = ChatViewModel(api, store, true, pollDelaysMs = listOf(0, 1, 2))
        vm.connect("http://localhost:8000", "synthetic-test-token"); advanceUntilIdle()
        vm.openConversation(conversation.id); advanceUntilIdle()
        store.writes.clear()
        return Triple(vm, api, store)
    }

    @Test fun provisionalStreamingSavesBeforePostAndStopTargetsOriginalAttempt() = runTest {
        val (vm, api, store) = ready(streaming = true)
        vm.updateDraft("Synthetic streamed turn"); vm.send(); vm.send(); advanceUntilIdle()
        val snapshot = api.streamSnapshot!!
        val delta = StreamEventDto(snapshot.request_id, snapshot.attempt, 2, "delta", kotlinx.serialization.json.JsonObject(mapOf("text" to kotlinx.serialization.json.JsonPrimitive("Provisional [M"))), 1)
        api.streamChannel.send(ApiResult.Success(delta)); api.streamChannel.send(ApiResult.Success(delta)); runCurrent()
        assertEquals("Provisional [M", vm.state.value.stream!!.provisional)
        assertTrue(vm.state.value.sources.isEmpty()); assertEquals(1, api.streamPosts)
        assertEquals(listOf("journal", "stream-post"), store.writes)
        vm.stopGeneration(); vm.stopGeneration(); runCurrent()
        assertEquals(listOf(snapshot.request_id to snapshot.attempt), api.stops)
        assertNotNull(store.journal)
        vm.observeForeground(false); runCurrent(); assertEquals(1, api.detached)
        assertEquals(1, api.streamPosts); assertEquals(1, api.stops.size)
    }

    @Test fun leavingChatDetachesAndReattachesWithoutResubmitOrCancel() = runTest {
        val (vm, api, store) = ready(streaming = true)
        vm.updateDraft("Synthetic observer turn"); vm.send(); advanceUntilIdle()
        val reserved = store.journal!!
        vm.navigate(ChatDestination.Settings); runCurrent()
        assertEquals(1, api.detached); assertTrue(api.stops.isEmpty())
        vm.navigate(ChatDestination.Chat); runCurrent()
        assertEquals(reserved, store.journal); assertEquals(1, api.streamPosts)
        vm.observeForeground(false); runCurrent()
    }

    @Test fun authoritativeTerminalReplacesProvisionalAndClearsOriginalJournal() = runTest {
        val (vm, api, store) = ready(streaming = true)
        vm.updateDraft("Synthetic complete turn"); vm.send(); advanceUntilIdle()
        val snapshot = api.streamSnapshot!!
        api.streamSnapshot = snapshot.copy(stream_state = "completed", sequence = 2, result = completed(snapshot.request_id))
        api.streamChannel.send(ApiResult.Success(StreamEventDto(snapshot.request_id, snapshot.attempt, 2, "completed", kotlinx.serialization.json.JsonObject(mapOf("legacy_status" to kotlinx.serialization.json.JsonPrimitive("completed"))), 1)))
        api.streamChannel.close(); advanceUntilIdle()
        assertNull(store.journal); assertNull(vm.state.value.pending); assertNull(vm.state.value.stream)
        assertEquals(completed(snapshot.request_id), vm.state.value.sources[snapshot.request_id]); assertEquals(1, api.streamPosts)
    }

    @Test fun switchingConversationDetachesUntilOriginalConversationReturns() = runTest {
        val (vm, api, store) = ready(streaming = true)
        vm.updateDraft("Synthetic detached conversation"); vm.send(); advanceUntilIdle()
        val reserved = store.journal!!
        val other = conversation.copy(id = UUID.randomUUID())
        api.conversationRow = other
        vm.openConversation(other.id); runCurrent()
        assertEquals(1, api.detached)
        assertFalse(vm.state.value.streamConnected)
        assertEquals(reserved, store.journal); assertTrue(api.stops.isEmpty())
        api.conversationRow = conversation
        vm.openConversation(conversation.id); runCurrent()
        assertTrue(vm.state.value.streamConnected)
        assertEquals(1, api.streamPosts)
        vm.observeForeground(false); runCurrent()
    }

    @Test fun durableJournalPrecedesPostAndDoubleTapCannotAllocateSecondTurn() = runTest {
        val (vm, api, store) = ready()
        vm.updateDraft("Exact \uD83D\uDE00 text\n"); vm.updateMemory(false); vm.updateAsOf("2026-10-08T00:00:00.000Z")
        vm.send(); vm.send(); advanceUntilIdle()
        assertEquals(1, api.sent.size)
        assertEquals(listOf("journal", "post", "remove"), store.writes)
        assertEquals("Exact \uD83D\uDE00 text\n", api.sent.single().content)
        assertFalse(api.sent.single().use_memory)
        assertNull(store.journal)
        assertEquals(api.sent.single().request_id, vm.state.value.sources.keys.single())
    }

    @Test fun failedDurableSavePreventsNetworkWriteAndPreservesEditableDraft() = runTest {
        val (vm, api, store) = ready(); store.failJournal = true
        vm.updateDraft("Synthetic unsent draft"); vm.send(); advanceUntilIdle()
        assertTrue(api.sent.isEmpty())
        assertEquals("Synthetic unsent draft", vm.state.value.draft)
        assertNull(vm.state.value.pending)
    }

    @Test fun completedAnswerWithFailedCleanupRecoversByExactGetWithoutAnotherPost() = runTest {
        val (vm, api, store) = ready(); store.failRemove = true
        vm.updateDraft("Synthetic committed message"); vm.send(); advanceUntilIdle()
        val original = api.sent.single()
        val reserved = store.journal!!
        assertEquals(PendingPhase.Blocked, vm.state.value.pending?.phase)
        assertEquals(ObservedRequestState.Completed, vm.state.value.pending?.response?.observedState)
        assertEquals(completed(original.request_id), vm.state.value.sources[original.request_id])
        assertTrue(vm.state.value.notice!!.contains("could not be cleared"))
        assertTrue(api.queried.isEmpty())
        vm.updateDraft("Separate editable draft"); vm.send(); vm.retry(); advanceUntilIdle()
        assertEquals(listOf(original), api.sent); assertEquals(reserved, store.journal)

        store.failRemove = false; vm.reconcile(); advanceUntilIdle()
        assertEquals(listOf(original.request_id), api.queried)
        assertEquals(listOf(original), api.sent)
        assertEquals(listOf("journal", "post", "remove"), store.writes)
        assertNull(store.journal); assertNull(vm.state.value.pending)
        assertNull(vm.state.value.notice); assertEquals("Separate editable draft", vm.state.value.draft)
        assertEquals(completed(original.request_id), vm.state.value.sources[original.request_id])
    }

    @Test fun promptUpgradeIsExplicitAndKeepsOriginalStyleEventsAndSourceCards() = runTest {
        val (vm, api, _) = ready()
        val recorded = adaJson.decodeFromString<List<EventDto>>(fixture("events-current.json"))
        api.eventPages = mutableListOf(recorded)
        api.conversationRow = conversation.copy(prompt_version = "ada-baseline-v2")
        vm.openConversation(conversation.id); advanceUntilIdle()
        vm.openSources(recorded.last().request_id); advanceUntilIdle(); vm.back()
        val originalCards = vm.state.value.sources
        assertTrue(api.upgraded.isEmpty())
        assertEquals("ada-baseline-v2", vm.state.value.conversation?.prompt_version)
        val gate = CompletableDeferred<Unit>()
        api.upgradeCall = { id ->
            gate.await()
            api.conversationRow = api.conversationRow.copy(prompt_version = "ada-baseline-v3", revision = 1)
            ApiResult.Success(PromptUpgradeDto(id, "ada-baseline-v3", 1))
        }
        vm.upgradePrompt(); vm.upgradePrompt(); runCurrent()
        assertEquals(listOf(conversation.id), api.upgraded)
        assertTrue(vm.state.value.upgrading)
        gate.complete(Unit); advanceUntilIdle()
        assertFalse(vm.state.value.upgrading)
        assertEquals("ada-baseline-v3", vm.state.value.conversation?.prompt_version)
        assertEquals(conversation.personality, vm.state.value.conversation?.personality)
        assertEquals(recorded, vm.state.value.events.items)
        assertEquals(originalCards, vm.state.value.sources)
        assertTrue(vm.state.value.notice?.contains("Prompt updated for future replies") == true)
        assertTrue(api.sent.isEmpty())
    }

    @Test fun rejectedPromptUpgradeRefreshesWithoutRetryOrFalseSuccessAndKeepsNotice() = runTest {
        val (vm, api, _) = ready()
        api.conversationRow = conversation.copy(prompt_version = "ada-baseline-v2")
        vm.openConversation(conversation.id); advanceUntilIdle()
        val readsBefore = api.conversationReads
        vm.upgradePrompt(); advanceUntilIdle()
        assertEquals(listOf(conversation.id), api.upgraded)
        assertFalse(vm.state.value.upgrading)
        assertEquals("ada-baseline-v2", vm.state.value.conversation?.prompt_version)
        assertEquals(conversation.personality, vm.state.value.conversation?.personality)
        assertTrue(api.conversationReads > readsBefore)
        assertTrue(vm.state.value.notice?.contains("Prompt update was not confirmed") == true)
        assertTrue(api.sent.isEmpty())
    }

    @Test fun composingNextDraftDuringJournalSaveDoesNotChangeOrEraseReservedPayload() = runTest {
        val (vm, api, store) = ready(); val gate = CompletableDeferred<Unit>(); store.journalGate = gate
        vm.updateDraft("Original reserved draft"); vm.send(); runCurrent()
        vm.updateDraft("New independent draft"); vm.updateMemory(false)
        gate.complete(Unit); advanceUntilIdle()
        assertEquals("Original reserved draft", api.sent.single().content)
        assertTrue(api.sent.single().use_memory)
        assertEquals("New independent draft", vm.state.value.draft)
        assertFalse(vm.state.value.useMemory)
    }

    @Test fun restartVerifiesIdentityThenQueriesSameJournalWithoutAnyPost() = runTest {
        val store = MemorySessionStore()
        val identity = SessionIdentity("http://localhost:8000/", owner)
        store.credential = StoredCredential(identity, "synthetic-test-token"); store.journal = journal(identity)
        val id = store.journal!!.body.request_id
        val api = ChatApiMock(store); val vm = ChatViewModel(api, store, true, listOf(0, 1))
        vm.restore(); advanceUntilIdle()
        assertEquals(listOf(id), api.queried)
        assertTrue(api.sent.isEmpty()); assertNull(store.journal)
        assertEquals(conversation.id, vm.state.value.conversation?.id)
    }

    @Test fun failedRetryUsesImmutablePayloadDespiteChangedDraftAndOptions() = runTest {
        val (vm, api, _) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Provider) }
        api.requestCall = { ApiResult.Success(completed(it).copy(status = "failed", response = null)) }
        vm.updateDraft("Original reserved content"); vm.updateMemory(false); vm.send(); advanceUntilIdle()
        val original = api.sent.single()
        assertEquals(PendingPhase.Failed, vm.state.value.pending?.phase)
        vm.updateDraft("Consciously new draft"); vm.updateMemory(true)
        api.sendCall = { ApiResult.Success(completed(it.request_id)) }
        vm.retry(); advanceUntilIdle()
        assertEquals(listOf(original, original), api.sent)
        assertEquals("Consciously new draft", vm.state.value.draft)
    }

    @Test fun missingRequestNeverAutoSubmitsAndExplicitResubmitKeepsSameId() = runTest {
        val (vm, api, _) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Timeout) }
        api.requestCall = { ApiResult.Failure(ApiFailure.NotFound) }
        vm.updateDraft("Synthetic uncertain request"); vm.send(); advanceUntilIdle()
        assertEquals(1, api.sent.size); assertEquals(PendingPhase.Missing, vm.state.value.pending?.phase)
        api.sendCall = { ApiResult.Success(completed(it.request_id)) }
        vm.resubmitSamePayload(); advanceUntilIdle()
        assertEquals(api.sent[0], api.sent[1])
    }

    @Test fun runningRecoveryCompletesOnceAndUnknownPollingIsBounded() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Timeout) }
        api.requestCall = { ApiResult.Success(completed(it).copy(status = "future_unknown", response = null)) }
        vm.updateDraft("Synthetic future status"); vm.send(); advanceUntilIdle()
        assertEquals(3, api.queried.size); assertNotNull(store.journal)
        assertEquals(PendingPhase.Unknown, vm.state.value.pending?.phase)
        var reads = 0
        api.requestCall = { ApiResult.Success(completed(it).copy(status = if (reads++ == 0) "running" else "completed")) }
        vm.reconcile(); advanceUntilIdle()
        assertNull(store.journal); assertEquals(1, api.sent.size)
    }

    @Test fun revokedTokenHidesAndWipesPrivateStateWithoutAnotherPoll() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Timeout) }
        api.requestCall = { ApiResult.Failure(ApiFailure.Unauthorized) }
        vm.updateDraft("Synthetic private draft"); vm.send(); advanceUntilIdle()
        assertEquals(1, api.queried.size); assertNull(vm.state.value.account)
        assertTrue(vm.state.value.events.items.isEmpty()); assertTrue(vm.state.value.sources.isEmpty())
        assertEquals("", vm.state.value.draft); assertNull(store.credential); assertNull(store.journal)
    }

    @Test fun changedOwnerOnRestoreCannotExposeOrSubmitPriorOwnersJournal() = runTest {
        val store = MemorySessionStore(); val identity = SessionIdentity("http://localhost:8000/", owner)
        store.credential = StoredCredential(identity, "synthetic-test-token"); store.journal = journal(identity)
        val api = ChatApiMock(store); api.user = UUID.randomUUID()
        val vm = ChatViewModel(api, store, true, listOf(0)); vm.restore(); advanceUntilIdle()
        assertNull(vm.state.value.account); assertNull(store.journal)
        assertTrue(api.sent.isEmpty()); assertTrue(api.queried.isEmpty())
    }

    @Test fun logoutImmediatelyFollowedByReconnectStillDurablyDropsJournal() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Timeout) }
        api.requestCall = { ApiResult.Failure(ApiFailure.NotFound) }
        vm.updateDraft("Old recovery bytes"); vm.send(); advanceUntilIdle(); assertNotNull(store.journal)
        val beforeReads = api.queried.size
        vm.logout(); vm.connect("http://localhost:8000", "synthetic-rotated-token"); advanceUntilIdle()
        assertNull(store.journal); assertEquals(beforeReads, api.queried.size)
        assertNull(vm.state.value.pending); assertEquals("", vm.state.value.draft)
    }

    @Test fun deliberateVerifiedTokenRotationRetainsSameIdentityJournalWithoutPostReplay() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Timeout) }; api.requestCall = { ApiResult.Failure(ApiFailure.NotFound) }
        vm.updateDraft("Original rotation-safe bytes"); vm.send(); advanceUntilIdle()
        val reserved = store.journal!!
        vm.rotateCredential("http://localhost:8000", "synthetic-rotated-token"); advanceUntilIdle()
        assertEquals(reserved.body, store.journal?.body); assertEquals(1, api.sent.size)
        assertEquals("synthetic-rotated-token", store.credential?.token)
        assertEquals(reserved.body.request_id, api.queried.last())
    }

    @Test fun retryRequiresDurableJournalVerificationAgainAndManualLogoutIsNotAuthFailure() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Provider) }
        api.requestCall = { ApiResult.Success(completed(it).copy(status = "failed", response = null)) }
        vm.updateDraft("Synthetic failed message"); vm.send(); advanceUntilIdle()
        store.failJournal = true; vm.retry(); advanceUntilIdle()
        assertEquals(1, api.sent.size)
        vm.logout(); advanceUntilIdle(); assertNull(vm.state.value.fault)
    }

    @Test fun failedLogoutCleanupIsVisibleAndNeverClaimsPersistedDataWasRemoved() = runTest {
        val (vm, _, store) = ready(); store.failClear = true
        vm.logout(); advanceUntilIdle()
        assertNull(vm.state.value.account); assertNotNull(store.credential)
        assertEquals(ApiFailure.IncompatibleContract, vm.state.value.fault)
        assertTrue(vm.state.value.notice!!.contains("could not"))
        assertFalse(vm.state.value.notice!!.contains("were cleared"))
    }

    @Test fun explicitFailedSwitchWipesPriorJournalEvenOnSameServerNetworkFailure() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Timeout) }; api.requestCall = { ApiResult.Failure(ApiFailure.NotFound) }
        vm.updateDraft("Prior owner's pending bytes"); vm.send(); advanceUntilIdle()
        api.meCall = { ApiResult.Failure(ApiFailure.Unreachable) }
        vm.connect("http://localhost:8000", "synthetic-another-account-token"); advanceUntilIdle()
        assertNull(store.credential); assertNull(store.journal); assertNull(vm.state.value.account)
    }

    @Test fun changedHistoryConflictCannotOfferAnImpossibleExactRetry() = runTest {
        val (vm, api, _) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Conflict, "retry_history_changed") }
        api.requestCall = { ApiResult.Success(completed(it).copy(status = "failed", response = null)) }
        vm.updateDraft("Reserved old context"); vm.send(); advanceUntilIdle()
        assertEquals(PendingPhase.Conflict, vm.state.value.pending?.phase)
        assertEquals("retry_history_changed", vm.state.value.pending?.code)
        vm.retry(); advanceUntilIdle(); assertEquals(1, api.sent.size)
    }

    @Test fun unsupportedMemoryAndHistoricalFeaturesAreEnforcedBeforePost() = runTest {
        val store = MemorySessionStore(); val api = ChatApiMock(store)
        api.features = capabilities.copy(memory_in_chat = false, historical_memory_queries = false)
        val vm = ChatViewModel(api, store, true, listOf(0)); vm.connect("http://localhost:8000", "synthetic-test-token"); advanceUntilIdle()
        vm.openConversation(conversation.id); advanceUntilIdle()
        vm.updateDraft("Synthetic options"); vm.updateMemory(true); vm.updateAsOf("2026-10-08T00:00:00Z"); vm.send(); advanceUntilIdle()
        assertTrue(api.sent.isEmpty()); assertNull(store.journal)
        vm.updateAsOf(""); vm.send(); advanceUntilIdle()
        assertFalse(api.sent.single().use_memory)
    }

    @Test fun largeRetryAfterEndsAutomaticPollingInsteadOfPollingEarly() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Busy(600)) }
        vm.updateDraft("Synthetic busy request"); vm.send(); advanceUntilIdle()
        assertEquals(1, api.sent.size); assertTrue(api.queried.isEmpty()); assertNotNull(store.journal)
        vm.reconcile(); advanceUntilIdle(); assertTrue(api.queried.isEmpty())
    }

    @Test fun lateOldConnectionCannotRestorePrivateDataAfterServerSwitch() = runTest {
        val store = MemorySessionStore(); val api = ChatApiMock(store)
        val gate = CompletableDeferred<ApiResult<MeDto>>()
        api.meCall = { withContext(NonCancellable) { gate.await() } }
        val vm = ChatViewModel(api, store, true, listOf(0))
        vm.connect("http://localhost:8000", "synthetic-old-token"); runCurrent()
        vm.connect("http://external.example", "synthetic-new-token")
        gate.complete(ApiResult.Success(MeDto(owner, "Old private account"))); advanceUntilIdle()
        assertNull(vm.state.value.account); assertNull(store.credential)
    }

    @Test fun ambiguousConversationCreationRefreshesListWithoutDuplicatePost() = runTest {
        val (vm, api, _) = ready()
        val owned = PersonalityDto(UUID.randomUUID(), "Owned style", "direct", "reserved", "concise")
        api.profileRows = listOf(owned); vm.refreshProfiles(); advanceUntilIdle()
        vm.beginCreate(); vm.selectProfile(owned.id); vm.updateCreateTitle("Synthetic new conversation")
        api.createCall = { ApiResult.Failure(ApiFailure.Timeout) }
        val priorReads = api.conversationReads
        vm.createConversation(); vm.createConversation(); advanceUntilIdle()
        assertEquals(1, api.created); assertTrue(api.conversationReads > priorReads)
        assertTrue(vm.state.value.creationUncertain)
    }

    @Test fun ambiguousProfileCreationNeverBlindlyRepeatsUnkeyedPost() = runTest {
        val (vm, api, _) = ready()
        vm.createProfile("Synthetic style"); vm.createProfile("Synthetic style"); advanceUntilIdle()
        assertEquals(1, api.profilesCreated); assertTrue(vm.state.value.profileUncertain)
        vm.createProfile("Synthetic style"); advanceUntilIdle()
        assertEquals(1, api.profilesCreated)
    }

    @Test fun createdProfileIsSelectedButListOrderComesFromRefreshedServerPage() = runTest {
        val (vm, api, _) = ready()
        val old = PersonalityDto(UUID.randomUUID(), "Old style", "direct", "reserved", "concise")
        val created = old.copy(id = UUID.randomUUID(), name = "New style")
        api.profileRows = listOf(old); vm.refreshProfiles(); advanceUntilIdle()
        api.profileCall = { api.profileRows = listOf(created, old); ApiResult.Success(created) }
        vm.createProfile("New style"); advanceUntilIdle()
        assertEquals(created.id, vm.state.value.createProfileId)
        assertEquals(listOf(created.id, old.id), vm.state.value.profiles.items.map { it.id })
    }
    @Test fun createdProfileOutsideFirstPageRemainsSelectedForNewConversation() = runTest {
        val (vm, api, _) = ready()
        val first = PersonalityDto(UUID.randomUUID(), "First style", "direct", "reserved", "concise")
        val created = first.copy(id = UUID.randomUUID(), name = "Created style")
        api.profileRows = List(50) { first.copy(id = UUID.randomUUID()) }
        api.profileCall = { ApiResult.Success(created) }
        vm.createProfile("Created style"); advanceUntilIdle()
        assertEquals(50, vm.state.value.profiles.items.size)
        vm.beginCreate(); advanceUntilIdle()
        assertEquals(created.id, vm.state.value.createProfileId)
        assertEquals(api.profileRows, vm.state.value.profiles.items)
    }

    @Test fun conflictingIdNeverTreatsDifferentSavedAnswerAsThisReservationsReply() = runTest {
        val (vm, api, store) = ready()
        api.sendCall = { ApiResult.Failure(ApiFailure.Conflict, "idempotency_key_reused") }
        vm.updateDraft("New local bytes"); vm.send(); advanceUntilIdle()
        assertEquals(PendingPhase.Conflict, vm.state.value.pending?.phase)
        assertTrue(api.queried.isEmpty()); assertTrue(vm.state.value.sources.isEmpty())
        vm.discardPending(); advanceUntilIdle()
        assertNull(store.journal); assertEquals("New local bytes", vm.state.value.draft)
        api.sendCall = { ApiResult.Success(completed(it.request_id)) }
        vm.send(); advanceUntilIdle()
        assertNotEquals(api.sent[0].request_id, api.sent[1].request_id)
    }

    @Test fun sourcesUseOriginalRequestCardsAndLegacyTraceHasNoInventedFallback() = runTest {
        val (vm, api, _) = ready()
        vm.updateDraft("Synthetic source example"); vm.send(); advanceUntilIdle()
        val id = api.sent.single().request_id
        vm.openSources(id, "M99"); advanceUntilIdle()
        assertEquals("M99", vm.state.value.sourceLabel)
        assertNull(vm.state.value.sources[id]?.citations?.find { it.label == "M99" })
        assertEquals(completed(id).citations, vm.state.value.sources[id]?.citations)
        vm.loadTrace(); advanceUntilIdle()
        assertTrue(vm.state.value.traceMissing); assertNull(vm.state.value.trace)
        assertEquals(completed(id).citations, vm.state.value.sources[id]?.citations)
    }

    @Test fun overlappingHistoryPagesDeduplicateWithoutSortingByEventTime() = runTest {
        val (vm, api, _) = ready()
        val request = UUID.randomUUID()
        val first = (0 until 50).map { EventDto(UUID.randomUUID(), "user", "Synthetic $it", "user_explicit", request, "completed", (50 - it).toLong(), UUID.randomUUID()) }
        val last = first.last().copy(id = UUID.randomUUID(), content = "Synthetic final")
        api.eventPages = mutableListOf(first, listOf(first.last(), last))
        vm.refreshEvents(); advanceUntilIdle(); vm.loadMoreEvents(); advanceUntilIdle()
        assertEquals(first.map { it.id } + last.id, vm.state.value.events.items.map { it.id })
        assertEquals(listOf(0, 50), api.eventOffsets.takeLast(2))
    }

    @Test fun unicodeLimitCountsCodePointsAndInvalidDraftNeverCreatesJournal() = runTest {
        val (vm, api, store) = ready()
        vm.updateDraft("\uD83D\uDE00".repeat(4001)); vm.send(); advanceUntilIdle()
        assertTrue(api.sent.isEmpty()); assertNull(store.journal)
        vm.updateDraft("\uD83D\uDE00".repeat(4000)); vm.send(); advanceUntilIdle()
        assertEquals(4000, api.sent.single().content.codePointCount(0, api.sent.single().content.length))
    }
}
