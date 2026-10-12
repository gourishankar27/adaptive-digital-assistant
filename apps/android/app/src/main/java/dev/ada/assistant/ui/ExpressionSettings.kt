package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import java.util.UUID

@Composable fun ExpressionSettings(controller: ExpressionController, conversationId: UUID?) {
    val s by controller.state.collectAsStateWithLifecycle()
    LaunchedEffect(conversationId, s.journal?.operationId) { controller.activateConversation(conversationId) }
    Text("Interaction preferences", style = MaterialTheme.typography.titleLarge)
    if (!s.enabled) { Text("This server does not support interaction preferences."); return }
    Text("Choose where to save these settings. Conversation changes apply to future replies. Account, project and style defaults apply to new conversations; current snapshots stay saved.")
    Column(Modifier.selectableGroup()) {
        listOf("conversation" to "This conversation", "profile" to "This conversation’s chat style",
            "scope" to "This conversation’s knowledge scope", "account" to "Account-wide defaults").forEach { (kind, label) ->
            val allowed = !s.busy && s.journal == null && (kind == "account" || s.expression != null)
            Row(Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).selectable(s.targetKind == kind, enabled = allowed,
                role = Role.RadioButton, onClick = { controller.select(kind) }).testTag("expression-target-$kind")) {
                RadioButton(s.targetKind == kind, null, enabled = allowed); Text(label, Modifier.padding(vertical = 12.dp))
            }
        }
    }
    if (s.busy) LinearProgressIndicator(Modifier.fillMaxWidth())
    s.notice?.let { Text(it) }
    s.fault?.let { Text("Settings could not be confirmed. Refresh or check the saved change.") }
    if (s.journal != null) {
        Text("A pending change is pinned to its original scope. Restart checks its receipt without submitting again.")
        OutlinedButton(controller::checkPending, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("expression-check")) { Text("Check saved change") }
        OutlinedButton(controller::retry, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("expression-retry")) { Text("Retry identical change") }
        TextButton(controller::discard, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Discard local reservation") }
        return
    }
    val values = listOf(s.draft.verbosity, s.draft.initiative, s.draft.formality, s.draft.humor, s.draft.cadence)
    preferenceChoices.entries.zip(values).forEach { (entry, chosen) ->
        var expanded by remember(s.targetKind, s.targetId, entry.key) { mutableStateOf(false) }
        Box {
            OutlinedButton({ expanded = true }, enabled = !s.busy && s.preference != null,
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("expression-field-${entry.key}")) {
                Text("${entry.key.replaceFirstChar { it.uppercase() }}: ${chosen ?: "Use inherited value"}")
            }
            DropdownMenu(expanded, { expanded = false }) {
                (listOf<String?>(null) + entry.value).forEach { value ->
                    DropdownMenuItem(text = { Text(value ?: "Use inherited value") }, onClick = {
                        expanded = false
                        val old = s.draft
                        controller.edit(when (entry.key) { "verbosity" -> old.copy(verbosity = value); "initiative" -> old.copy(initiative = value);
                            "formality" -> old.copy(formality = value); "humor" -> old.copy(humor = value); else -> old.copy(cadence = value) })
                    }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("expression-choice-${entry.key}-${value ?: "inherit"}"))
                }
            }
        }
    }
    if (s.targetKind == "conversation") {
        Row(Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) {
            Checkbox(s.dynamic, controller::dynamic, enabled = !s.busy, modifier = Modifier.semantics { contentDescription = "Allow bounded session tone adjustments" }.testTag("expression-dynamic"))
            Text("Allow bounded session tone adjustments", Modifier.padding(vertical = 12.dp))
        }
        Text("Off by default. Tone is temporary expression, not a feeling or a diagnosis. Signals need your explicit review; model text cannot update settings automatically.")
    }
    Button({ controller.save() }, enabled = !s.busy && s.preference != null,
        modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("expression-save")) { Text("Save reviewed preferences") }
    OutlinedButton({ controller.save(reset = true) }, enabled = !s.busy && s.preference != null,
        modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Reset preferences to inherited values") }
    OutlinedButton(controller::refresh, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh preferences") }
    if (s.targetKind == "conversation" && s.expression?.active == true) {
        val x = s.expression!!
        Text("Effective preferences: ${x.preferences.verbosity}, ${x.preferences.initiative}, ${x.preferences.formality}, ${x.preferences.humor}, ${x.preferences.cadence}.")
        Text(if (x.expired) "Session tone expired; defaults apply to the next reply." else "Session tone decays toward defaults and expires after 30 minutes idle or two hours total.")
        OutlinedButton(controller::resetSession, enabled = !s.busy && x.session_id != null && !x.expired,
            modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("expression-reset-session")) { Text("Reset session tone") }
        if (x.dynamic_enabled) {
            Text("After a completed reply, choose one bounded adjustment for the next turn.")
            OutlinedButton({ controller.signal("warmth") }, enabled = !s.busy && !x.expired && x.last_request_id != null,
                modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("expression-warmth")) { Text("Use a gentler tone next turn") }
            OutlinedButton({ controller.signal("focus") }, enabled = !s.busy && !x.expired && x.last_request_id != null,
                modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Use a more focused tone next turn") }
        }
    }
}
