package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class SpeechAvailability { Available, UnsupportedDevice, NoMicrophone, NoEngine }
enum class VoicePhase { Idle, Permission, Checking, Recording, Transcribing, Review, Denied, Interrupted, Unavailable, Error }
data class SpeechVoice(val id: String, val label: String, val language: String)
interface SpeechCapture {
    val availability: SpeechAvailability
    val version: String
    fun start(language: String, listener: CaptureListener)
    fun stop()
    fun cancel()
    fun close()
}
interface CaptureListener {
    fun ready()
    fun ended()
    fun result(text: String)
    fun failed(code: String)
}
interface SpeechPlayback {
    fun initialize(ready: (List<SpeechVoice>) -> Unit)
    fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit)
    fun stop()
    fun close()
}
data class VoiceState(val enabled: Boolean = false, val availability: SpeechAvailability = SpeechAvailability.NoEngine,
    val phase: VoicePhase = VoicePhase.Idle, val durationMs: Long = 0,
    val language: String = "en-US", val draft: VoiceDraft? = null,
    val savedDraftConversation: UUID? = null, val savedDraftTranscript: UUID? = null,
    val saving: Boolean = false, val draftLoading: Boolean = false, val permissionPermanent: Boolean = false,
    val voices: List<SpeechVoice> = emptyList(), val voiceId: String? = null, val speed: Float = 1f,
    val playing: Boolean = false, val playbackLoading: Boolean = false, val playbackRequest: UUID? = null,
    val history: List<VoiceLineageDto> = emptyList(), val historyLoading: Boolean = false,
    val lineage: VoiceLineageDto? = null, val lineageRequest: UUID? = null,
    val fault: ApiFailure? = null, val notice: String? = null) {
    override fun toString() = "VoiceState(redacted)"
}

