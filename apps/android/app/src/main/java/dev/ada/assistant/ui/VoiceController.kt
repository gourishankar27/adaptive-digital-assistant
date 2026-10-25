package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import dev.ada.assistant.audio.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class SpeechAvailability { Available, UnsupportedDevice, NoMicrophone, NoEngine }
enum class VoicePhase { Idle, Permission, Checking, Recording, Transcribing, Review, Denied, Interrupted, Unavailable, Error }
data class SpeechVoice(val id: String, val label: String, val language: String)
const val VOICE_PREVIEW_TEXT = "The blue notebook is beside the green cup. Tomorrow, we can explore a new idea together."
interface SpeechCapture {
    val longForm: Boolean get() = false
    val longFormAvailable: Boolean get() = false
    val modelSha256: String? get() = null
    fun selectLongForm(enabled: Boolean): Boolean = !enabled
    fun transcriptSegments(): List<TranscriptSegmentDto> = emptyList()
    fun capturedDurationMs(): Long? = null
    val adapterInfo: SpeechAdapterInfo get() = SpeechAdapterInfo(PLATFORM_ASR_ADAPTER, SpeechTask.Asr)
    val availability: SpeechAvailability
    val version: String
    fun start(language: String, listener: CaptureListener)
    fun stop()
    fun cancel()
    fun close()
}
interface CaptureListener {
    fun checkpoint(segments: List<TranscriptSegmentDto>, duration: Long, saved: (Boolean) -> Unit) { saved(false) }
    fun ready()
    fun ended()
    fun partial(text: String) {}
    fun result(text: String)
    fun failed(code: String)
}
interface SpeechPlayback {
    val adapterInfo: SpeechAdapterInfo get() = SpeechAdapterInfo(PLATFORM_TTS_ADAPTER, SpeechTask.Tts)
    fun initialize(ready: (List<SpeechVoice>) -> Unit)
    fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit)
    fun stop()
    fun close()
}
data class VoiceState(val enabled: Boolean = false, val availability: SpeechAvailability = SpeechAvailability.NoEngine,
    val longFormEnabled: Boolean = false, val longFormAvailable: Boolean = false, val longFormSupported: Boolean = false,
    val conversationPlayback: Boolean = false, val conversationStyle: String = "listen",
    val localModelsIncluded: Boolean = false, val localModelsInstalled: Boolean = false, val modelWork: Boolean = false,
    val captureAdapter: SpeechAdapterInfo? = null, val playbackAdapter: SpeechAdapterInfo? = null,
    val phase: VoicePhase = VoicePhase.Idle, val durationMs: Long = 0,
    val language: String = "en-US", val draft: VoiceDraft? = null, val partialText: String? = null,
    val savedDraftConversation: UUID? = null, val savedDraftTranscript: UUID? = null,
    val saving: Boolean = false, val draftLoading: Boolean = false, val permissionPermanent: Boolean = false,
    val voices: List<SpeechVoice> = emptyList(), val voiceId: String? = null, val speed: Float = 1f,
    val playing: Boolean = false, val playbackLoading: Boolean = false, val playbackRequest: UUID? = null,
    val history: List<VoiceLineageDto> = emptyList(), val historyLoading: Boolean = false,
    val lineage: VoiceLineageDto? = null, val longLineage: LongVoiceLineageDto? = null, val lineageRequest: UUID? = null,
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
    private var permissionDialog = false
    private var permissionDecision: Pair<Boolean, Boolean>? = null
    private var heldCapture: Long? = null
    private var recordingPrefix = ""
    private var capturedCheckpoint = false
    private var activeTranscript: UUID?=null
    private val captureStorage = kotlinx.coroutines.sync.Mutex()
    private var runtime: LocalSpeechRuntime?=null
    private var sessionRenewing=false
    private var privateReadKey=0L
    private var restoreRecordingMode:Pair<SessionIdentity,Boolean>?=null
    private var serverVoiceInput=false
    fun attachRuntime(value: LocalSpeechRuntime) { runtime=value; update { it.copy(localModelsIncluded=value.available,localModelsInstalled=value.installed,longFormAvailable=value.installed) } }
    fun installModels(remove: Boolean=false) {
        val engine=runtime ?: return
        if(identity==null || !visible || !foreground || captureActive || state.value.modelWork) return
        stopPlayback(); WakeAuthority.revoke(); input?.selectLongForm(false)
        val e=epoch; val s=selection
        update { it.copy(modelWork=true,notice="Checking local speech files…") }
        scope.launch {
            val success=withContext(Dispatchers.IO) { try { if(remove) engine.remove() else engine.install(); true } catch (_: Exception) { false } }
            if(!current(e,s)) return@launch
            update { it.copy(modelWork=false,localModelsInstalled=engine.installed,longFormAvailable=engine.installed,longFormEnabled=false,
                notice=if(success) "Local speech files ${if(remove) "removed" else "verified"}. Choose the recording mode and preview a voice explicitly." else "Local speech files could not be changed. Stop audio, check free space and retry; text and platform speech remain available.") }
            output?.initialize { voices -> if(current(e,s)) update { it.copy(voices=voices,voiceId=null) } }
        }
    }
    private fun update(f: (VoiceState) -> VoiceState) { mutable.value = f(state.value) }
    private fun current(e: Long, s: Long) = e == epoch && s == selection && identity != null
    fun attachAudio(recorder: SpeechCapture, player: SpeechPlayback) {
        detachAudio(); input = recorder; output = player
        update { it.copy(availability = recorder.availability, captureAdapter = recorder.adapterInfo, playbackAdapter = player.adapterInfo, longFormAvailable = recorder.longFormAvailable) }
        val key = audioKey
        player.initialize { voices -> if (key == audioKey) update { it.copy(voices = voices, voiceId = voices.firstOrNull { v -> v.language.equals(it.language, true) }?.id) } }
    }
    fun detachAudio() { audioKey++; interruptCapture(); stopPlayback(); input?.close(); output?.close(); input = null; output = null; update { it.copy(voices = emptyList(), voiceId = null, captureAdapter = null, playbackAdapter = null, availability = SpeechAvailability.NoEngine) } }
    fun reset(preserveWake:Boolean=false) {
        serverVoiceInput=false
        if(preserveWake) identity?.let {restoreRecordingMode=it to state.value.longFormEnabled} else restoreRecordingMode=null
        sessionRenewing=false;privateReadKey++
        if(!preserveWake) WakeAuthority.revoke(); input?.selectLongForm(false)
        epoch++; selection++; recoveryNeeded = false; saver?.cancel(); interruptCapture(); stopPlayback(); connection = null; identity = null
        conversation = null; scopeId = null; visible = false; pending = false
        mutable.value = VoiceState(availability = input?.availability ?: SpeechAvailability.NoEngine,
            localModelsIncluded=runtime?.available==true,localModelsInstalled=runtime?.installed==true,longFormAvailable=runtime?.installed==true,
            captureAdapter = input?.adapterInfo, playbackAdapter = output?.adapterInfo,
            voices = state.value.voices, voiceId = state.value.voiceId)
    }
    fun setVerifiedSession(c: ConnectionCredential, verified: SessionIdentity, features: CapabilitiesDto) {
        val selected=restoreRecordingMode?.takeIf {it.first==verified}?.second ?: (identity==verified && state.value.longFormEnabled)
        reset(WakeAuthority.current()?.let { it.identity==verified && it.dataEpoch==c.dataEpoch }==true); connection = c; identity = verified
        serverVoiceInput=features.hasVoiceInput()
        val restored=!selected || (features.hasLongVoice() && input?.longFormAvailable==true && input?.selectLongForm(true)==true)
        update { it.copy(enabled = features.hasVoiceInput() && restored, longFormSupported = features.hasLongVoice(), longFormAvailable = input?.longFormAvailable == true, longFormEnabled = input?.longForm == true,
            notice=if(restored) null else "Continuous recording is unavailable. Reinstall local speech files or reconnect before explicitly choosing Android short recording.") }
    }
    /** Same verified owner/epoch/scope only; renewal must not reset an owned mic gesture. */
    fun renewCaptureSession(c:ConnectionCredential,verified:SessionIdentity,features:CapabilitiesDto,row:ConversationDto):Boolean {
        if(identity!=verified || connection?.dataEpoch!=c.dataEpoch || conversation!=row.id || scopeId!=row.scope_id ||
            !foreground || !visible || !state.value.longFormEnabled || !features.hasLongVoice() || !features.hasVoiceInput()) return false
        connection=c;sessionRenewing=false;serverVoiceInput=features.hasVoiceInput()
        update {it.copy(history=emptyList(),historyLoading=false,lineage=null,longLineage=null,lineageRequest=null)}
        return true
    }
    fun hidePrivatePlayback() {sessionRenewing=true;privateReadKey++;stopPlayback();update {it.copy(history=emptyList(),historyLoading=false,lineage=null,longLineage=null,lineageRequest=null)}}
    fun longForm(enabled: Boolean) {
        if (captureActive || state.value.draft != null || (enabled && !state.value.longFormSupported)) return
        if (input?.selectLongForm(enabled) == true) update { it.copy(enabled=serverVoiceInput,longFormEnabled=enabled,availability=input?.availability ?: SpeechAvailability.NoEngine,captureAdapter=input?.adapterInfo,language="en-US",notice=null) }
    }
    fun conversationPlayback(enabled: Boolean) { stopPlayback(); update { it.copy(conversationPlayback=enabled) } }
    fun conversationStyle(style: String) { if(style in setOf("listen", "questions", "suggestions")) update { it.copy(conversationStyle=style) } }
    fun chooseContext(start: Int, end: Int) {
        val draft = state.value.draft ?: return
        if (!draft.transcript.isLong()) return
        val next = draft.copy(contextStart=start,contextEnd=end,approved=false)
        if (next.contextText() == null) { update { it.copy(notice="Select an exact excerpt of up to 4,000 characters for this reply.") }; return }
        update { it.copy(draft=next) }; persist(next)
    }
    fun context(row: ConversationDto?, show: Boolean, hasPending: Boolean) {
        pending = hasPending
        if (hasPending && state.value.phase == VoicePhase.Permission) interruptCapture()
        if (!show && visible) { interruptCapture(); stopPlayback() }
        visible = show
        if (conversation == row?.id && scopeId == row?.scope_id) {
            if (recoveryNeeded && visible && foreground) restoreDraft()
            return
        }
        selection++; if(WakeAuthority.current()?.let { it.identity==identity && it.conversation==row?.id && it.scope==row.scope_id }!=true) WakeAuthority.revoke(); interruptCapture(); stopPlayback(); saver?.cancel()
        conversation = row?.id; scopeId = row?.scope_id
        update { it.copy(draft = null, savedDraftConversation = null, savedDraftTranscript = null, phase = VoicePhase.Idle, saving = false, history = emptyList(), historyLoading = false, lineage = null, longLineage = null, lineageRequest = null, fault = null, notice = null) }
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
            if (!(permissionDialog && state.value.phase == VoicePhase.Permission)) interruptCapture()
            stopPlayback()
            if (state.value.saving) { recoveryNeeded = true; saver?.cancel(); update { it.copy(draft = null, saving = false, phase = VoicePhase.Interrupted, notice = "The voice draft was hidden while storage was finishing. Reopen this conversation to check the encrypted saved draft. Nothing was sent.") } }
        }
        if (active && recoveryNeeded && visible) restoreDraft()
        if (active) permissionDecision?.let { permissionResult(it.first,it.second) }
    }
    /** The OS prompt may pause this same visible activity; it is not microphone capture. */
    fun permissionDialogLaunched() {
        if (state.value.phase == VoicePhase.Permission && foreground && visible && identity != null && !pending) permissionDialog = true
    }
    /** A stopped activity is a real departure, including Home while the prompt is open. */
    fun permissionHostStopped() { if (state.value.phase == VoicePhase.Permission) interruptCapture() }
    val captureActive get() = state.value.phase in setOf(VoicePhase.Permission, VoicePhase.Checking, VoicePhase.Recording, VoicePhase.Transcribing)
    fun requestRecording(prefix: String = ""): Boolean {
        if (!state.value.enabled || identity == null || conversation == null || !visible || !foreground || pending || state.value.draftLoading || state.value.fault == ApiFailure.IncompatibleContract || state.value.draft != null || state.value.savedDraftConversation != null || recoveryNeeded || captureActive) return false
        if (input?.availability != SpeechAvailability.Available) { update { it.copy(phase = VoicePhase.Unavailable, notice = "On-device speech input is unavailable. Text entry remains available.") }; return false }
        if (!voiceLanguageValid(state.value.language)) { update { it.copy(fault = ApiFailure.Validation, notice = "Choose a valid language tag, such as en-US or hi-IN.") }; return false }
        if (prefix.isNotEmpty() && !voiceTextValid(prefix) && !(prefix.isBlank() && prefix.length <= 4000)) { update { it.copy(fault = ApiFailure.Validation, notice = "Shorten or clear the typed draft before recording.") }; return false }
        permissionDialog = false; permissionDecision = null
        recordingPrefix = prefix; heldCapture = null; capturedCheckpoint = false
        captureKey++; stopPlayback(); update { it.copy(phase = VoicePhase.Permission, partialText = null, fault = null, notice = null, durationMs = 0) }; return true
    }
    fun requestHoldRecording(prefix: String = ""): Long? {
        if (!requestRecording(prefix)) return null
        return captureKey.also { heldCapture = it }
    }
    fun releaseHoldRecording(key: Long, cancelled: Boolean = false) {
        if (heldCapture != key || captureKey != key) return
        heldCapture = null
        if (cancelled || state.value.phase in setOf(VoicePhase.Permission, VoicePhase.Checking)) {
            interruptCapture()
            update { it.copy(notice = if (cancelled) "Voice gesture cancelled. Nothing was sent." else "Hold ended before recording was ready. Allow microphone access, then hold again or tap Record.") }
        } else stopCapture()
    }
    fun permissionResult(granted: Boolean, permanent: Boolean = false) {
        if (state.value.phase != VoicePhase.Permission || !visible || identity == null || pending || !state.value.enabled) return
        if (!foreground) {
            if (permissionDialog) permissionDecision = granted to permanent
            return
        }
        permissionDialog = false; permissionDecision = null
        if (!granted) { update { it.copy(phase = VoicePhase.Denied, permissionPermanent = permanent, notice = if (permanent) "Microphone access is blocked. Enable it in Android app settings or type your message." else "Microphone access was denied. You can retry or type your message.") }; return }
        val recorder = input ?: return; val verified = identity ?: return
        val cid = conversation ?: return; val sid = scopeId ?: return
        val e = epoch; val s = selection; val key = captureKey; val language = state.value.language; val prefix = recordingPrefix
        fun allowed() = current(e,s) && key == captureKey && foreground && visible
        started = 0; stoppedAt = 0; checkingStarted = now()
        update { it.copy(phase = VoicePhase.Checking, permissionPermanent = false, notice = "Checking on-device language support") }
        recorder.start(language, object : CaptureListener {
            private val transcriptId = UUID.randomUUID().also { activeTranscript=it }
            override fun checkpoint(segments: List<TranscriptSegmentDto>, duration: Long, saved: (Boolean) -> Unit) {
                if (!allowed() || !recorder.longForm) { saved(false); return }
                val text = segments.joinToString(" ") { it.text }
                val transcript = TranscriptInputDto(transcriptId,LONG_VOICE_ENGINE,recorder.version,language,duration,text,recorder.modelSha256,segments)
                val draft = VoiceDraft(verified,cid,sid,transcript,combineVoiceText(prefix,text),conversationStyle=state.value.conversationStyle)
                scope.launch {
                    var success = false
                    try {
                        captureStorage.lock()
                        try { if (allowed()) { store.saveVoiceDraft(draft); capturedCheckpoint=true; success=true } }
                        finally { captureStorage.unlock() }
                    } catch (_: Exception) { }
                    saved(success)
                }
            }
            override fun ready() { if (allowed()) { started = now(); update { it.copy(phase = VoicePhase.Recording, notice = if (heldCapture == key) "Recording on device. Release to finish, then edit and Send." else "Recording on device. Stop to review; Discard abandons this recording.") } } }
            override fun ended() { if (allowed()) { stoppedAt = now(); update { it.copy(phase = VoicePhase.Transcribing, notice = "Finishing the on-device transcript") } } }
            override fun partial(text: String) {
                if (allowed() && state.value.phase == VoicePhase.Recording && voiceTextValid(text,if(recorder.longForm) LONG_VOICE_TEXT else 4000)) update { it.copy(partialText = combineVoiceText(prefix, text)) }
            }
            override fun failed(code: String) {
                if (!allowed()) return
                captureKey++; timer?.cancel(); recorder.cancel()
                if (capturedCheckpoint) { recoveryNeeded=true; restoreDraft() }
                update { it.copy(phase = VoicePhase.Error, partialText = null, notice = when(code) {
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
                captureKey++; heldCapture = null; timer?.cancel(); recorder.cancel()
                val elapsedBase = ((if (stoppedAt > 0) stoppedAt else now()) - (if (started > 0) started else checkingStarted)).coerceIn(1,if(recorder.longForm) LONG_VOICE_DURATION else 60_000)
                val elapsed = recorder.capturedDurationMs() ?: elapsedBase
                val transcript = TranscriptInputDto(transcriptId,if(recorder.longForm) LONG_VOICE_ENGINE else "android_on_device",recorder.version,language,elapsed,text,
                    if(recorder.longForm) recorder.modelSha256 else null,if(recorder.longForm) recorder.transcriptSegments() else emptyList())
                try { validateTranscript(transcript) } catch (_: Exception) { update { it.copy(phase = VoicePhase.Error, partialText = null, notice = "The transcript was empty, invalid or too long. Nothing was sent.") }; return }
                val draft = VoiceDraft(verified,cid,sid,transcript,combineVoiceText(prefix, text),conversationStyle=state.value.conversationStyle)
                update { it.copy(draft = draft, partialText = null, phase = VoicePhase.Review, durationMs = elapsed, notice = "Voice draft: edit the message field, then Send to approve this wording. Nothing was sent.") }
                if (voiceTextValid(draft.reviewedText,if(recorder.longForm) LONG_VOICE_TEXT else 4000)) persist(draft)
                else update { it.copy(fault = ApiFailure.Validation, notice = "Shorten the combined typed and voice draft to 4,000 characters before saving or sending.") }
            }
        })
        timer = scope.launch {
            while (allowed()) {
                delay(250)
                if (!allowed()) break
                if (state.value.phase == VoicePhase.Recording) {
                    val maximum = if(recorder.longForm) LONG_VOICE_DURATION else 60_000L
                    val elapsed = (now() - started).coerceIn(0,maximum); update { it.copy(durationMs = elapsed) }
                    if (elapsed >= maximum) stopCapture()
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
        permissionDialog = false; permissionDecision = null; heldCapture = null; recordingPrefix = ""
        val active = captureActive; captureKey++; timer?.cancel(); input?.cancel()
        if (capturedCheckpoint && active) recoveryNeeded=true
        update { it.copy(partialText = null) }
        if (active) update { it.copy(phase = VoicePhase.Interrupted, notice = "Recording was discarded after leaving the recording screen or an interruption.") }
    }
    fun edit(text: String) { val draft = state.value.draft ?: return; val next = draft.copy(reviewedText=text,approved=false,contextStart=null,contextEnd=null); update { it.copy(draft = next) }; if (voiceTextValid(text,if(draft.transcript.isLong()) LONG_VOICE_TEXT else 4000)) persist(next) else update { it.copy(fault = ApiFailure.Validation, notice = "Use 1–4000 valid Unicode characters before approving.") } }
    fun approve(approved: Boolean) { val draft = state.value.draft ?: return; if (draft.contextText() == null) return; val next = draft.copy(approved = approved); update { it.copy(draft = next) }; persist(next) }
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
    /** Only the explicit composer Send action may turn this reviewed snapshot into approval. */
    fun composerDraftForSend(): VoiceDraft? = state.value.draft?.takeIf { state.value.enabled && it.contextText() != null && !state.value.saving && !state.value.draftLoading && !captureActive && state.value.fault == null && visible && foreground && !pending && it.identity == identity && it.conversationId == conversation && it.scopeId == scopeId }
    fun sent(transcript: UUID) { if (state.value.draft?.transcript?.transcript_id == transcript) { saver?.cancel(); update { it.copy(draft = null, saving = false, phase = VoicePhase.Idle, notice = "Reviewed voice input reserved with the original request ID") } } }
    fun rejected(message: PendingMessage) {
        val transcript = message.voiceTranscript ?: return
        if (message.identity != identity || message.conversationId != conversation || message.voiceScopeId != scopeId) return
        val draft = VoiceDraft(message.identity, message.conversationId, requireNotNull(message.voiceScopeId), transcript,message.longReviewedText ?: message.body.content,contextStart=message.longContextStart,contextEnd=message.longContextStart + message.body.content.codePointCount(0,message.body.content.length),conversationStyle=message.longConversationStyle)
        update { it.copy(draft = draft, phase = VoicePhase.Review, fault = null) }; persist(draft)
    }
    fun discard() {
        val checkpoint=activeTranscript.takeIf { capturedCheckpoint }
        interruptCapture(); val draft = state.value.draft
        if(draft==null && checkpoint!=null) {
            val verified=identity ?: return; val e=epoch; val s=selection
            update { it.copy(saving=true) }
            scope.launch {
                try {
                    captureStorage.lock()
                    try { store.removeVoiceDraft(verified,checkpoint) } finally { captureStorage.unlock() }
                    if(current(e,s)) { recoveryNeeded=false; capturedCheckpoint=false; update { it.copy(saving=false,phase=VoicePhase.Idle,notice="Recording and its encrypted checkpoints discarded") } }
                } catch (_: Exception) { if(current(e,s)) update { it.copy(saving=false,notice="Checkpoint deletion could not be confirmed. Reopen to recover or discard it.") } }
            }
            return
        }
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
    /** Public, fixed sample only: no HTTP request, microphone, draft or saved reply. */
    fun previewVoice() {
        val player = output ?: return; val selected = state.value.voiceId ?: return
        if (identity == null || !visible || !foreground || captureActive) return
        stopPlayback(); val key = playbackKey; val e = epoch; val s = selection
        update { it.copy(playing = true, notice = "Previewing the selected installed voice with a public sample. Nothing is sent or saved.") }
        player.play(VOICE_PREVIEW_TEXT, selected, state.value.speed) { error ->
            if (current(e,s) && key == playbackKey) update { it.copy(playing = false, notice = if (error == null) "Voice preview finished" else "Voice preview stopped. Text remains available; choose an installed voice or try again.") }
        }
    }
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
        if(sessionRenewing) return
        val c = connection ?: return; val cid = conversation ?: return; val sid = scopeId ?: return
        if (!state.value.enabled) return
        val e = epoch; val s = selection; val read=privateReadKey
        update { it.copy(lineage = null, longLineage = null, lineageRequest = request) }
        scope.launch {
            try {
                if(state.value.longFormSupported) {
                    val result=api.longVoiceInput(c,request)
                    if(!current(e,s) || read!=privateReadKey || state.value.lineageRequest!=request) return@launch
                    if(result is ApiResult.Success) {
                        result.value.validate(cid,sid); require(result.value.request_id==request)
                        update { it.copy(longLineage=result.value) }; return@launch
                    }
                    if(result is ApiResult.Failure && result.reason!=ApiFailure.NotFound) {
                        if(result.reason==ApiFailure.Unauthorized) unauthorized()
                        else update { it.copy(notice="Long voice provenance could not be loaded. Retry when the server is available.") }
                        return@launch
                    }
                }
                val result = api.voiceInput(c,request)
                if (!current(e,s) || read!=privateReadKey || state.value.lineageRequest != request) return@launch
                when(result) {
                    is ApiResult.Success -> { result.value.validate(cid,sid); require(result.value.request_id == request); update { it.copy(lineage = result.value) } }
                    is ApiResult.Failure -> if (result.reason == ApiFailure.Unauthorized) unauthorized()
                }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(e,s) && read==privateReadKey) update { it.copy(notice = "Voice input provenance could not be verified.") } }
        }
    }
    fun refreshHistory() {
        if(sessionRenewing) return
        val c = connection ?: return; val cid = conversation ?: return; val sid = scopeId ?: return
        if (!state.value.enabled || state.value.historyLoading) return
        val e = epoch; val s = selection; val read=privateReadKey; update { it.copy(historyLoading = true) }
        scope.launch {
            try {
                when(val result = api.voiceInputs(c,cid)) {
                    is ApiResult.Failure -> { if (current(e,s) && read==privateReadKey) { if (result.reason == ApiFailure.Unauthorized) unauthorized() else update { it.copy(historyLoading = false) } } }
                    is ApiResult.Success -> { if (!current(e,s) || read!=privateReadKey) return@launch; result.value.forEach { it.validate(cid,sid) }; update { it.copy(history = result.value, historyLoading = false) } }
                }
            } catch (_: Exception) { if (current(e,s) && read==privateReadKey) update { it.copy(historyLoading = false, notice = "Voice input provenance could not be verified.") } }
        }
    }
}

private fun combineVoiceText(prefix: String, transcript: String) = when {
    prefix.isEmpty() -> transcript
    prefix.last().isWhitespace() -> prefix + transcript
    else -> "$prefix $transcript"
}
