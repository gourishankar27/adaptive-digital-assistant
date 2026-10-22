package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun PasswordSessionPanel(vm: ChatViewModel) {
    val sessions by vm.passwordSessions.collectAsStateWithLifecycle()
    var revoke by remember { mutableStateOf<java.util.UUID?>(null) }
    var old by remember { mutableStateOf("") }
    var replacement by remember { mutableStateOf("") }
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text("Password changes and sign out all revoke password sessions. Separately issued CLI and device tokens keep their own revocation policy.")
        AdaOutlinedButton(onClick = vm::loadPasswordSessions) { Text("Review signed-in devices") }
        sessions.forEach { session ->
            if (session.revoked_at == null) Row(Modifier.fillMaxWidth()) {
                Text(session.label, Modifier.weight(1f))
                AdaTextButton(onClick = { revoke = session.id }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Revoke") }
            }
        }
        OutlinedTextField(old, { old = it }, label = { Text("Current password") }, singleLine = true, visualTransformation = PasswordVisualTransformation())
        OutlinedTextField(replacement, { replacement = it }, label = { Text("New password (15–1024 characters)") }, singleLine = true, visualTransformation = PasswordVisualTransformation())
        AdaOutlinedButton(onClick = { vm.changePassword(old, replacement); old = ""; replacement = "" }, enabled = old.isNotEmpty() && replacement.codePointCount(0, replacement.length) in 15..1024) { Text("Change password and sign out") }
    }
    revoke?.let { id -> AdaConfirmation("Revoke this password session?", "That signed-in device will need to sign in again. Revoking this session may sign you out. Saved server content remains.", "Revoke session", { revoke = null }, { revoke = null; vm.revokePasswordSession(id) }, "password-revoke") }
}
