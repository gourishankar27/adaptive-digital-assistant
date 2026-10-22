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
    var remove by remember { mutableStateOf<ServerProfile?>(null) }
    var feedbackError by remember { mutableStateOf(false) }
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
    LaunchedEffect(server) { checkJob?.cancel(); checking = false; feedback = ""; feedbackError = false }
    AdaTextButton(onClick = { expanded = !expanded }, enabled = enabled) { Text(if (expanded) "Close server addresses" else "Saved servers and connection checks") }
    if (!expanded) return
    remove?.let { profile -> AdaConfirmation("Remove this saved server?", "This removes the address bookmark. It does not delete the server or your account.", "Remove bookmark", { remove = null }, {
        remove = null
        val next = profiles.filter { it.origin != profile.origin }
        feedbackError = !preferences.save(next)
        if (!feedbackError) profiles = next
        feedback = if (feedbackError) "Server addresses could not be saved. Check device storage and retry." else "Saved server address removed."
    }, "remove-server") }
    fun save(next: List<ServerProfile>) {
        feedbackError = false
        if (preferences.save(next)) { profiles = next; feedback = "Saved server addresses updated." }
        else { feedbackError = true; feedback = "Server addresses could not be saved. Check device storage and retry." }
    }
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Saved servers")
        Text("Addresses are bookmarks, not trusted identities. Selecting one clears the current login and requires fresh verification.")
        profiles.forEach { profile ->
            AdaTextButton(onClick = { change(profile.origin) }, enabled = enabled,
                modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Use ${profile.label}: ${profile.origin}") }
            AdaTextButton(onClick = { remove = profile }, enabled = enabled) { Text("Remove ${profile.label}") }
        }
        OutlinedTextField(label, { label = it }, label = { Text("Server name") }, singleLine = true, enabled = enabled, modifier = Modifier.fillMaxWidth())
        AdaTextButton(onClick = {
            val profile = ServerProfile.parse(label, server)
            if (profile == null) { feedbackError = true; feedback = "Use a short name and an HTTPS origin without credentials, path, query or fragment." }
            else {
                val next = profiles.filter { it.origin != profile.origin } + profile
                if (next.size > 12) { feedbackError = true; feedback = "Remove a saved server before adding another (maximum 12)." } else save(next)
            }
        }, enabled = enabled) { Text("Save server address") }
        AdaTextButton(onClick = { change(""); label = "" }, enabled = enabled) { Text("Clear selected address") }
        AdaButton(onClick = {
            val origin = serverOrigin(server, BuildConfig.DEBUG)
            if (origin == null) { feedbackError = true; feedback = "Use an HTTPS origin, or a listed debug development host." }
            else {
                val selected = server
                checking = true; feedback = "Checking the server without a credential…"
                checkJob?.cancel()
                checkJob = scope.launch {
                    val result = HttpServerProbe().check(origin)
                    if (selected == latestServer) {
                        checking = false
                        feedbackError = result is ApiResult.Failure
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
        AdaTextButton(onClick = {
            imported = ServerProfiles.decodeImport(importedText)
            feedbackError = imported == null
            feedback = if (imported == null) "Invalid address import. Only version 1 HTTPS origin and label metadata are accepted." else "Review the imported origin before selecting it."
        }, enabled = enabled) { Text("Preview address import") }
        imported?.let { profile ->
            Text("${profile.label}: ${profile.origin}")
            AdaTextButton(onClick = { change(profile.origin); label = profile.label; imported = null; importedText = "" }, enabled = enabled) { Text("Use reviewed address") }
        }
        if (checking) AdaLoading("Checking server without signing in")
        if (feedback.isNotBlank()) AdaNotice(feedback, error = feedbackError)
    }
}
