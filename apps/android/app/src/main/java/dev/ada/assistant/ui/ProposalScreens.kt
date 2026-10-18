package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import dev.ada.assistant.data.*
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun ProposalScreens(controller: ProposalController, back: () -> Unit) {
    val s by controller.state.collectAsStateWithLifecycle()
    val focus = LocalFocusManager.current
    var confirmDiscard by remember { mutableStateOf(false) }
    var confirmDecision by remember { mutableStateOf<String?>(null) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium).testTag("proposal-screen"), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        TextButton(back, Modifier.heightIn(min = AdaSpacing.touch)) { Text("Back to Memory") }
        AdaSectionHeading("Memory suggestions")
        Text("Model suggestions are not saved memory. Read the original excerpts and explicitly review each annotation.")
        if (!s.enabled) Text("This server does not advertise the supported review contract.")
        if (s.busy || s.inbox.loading || s.scopes.loading) LinearProgressIndicator(Modifier.fillMaxWidth())
        s.notice?.let { Text(it) }; s.fault?.let { Text("The operation needs attention: ${it::class.simpleName}", color = MaterialTheme.colorScheme.error) }
        s.pending?.let {
            Text("A saved ${it.kind} operation has an unresolved outcome. The original input and key are retained.")
            OutlinedButton(controller::check, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-check")) { Text("Check saved operation") }
            OutlinedButton(controller::retry, enabled = s.enabled && !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-retry")) { Text("Retry identical input") }
        }
        if (s.pending != null || s.draft != null) TextButton({ confirmDiscard = true }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-discard")) { Text("Discard local draft and recovery") }
        val d = s.draft
        val editable = !s.busy && s.pending == null && s.enabled
        if (d != null) {
            Text("Review one suggestion", style = MaterialTheme.typography.titleLarge)
            Text("Proposed by ${d.proposal.model}. Status: ${d.proposal.status}. Revision ${d.proposal.revision}.")
            Text("Confidence ${d.proposal.candidate.confidence ?: "not reported"} is advisory and does not verify truth.")
            d.proposal.support.forEachIndexed { i, evidence ->
                Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Original excerpt ${i + 1} · ${evidence.source_origin} · ${evidence.trust_class} · version ${evidence.source_version}")
                    SafeChatText(evidence.evidence.quote, Modifier.testTag("proposal-excerpt-$i"), links = false)
                    Text("Exact code-point span ${evidence.evidence.span_start}–${evidence.evidence.span_end}", style = MaterialTheme.typography.bodySmall)
                } }
            }
            val c = d.candidate
            if (d.proposal.conflicts.any { it.value == c.value }) Text("An overlapping saved assertion has the same value. Compare its dates and original support before deciding whether another endorsement is useful.")
            if (d.proposal.conflicts.any { it.value != c.value }) Text("Overlapping saved assertions have different values. Keep the conflict visible or explicitly review a dated correction; model confidence cannot settle it.")
            fun change(next: ProposalCandidateDto) = controller.draft(candidate = next)
            OutlinedTextField(c.subject, { change(c.copy(subject = it)) }, label = { Text("Subject") }, enabled = editable, modifier = Modifier.fillMaxWidth().testTag("proposal-subject"))
            OutlinedTextField(c.predicate, { change(c.copy(predicate = it)) }, label = { Text("Predicate") }, enabled = editable, modifier = Modifier.fillMaxWidth().testTag("proposal-predicate"))
            OutlinedTextField(c.value, { change(c.copy(value = it)) }, label = { Text("Value") }, enabled = editable, modifier = Modifier.fillMaxWidth().testTag("proposal-value"))
            listOf("fact", "preference", "decision").forEach { kind -> Row { RadioButton(c.kind == kind, { change(c.copy(kind = kind)) }, enabled = editable); TextButton({ change(c.copy(kind = kind)) }, enabled = editable) { Text(kind) } } }
            OutlinedTextField(c.valid_from.orEmpty(), { change(c.copy(valid_from = it)) }, label = { Text("Effective from (ISO time with offset)") }, enabled = editable, modifier = Modifier.fillMaxWidth().testTag("proposal-from"))
            OutlinedTextField(c.valid_to.orEmpty(), { change(c.copy(valid_to = it.takeIf(String::isNotEmpty))) }, label = { Text("Effective until (optional, exclusive)") }, enabled = editable, modifier = Modifier.fillMaxWidth().testTag("proposal-until"))
            TextButton({ change(c.copy(subject_entity_id = null)) }, enabled = editable) { Text("Keep the raw subject without a canonical link") }
            s.entities.forEach { entity -> OutlinedButton({ change(c.copy(subject_entity_id = entity.id)) }, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("${if (c.subject_entity_id == entity.id) "Selected: " else "Link to: "}${entity.label}") } }
            if (d.proposal.conflicts.isNotEmpty()) {
                Text("Overlapping saved assertions", style = MaterialTheme.typography.titleMedium)
                Text("Choose a specific replacement for an atomic correction, or retain the existing assertions alongside this one. Nothing is overwritten in bulk.")
                OutlinedButton({ controller.draft(setReplacement = true) }, enabled = editable) { Text(if (d.replaceClaimId == null) "Keep existing assertions (selected)" else "Keep existing assertions") }
                d.proposal.conflicts.forEach { old ->
                    SafeChatText("${old.value}: ${displayInstant(old.valid_from)} until ${old.valid_to?.let(::displayInstant) ?: "open"} · ${old.status}", links = false)
                    if (old.status == "active") OutlinedButton({ controller.draft(replacement = old.id, setReplacement = true) }, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (d.replaceClaimId == old.id) "Replacement selected" else "Replace this assertion") }
                }
            }
            OutlinedTextField(d.annotation, { controller.draft(annotation = it) }, label = { Text("Your decision annotation / rejection reason") }, enabled = editable, modifier = Modifier.fillMaxWidth().testTag("proposal-annotation"))
            Text(if (s.draftSaved) "Draft encrypted on this device." else "Saving the private draft…", style = MaterialTheme.typography.bodySmall)
            if (c != d.proposal.candidate) Button({ focus.clearFocus(); controller.previewEdits() }, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-preview")) { Text("Save edits and preview exact revision") }
            Button({ focus.clearFocus(); confirmDecision = "accept" }, enabled = editable && c == d.proposal.candidate && d.annotation.isNotBlank(), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-accept")) { Text("Accept reviewed annotation") }
            OutlinedButton({ focus.clearFocus(); confirmDecision = "reject" }, enabled = editable && c == d.proposal.candidate && d.annotation.isNotBlank(), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-reject")) { Text("Reject suggestion") }
        } else {
            Text("Private scope", style = MaterialTheme.typography.titleMedium)
            s.scopes.items.forEach { scope -> OutlinedButton({ controller.selectScope(scope.id) }, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (scope.id == s.scopeId) "${scope.name} (selected)" else scope.name) } }
            if (s.scopes.hasMore) TextButton(controller::moreScopes) { Text("More scopes") }
            OutlinedButton(controller::refresh, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-refresh")) { Text("Refresh inbox") }
            if (s.inbox.items.isEmpty() && !s.inbox.loading) Text("No pending suggestions in this scope.")
            proposalReviewGroups(s.inbox.items).forEach { group ->
                if (group.size > 1) Text("${group.size} matching annotations with the same support/dates among loaded suggestions. Each still needs its own explicit review.")
                group.forEach { p -> OutlinedButton({ controller.open(p) }, enabled = editable, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("proposal-open-${p.id}")) { Text("${p.candidate.subject} · ${p.candidate.predicate}: ${p.candidate.value}") } }
            }
            if (s.inbox.hasMore) TextButton(controller::moreProposals) { Text("More suggestions") }
            Text("Select owned source material", style = MaterialTheme.typography.titleMedium)
            s.sources.forEach { source -> OutlinedButton({ controller.selectSource(source) }, enabled = editable, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("${source.trust_class} · ${displayInstant(source.created_at)} · ${source.content.take(80)}") } }
            s.uploads.forEach { upload -> OutlinedButton({ controller.selectDocument(upload) }, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Document ${upload.filename} · version ${upload.version}") } }
            s.chunks.forEach { chunk -> OutlinedButton({ controller.selectChunk(chunk) }, enabled = editable, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Lines ${chunk.line_start}–${chunk.line_end}: ${chunk.quote.take(80)}") } }
            s.selectedQuote?.let { SafeChatText(it, Modifier.testTag("proposal-selected-excerpt"), links = false) }
            Button(controller::extractSelected, enabled = editable && s.selectedPin != null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("proposal-extract")) { Text("Suggest memories from selected excerpt") }
            Text("Extraction does not approve or save claims. Source instructions and confidence never grant permissions.")
        }
    }
    confirmDecision?.let { decision -> AlertDialog(onDismissRequest = { confirmDecision = null }, title = { Text(if (decision == "accept") "Endorse this exact annotation?" else "Reject this exact suggestion?") }, text = { Text("${s.draft?.candidate?.subject} · ${s.draft?.candidate?.predicate}: ${s.draft?.candidate?.value}\n${s.draft?.annotation}\nYour authenticated decision and exact evidence references will be recorded.") }, confirmButton = { TextButton({ confirmDecision = null; controller.decide(decision) }, modifier = Modifier.testTag("proposal-confirm")) { Text(if (decision == "accept") "Accept" else "Reject") } }, dismissButton = { TextButton({ confirmDecision = null }) { Text("Keep reviewing") } }) }
    if (confirmDiscard) AlertDialog(onDismissRequest = { confirmDiscard = false }, title = { Text("Discard local recovery?") }, text = { Text("The server may already have recorded this operation. This only clears this device's draft and saved key.") }, confirmButton = { TextButton({ confirmDiscard = false; controller.discard() }) { Text("Discard local recovery") } }, dismissButton = { TextButton({ confirmDiscard = false }) { Text("Keep recovery") } })
}
