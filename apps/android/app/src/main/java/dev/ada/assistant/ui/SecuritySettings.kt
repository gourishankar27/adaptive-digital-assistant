package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.PersistableBundle
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable fun SecuritySettings(controller: SecurityController) {
    val context = LocalContext.current
    var copied by remember { mutableStateOf(false) }
    val state by controller.state.collectAsStateWithLifecycle()
    val history by controller.deletionHistory.collectAsStateWithLifecycle()
    var confirmDelete by remember { mutableStateOf(false) }
    var rotate by remember { mutableStateOf<dev.ada.assistant.data.DeviceCredentialDto?>(null) }
    var label by remember { mutableStateOf("") }
    var confirm by remember(state.preview?.id) { mutableStateOf(false) }
    var technicalDetails by remember { mutableStateOf(false) }
    var revoke by remember { mutableStateOf<dev.ada.assistant.data.DeviceCredentialDto?>(null) }
    LaunchedEffect(state.issued?.credential?.id) { copied = false }
    if (!state.enabled) { Text("Device and content management is unavailable on this server."); return }
    Text("Content is retained until you explicitly delete it. Revoking access does not delete content or undo work already admitted.")
    state.notice?.let { AdaNotice(it) }
    if (state.busy) AdaLoading("Checking devices and saved content")
    AdaOutlinedButton(controller::refresh, enabled = !state.busy, modifier = Modifier.testTag("security-refresh")) { Text("Refresh devices and deletion status") }
    OutlinedTextField(label, { label = it.take(80) }, label = { Text("Device label") }, singleLine = true, modifier = Modifier.testTag("security-label"))
    AdaButton({ controller.enroll(label) }, enabled = !state.busy && state.pending == null && state.status?.enrollment_enabled == true && label.isNotBlank()) { Text("Enroll device (30 days)") }
    state.issued?.let { issued ->
        issued.token?.let { token ->
            OutlinedTextField(token, {}, readOnly = true, visualTransformation = PasswordVisualTransformation(), label = { Text("One-time bearer token") })
            AdaTextButton({
                val clip = ClipData.newPlainText("ADA device credential", token)
                clip.description.extras = PersistableBundle().apply { putBoolean("android.content.extra.IS_SENSITIVE", true) }
                (context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager).setPrimaryClip(clip)
                copied = true
            }, Modifier.heightIn(min = AdaSpacing.touch).testTag("copy-device-token")) { Text("Copy one-time token") }
            if (copied) AdaNotice("Copied sensitive credential. Store it in your password manager and clear the clipboard when finished.")
            AdaOutlinedButton(controller::useIssued, enabled = !state.busy) { Text("Use issued token on this device") }
        }
    }
    state.devices.forEach { device ->
        Column {
            SafeChatText(device.label, links = false)
            Text("Expires ${displayInstant(device.expires_at)} · ${if (device.revoked_at != null) "revoked" else "issued"}", style = MaterialTheme.typography.bodySmall)
            if (technicalDetails) Text(device.id.toString(), style = MaterialTheme.typography.bodySmall)
            Row {
                AdaTextButton({ revoke = device }, enabled = !state.busy && device.revoked_at == null) { Text("Revoke") }
                AdaTextButton({ rotate = device }, enabled = !state.busy && state.pending == null && device.revoked_at == null && state.status?.enrollment_enabled == true) { Text("Rotate") }
            }
        }
    }
    Text("Rotate immediately revokes the old token. Keep another valid credential or local CLI recovery access. A lost response cannot recover the new secret.")
    AdaOutlinedButton(controller::preview, enabled = !state.busy && state.pending == null, modifier = Modifier.testTag("delete-preview")) { Text("Preview deletion of all saved assistant content") }
    state.preview?.let { preview ->
        Text("This removes ${preview.counts.values.sum()} saved items and related records, including messages, documents, evidence copies, traces, voice transcripts and saved memory.")
        if (technicalDetails) preview.counts.filterValues { it > 0 }.forEach { (table, count) -> Text("$table: $count", style = MaterialTheme.typography.bodySmall) }
        Text("Retains account, device credentials, admin grants and minimal operation metadata. Backups and offline clients may retain copies. Stop active work first. This cannot be undone.")
        AdaToggle(confirm, "I want to erase all saved assistant content for this account", { confirm = it }, Modifier.testTag("delete-ack"))
        AdaButton({ confirmDelete = true }, enabled = confirm && !state.busy && state.status?.deletion_worker_enabled == true, modifier = Modifier.testTag("delete-confirm")) { Text("Confirm deletion") }
    }
    state.pending?.let {
        Text("A ${jobLabel(it.kind)} operation is saved. Refresh checks its status without submitting again.")
        if (technicalDetails) Text(it.operation.toString(), style = MaterialTheme.typography.bodySmall)
        AdaOutlinedButton(controller::retrySaved, enabled = !state.busy) { Text("Retry exact saved operation") }
        AdaOutlinedButton(controller::forgetReservation, enabled = !state.busy && state.deletion?.status !in setOf("queued", "running")) { Text("Clear local reservation") }
    }
    history.forEach { job -> Text("Deletion: ${statusLabel(job.status)}", style = MaterialTheme.typography.bodySmall)
        if (technicalDetails) Text("${job.id} · attempt ${job.attempt}", style = MaterialTheme.typography.bodySmall) }
    AdaTextButton({ technicalDetails = !technicalDetails }) { Text(if (technicalDetails) "Hide technical details" else "Show technical details") }
    revoke?.let { device -> AlertDialog(onDismissRequest = { revoke = null }, title = { Text("Revoke device access?") },
        text = { Text("This credential will stop working. Revoking this device signs you out and clears local recovery. Server content is retained.") },
        confirmButton = { AdaTextButton({ revoke = null; controller.revoke(device.id) }) { Text("Revoke access") } },
        dismissButton = { AdaTextButton({ revoke = null }) { Text("Cancel") } }) }
    if (confirmDelete) AdaConfirmation("Erase all saved assistant content?", "This permanently deletes the content in the reviewed preview. Backups and offline clients may retain copies. Your account remains. This cannot be undone.", "Erase reviewed content", { confirmDelete = false }, { confirmDelete = false; controller.confirm() }, "erase-content")
    rotate?.let { device -> AdaConfirmation("Rotate device access?", "The old token stops working immediately. Keep another valid credential or recovery access. A lost response cannot recover the replacement secret.", "Rotate access", { rotate = null }, { rotate = null; controller.enroll(label.ifBlank { device.label }, device.id) }, "rotate-device") }

}
