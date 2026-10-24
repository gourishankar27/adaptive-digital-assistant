package dev.ada.assistant.ui

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import androidx.core.net.toUri
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import java.util.UUID
import android.os.Build
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LocalLifecycleOwner
import dev.ada.assistant.audio.HelloAdaService
import dev.ada.assistant.audio.WakeAuthority

@Composable fun VoicePanel(vm: ChatViewModel) {
    val state by vm.voice.state.collectAsStateWithLifecycle()
    val chat by vm.state.collectAsStateWithLifecycle()
    var expanded by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val permissions = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        val permanent = !granted && (context as? Activity)?.shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO) == false
        vm.voice.permissionResult(granted, permanent)
    }
    fun permission() {
        if (context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) vm.voice.permissionResult(true)
        else {
            vm.voice.permissionDialogLaunched()
            try { permissions.launch(Manifest.permission.RECORD_AUDIO) }
            catch (_: Exception) { vm.voice.discard() }
        }
    }
    PushToTalkButton(onClick = {
        if (state.phase == VoicePhase.Recording) vm.voice.stopCapture() else expanded = true
    }, onHold = {
        // Keep the IME/layout stable under the held finger.
        vm.requestHeldVoiceRecording()?.also { permission() }
    }, onRelease = vm.voice::releaseHoldRecording, recording = state.phase == VoicePhase.Recording,
        modifier = Modifier.testTag("voice-toggle").semantics {
            stateDescription = when {
                vm.voice.captureActive -> "Recording or processing on device"
                state.draft != null -> "Transcript ready for review"
                state.playing || state.playbackLoading -> "Reply playback active"
                else -> if (expanded) "Open" else "Closed"
            }
        })
    // Final/recovered transcripts are reviewed in the ordinary composer. Controls
    // remain an explicit tap, including original-ASR inspection and discard.
    LaunchedEffect(state.draft?.transcript?.transcript_id) {
        if (state.draft != null) expanded = false
    }
    if (!expanded) return
    val canDismiss = !vm.voice.captureActive
    Dialog(
        onDismissRequest = { if (canDismiss) expanded = false },
        properties = DialogProperties(dismissOnBackPress = canDismiss, dismissOnClickOutside = canDismiss),
    ) {
        BoxWithConstraints(Modifier.fillMaxWidth().imePadding()) {
            AdaGlassSurface(Modifier.widthIn(max = AdaLayout.form).fillMaxWidth()
                .heightIn(max = (maxHeight - 24.dp).coerceAtLeast(96.dp)).testTag("voice-controls-dialog")) {
                Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Voice controls", style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                        AdaIconButton(AdaIcon.Close, "Close voice controls", onClick = { expanded = false },
                            enabled = canDismiss, modifier = Modifier.testTag("voice-controls-close"))
                    }
                    Column(Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        if (!canDismiss) Text("Stop or discard the recording before closing.", style = MaterialTheme.typography.bodySmall)
                        VoiceControlsContent(vm, state, chat) {
                            if (vm.requestVoiceRecording()) permission()
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable private fun VoiceControlsContent(vm: ChatViewModel, state: VoiceState, chat: ChatState, record: () -> Unit) {
    val context = LocalContext.current
    var discardDraft by remember { mutableStateOf(false) }
    val focus = LocalFocusManager.current
    val keyboard = LocalSoftwareKeyboardController.current
    val host=LocalLifecycleOwner.current
    val wakeStatus by HelloAdaService.status.collectAsStateWithLifecycle()
    fun armWake() {
        if(!host.lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) return
        vm.armHelloAda { allowed ->
            if(allowed && host.lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) {
                try { ContextCompat.startForegroundService(context,Intent(context,HelloAdaService::class.java)) }
                catch (_: Exception) { WakeAuthority.revoke() }
            } else WakeAuthority.revoke()
        }
    }
    val wakePermission=rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { grants ->
        if(grants.values.all { it }) armWake()
    }
    AdaPresenceHeading("On-device voice", adaPresenceState(chat, state).label, adaPresenceState(chat, state), compact = true)
    Text("Tap Record here, or hold the microphone in chat and release to finish. Edit the transcript in the message field; Send approves your wording. ADA uploads no audio.", style = MaterialTheme.typography.bodySmall)
    var engineDetails by remember { mutableStateOf(false) }
    AdaTextButton(onClick = { engineDetails = !engineDetails }, modifier = Modifier.testTag("voice-engine-details-toggle")) {
        Text(if (engineDetails) "Hide engine & model details" else "Engine & model details")
    }
    if (engineDetails) {
        Text("Recognition: Android on-device service · ${speechAvailabilityLabel(state.availability)}", modifier = Modifier.testTag("voice-engine-status"))
        Text("Playback: installed offline Android voices. Android manages their model files; ADA does not verify their model digests.")
        Text("Additional local models: none installed or enabled. Candidate engines await license, compatibility and physical-device checks.")
        Text("Voice names describe playback only, not recognition accuracy. Optional native speech is available only in explicitly prepared evaluation builds. Text entry remains available.")
        Text("Style: normal. This adapter offers voice and rate selection; no separate style or generated shorter reply is applied.")
        state.captureAdapter?.let { Text(it.id, style = MaterialTheme.typography.bodySmall) }
        state.playbackAdapter?.let { Text(it.id, style = MaterialTheme.typography.bodySmall) }
    }
    if (state.draftLoading) Text("Checking encrypted voice draft…")
    state.savedDraftConversation?.let { saved ->
        AdaOutlinedButton(onClick = { vm.openConversation(saved) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Open saved voice draft") }
        AdaOutlinedButton(onClick = { discardDraft = true }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Discard saved voice draft") }
    }
    if (!state.enabled) Text("Reviewed voice input is unavailable on this server. You can type your message.")
    else if (state.draft == null && !vm.voice.captureActive) {
        OutlinedTextField(state.language, vm.voice::language, label = { Text("Recognition language") }, supportingText = { Text("Installed on-device language, such as en-US") }, singleLine = true, modifier = Modifier.fillMaxWidth().testTag("voice-language"))
        if (state.availability != SpeechAvailability.Available) Text(when(state.availability) {
            SpeechAvailability.UnsupportedDevice -> "On-device recording requires Android 12 or later. Text entry remains available."
            SpeechAvailability.NoMicrophone -> "This device has no microphone. Text entry remains available."
            else -> "No on-device recognition engine is available. Text entry remains available."
        })
        AdaButton(onClick = { focus.clearFocus(); keyboard?.hide(); record() }, enabled = chat.pending == null && !state.saving && !state.draftLoading && state.savedDraftConversation == null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("voice-record")) { Text("Record voice") }
    }
    if (vm.voice.captureActive) {
        Text("${voicePhaseLabel(state.phase)} · ${state.durationMs / 1000}s · limit ${if(state.longFormEnabled) "2h / 32,768 characters" else "60s"}", modifier = Modifier.testTag("voice-recording-state"))
        if (state.phase == VoicePhase.Recording) AdaButton(onClick = vm.voice::stopCapture, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("voice-stop-recording")) { Text("Stop recording") }
        AdaOutlinedButton(onClick = vm.voice::discard, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("voice-discard-recording")) { Text("Discard recording") }
    }
    state.notice?.let { AdaNotice(it, Modifier.testTag("voice-notice")) }
    if (state.phase == VoicePhase.Denied && state.permissionPermanent) AdaOutlinedButton(onClick = {
        context.startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, "package:${context.packageName}".toUri()))
    }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Open microphone settings") }
    state.draft?.let { draft ->
        if(draft.transcript.isLong() && draft.reviewedText.codePointCount(0,draft.reviewedText.length)>4000) {
            var start by remember(draft.transcript.transcript_id) { mutableStateOf("0") }
            var end by remember(draft.transcript.transcript_id) { mutableStateOf("4000") }
            Text("Choose an exact excerpt for this reply. Send retains the full reviewed story; only the selected excerpt enters model context. Positions count Unicode characters from zero.")
            OutlinedTextField(start,{start=it},label={Text("Context start")},modifier=Modifier.testTag("voice-context-start"))
            OutlinedTextField(end,{end=it},label={Text("Context end (exclusive)")},modifier=Modifier.testTag("voice-context-end"))
            AdaOutlinedButton(onClick={ val a=start.toIntOrNull(); val b=end.toIntOrNull(); if(a!=null && b!=null) vm.voice.chooseContext(a,b) },modifier=Modifier.testTag("voice-context-select")) { Text("Review this excerpt") }
            draft.contextText()?.let { Text("Exact reply context:"); SafeChatText(it,links=false) }
        }

        Text("Review generated transcript", style = MaterialTheme.typography.titleMedium)
        Text("Speech recognition may mishear words. Only your approved wording becomes the conversational input.")
        var showOriginal by remember(draft.transcript.transcript_id) { mutableStateOf(false) }
        AdaTextButton(onClick = { showOriginal = !showOriginal }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (showOriginal) "Hide original ASR words" else "Original ASR words (generated)") }
        if (showOriginal) SafeChatText(draft.transcript.original_text, links = false)
        OutlinedTextField(draft.reviewedText, vm.voice::edit, label = { Text("Reviewed wording") }, supportingText = { Text("${draft.reviewedText.codePointCount(0, draft.reviewedText.length)}/4000 characters") }, enabled = chat.pending == null, modifier = Modifier.fillMaxWidth().testTag("voice-review"))
        AdaToggle(draft.approved, "I approve this wording for this conversation", vm.voice::approve, Modifier.testTag("voice-approve"), enabled = chat.pending == null && voiceTextValid(draft.reviewedText))
        if (state.saving) Text("Saving encrypted review draft…")
        if (state.fault != null && !state.saving) AdaOutlinedButton(onClick = vm.voice::saveAgain, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Try saving draft again") }
        AdaButton(onClick = vm::sendReviewedVoice, enabled = vm.voice.approvedDraft() != null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("voice-send")) { Text("Send reviewed voice") }
        AdaOutlinedButton(onClick = { discardDraft = true }, enabled = !state.saving && chat.pending == null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("voice-discard")) { Text("Discard voice draft") }
    }
    if(state.longFormEnabled && !vm.voice.captureActive && state.draft==null) {
        Text("For this voice story")
        FlowRow { listOf("listen" to "Just listen","questions" to "Gentle questions","suggestions" to "Practical suggestions").forEach { (key,label) -> AdaChoiceChip(state.conversationStyle==key,label,{vm.voice.conversationStyle(key)}) } }
        Text("Expression choices apply to the next long-form voice turn. They do not save memories or change curiosity consent.",style=MaterialTheme.typography.bodySmall)
    }
    Text("Reply playback", style = MaterialTheme.typography.titleMedium)
    AdaToggle(state.conversationPlayback,"Conversation mode · read completed replies aloud",vm.voice::conversationPlayback,Modifier.testTag("voice-conversation-mode"))
    Text("Reply playback stops on leaving ADA or locking the screen. Sources and the full saved reply remain on screen.",style=MaterialTheme.typography.bodySmall)
    if(state.localModelsIncluded) {
        Text("Private speech models",style=MaterialTheme.typography.titleMedium)
        Text("Local evaluation: about 400 MiB plus runtime. Installation copies verified data from this APK; it makes no network request. Native quality, battery and redistribution gates are recorded separately.",style=MaterialTheme.typography.bodySmall)
        AdaOutlinedButton(onClick={ vm.voice.installModels() },enabled=!state.modelWork && !vm.voice.captureActive,modifier=Modifier.testTag("voice-install-local")) { Text(if(state.localModelsInstalled) "Verify local speech files" else "Install bundled local speech files") }
        if(state.localModelsInstalled) {
            AdaOutlinedButton(onClick={ vm.voice.installModels(true) },enabled=!state.modelWork && !vm.voice.captureActive,modifier=Modifier.testTag("voice-remove-local")) { Text("Remove local speech files") }
            if(state.longFormSupported) AdaToggle(state.longFormEnabled,"Long-form local recording · silence keeps recording",vm.voice::longForm,Modifier.testTag("voice-long-form"),enabled=!vm.voice.captureActive && state.draft==null)
            Text("Long-form limit: 2 hours or 32,768 characters; up to 512 internal segments. Full reviewed wording is retained. Choose a context excerpt of up to 4,000 characters when needed before Send. The server prompt byte budget can require a shorter excerpt; a rejection keeps the draft editable.",style=MaterialTheme.typography.bodySmall)
            Text(wakeStatus,modifier=Modifier.testTag("voice-wake-status"))
            Text("Hello Ada: opt-in background/locked local detection. Stays armed through shared session renewal while authorized and connected. Sign-in failure or interruption requires re-arming. It vibrates and offers Open ADA; unlock before recording or private access. No automatic restart after reboot, force-stop, audio interruption or logout.",style=MaterialTheme.typography.bodySmall)
            AdaOutlinedButton(onClick={
                val required=mutableListOf(Manifest.permission.RECORD_AUDIO)
                if(Build.VERSION.SDK_INT>=33) required+=Manifest.permission.POST_NOTIFICATIONS
                if(required.all { context.checkSelfPermission(it)==PackageManager.PERMISSION_GRANTED }) armWake()
                else wakePermission.launch(required.toTypedArray())
            },enabled=!vm.voice.captureActive && !state.playing && !state.modelWork,modifier=Modifier.testTag("voice-arm-wake")) { Text("Arm Hello Ada") }
            AdaOutlinedButton(onClick={ WakeAuthority.revoke(); context.stopService(Intent(context,HelloAdaService::class.java)) },modifier=Modifier.testTag("voice-stop-wake")) { Text("Stop wake listening") }
        }
    } else Text("Additional local speech models are not included in this build. Platform speech stays available.",style=MaterialTheme.typography.bodySmall)
    if (state.voices.isEmpty()) Text("No installed offline playback voice is available. Replies remain readable.")
    else {
        if(state.voices.any { it.id=="neural/1" }) AdaOutlinedButton(onClick={vm.voice.selectVoice("neural/1")},modifier=Modifier.testTag("voice-choose-bella")) { Text("Choose Bella · calm feminine voice") }
        var menu by remember { mutableStateOf(false) }
        Box {
            AdaOutlinedButton(onClick = { menu = true }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("voice-choice")) { Text(state.voices.firstOrNull { it.id == state.voiceId }?.label ?: "Choose playback voice") }
            DropdownMenu(expanded = menu, onDismissRequest = { menu = false }) {
                state.voices.forEach { voice -> DropdownMenuItem(text = { Text(voice.label) }, onClick = { vm.voice.selectVoice(voice.id); menu = false }, modifier = Modifier.heightIn(min = AdaSpacing.touch).semantics { selected = state.voiceId == voice.id }) }
            }
        }
        FlowRow { listOf(.75f, 1f, 1.25f, 1.5f).forEach { speed -> AdaChoiceChip(speed == state.speed, "${speed}×", { vm.voice.speed(speed) }) } }
        if (state.voiceId == null) Text("No voice matches the default en-US language. Choose an installed voice explicitly; ADA will not switch languages for you.")
        AdaOutlinedButton(onClick = vm.voice::previewVoice, enabled = state.voiceId != null && !vm.voice.captureActive,
            modifier = Modifier.testTag("voice-preview")) { Text("Preview voice") }
    }
    if (state.playing || state.playbackLoading) AdaButton(onClick = vm.voice::stopPlayback, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("voice-stop-playback")) { Text("Stop playback") }
    if (state.history.isNotEmpty()) {
        var historyOpen by remember { mutableStateOf(false) }
        AdaTextButton(onClick = { historyOpen = !historyOpen }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Recent reviewed voice inputs (up to 25)") }
        if (historyOpen) state.history.forEach { VoiceLineageCard(it) }
    }
    if (discardDraft) AdaConfirmation("Discard this voice draft?", "This removes the saved transcript review from this device. It does not cancel a submitted message or delete server history.", "Discard draft", { discardDraft = false }, { discardDraft = false; vm.voice.discard() }, "voice-discard")

}

private fun speechAvailabilityLabel(value: SpeechAvailability) = when (value) {
    SpeechAvailability.Available -> "engine available; selected language checked when recording"
    SpeechAvailability.UnsupportedDevice -> "requires Android 12 or later"
    SpeechAvailability.NoMicrophone -> "microphone unavailable"
    SpeechAvailability.NoEngine -> "engine unavailable"
}

@Composable fun ReadReplyButton(vm: ChatViewModel, request: UUID) {
    val state by vm.voice.state.collectAsStateWithLifecycle()
    if (state.voices.isNotEmpty()) AdaTextButton(onClick = { vm.voice.play(request) }, enabled = !vm.voice.captureActive && state.voiceId != null,
        modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("read-reply-$request")) { Text("Read reply") }
}

@Composable fun VoiceLineageCard(row: VoiceLineageDto) {
    Card(Modifier.fillMaxWidth().testTag("voice-lineage-${row.request_id}")) { Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Reviewed voice input", style = MaterialTheme.typography.titleSmall)
        Text("Original recognition · generated interpretation")
        SafeChatText(row.original_text, links = false)
        Text("Approved wording · explicit user endorsement")
        SafeChatText(row.reviewed_text, links = false)
        Text("${row.language} · ${row.duration_ms}ms · ${row.engine_version} (client reported)", style = MaterialTheme.typography.bodySmall)
        Text("Audio was not received by the server. No server audio hash exists.", style = MaterialTheme.typography.bodySmall)
    } }
}

@Composable fun LongVoiceLineageCard(row: LongVoiceLineageDto) {
    Card(Modifier.fillMaxWidth().testTag("long-voice-lineage-${row.request_id}")) { Column(Modifier.padding(AdaSpacing.medium),verticalArrangement=Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Reviewed voice story",style=MaterialTheme.typography.titleMedium)
        Text("Original recognition · generated interpretation")
        SafeChatText(row.transcript.segments.joinToString(" ") { it.text },links=false)
        Text("Full reviewed wording · explicit endorsement")
        SafeChatText(row.reviewed_text,links=false)
        Text("Only the explicitly selected excerpt entered this reply's model context. The full story is retained without automatic factual-memory promotion.")
        Text("${row.transcript.language} · ${row.transcript.duration_ms}ms · engine/model client reported. Server received no audio.",style=MaterialTheme.typography.bodySmall)
    } }
}
