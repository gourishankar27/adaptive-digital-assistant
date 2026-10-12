package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*

@Composable
fun LearningSettings(controller: LearningController, chat: ChatState) {
    val s by controller.state.collectAsStateWithLifecycle()
    LaunchedEffect(chat.conversation?.scope_id, s.journal?.operationId, s.busy) { controller.activate(chat.conversation?.scope_id) }
    Text("Interaction learning and continuity", style = MaterialTheme.typography.titleMedium)
    Text("Learning is off by default. You select completed user messages as evidence for wording preferences. Interpretations stay tentative until reviewed. No facts, permissions, diagnosis or attachment score are learned.")
    if (!s.enabled) { Text("This server does not support interaction learning."); return }
    if (s.scopeId == null) { Text("Open a conversation to choose its knowledge scope."); return }
    Text("Applies to: ${chat.scopes.items.firstOrNull { it.id == s.scopeId }?.name ?: "this conversation’s scope"}. Explicit instructions and selected preferences override learned defaults.")
    if (s.busy) LinearProgressIndicator(Modifier.fillMaxWidth())
    s.notice?.let { Text(it) }; s.fault?.let { Text("The operation could not be confirmed. Check the saved receipt before retrying.") }
    if (s.journal != null) {
        Text("The pending change stays pinned to its original scope. Restart reads its receipt without submitting again.")
        OutlinedButton(controller::checkPending, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-check")) { Text("Check saved learning change") }
        OutlinedButton(controller::retry, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Retry identical learning change") }
        TextButton(controller::discard, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Discard local learning reservation") }
        return
    }
    val data = s.data ?: return
    var consent by remember(s.scopeId) { mutableStateOf(false) }
    var continuity by remember(s.scopeId, data.config.revision) { mutableStateOf(data.config.continuity_enabled) }
    var confirmReset by remember { mutableStateOf(false) }
    Text("Learning: ${data.config.status}. ${data.config.threshold} distinct interactions are required for a durable suggestion; a threshold is not proof. Weak guesses expire after seven days and cannot promote a rule.")
    Row(Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) {
        Checkbox(continuity, { continuity = it }, enabled = !s.busy, modifier = Modifier.testTag("learning-continuity").semantics { contentDescription = "Use source-linked episodes for relevant continuity" })
        Text("Use source-linked episodes for relevant continuity", Modifier.padding(vertical = 12.dp))
    }
    Text("Continuity uses exact authorized excerpts with C source cards. Generated summaries remain separate navigation; recorded text can be incomplete or conflicting. No personal experience or bond is implied.")
    if (data.config.status != "enrolled") {
        Row(Modifier.heightIn(min = AdaSpacing.touch)) { Checkbox(consent, { consent = it }, modifier = Modifier.testTag("learning-consent").semantics { contentDescription = "I choose learning in this scope" }); Text("I choose learning in this scope", Modifier.padding(vertical = 12.dp)) }
        Button({ controller.configure("enrolled", continuity) }, enabled = !s.busy && consent, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-enroll")) { Text("Enable reviewed learning") }
    } else {
        OutlinedButton({ controller.configure("enrolled", continuity) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Save continuity choice") }
        OutlinedButton({ controller.configure("paused") }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-pause")) { Text("Pause learning and reuse") }
    }
    OutlinedButton({ confirmReset = true }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-reset")) { Text("Disable and reset learned state") }
    if (confirmReset) AlertDialog(onDismissRequest = { confirmReset = false }, title = { Text("Reset this scope’s learning?") },
        text = { Text("Removes live observations, suggestions and learned defaults, including reuse in other scopes. Minimal operation audit and historical chat/request snapshots remain for exact replay. Original messages and episodes are retained. This is not complete account erasure.") },
        confirmButton = { TextButton({ confirmReset = false; controller.resetLearned() }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-reset-confirm")) { Text("Disable and reset") } },
        dismissButton = { TextButton({ confirmReset = false }) { Text("Keep learning") } })
    OutlinedButton(controller::refresh, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-refresh")) { Text("Refresh learning") }
    data.learned.forEach { learned ->
        Text("Reviewed default: ${preferenceMap(learned.values).entries.joinToString { "${it.key}: ${it.value}" }} · ${if(learned.account_wide) "Account reuse chosen" else "This scope only"}")
        Text("Original reviewed evidence remains inspectable until reset; expiry stops new inference from observations.")
        data.observations.filter { it.id in learned.observation_ids }.forEach { original -> SafeChatText(original.evidence.evidence.quote, links = false) }
    }
    if (data.config.status != "enrolled") return
    Text("Select evidence", style = MaterialTheme.typography.titleSmall)
    val events = chat.events.items.filter { it.role == "user" && it.request_status == "completed" }.takeLast(20)
    if (events.isEmpty()) Text("No completed user messages loaded. Send a reply or load conversation history first.")
    events.forEach { event -> OutlinedButton({ controller.chooseSource(event) }, enabled = !s.busy, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("learning-source-${event.source_version_id}")) { Text(event.content.take(120)) } }
    s.source?.let { source ->
        Text("Exact selected user excerpt:"); SafeChatText(source.content, links = false)
        var field by remember(source.id) { mutableStateOf("verbosity") }
        var chosen by remember(source.id, field) { mutableStateOf(preferenceChoices.getValue(field).first()) }
        var confidence by remember(source.id) { mutableStateOf("repeated_observation") }
        LearningChoice("Preference", field, preferenceChoices.keys.toList(), { field = it }, !s.busy)
        LearningChoice("Suggested value", chosen, preferenceChoices.getValue(field), { chosen = it }, !s.busy)
        LearningChoice("Evidence class", confidence, listOf("explicit_statement", "repeated_observation", "weak_inference"), { confidence = it }, !s.busy)
        Button({ controller.observe(singlePreference(field, chosen), confidence) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-observe")) { Text("Save selected tentative observation") }
    }
    data.proposals.forEach { p -> Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        val field = preferenceMap(p.values).keys.single(); val proposed = preferenceMap(p.values).values.single()!!
        var edited by remember(p.id, p.revision) { mutableStateOf(proposed) }
        var account by remember(p.id, p.revision) { mutableStateOf(false) }
        Text("Suggested $field: $proposed · ${p.status}")
        Text("${p.independent_count} independent interactions. Interpretation is unreviewed; confidence is not authority. Expires ${java.time.Instant.ofEpochMilli(p.expires_at)}.")
        data.observations.filter { it.id in p.observations }.forEach { observation -> Text("${observation.confidence_class} · ${observation.evidence.trust_class}"); SafeChatText(observation.evidence.evidence.quote, links = false) }
        if (p.status == "pending") {
            LearningChoice("Reviewed value", edited, preferenceChoices.getValue(field), { edited = it }, !s.busy)
            Row(Modifier.heightIn(min = AdaSpacing.touch)) { Checkbox(account, { account = it }, enabled = !s.busy, modifier = Modifier.semantics { contentDescription = "Reuse wording in other opted-in scopes" }); Text("Reuse wording in other opted-in scopes", Modifier.padding(vertical = 12.dp)) }
            Text("Account reuse exports only the wording enum. Project facts, quotes, sources and episode history stay in this scope.")
            Button({ controller.review(p, "approve", account, singlePreference(field, edited)) }, enabled = !s.busy && p.eligible, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-approve-${p.id}")) { Text("Approve reviewed preference") }
            OutlinedButton({ controller.review(p, "reject", false) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-reject-${p.id}")) { Text("Reject suggestion") }
        }
    } } }
}

@Composable private fun LearningChoice(label: String, chosen: String, choices: List<String>, select: (String) -> Unit, enabled: Boolean) {
    var expanded by remember { mutableStateOf(false) }
    Box { OutlinedButton({ expanded = true }, enabled = enabled, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("$label: ${chosen.replace('_', ' ')}") }
        DropdownMenu(expanded, { expanded = false }) { choices.forEach { value -> DropdownMenuItem(text = { Text(value.replace('_', ' ')) }, onClick = { expanded = false; select(value) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) } } }
}
