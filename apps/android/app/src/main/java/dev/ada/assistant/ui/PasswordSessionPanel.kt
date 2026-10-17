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
    var old by remember { mutableStateOf("") }
    var replacement by remember { mutableStateOf("") }
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Password sessions", style = MaterialTheme.typography.titleMedium)
        Text("Password changes and sign out all revoke password sessions. Separately issued CLI and device tokens keep their own revocation policy.")
        OutlinedButton(onClick = vm::loadPasswordSessions) { Text("Review signed-in devices") }
        sessions.forEach { session ->
            if (session.revoked_at == null) Row(Modifier.fillMaxWidth()) {
                Text(session.label, Modifier.weight(1f))
                TextButton(onClick = { vm.revokePasswordSession(session.id) }) { Text("Revoke") }
            }
        }
        OutlinedTextField(old, { old = it }, label = { Text("Current password") }, singleLine = true, visualTransformation = PasswordVisualTransformation())
        OutlinedTextField(replacement, { replacement = it }, label = { Text("New password (15–1024 characters)") }, singleLine = true, visualTransformation = PasswordVisualTransformation())
        OutlinedButton(onClick = { vm.changePassword(old, replacement); old = ""; replacement = "" }, enabled = old.isNotEmpty() && replacement.codePointCount(0, replacement.length) in 15..1024) { Text("Change password and sign out") }
    }
}
