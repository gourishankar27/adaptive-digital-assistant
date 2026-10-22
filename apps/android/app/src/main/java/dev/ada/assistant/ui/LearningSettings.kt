package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*

@Composable
fun LearningSettings(controller: LearningController, chat: ChatState) {
    val s by controller.state.collectAsStateWithLifecycle()
    LaunchedEffect(chat.conversation?.scope_id, s.journal?.operationId, s.busy) { controller.activate(chat.conversation?.scope_id) }
    Text("Learning is off by default. You select completed user messages as evidence for wording preferences. Interpretations stay tentative until reviewed. No facts, permissions, diagnosis or attachment score are learned.")
    if (!s.enabled) { Text("This server does not support interaction learning."); return }
    if (s.scopeId == null) { Text("Open a conversation to choose its knowledge scope."); return }
    Text("Applies to: ${chat.scopes.items.firstOrNull { it.id == s.scopeId }?.name ?: "this conversation’s scope"}. Explicit instructions and selected preferences override learned defaults.")
    if (s.busy) AdaLoading("Checking interaction learning")
    s.notice?.let { AdaNotice(it) }; s.fault?.let { AdaFailureNotice(it) }
    if (s.journal != null) {
        Text("The pending change stays pinned to its original scope. Restart reads its receipt without submitting again.")
        AdaOutlinedButton(controller::checkPending, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-check")) { Text("Check saved learning change") }
        AdaOutlinedButton(controller::retry, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Retry identical learning change") }
        AdaTextButton(controller::discard, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Discard local learning reservation") }
        return
    }
    val data = s.data ?: return
    var consent by remember(s.scopeId) { mutableStateOf(false) }
    var continuity by remember(s.scopeId, data.config.revision) { mutableStateOf(data.config.continuity_enabled) }
    var confirmReset by remember { mutableStateOf(false) }
    Text("Learning: ${statusLabel(data.config.status)}. ${data.config.threshold} distinct interactions are required for a durable suggestion; a threshold is not proof. Weak guesses expire after seven days and cannot promote a rule.")
    AdaToggle(continuity, "Use source-linked episodes for relevant continuity", { continuity = it }, Modifier.testTag("learning-continuity"), enabled = !s.busy)

    Text("Continuity uses exact authorized excerpts with C source cards. Generated summaries remain separate navigation; recorded text can be incomplete or conflicting. No personal experience or bond is implied.")
    if (data.config.status != "enrolled") {
        AdaToggle(consent, "I choose learning in this scope", { consent = it }, Modifier.testTag("learning-consent"))
        AdaButton({ controller.configure("enrolled", continuity) }, enabled = !s.busy && consent, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-enroll")) { Text("Enable reviewed learning") }
    } else {
        AdaOutlinedButton({ controller.configure("enrolled", continuity) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Save continuity choice") }
        AdaOutlinedButton({ controller.configure("paused") }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-pause")) { Text("Pause learning and reuse") }
    }
    AdaOutlinedButton({ confirmReset = true }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-reset")) { Text("Disable and reset learned state") }
    if (confirmReset) AlertDialog(onDismissRequest = { confirmReset = false }, title = { Text("Reset this scope’s learning?") },
        text = { Text("Removes live observations, suggestions and learned defaults, including reuse in other scopes. Minimal operation audit and historical chat/request snapshots remain for exact replay. Original messages and episodes are retained. This is not complete account erasure.") },
        confirmButton = { AdaTextButton({ confirmReset = false; controller.resetLearned() }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-reset-confirm")) { Text("Disable and reset") } },
        dismissButton = { AdaTextButton({ confirmReset = false }) { Text("Keep learning") } })
    AdaOutlinedButton(controller::refresh, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-refresh")) { Text("Refresh learning") }
    data.learned.forEach { learned ->
        Text("Reviewed default: ${preferenceMap(learned.values).entries.joinToString { "${preferenceLabel(it.key)}: ${preferenceLabel(it.value)}" }} · ${if(learned.account_wide) "Account reuse chosen" else "This scope only"}")
        Text("Original reviewed evidence remains inspectable until reset; expiry stops new inference from observations.")
        data.observations.filter { it.id in learned.observation_ids }.forEach { original -> SafeChatText(original.evidence.evidence.quote, links = false) }
    }
    if (data.config.status != "enrolled") return
    Text("Select evidence", style = MaterialTheme.typography.titleSmall)
    val events = chat.events.items.filter { it.role == "user" && it.request_status == "completed" }.takeLast(20)
    if (events.isEmpty()) Text("No completed user messages loaded. Send a reply or load conversation history first.")
    events.forEach { event -> AdaOutlinedButton({ controller.chooseSource(event) }, enabled = !s.busy, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("learning-source-${event.source_version_id}")) { Text(event.content.take(120)) } }
    s.source?.let { source ->
        Text("Exact selected user excerpt:"); SafeChatText(source.content, links = false)
        var field by remember(source.id) { mutableStateOf("verbosity") }
        var chosen by remember(source.id, field) { mutableStateOf(preferenceChoices.getValue(field).first()) }
        var confidence by remember(source.id) { mutableStateOf("repeated_observation") }
        LearningChoice("Preference", field, preferenceChoices.keys.toList(), { field = it }, !s.busy)
        LearningChoice("Suggested value", chosen, preferenceChoices.getValue(field), { chosen = it }, !s.busy)
        LearningChoice("Evidence class", confidence, listOf("explicit_statement", "repeated_observation", "weak_inference"), { confidence = it }, !s.busy)
        AdaButton({ controller.observe(singlePreference(field, chosen), confidence) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-observe")) { Text("Save selected tentative observation") }
    }
    data.proposals.forEach { p -> Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        val field = preferenceMap(p.values).keys.single(); val proposed = preferenceMap(p.values).values.single()!!
        var edited by remember(p.id, p.revision) { mutableStateOf(proposed) }
        var account by remember(p.id, p.revision) { mutableStateOf(false) }
        Text("Suggested ${preferenceLabel(field)}: ${preferenceLabel(proposed)} · ${statusLabel(p.status)}")
        Text("${p.independent_count} independent interactions. Interpretation is unreviewed; confidence is not authority. Expires ${displayInstant(p.expires_at)}.")
        data.observations.filter { it.id in p.observations }.forEach { observation -> Text("${preferenceLabel(observation.confidence_class)} · ${trustLabel(observation.evidence.trust_class)}"); SafeChatText(observation.evidence.evidence.quote, links = false) }
        if (p.status == "pending") {
            LearningChoice("Reviewed value", edited, preferenceChoices.getValue(field), { edited = it }, !s.busy)
            AdaToggle(account, "Reuse wording in other opted-in scopes", { account = it }, enabled = !s.busy)
            Text("Account reuse exports only the wording enum. Project facts, quotes, sources and episode history stay in this scope.")
            AdaButton({ controller.review(p, "approve", account, singlePreference(field, edited)) }, enabled = !s.busy && p.eligible, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-approve-${p.id}")) { Text("Approve reviewed preference") }
            AdaOutlinedButton({ controller.review(p, "reject", false) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("learning-reject-${p.id}")) { Text("Reject suggestion") }
        }
    } } }
}

@Composable private fun LearningChoice(label: String, chosen: String, choices: List<String>, select: (String) -> Unit, enabled: Boolean) {
    var expanded by remember { mutableStateOf(false) }
    Box { AdaOutlinedButton({ expanded = true }, enabled = enabled, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("$label: ${preferenceLabel(chosen)}") }
        DropdownMenu(expanded, { expanded = false }) { choices.forEach { value -> DropdownMenuItem(text = { Text(preferenceLabel(value)) }, onClick = { expanded = false; select(value) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).semantics { selected = chosen == value }) } } }
}
