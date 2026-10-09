package dev.ada.assistant.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.focusable
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.sp

@Composable fun FoundationScreen(state: ConnectionState, connect: (String, String) -> Unit, disconnect: () -> Unit, openSettings: () -> Unit) {
    var server by remember { mutableStateOf("") }
    var token by remember { mutableStateOf("") } // Never saved to Bundle, preferences or disk.
    var largePreview by remember { mutableStateOf(false) }
    val errorFocus = remember { FocusRequester() }
    val validating = state == ConnectionState.Validating
    val error = when (state) {
        is ConnectionState.Error -> state.failure.message()
        ConnectionState.InvalidInput -> "Enter an HTTPS ADA server address and token. Debug builds also allow listed local development hosts."
        else -> null
    }
    LaunchedEffect(error) { if (error != null) errorFocus.requestFocus() }
    Surface(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.fillMaxSize().imePadding().verticalScroll(rememberScrollState()).padding(AdaSpacing.large),
            verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
        ) {
            Text("ADA", style = MaterialTheme.typography.headlineLarge)
            TextButton(onClick = openSettings, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Settings") }
            Text("Development foundation", style = MaterialTheme.typography.titleMedium)
            Text("Connect to your ADA server to check your account and API compatibility. Chat and Memory are planned screens.")
            if (state is ConnectionState.Connected) {
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        Text("Connected", style = MaterialTheme.typography.titleLarge)
                        Text("Account: ${state.account.name}")
                        Text("Server: ${state.account.server}")
                        Text("Model: ${state.account.model}")
                        Button(onClick = { token = ""; disconnect() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Disconnect") }
                    }
                }
            } else {
                OutlinedTextField(server, { server = it }, label = { Text("ADA server URL") },
                    singleLine = true, enabled = !validating, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri), modifier = Modifier.fillMaxWidth())
                OutlinedTextField(token, { token = it }, label = { Text("Bearer token") },
                    singleLine = true, enabled = !validating, visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password), modifier = Modifier.fillMaxWidth())
                if (error != null) {
                    Text(error, color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.focusRequester(errorFocus).focusable().semantics { liveRegion = LiveRegionMode.Polite })
                }
                Button(onClick = { connect(server, token); token = "" }, enabled = !validating && server.isNotBlank() && token.isNotBlank(),
                    modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text(if (validating) "Connecting…" else "Connect") }
                if (validating) CircularProgressIndicator(Modifier.semantics { contentDescription = "Validating the ADA connection" })
            }
            Text("Appearance preview", style = MaterialTheme.typography.titleMedium)
            TextButton(onClick = { largePreview = !largePreview }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (largePreview) "Use normal text preview" else "Preview larger text") }
            Text("Readable text, clear actions, and room for your words.", fontSize = if (largePreview) 24.sp else 16.sp)
            Text("Screen map", style = MaterialTheme.typography.titleMedium)
            screenMap.forEach {
                Text("${it.destination.name.replace("NewConversation", "New conversation")} · ${if (it.enabledPhase == 3) "connection foundation" else "planned Phase ${it.enabledPhase}"}")
            }
            Text("Credentials are held in memory for this connection check. Secure storage and enrollment are scheduled for Phase 04.", style = MaterialTheme.typography.bodySmall)
        }
    }
}