/** Generated input is a separate encrypted review draft. This controller never submits a turn. */
class VoiceController(private val api: AdaApi, private val store: SessionStore,
    private val scope: CoroutineScope, private val unauthorized: () -> Unit,
    private val now: () -> Long = System::currentTimeMillis) {
    private val mutable = MutableStateFlow(VoiceState()); val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null; private var identity: SessionIdentity? = null
    private var conversation: UUID? = null; private var scopeId: UUID? = null
    private var visible = false; private var foreground = true; private var pending = false
    private var epoch = 0L; private var selection = 0L; private var captureKey = 0L; private var playbackKey = 0L; private var audioKey = 0L
    private var input: SpeechCapture? = null; private var output: SpeechPlayback? = null
    private var started = 0L; private var checkingStarted = 0L; private var stoppedAt = 0L
    private var timer: Job? = null; private var saver: Job? = null; private var playerJob: Job? = null
    private var recoveryNeeded = false
    private fun update(f: (VoiceState) -> VoiceState) { mutable.value = f(state.value) }
    private fun current(e: Long, s: Long) = e == epoch && s == selection && identity != null
    fun attachAudio(recorder: SpeechCapture, player: SpeechPlayback) {
        detachAudio(); input = recorder; output = player
        update { it.copy(availability = recorder.availability) }
        val key = audioKey
        player.initialize { voices -> if (key == audioKey) update { it.copy(voices = voices, voiceId = voices.firstOrNull { v -> v.language == it.language }?.id ?: voices.firstOrNull()?.id) } }
    }
    fun detachAudio() { audioKey++; interruptCapture(); stopPlayback(); input?.close(); output?.close(); input = null; output = null; update { it.copy(voices = emptyList(), voiceId = null, availability = SpeechAvailability.NoEngine) } }
    fun reset() {
        epoch++; selection++; recoveryNeeded = false; saver?.cancel(); interruptCapture(); stopPlayback(); connection = null; identity = null
        conversation = null; scopeId = null; visible = false; pending = false
        mutable.value = VoiceState(availability = input?.availability ?: SpeechAvailability.NoEngine,
            voices = state.value.voices, voiceId = state.value.voiceId)
    }
    fun setVerifiedSession(c: ConnectionCredential, verified: SessionIdentity, features: CapabilitiesDto) {
        reset(); connection = c; identity = verified; update { it.copy(enabled = features.hasVoiceInput()) }
    }
    fun context(row: ConversationDto?, show: Boolean, hasPending: Boolean) {
        pending = hasPending
        if (!show && visible) { interruptCapture(); stopPlayback() }
        visible = show
        if (conversation == row?.id && scopeId == row?.scope_id) {
            if (recoveryNeeded && visible && foreground) restoreDraft()
            return
        }
        selection++; interruptCapture(); stopPlayback(); saver?.cancel()
        conversation = row?.id; scopeId = row?.scope_id
        update { it.copy(draft = null, savedDraftConversation = null, savedDraftTranscript = null, phase = VoicePhase.Idle, saving = false, history = emptyList(), historyLoading = false, lineage = null, lineageRequest = null, fault = null, notice = null) }
        restoreDraft()
        if (state.value.enabled) refreshHistory()
    }
    private fun restoreDraft() {
        val verified = identity ?: return; val cid = conversation ?: return; val sid = scopeId ?: return
        recoveryNeeded = false
        val e = epoch; val s = selection
        update { it.copy(draftLoading = true) }
        scope.launch {
            try {
                val saved = store.voiceDraft(verified)
                if (!current(e, s)) return@launch
                update { it.copy(draftLoading = false) }
                if (saved != null) {
                    validateVoiceDraft(saved)
                    if (saved.conversationId == cid && saved.scopeId == sid) update { it.copy(draft = saved, savedDraftConversation = null, savedDraftTranscript = null, phase = VoicePhase.Review, notice = "Saved voice draft restored for review. Nothing was sent.") }
                    else update { it.copy(savedDraftConversation = saved.conversationId, savedDraftTranscript = saved.transcript.transcript_id, notice = "A saved voice draft belongs to another conversation. Open or discard it before recording here.") }
                } else if (state.value.draft == null) {
                    update { it.copy(savedDraftConversation = null, savedDraftTranscript = null, phase = VoicePhase.Idle) }
                }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(e, s)) update { it.copy(draftLoading = false, notice = "Voice draft recovery is unavailable. Reconnect before recording.", fault = ApiFailure.IncompatibleContract) } }
        }
    }
    fun observeForeground(active: Boolean) {
        foreground = active
        if (!active) {
            interruptCapture(); stopPlayback()
            if (state.value.saving) { recoveryNeeded = true; saver?.cancel(); update { it.copy(draft = null, saving = false, phase = VoicePhase.Interrupted, notice = "The voice draft was hidden while storage was finishing. Reopen this conversation to check the encrypted saved draft. Nothing was sent.") } }
        }
        if (active && recoveryNeeded && visible) restoreDraft()
    }
    val captureActive get() = state.value.phase in setOf(VoicePhase.Permission, VoicePhase.Checking, VoicePhase.Recording, VoicePhase.Transcribing)
    fun requestRecording(): Boolean {
        if (!state.value.enabled || identity == null || conversation == null || !visible || !foreground || pending || state.value.draftLoading || state.value.fault == ApiFailure.IncompatibleContract || state.value.draft != null || state.value.savedDraftConversation != null || recoveryNeeded || captureActive) return false
        if (input?.availability != SpeechAvailability.Available) { update { it.copy(phase = VoicePhase.Unavailable, notice = "On-device speech input is unavailable. Text entry remains available.") }; return false }
        if (!voiceLanguageValid(state.value.language)) { update { it.copy(fault = ApiFailure.Validation, notice = "Choose a valid language tag, such as en-US or hi-IN.") }; return false }
        captureKey++; stopPlayback(); update { it.copy(phase = VoicePhase.Permission, fault = null, notice = null, durationMs = 0) }; return true
    }
    fun permissionResult(granted: Boolean, permanent: Boolean = false) {
        if (state.value.phase != VoicePhase.Permission || !foreground || !visible || identity == null) return
        if (!granted) { update { it.copy(phase = VoicePhase.Denied, permissionPermanent = permanent, notice = if (permanent) "Microphone access is blocked. Enable it in Android app settings or type your message." else "Microphone access was denied. You can retry or type your message.") }; return }
        val recorder = input ?: return; val verified = identity ?: return
        val cid = conversation ?: return; val sid = scopeId ?: return
        val e = epoch; val s = selection; val key = captureKey; val language = state.value.language
        fun allowed() = current(e,s) && key == captureKey && foreground && visible
        started = 0; stoppedAt = 0; checkingStarted = now()
        update { it.copy(phase = VoicePhase.Checking, permissionPermanent = false, notice = "Checking on-device language support") }
        recorder.start(language, object : CaptureListener {
            override fun ready() { if (allowed()) { started = now(); update { it.copy(phase = VoicePhase.Recording, notice = "Recording on device. Stop to review; Discard abandons this recording.") } } }
            override fun ended() { if (allowed()) { stoppedAt = now(); update { it.copy(phase = VoicePhase.Transcribing, notice = "Finishing the on-device transcript") } } }
            override fun failed(code: String) {
                if (!allowed()) return
                captureKey++; timer?.cancel(); recorder.cancel()
                update { it.copy(phase = VoicePhase.Error, notice = when(code) {
                    "language_unavailable" -> "This language is not installed for on-device recognition. Choose another language or type your message."
                    "support_unavailable" -> "Installed on-device language support could not be verified. You can type your message or try another engine configuration."
                    "permission_lost" -> "Microphone permission was removed. Recording stopped."
                    "interrupted" -> "Audio input was interrupted. The recording was discarded."
                    "no_match" -> "No transcript was recognized. Try again or type your message."
                    else -> "On-device recognition failed. Try again or type your message."
                }) }
            }
            override fun result(text: String) {
                if (!allowed()) return
                captureKey++; timer?.cancel(); recorder.cancel()
                val elapsed = ((if (stoppedAt > 0) stoppedAt else now()) - (if (started > 0) started else checkingStarted)).coerceIn(1,60_000)
                val transcript = TranscriptInputDto(UUID.randomUUID(), "android_on_device", recorder.version, language, elapsed, text)
                try { validateTranscript(transcript) } catch (_: Exception) { update { it.copy(phase = VoicePhase.Error, notice = "The transcript was empty, invalid or too long. Nothing was sent.") }; return }
                val draft = VoiceDraft(verified,cid,sid,transcript,text)
                update { it.copy(draft = draft, phase = VoicePhase.Review, durationMs = elapsed, notice = "Generated transcript: review and edit the wording, then approve it before Send.") }
                persist(draft)
            }
        })
        timer = scope.launch {
            while (allowed()) {
                delay(250)
                if (!allowed()) break
                if (state.value.phase == VoicePhase.Recording) {
                    val elapsed = (now() - started).coerceIn(0,60_000); update { it.copy(durationMs = elapsed) }
                    if (elapsed >= 60_000) stopCapture()
                } else if ((state.value.phase == VoicePhase.Checking && now() - checkingStarted >= 15_000) ||
                    (state.value.phase == VoicePhase.Transcribing && now() - stoppedAt >= 15_000)) {
                    interruptCapture(); update { it.copy(phase = VoicePhase.Error, notice = "Speech recognition timed out. Nothing was sent.") }
                }
            }
        }
    }
    fun stopCapture() {
        if (state.value.phase != VoicePhase.Recording) return
        stoppedAt = now(); update { it.copy(phase = VoicePhase.Transcribing, notice = "Recording stopped; finishing the transcript") }; input?.stop()
    }
    private fun interruptCapture() {
        val active = captureActive; captureKey++; timer?.cancel(); input?.cancel()
        if (active) update { it.copy(phase = VoicePhase.Interrupted, notice = "Recording was discarded after leaving the recording screen or an interruption.") }
    }
    fun edit(text: String) { val draft = state.value.draft ?: return; val next = draft.copy(reviewedText = text, approved = false); update { it.copy(draft = next) }; if (voiceTextValid(text)) persist(next) else update { it.copy(fault = ApiFailure.Validation, notice = "Use 1–4000 valid Unicode characters before approving.") } }
    fun approve(approved: Boolean) { val draft = state.value.draft ?: return; if (!voiceTextValid(draft.reviewedText)) return; val next = draft.copy(approved = approved); update { it.copy(draft = next) }; persist(next) }
    private fun persist(draft: VoiceDraft) {
        saver?.cancel(); val e = epoch; val s = selection
        update { it.copy(saving = true) }
        saver = scope.launch {
            try { store.saveVoiceDraft(draft); if (current(e,s) && state.value.draft == draft) update { it.copy(saving = false, fault = null) } }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(e,s)) update { it.copy(saving = false, draft = it.draft?.copy(approved = false), fault = ApiFailure.IncompatibleContract, notice = "The voice draft could not be encrypted. Nothing was sent. Discard it or try saving again.") } }
        }
    }
    fun saveAgain() { state.value.draft?.let(::persist) }
    fun approvedDraft(): VoiceDraft? = state.value.draft?.takeIf { state.value.enabled && it.approved && !state.value.saving && !state.value.draftLoading && !captureActive && state.value.fault == null && visible && foreground && !pending && it.identity == identity && it.conversationId == conversation && it.scopeId == scopeId }
    fun sent(transcript: UUID) { if (state.value.draft?.transcript?.transcript_id == transcript) { saver?.cancel(); update { it.copy(draft = null, saving = false, phase = VoicePhase.Idle, notice = "Reviewed voice input reserved with the original request ID") } } }
    fun rejected(message: PendingMessage) {
        val transcript = message.voiceTranscript ?: return
        if (message.identity != identity || message.conversationId != conversation || message.voiceScopeId != scopeId) return
        val draft = VoiceDraft(message.identity, message.conversationId, requireNotNull(message.voiceScopeId), transcript, message.body.content)
        update { it.copy(draft = draft, phase = VoicePhase.Review, fault = null) }; persist(draft)
    }
    fun discard() {
        interruptCapture(); val draft = state.value.draft
        if (draft == null && state.value.savedDraftTranscript != null) {
            val verified = identity ?: return; val tid = state.value.savedDraftTranscript ?: return
            val e = epoch; val s = selection
            scope.launch {
                try { store.removeVoiceDraft(verified,tid); if (current(e,s)) { update { it.copy(savedDraftConversation = null, savedDraftTranscript = null, notice = "Saved voice draft discarded on this device") }; restoreDraft() } }
                catch (_: Exception) { if (current(e,s)) update { it.copy(notice = "Encrypted voice draft could not be discarded. Resolve storage before recording again.") } }
            }
            return
        }
        if (draft == null) { update { it.copy(phase = VoicePhase.Idle, notice = "Recording discarded") }; return }
        val e = epoch; val s = selection
        saver?.cancel(); update { it.copy(saving = true) }
        scope.launch {
            try { store.removeVoiceDraft(draft.identity,draft.transcript.transcript_id); if (current(e,s)) update { it.copy(draft = null, saving = false, phase = VoicePhase.Idle, notice = "Voice draft discarded on this device") } }
            catch (_: Exception) { if (current(e,s)) update { it.copy(saving = false, notice = "Encrypted voice draft could not be discarded. Resolve storage before recording again.") } }
        }
    }
    fun language(tag: String) { if (!captureActive && state.value.draft == null) update { it.copy(language = tag, fault = null) } }
    fun selectVoice(id: String) { if (state.value.voices.any { it.id == id }) { stopPlayback(); update { it.copy(voiceId = id) } } }
    fun speed(value: Float) { if (value in setOf(0.75f,1f,1.25f,1.5f)) { stopPlayback(); update { it.copy(speed = value) } } }
    fun play(request: UUID) {
        val c = connection ?: return; val cid = conversation ?: return; val player = output ?: return
        val selected = state.value.voiceId ?: return
        if (!visible || !foreground || captureActive) return
        stopPlayback(); val key = playbackKey; val e = epoch; val s = selection
        update { it.copy(playbackLoading = true, playbackRequest = request, notice = "Checking the completed reply for playback") }
        playerJob = scope.launch {
            when(val result = api.request(c,request)) {
                is ApiResult.Failure -> { if (current(e,s) && key == playbackKey) { if (result.reason == ApiFailure.Unauthorized) unauthorized() else update { it.copy(playbackLoading = false, fault = result.reason, notice = "The completed reply could not be loaded for playback.") } } }
                is ApiResult.Success -> {
                    if (!current(e,s) || key != playbackKey || !visible || !foreground) return@launch
                    val row = result.value
                    if (row.request_id != request || row.conversation_id != cid || row.status != "completed" || row.response == null) { update { it.copy(playbackLoading = false, notice = "Playback is available only for an owned completed reply.") }; return@launch }
                    val text = safeSpeechText(row.response)
                    if (text.isBlank()) { update { it.copy(playbackLoading = false, notice = "This reply has no plain text to read. It remains available on screen.") }; return@launch }
                    update { it.copy(playing = true, playbackLoading = false, notice = "Reading completed reply text (up to 12,000 characters). Sources remain on screen.") }
                    player.play(text,selected,state.value.speed) { error -> if (current(e,s) && key == playbackKey) update { it.copy(playing = false, notice = if (error == null) "Playback finished" else "Playback stopped after an audio interruption or engine error") } }
                }
            }
        }
    }
    fun stopPlayback() { playbackKey++; playerJob?.cancel(); output?.stop(); update { it.copy(playing = false, playbackLoading = false, playbackRequest = null) } }
    fun inspectLineage(request: UUID) {
        val c = connection ?: return; val cid = conversation ?: return; val sid = scopeId ?: return
        if (!state.value.enabled) return
        val e = epoch; val s = selection
        update { it.copy(lineage = null, lineageRequest = request) }
        scope.launch {
            try {
                val result = api.voiceInput(c,request)
                if (!current(e,s) || state.value.lineageRequest != request) return@launch
                when(result) {
                    is ApiResult.Success -> { result.value.validate(cid,sid); require(result.value.request_id == request); update { it.copy(lineage = result.value) } }
                    is ApiResult.Failure -> if (result.reason == ApiFailure.Unauthorized) unauthorized()
                }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(e,s)) update { it.copy(notice = "Voice input provenance could not be verified.") } }
        }
    }
    fun refreshHistory() {
        val c = connection ?: return; val cid = conversation ?: return; val sid = scopeId ?: return
        if (!state.value.enabled || state.value.historyLoading) return
        val e = epoch; val s = selection; update { it.copy(historyLoading = true) }
        scope.launch {
            try {
                when(val result = api.voiceInputs(c,cid)) {
                    is ApiResult.Failure -> { if (current(e,s)) { if (result.reason == ApiFailure.Unauthorized) unauthorized() else update { it.copy(historyLoading = false) } } }
                    is ApiResult.Success -> { if (!current(e,s)) return@launch; result.value.forEach { it.validate(cid,sid) }; update { it.copy(history = result.value, historyLoading = false) } }
                }
            } catch (_: Exception) { if (current(e,s)) update { it.copy(historyLoading = false, notice = "Voice input provenance could not be verified.") } }
        }
    }
}
