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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import java.util.UUID

@Composable fun VoicePanel(vm: ChatViewModel) {
    val state by vm.voice.state.collectAsStateWithLifecycle()
    val chat by vm.state.collectAsStateWithLifecycle()
    var expanded by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val permissions = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        val permanent = !granted && (context as? Activity)?.shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO) == false
        vm.voice.permissionResult(granted, permanent)
    }
    AdaIconButton(AdaIcon.Microphone, "Voice controls", onClick = { expanded = true },
        modifier = Modifier.testTag("voice-toggle").semantics {
            stateDescription = when {
                vm.voice.captureActive -> "Recording or processing on device"
                state.draft != null -> "Transcript ready for review"
                state.playing || state.playbackLoading -> "Reply playback active"
                else -> if (expanded) "Open" else "Closed"
            }
        })
    // A newly recovered/generated transcript remains visible for explicit review.
    // Closing this dialog never approves, discards or submits that draft.
    LaunchedEffect(state.draft?.transcript?.transcript_id, state.savedDraftConversation) {
        if (state.draft != null || state.savedDraftConversation != null) expanded = true
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
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Voice controls", style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                        AdaIconButton(AdaIcon.Close, "Close voice controls", onClick = { expanded = false },
                            enabled = canDismiss, modifier = Modifier.testTag("voice-controls-close"))
                    }
                    Column(Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (!canDismiss) Text("Stop or discard the recording before closing.", style = MaterialTheme.typography.bodySmall)
                        VoiceControlsContent(vm, state, chat) {
                            if (vm.voice.requestRecording()) {
                                if (context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) vm.voice.permissionResult(true)
                                else {
                                    vm.voice.permissionDialogLaunched()
                                    try { permissions.launch(Manifest.permission.RECORD_AUDIO) }
                                    catch (_: Exception) { vm.voice.discard() }
                                }
                            }
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
    val focus = LocalFocusManager.current
    val keyboard = LocalSoftwareKeyboardController.current
    AdaPresenceHeading("On-device voice", adaPresenceState(chat, state).label, adaPresenceState(chat, state), compact = true)
    Text("Tap Record to use the microphone. Review and approve generated words before sending. ADA uploads no audio.", style = MaterialTheme.typography.bodySmall)
    if (state.draftLoading) Text("Checking encrypted voice draft…")
    state.savedDraftConversation?.let { saved ->
        OutlinedButton(onClick = { vm.openConversation(saved) }, modifier = Modifier.heightIn(min = 48.dp)) { Text("Open saved voice draft") }
        OutlinedButton(onClick = vm.voice::discard, modifier = Modifier.heightIn(min = 48.dp)) { Text("Discard saved voice draft") }
    }
    if (!state.enabled) Text("Reviewed voice input is unavailable on this server. You can type your message.")
    else if (state.draft == null && !vm.voice.captureActive) {
        OutlinedTextField(state.language, vm.voice::language, label = { Text("Recognition language") }, supportingText = { Text("Installed on-device language, such as en-US") }, singleLine = true, modifier = Modifier.fillMaxWidth().testTag("voice-language"))
        if (state.availability != SpeechAvailability.Available) Text(when(state.availability) {
            SpeechAvailability.UnsupportedDevice -> "On-device recording requires Android 12 or later. Text entry remains available."
            SpeechAvailability.NoMicrophone -> "This device has no microphone. Text entry remains available."
            else -> "No on-device recognition engine is available. Text entry remains available."
        })
        Button(onClick = { focus.clearFocus(); keyboard?.hide(); record() }, enabled = chat.pending == null && !state.saving && !state.draftLoading && state.savedDraftConversation == null, modifier = Modifier.heightIn(min = 48.dp).testTag("voice-record")) { Text("Record voice") }
    }
    if (vm.voice.captureActive) {
        Text("${state.phase.name} · ${state.durationMs / 1000}s · limit 60s", modifier = Modifier.testTag("voice-recording-state"))
        if (state.phase == VoicePhase.Recording) Button(onClick = vm.voice::stopCapture, modifier = Modifier.heightIn(min = 48.dp).testTag("voice-stop-recording")) { Text("Stop recording") }
        OutlinedButton(onClick = vm.voice::discard, modifier = Modifier.heightIn(min = 48.dp).testTag("voice-discard-recording")) { Text("Discard recording") }
    }
    state.notice?.let { Text(it, style = MaterialTheme.typography.bodySmall, modifier = Modifier.testTag("voice-notice")) }
    if (state.phase == VoicePhase.Denied && state.permissionPermanent) OutlinedButton(onClick = {
        context.startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, "package:${context.packageName}".toUri()))
    }, modifier = Modifier.heightIn(min = 48.dp)) { Text("Open microphone settings") }
    state.draft?.let { draft ->
        Text("Review generated transcript", style = MaterialTheme.typography.titleMedium)
        Text("Speech recognition may mishear words. Only your approved wording becomes the conversational input.")
        var showOriginal by remember(draft.transcript.transcript_id) { mutableStateOf(false) }
        TextButton(onClick = { showOriginal = !showOriginal }, modifier = Modifier.heightIn(min = 48.dp)) { Text(if (showOriginal) "Hide original ASR words" else "Original ASR words (generated)") }
        if (showOriginal) SafeChatText(draft.transcript.original_text, links = false)
        OutlinedTextField(draft.reviewedText, vm.voice::edit, label = { Text("Reviewed wording") }, supportingText = { Text("${draft.reviewedText.codePointCount(0, draft.reviewedText.length)}/4000 characters") }, enabled = chat.pending == null, modifier = Modifier.fillMaxWidth().testTag("voice-review"))
        Row {
            Checkbox(draft.approved, vm.voice::approve, enabled = chat.pending == null && voiceTextValid(draft.reviewedText), modifier = Modifier.testTag("voice-approve"))
            Text("I approve this wording for this conversation")
        }
        if (state.saving) Text("Saving encrypted review draft…")
        if (state.fault != null && !state.saving) OutlinedButton(onClick = vm.voice::saveAgain, modifier = Modifier.heightIn(min = 48.dp)) { Text("Try saving draft again") }
        Button(onClick = vm::sendReviewedVoice, enabled = vm.voice.approvedDraft() != null, modifier = Modifier.heightIn(min = 48.dp).testTag("voice-send")) { Text("Send reviewed voice") }
        OutlinedButton(onClick = vm.voice::discard, enabled = !state.saving && chat.pending == null, modifier = Modifier.heightIn(min = 48.dp).testTag("voice-discard")) { Text("Discard voice draft") }
    }
    Text("Reply playback", style = MaterialTheme.typography.titleMedium)
    if (state.voices.isEmpty()) Text("No installed offline playback voice is available. Replies remain readable.")
    else {
        var menu by remember { mutableStateOf(false) }
        Box {
            OutlinedButton(onClick = { menu = true }, modifier = Modifier.heightIn(min = 48.dp).testTag("voice-choice")) { Text(state.voices.firstOrNull { it.id == state.voiceId }?.label ?: "Choose playback voice") }
            DropdownMenu(expanded = menu, onDismissRequest = { menu = false }) {
                state.voices.forEach { voice -> DropdownMenuItem(text = { Text(voice.label) }, onClick = { vm.voice.selectVoice(voice.id); menu = false }) }
            }
        }
        FlowRow { listOf(.75f, 1f, 1.25f, 1.5f).forEach { speed -> TextButton(onClick = { vm.voice.speed(speed) }, modifier = Modifier.heightIn(min = 48.dp)) { Text(if (speed == state.speed) "✓ ${speed}×" else "${speed}×") } } }
    }
    if (state.playing || state.playbackLoading) Button(onClick = vm.voice::stopPlayback, modifier = Modifier.heightIn(min = 48.dp).testTag("voice-stop-playback")) { Text("Stop playback") }
    if (state.history.isNotEmpty()) {
        var historyOpen by remember { mutableStateOf(false) }
        TextButton(onClick = { historyOpen = !historyOpen }, modifier = Modifier.heightIn(min = 48.dp)) { Text("Recent reviewed voice inputs (up to 25)") }
        if (historyOpen) state.history.forEach { VoiceLineageCard(it) }
    }
}

@Composable fun ReadReplyButton(vm: ChatViewModel, request: UUID) {
    val state by vm.voice.state.collectAsStateWithLifecycle()
    if (state.voices.isNotEmpty()) TextButton(onClick = { vm.voice.play(request) }, enabled = !vm.voice.captureActive,
        modifier = Modifier.heightIn(min = 48.dp).testTag("read-reply-$request")) { Text("Read reply") }
}

@Composable fun VoiceLineageCard(row: VoiceLineageDto) {
    Card(Modifier.fillMaxWidth().testTag("voice-lineage-${row.request_id}")) { Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("Reviewed voice input · user_reviewed", style = MaterialTheme.typography.titleSmall)
        Text("Original recognition · generated_interpretation")
        SafeChatText(row.original_text, links = false)
        Text("Approved wording · user_explicit endorsement")
        SafeChatText(row.reviewed_text, links = false)
        Text("${row.language} · ${row.duration_ms}ms · ${row.engine_version} (client reported)", style = MaterialTheme.typography.bodySmall)
        Text("Audio was not received by the server. No server audio hash exists.", style = MaterialTheme.typography.bodySmall)
    } }
}
