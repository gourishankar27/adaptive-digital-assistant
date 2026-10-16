package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable fun SecuritySettings(controller: SecurityController) {
    val state by controller.state.collectAsStateWithLifecycle()
    val history by controller.deletionHistory.collectAsStateWithLifecycle()
    var label by remember { mutableStateOf("") }
    var confirm by remember(state.preview?.id) { mutableStateOf(false) }
    var technicalDetails by remember { mutableStateOf(false) }
    var revoke by remember { mutableStateOf<dev.ada.assistant.data.DeviceCredentialDto?>(null) }
    if (!state.enabled) return
    Text("Devices and saved content", style = MaterialTheme.typography.titleMedium)
    Text("Content is retained until you explicitly delete it. Revoking access does not delete content or undo work already admitted.")
    state.notice?.let { Text(it) }
    OutlinedButton(controller::refresh, enabled = !state.busy, modifier = Modifier.testTag("security-refresh")) { Text("Refresh devices and deletion status") }
    OutlinedTextField(label, { label = it.take(80) }, label = { Text("Device label") }, singleLine = true, modifier = Modifier.testTag("security-label"))
    Button({ controller.enroll(label) }, enabled = !state.busy && state.pending == null && state.status?.enrollment_enabled == true && label.isNotBlank()) { Text("Enroll device (30 days)") }
    state.issued?.let { issued ->
        issued.token?.let { token ->
            OutlinedTextField(token, {}, readOnly = true, visualTransformation = PasswordVisualTransformation(), label = { Text("One-time bearer token — select to copy securely") })
            OutlinedButton(controller::useIssued, enabled = !state.busy) { Text("Use issued token on this device") }
        }
    }
    state.devices.forEach { device ->
        Column {
            SafeChatText(device.label, links = false)
            Text("Expires ${java.time.Instant.ofEpochMilli(device.expires_at)} · ${if (device.revoked_at != null) "revoked" else "issued"}", style = MaterialTheme.typography.bodySmall)
            if (technicalDetails) Text(device.id.toString(), style = MaterialTheme.typography.bodySmall)
            Row {
                TextButton({ revoke = device }, enabled = !state.busy && device.revoked_at == null) { Text("Revoke") }
                TextButton({ controller.enroll(label.ifBlank { device.label }, device.id) }, enabled = !state.busy && state.pending == null && device.revoked_at == null && state.status?.enrollment_enabled == true) { Text("Rotate") }
            }
        }
    }
    Text("Rotate immediately revokes the old token. Keep another valid credential or local CLI recovery access. A lost response cannot recover the new secret.")
    OutlinedButton(controller::preview, enabled = !state.busy && state.pending == null, modifier = Modifier.testTag("delete-preview")) { Text("Preview deletion of all saved assistant content") }
    state.preview?.let { preview ->
        Text("This removes ${preview.counts.values.sum()} saved items and related records, including messages, documents, evidence copies, traces, voice transcripts and saved memory.")
        if (technicalDetails) preview.counts.filterValues { it > 0 }.forEach { (table, count) -> Text("$table: $count", style = MaterialTheme.typography.bodySmall) }
        Text("Retains account, device credentials, admin grants and minimal operation metadata. Backups and offline clients may retain copies. Stop active work first. This cannot be undone.")
        Row { Checkbox(confirm, { confirm = it }, modifier = Modifier.testTag("delete-ack")); Text("I want to erase all saved assistant content for this account") }
        Button(controller::confirm, enabled = confirm && !state.busy && state.status?.deletion_worker_enabled == true, modifier = Modifier.testTag("delete-confirm")) { Text("Confirm deletion") }
    }
    state.pending?.let {
        Text("A ${it.kind} operation is saved. Refresh checks its status without submitting again.")
        if (technicalDetails) Text(it.operation.toString(), style = MaterialTheme.typography.bodySmall)
        OutlinedButton(controller::retrySaved, enabled = !state.busy) { Text("Retry exact saved operation") }
        OutlinedButton(controller::forgetReservation, enabled = !state.busy && state.deletion?.status !in setOf("queued", "running")) { Text("Clear local reservation") }
    }
    history.forEach { job -> Text("Deletion: ${job.status}", style = MaterialTheme.typography.bodySmall)
        if (technicalDetails) Text("${job.id} · attempt ${job.attempt}", style = MaterialTheme.typography.bodySmall) }
    TextButton({ technicalDetails = !technicalDetails }) { Text(if (technicalDetails) "Hide technical details" else "Show technical details") }
    revoke?.let { device -> AlertDialog(onDismissRequest = { revoke = null }, title = { Text("Revoke device access?") },
        text = { Text("This credential will stop working. Revoking this device signs you out and clears local recovery. Server content is retained.") },
        confirmButton = { TextButton({ revoke = null; controller.revoke(device.id) }) { Text("Revoke access") } },
        dismissButton = { TextButton({ revoke = null }) { Text("Cancel") } }) }
}
