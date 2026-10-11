package dev.ada.assistant.ui

import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.input.TextFieldValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.ClaimDto
import dev.ada.assistant.data.reviewOriginLabel
import dev.ada.assistant.data.PendingMemory
import dev.ada.assistant.data.SourceVersionDto

/** Explicit owner-scoped annotations; nothing here infers or promotes model output. */
@Composable
fun MemoryScreens(controller: MemoryController) {
    val state by controller.state.collectAsStateWithLifecycle()
    if (!state.enabled) {
        Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.large)) {
            MemoryHeading("Memory", "This server does not offer structured memory for this connection.")
        }
        return
    }
    when (state.screen) {
        MemoryScreen.Browse -> MemoryBrowse(state, controller)
        MemoryScreen.Detail -> MemoryDetail(state, controller)
        MemoryScreen.Edit -> MemoryEdit(state, controller)
        MemoryScreen.Preview -> MemoryPreview(state, controller)
    }
}

@Composable
private fun MemoryBrowse(state: MemoryState, controller: MemoryController) {
    var chooseScope by remember { mutableStateOf(false) }
    val scope = state.scopes.items.firstOrNull { it.id == state.scopeId }
    val competing = remember(state.claims.items) { competingAssertions(state.claims.items) }
    val focus = LocalFocusManager.current
    LazyColumn(
        Modifier.fillMaxSize().testTag("memory-list"),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium),
        verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
    ) {
        item {
            MemoryHeading("Your memory", "Inspect statements you explicitly saved, together with their evidence and recorded validity.")
            MemoryFeedback(state)
            MemoryPending(state, controller)
        }
        item {
            Text("Knowledge scope", style = MaterialTheme.typography.titleMedium)
            Text(scope?.name ?: "Choose a private scope", style = MaterialTheme.typography.bodyLarge)
            Text("A scope controls which knowledge belongs together. Chat style does not change access.", style = MaterialTheme.typography.bodySmall)
            Row(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                OutlinedButton(onClick = { chooseScope = !chooseScope }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-choose-scope")) { Text(if (chooseScope) "Close scope list" else "Choose scope") }
                TextButton(onClick = controller::refreshScopes, enabled = !state.scopes.loading, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh scopes") }
            }
        }
        if (chooseScope || state.scopeId == null) {
            items(state.scopes.items, key = { "scope-${it.id}" }) { item ->
                MemoryChoice(state.scopeId == item.id, item.name, modifier = Modifier.testTag("memory-scope-${item.id}")) {
                    focus.clearFocus(); controller.selectScope(item.id); chooseScope = false
                }
            }
            if (state.scopes.items.isEmpty() && !state.scopes.loading) item { Text("No owned scopes are available. Creating a conversation can create a private personal scope.") }
            if (state.scopes.hasMore && !state.scopes.loading) item {
                OutlinedButton(onClick = controller::loadMoreScopes, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more scopes") }
            }
        }
        if (state.scopes.loading) item { MemoryProgress("Loading owned scopes") }
        if (state.scopeId != null) {
            item {
                Text("View", style = MaterialTheme.typography.titleMedium)
                Column(Modifier.selectableGroup()) {
                    MemoryChoice(state.mode == MemoryMode.Current, "Current", Modifier.testTag("memory-mode-current")) { focus.clearFocus(); controller.setMode(MemoryMode.Current) }
                    if (state.historicalEnabled) {
                        MemoryChoice(state.mode == MemoryMode.AsOf, "At a date", Modifier.testTag("memory-mode-asof")) { controller.setMode(MemoryMode.AsOf) }
                        MemoryChoice(state.mode == MemoryMode.History, "All history", Modifier.testTag("memory-mode-history")) { focus.clearFocus(); controller.setMode(MemoryMode.History) }
                    }
                }
                if (state.mode == MemoryMode.AsOf) {
                    OutlinedTextField(state.asOf, controller::updateAsOf, label = { Text("Memory valid at") }, singleLine = true,
                        supportingText = { Text("Include a timezone and at most millisecond precision, for example 2026-10-09T12:00:00.000Z.") },
                        modifier = Modifier.fillMaxWidth().testTag("memory-asof"))
                    Button(onClick = { focus.clearFocus(); controller.applyQuery() }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-apply-query")) { Text("Apply date") }
                }
                if (state.mode != MemoryMode.Current) Text("This view uses when a statement was valid. It does not reconstruct what ADA knew or had stored on that date.", style = MaterialTheme.typography.bodySmall)
                Row(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Button(onClick = controller::beginRemember, enabled = state.writesEnabled && state.pending == null && !state.saving,
                        modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-remember")) { Text("Remember") }
                    TextButton(onClick = controller::refreshClaims, enabled = !state.claims.loading, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh memory") }
                }
                if (!state.writesEnabled) Text("This server offers memory inspection without explicit writes.", style = MaterialTheme.typography.bodySmall)
            }
            if (competing.isNotEmpty()) item { MemoryInfo("Competing assertions", "Some loaded statements have different values in overlapping validity intervals. Review their evidence; this view does not rank truth.") }
            items(state.claims.items, key = { it.id }) { claim ->
                Card(onClick = { controller.openClaim(claim.id) }, modifier = Modifier.fillMaxWidth().testTag("memory-claim-${claim.id}"),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow)) {
                    Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        SafeChatText("${claim.subject} · ${claim.predicate}: ${claim.value}", links = false)
                        Text(kindLabel(claim.kind), style = MaterialTheme.typography.labelLarge)
                        Text(intervalLabel(claim), style = MaterialTheme.typography.bodySmall)
                        if (claim.status == "superseded") Text("Superseded record; it remains valid within its recorded interval.", style = MaterialTheme.typography.bodySmall)
                        if (claim.id in competing) Text("Overlapping assertion with a different value", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
            if (state.claims.items.isEmpty() && !state.claims.loading && state.fault == null) item { MemoryInfo("No statements in this view", "Choose another date or explicitly Remember a statement supported by your words.") }
            if (state.claims.loading) item { MemoryProgress("Loading recorded memory") }
            if (state.claims.hasMore && !state.claims.loading) item {
                OutlinedButton(onClick = controller::loadMoreClaims, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-more-claims")) { Text("Load more memory") }
            }
        }
    }
}

@Composable
private fun MemoryDetail(state: MemoryState, controller: MemoryController) {
    var details by remember(state.detail?.id) { mutableStateOf(false) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium).testTag("memory-detail"), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        MemoryBack(controller)
        MemoryHeading("Saved statement", "The annotation is an explicit assertion. Its quote records provenance, not a guarantee that it is true.")
        MemoryFeedback(state)
        MemoryPending(state, controller)
        if (state.detailLoading) MemoryProgress("Loading the statement and exact source version")
        state.detail?.let { claim ->
            SafeChatText("${claim.subject} · ${claim.predicate}: ${claim.value}", links = false)
            Text(kindLabel(claim.kind))
            claim.provenance?.let { provenance ->
                Text(provenance.reviewOriginLabel())
                provenance.support.forEach { support -> MemoryQuote("Original support · ${support.source_origin} · ${support.trust_class}", support.evidence.quote, "memory-reviewed-support") }
            }
            Text(intervalLabel(claim))
            Text("Recorded ${displayInstant(claim.created_at)}. Recorded time is separate from the validity interval.", style = MaterialTheme.typography.bodySmall)
            if (claim.status == "superseded") Text("A replacement does not erase the earlier interval, including when that replacement starts in the future.")
            MemoryQuote("Exact supporting quote", claim.evidence.quote, "memory-detail-quote")
            if (!state.detailLoading && !state.evidenceVerified) MemoryInfo("Evidence unavailable or unverified", "Refresh the saved statement before using this evidence. Nothing is substituted from a newer source.")
            state.detailSource?.let { source ->
                Text("Original source version ${source.version} · ${sourceTrustLabel(source)}", style = MaterialTheme.typography.titleSmall)
                MemoryQuote("Full original source", source.content, "memory-detail-source")
            }
            if (claim.superseded_by != null) OutlinedButton(onClick = controller::openReplacement, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-replacement")) { Text("View replacement") }
            Button(onClick = controller::beginCorrection,
                enabled = state.writesEnabled && state.evidenceVerified && claim.status == "active" && claim.origin == "user_asserted" && state.pending == null && !state.saving,
                modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-correct")) { Text("Correct with new evidence") }
            TextButton(onClick = { controller.openClaim(claim.id) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh statement") }
            TextButton(onClick = { details = !details }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (details) "Hide evidence details" else "Evidence details") }
            if (details) SafeChatText("Claim: ${claim.id}\nScope: ${claim.scope_id}\nSource version: ${claim.evidence.source_version_id}\nOrigin: ${claim.origin}\nStatus: ${claim.status}\nCode-point span: ${claim.evidence.span_start}–${claim.evidence.span_end}\nSHA-256: ${claim.evidence.content_hash}\nUTC milliseconds: ${claim.valid_from} to ${claim.valid_to ?: "open"}", links = false)
        }
        if (!state.detailLoading && state.detail == null) TextButton(onClick = { controller.back() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Return to memory") }
    }
}

@Composable
private fun MemoryEdit(state: MemoryState, controller: MemoryController) {
    val draft = state.draft
    val correcting = draft.corrects != null
    val focus = LocalFocusManager.current
    val canEdit = state.writesEnabled && state.pending == null && !state.saving
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium).testTag("memory-form"), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        MemoryBack(controller)
        MemoryHeading(if (correcting) "Correct a statement" else "Remember a statement", "You endorse this annotation. A supporting quote does not verify its meaning or grant permissions.")
        Text("Scope: ${state.scopes.items.firstOrNull { it.id == state.scopeId }?.name ?: "Selected private scope"}")
        MemoryFeedback(state)
        MemoryPending(state, controller)
        draft.corrects?.let { old -> MemoryInfo("Earlier value", "${old.subject} · ${old.predicate}: ${old.value}\n${intervalLabel(old)}") }
        if (!correcting) {
            MemoryInput("Subject", draft.subject, "memory-subject", canEdit) { controller.updateDraft(draft.copy(subject = it)) }
            MemoryInput("Predicate", draft.predicate, "memory-predicate", canEdit) { controller.updateDraft(draft.copy(predicate = it)) }
        }
        MemoryInput(if (correcting) "Replacement value" else "Value", draft.value, "memory-value", canEdit) { controller.updateDraft(draft.copy(value = it)) }
        if (!correcting) {
            Text("Kind", style = MaterialTheme.typography.titleMedium)
            Column(Modifier.selectableGroup()) {
                listOf("fact", "preference", "decision").forEach { kind ->
                    MemoryChoice(draft.kind == kind, kindLabel(kind), Modifier.testTag("memory-kind-$kind"), canEdit) { controller.updateDraft(draft.copy(kind = kind)) }
                }
            }
        }
        MemoryInput(if (correcting) "Effective from" else "Valid from (optional)", draft.validFrom, "memory-valid-from", canEdit) { controller.updateDraft(draft.copy(validFrom = it)) }
        MemoryInput("Valid until (optional, exclusive)", draft.validTo, "memory-valid-to", canEdit) { controller.updateDraft(draft.copy(validTo = it)) }
        Text("Use ISO 8601 with a timezone and at most three fractional digits. Blank start uses the source version’s recorded time; a new note gets its recorded time from the server. Blank end leaves the interval open.", style = MaterialTheme.typography.bodySmall)
        Text("Supporting evidence", style = MaterialTheme.typography.titleMedium)
        Row(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            OutlinedButton(onClick = controller::selectNote, enabled = canEdit, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-use-note")) { Text("Write a note") }
            OutlinedButton(onClick = controller::loadSources, enabled = canEdit, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-choose-source")) { Text("Choose user source") }
        }
        if (draft.selectedSource == null) {
            OutlinedTextField(draft.note, { controller.updateDraft(draft.copy(note = it)) }, enabled = canEdit,
                label = { Text("Your supporting statement") }, minLines = 3, maxLines = 10,
                isError = draft.note.codePointCount(0, draft.note.length) > 4000,
                supportingText = { Text("${draft.note.codePointCount(0, draft.note.length)} / 4,000 Unicode characters") },
                modifier = Modifier.fillMaxWidth().testTag("memory-note"))
            Text("The note may be saved even if the later assertion step fails. Recovery reuses its original ID.", style = MaterialTheme.typography.bodySmall)
        } else {
            val source = draft.selectedSource
            Text("Original version ${source.version} · ${sourceTrustLabel(source)}")
            OutlinedTextField(
                value = TextFieldValue(source.content, TextRange(draft.startUtf16, draft.endUtf16)),
                onValueChange = { value -> controller.updateSelection(value.selection.start, value.selection.end) },
                readOnly = true, enabled = canEdit, label = { Text("Select exact supporting text") }, minLines = 6, maxLines = 12,
                modifier = Modifier.fillMaxWidth().testTag("memory-source-selection"),
            )
            Text("Select a nonblank passage from this unchanged source. Emoji and other Unicode characters retain their original boundaries.", style = MaterialTheme.typography.bodySmall)
        }
        state.sourceChoices.items.forEach { source ->
            Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow)) {
                Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text("${sourceTrustLabel(source)} · version ${source.version} · ${displayInstant(source.created_at)}")
                    if (source.trust_class != "user_explicit") Text("Model output or unrecognized source trust cannot support a user assertion.", style = MaterialTheme.typography.bodySmall)
                    OutlinedButton(onClick = { controller.selectSource(source) }, enabled = canEdit && source.trust_class == "user_explicit",
                        modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-select-source-${source.id}")) { Text("Use this user source") }
                }
            }
        }
        if (state.sourceChoices.loading) MemoryProgress("Loading owned source versions")
        if (state.sourceChoices.hasMore && !state.sourceChoices.loading) OutlinedButton(onClick = controller::loadMoreSources, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more sources") }
        // CoreTextField collapses its selection on focus loss; capture the reviewed span first.
        Button(onClick = { controller.preview(); focus.clearFocus() }, enabled = canEdit,
            modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("memory-preview")) { Text("Review before saving") }
    }
}

@Composable
private fun MemoryPreview(state: MemoryState, controller: MemoryController) {
    val preview = state.preview
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium).testTag("memory-preview-screen"), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        MemoryBack(controller)
        MemoryHeading("Review your assertion", "Save explicitly endorses this annotation using the unchanged supporting words below.")
        MemoryFeedback(state)
        MemoryPending(state, controller)
        if (preview != null) {
            WritePreview(preview, state)
            OutlinedButton(onClick = controller::editPreview, enabled = state.pending == null && !state.saving,
                modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-edit-preview")) { Text("Edit before saving") }
            Button(onClick = controller::savePreview, enabled = state.writesEnabled && state.pending == null && !state.saving,
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("memory-save")) { Text("Save assertion") }
        } else Text("No reviewed write is available. Return to your form before saving.")
        if (state.saving) MemoryProgress("Saving the reviewed assertion")
    }
}

@Composable
private fun WritePreview(preview: PendingMemory, state: MemoryState) {
    val write = preview.reservation
    var details by remember(write.claimId) { mutableStateOf(false) }
    val startMillis = write.validFrom?.let { runCatching { java.time.OffsetDateTime.parse(it).toInstant().toEpochMilli() }.getOrNull() } ?: preview.source?.created_at
    val endMillis = write.validTo?.let { runCatching { java.time.OffsetDateTime.parse(it).toInstant().toEpochMilli() }.getOrNull() }
    Text("Scope: ${state.scopes.items.firstOrNull { it.id == write.scopeId }?.name ?: "Original private scope"}")
    write.corrects?.let { old ->
        Text("Previous value", style = MaterialTheme.typography.titleMedium)
        SafeChatText(old.value, links = false)
        Text("Previous interval: ${intervalLabel(old)}", style = MaterialTheme.typography.bodySmall)
        Text("Replacement value", style = MaterialTheme.typography.titleMedium)
    }
    SafeChatText("${write.subject} · ${write.predicate}: ${write.value}", links = false)
    Text(kindLabel(write.kind))
    Text("Effective from: ${write.validFrom ?: preview.source?.created_at?.let(::displayInstant) ?: "New note’s recorded time, assigned by the server"}\nUntil: ${write.validTo ?: "Open interval"} (exclusive)")
    MemoryQuote("Exact supporting quote", write.evidence?.quote ?: write.note?.content.orEmpty(), "memory-preview-quote")
    Text("This is your assertion, not automatic knowledge extraction or model-verified truth.", style = MaterialTheme.typography.bodySmall)
    TextButton(onClick = { details = !details }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (details) "Hide write details" else "Write details") }
    if (details) SafeChatText("Claim: ${write.claimId}\nScope: ${write.scopeId}\nSource: ${write.note?.source_id ?: preview.source?.source_id}\nVersion: ${preview.source?.id ?: "Created by the note step"}\nCorrects: ${write.corrects?.id ?: "New assertion"}\nStart UTC milliseconds: ${startMillis ?: "Assigned when the new note is recorded"}\nEnd UTC milliseconds: ${endMillis ?: "open"}" +
        (write.evidence?.let { "\nCode-point span: ${it.span_start}–${it.span_end}\nSHA-256: ${it.content_hash}" } ?: ""), links = false)
}

@Composable
private fun MemoryPending(state: MemoryState, controller: MemoryController) {
    val pending = state.pending ?: return
    var discard by remember(pending.reservation.claimId) { mutableStateOf(false) }
    MemoryInfo(if (pending.reservation.note != null && pending.source != null) "Note saved; assertion needs checking" else "A saved write needs attention",
        "This write keeps its original scope, IDs and input. The note or assertion may already exist; a lost response does not prove it failed.")
    TextButton(onClick = controller::checkPending, enabled = !state.saving, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-check-pending")) { Text("Check saved write") }
    OutlinedButton(onClick = controller::resumePending, enabled = state.writesEnabled && !state.saving, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-resume-pending")) { Text("Resume with original IDs") }
    TextButton(onClick = { discard = true }, enabled = !state.saving, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-discard-pending")) { Text("Discard local recovery") }
    if (discard) AlertDialog(onDismissRequest = { discard = false }, title = { Text("Discard this local recovery?") },
        text = { Text("The note or assertion may already be saved on the server. This clears only the local recovery record; it deletes no server evidence or history. A new write would use new IDs and may conflict with an existing assertion.") },
        confirmButton = { TextButton(onClick = { discard = false; controller.discardPending() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Discard local record") } },
        dismissButton = { TextButton(onClick = { discard = false }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Keep recovery") } })
}

@Composable
private fun MemoryFeedback(state: MemoryState) {
    val issue = state.validation ?: state.fault?.message()
    if (issue != null) {
        val focus = remember { FocusRequester() }
        LaunchedEffect(issue) { focus.requestFocus() }
        Surface(color = MaterialTheme.colorScheme.errorContainer, contentColor = MaterialTheme.colorScheme.onErrorContainer, shape = MaterialTheme.shapes.medium) {
            Text(issue, style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.fillMaxWidth().padding(AdaSpacing.medium).testTag("memory-error").focusRequester(focus).focusable().semantics { liveRegion = LiveRegionMode.Polite })
        }
    }
    state.notice?.let { notice -> Surface(color = MaterialTheme.colorScheme.secondaryContainer, shape = MaterialTheme.shapes.medium) {
        Text(notice, modifier = Modifier.fillMaxWidth().padding(AdaSpacing.medium).semantics { liveRegion = LiveRegionMode.Polite }, style = MaterialTheme.typography.bodyMedium)
    } }
}

@Composable
private fun MemoryInput(label: String, value: String, tag: String, enabled: Boolean, update: (String) -> Unit) {
    OutlinedTextField(value, update, label = { Text(label) }, enabled = enabled, singleLine = true, modifier = Modifier.fillMaxWidth().testTag(tag))
}

@Composable
private fun MemoryChoice(selected: Boolean, label: String, modifier: Modifier = Modifier, enabled: Boolean = true, choose: () -> Unit) {
    Row(modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).selectable(selected, enabled = enabled, role = Role.RadioButton, onClick = choose).padding(AdaSpacing.small), verticalAlignment = Alignment.CenterVertically) {
        RadioButton(selected, onClick = null, enabled = enabled)
        Text(label, modifier = Modifier.padding(start = AdaSpacing.small), style = MaterialTheme.typography.bodyLarge)
    }
}

@Composable
private fun MemoryHeading(title: String, text: String) {
    Text(title, style = MaterialTheme.typography.headlineMedium, modifier = Modifier.semantics { heading() })
    Text(text, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
}

@Composable
private fun MemoryInfo(title: String, text: String) {
    Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow)) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text(title, style = MaterialTheme.typography.titleSmall)
            SafeChatText(text, links = false)
        }
    }
}

@Composable
private fun MemoryQuote(title: String, quote: String, tag: String) {
    Text(title, style = MaterialTheme.typography.titleSmall)
    Surface(color = MaterialTheme.colorScheme.surfaceContainerHighest, shape = MaterialTheme.shapes.medium) {
        SafeChatText(quote, Modifier.fillMaxWidth().padding(AdaSpacing.medium).testTag(tag).semantics(mergeDescendants = true) {}, links = false)
    }
}

@Composable
private fun MemoryBack(controller: MemoryController) {
    TextButton(onClick = { controller.back() }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-back")) { Text("Back to memory") }
}

@Composable
private fun MemoryProgress(label: String) {
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        LinearProgressIndicator(Modifier.fillMaxWidth().semantics { contentDescription = label })
        Text(label, style = MaterialTheme.typography.bodyMedium)
    }
}

private fun intervalLabel(claim: ClaimDto) = "Valid from ${displayInstant(claim.valid_from)} until ${claim.valid_to?.let(::displayInstant) ?: "open"} (exclusive)"
private fun kindLabel(kind: String) = when (kind) { "fact" -> "Fact"; "preference" -> "Preference"; "decision" -> "Decision"; else -> "Unrecognized kind (read only)" }
private fun sourceTrustLabel(source: SourceVersionDto) = when (source.trust_class) { "user_explicit" -> "User evidence"; "model_generated" -> "Model output"; else -> "Unrecognized source trust" }
