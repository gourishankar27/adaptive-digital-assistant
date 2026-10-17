package dev.ada.assistant.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import dev.ada.assistant.BuildConfig
import dev.ada.assistant.data.*
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch

/** Selecting an address is explicit and never authenticates or restores private state. */
@Composable
fun ServerAddressPanel(server: String, change: (String) -> Unit, enabled: Boolean) {
    val context = LocalContext.current
    val preferences = remember(context) { ServerProfilePreferences(context) }
    var expanded by remember { mutableStateOf(false) }
    var profiles by remember { mutableStateOf(preferences.load()) }
    var label by remember { mutableStateOf("") }
    var importedText by remember { mutableStateOf("") }
    var imported by remember { mutableStateOf<ServerProfile?>(null) }
    var feedback by remember { mutableStateOf("") }
    var checking by remember { mutableStateOf(false) }
    var checkJob by remember { mutableStateOf<Job?>(null) }
    val scope = rememberCoroutineScope()
    val latestServer by rememberUpdatedState(server)
    LaunchedEffect(server) { checkJob?.cancel(); checking = false; feedback = "" }
    TextButton(onClick = { expanded = !expanded }, enabled = enabled) { Text(if (expanded) "Close server addresses" else "Saved servers and connection checks") }
    if (!expanded) return
    fun save(next: List<ServerProfile>) {
        if (preferences.save(next)) { profiles = next; feedback = "Saved server addresses updated." }
        else feedback = "Server addresses could not be saved. Check device storage and retry."
    }
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Saved servers")
        Text("Addresses are bookmarks, not trusted identities. Selecting one clears the current login and requires fresh verification.")
        profiles.forEach { profile ->
            TextButton(onClick = { change(profile.origin) }, enabled = enabled,
                modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Use ${profile.label}: ${profile.origin}") }
            TextButton(onClick = { save(profiles.filter { it.origin != profile.origin }) }, enabled = enabled) { Text("Remove ${profile.label}") }
        }
        OutlinedTextField(label, { label = it }, label = { Text("Server name") }, singleLine = true, enabled = enabled, modifier = Modifier.fillMaxWidth())
        TextButton(onClick = {
            val profile = ServerProfile.parse(label, server)
            if (profile == null) feedback = "Use a short name and an HTTPS origin without credentials, path, query or fragment."
            else {
                val next = profiles.filter { it.origin != profile.origin } + profile
                if (next.size > 12) feedback = "Remove a saved server before adding another (maximum 12)." else save(next)
            }
        }, enabled = enabled) { Text("Save server address") }
        TextButton(onClick = { change(""); label = "" }, enabled = enabled) { Text("Clear selected address") }
        Button(onClick = {
            val origin = serverOrigin(server, BuildConfig.DEBUG)
            if (origin == null) { feedback = "Use an HTTPS origin, or a listed debug development host." }
            else {
                val selected = server
                checking = true; feedback = "Checking the server without a credential…"
                checkJob?.cancel()
                checkJob = scope.launch {
                    val result = HttpServerProbe().check(origin)
                    if (selected == latestServer) {
                        checking = false
                        feedback = when (result) {
                            is ApiResult.Success -> "Server ready over the selected connection. Sign in to verify account and feature compatibility."
                            is ApiResult.Failure -> result.reason.message()
                        }
                    }
                }
            }
        }, enabled = enabled && server.isNotBlank() && !checking) { Text(if (checking) "Checking server…" else "Check server without signing in") }
        OutlinedTextField(importedText, { importedText = it; imported = null }, label = { Text("Server address import (JSON)") },
            enabled = enabled, modifier = Modifier.fillMaxWidth())
        TextButton(onClick = {
            imported = ServerProfiles.decodeImport(importedText)
            feedback = if (imported == null) "Invalid address import. Only version 1 HTTPS origin and label metadata are accepted." else "Review the imported origin before selecting it."
        }, enabled = enabled) { Text("Preview address import") }
        imported?.let { profile ->
            Text("${profile.label}: ${profile.origin}")
            TextButton(onClick = { change(profile.origin); label = profile.label; imported = null; importedText = "" }, enabled = enabled) { Text("Use reviewed address") }
        }
        if (feedback.isNotBlank()) Text(feedback)
    }
}
