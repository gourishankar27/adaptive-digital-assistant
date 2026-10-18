package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import kotlinx.serialization.json.*

@Composable
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
fun EntityScreens(controller: EntityController, back: () -> Unit) {
    val s by controller.state.collectAsStateWithLifecycle()
    val focus = LocalFocusManager.current
    var discard by remember { mutableStateOf(false) }
    val editable = s.enabled && !s.busy && s.pending == null
    LazyColumn(Modifier.fillMaxSize().testTag("entities-list"), contentPadding = PaddingValues(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item {
            TextButton(onClick = back, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Back to memory") }
            AdaSectionHeading("Entities")
            Text("Explicit names for people, projects and objects in this scope. Similar names stay separate until you confirm a link or merge.")
            s.fault?.let { Text(it.message(), color = MaterialTheme.colorScheme.error) }
            s.notice?.let { Text(it, modifier = Modifier.testTag("entity-notice")) }
            if (s.busy || s.entities.loading || s.scopes.loading) CircularProgressIndicator()
        }
        if (s.pending != null) item {
            Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.medium)) {
                Text("Saved entity change: ${s.pending!!.action.replace('_', ' ')}", style = MaterialTheme.typography.titleMedium)
                Text("This keeps the original account, scope and exact input. Restoring does not submit it again.")
                OutlinedButton(controller::checkPending, enabled = s.enabled && !s.busy, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("entity-check")) { Text("Check saved operation") }
                OutlinedButton(controller::resumePending, enabled = s.enabled && !s.busy, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("entity-resume")) { Text("Resume identical change") }
                TextButton({ discard = true }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Discard local recovery") }
            } }
        }
        item {
            Text("Owned scope", style = MaterialTheme.typography.titleMedium)
            s.scopes.items.forEach { scope -> Row {
                RadioButton(s.scopeId == scope.id, { controller.selectScope(scope.id) }, enabled = !s.busy)
                TextButton({ controller.selectScope(scope.id) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(scope.name) }
            } }
            if (s.scopes.hasMore) TextButton(controller::moreScopes, enabled = !s.scopes.loading) { Text("More scopes") }
            TextButton(controller::refresh, enabled = s.scopeId != null && !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh") }
        }
        item {
            OutlinedTextField(s.label, controller::label, label = { Text("Name or alias") }, enabled = editable, singleLine = true, modifier = Modifier.fillMaxWidth().testTag("entity-label"))
            FlowRow { listOf("person", "project", "object", "other").forEach { kind -> TextButton({ controller.kind(kind) }, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (s.kind == kind) "$kind selected" else kind) } } }
            OutlinedButton({ focus.clearFocus(); controller.resolve() }, enabled = editable && s.label.isNotBlank(), modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("entity-resolve")) { Text("Check this name") }
            s.resolution?.let { resolution ->
                Text(when (resolution.state) { "absent" -> "No explicit match. Creation will make a separate identity."; "resolved" -> "An explicit match exists. Review it before creating another identity."; "ambiguous" -> "Ambiguous name. Select a person or project explicitly; these identities are separate."; else -> "Unrecognized resolution; review before continuing." }, modifier = Modifier.testTag("entity-resolution"))
                resolution.candidates.forEach { candidate -> TextButton({ controller.resolve(candidate.id) }, enabled = editable, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Choose ${candidate.label} (${candidate.kind})") } }
                if (resolution.truncated) Text("More matches exist. Refine the name or inspect the scoped entity list.")
            }
            Button({ focus.clearFocus(); controller.reviewCreate() }, enabled = editable && s.label.isNotBlank() && s.resolution != null, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("entity-create")) { Text("Review new entity") }
        }
        if (s.entities.items.isEmpty() && !s.entities.loading) item { Text("No entities loaded in this scope.") }
        items(s.entities.items, key = { it.id }) { entity ->
            Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.medium)) {
                TextButton({ controller.selectEntity(entity.id) }, enabled = !s.busy, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("entity-select-${entity.id}")) { Text("${entity.label} · ${entity.kind}${if (entity.redirect_id != null) " · merged" else ""}${if (entity.is_self) " · represents me" else ""}") }
                Text("Created ${displayInstant(entity.created_at)}", style = MaterialTheme.typography.bodySmall)
                var details by remember(entity.id) { mutableStateOf(false) }
                TextButton({ details = !details }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (details) "Hide details" else "Technical details") }
                if (details) SafeChatText("Entity: ${entity.id}\nScope: ${entity.scope_id}\nRedirect: ${entity.redirect_id ?: "none"}\nRevision: ${entity.revision}", links = false)
            } }
        }
        if (s.entities.hasMore) item { TextButton(controller::moreEntities, enabled = !s.entities.loading) { Text("More entities") } }
        s.selected?.let { entity ->
            item {
                Text("Selected: ${entity.label}", style = MaterialTheme.typography.titleMedium, modifier = Modifier.semantics { heading() })
                if (entity.redirect_id == null) {
                    OutlinedButton(controller::reviewAlias, enabled = editable && s.label.isNotBlank(), modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Review added alias") }
                    OutlinedButton(controller::reviewRename, enabled = editable && s.label.isNotBlank(), modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Review rename") }
                    if (entity.kind == "person") OutlinedButton(controller::reviewSelf, enabled = editable, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Review represents me in this scope") }
                } else OutlinedButton(controller::reviewUndo, enabled = editable, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Review undo merge") }
            }
            items(s.aliases, key = { it.id }) { alias -> Column {
                SafeChatText("${alias.label} · ${if (alias.canonical) "canonical name" else "alias"} · ${if (alias.valid_to == null) "current" else "retired"}", links = false)
                if (!alias.canonical && alias.valid_to == null) TextButton({ controller.reviewRetire(alias.id) }, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Review retiring alias") }
            } }
            item { Text("Choose an existing assertion to link its original subject", style = MaterialTheme.typography.titleMedium) }
            items(s.claims.items, key = { it.id }) { claim -> TextButton({ controller.selectClaim(claim.id) }, enabled = !s.busy, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("${if (s.selectedClaim == claim.id) "Selected: " else ""}${claim.subject} · ${claim.predicate}: ${claim.value}") } }
            if (s.claims.hasMore) item { TextButton(controller::moreClaims, enabled = !s.claims.loading) { Text("More assertions") } }
            item {
                OutlinedButton({ controller.reviewLink() }, enabled = editable && s.selectedClaim != null && entity.redirect_id == null, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Review subject link") }
                TextButton({ controller.reviewLink(clear = true) }, enabled = editable && s.claims.items.any { it.id == s.selectedClaim && it.subject_entity_id != null }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Review clearing subject link") }
                Text("Merge with another explicitly selected entity", style = MaterialTheme.typography.titleMedium)
                s.entities.items.filter { it.id != entity.id && it.redirect_id == null && it.kind == entity.kind }.forEach { target -> TextButton({ controller.previewMerge(target.id) }, enabled = editable && entity.redirect_id == null, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Preview merge into ${target.label}") } }
                s.mergePreview?.let { preview ->
                    SafeChatText("${preview.source.label} → ${preview.target.label}\n${preview.alias_count} aliases and ${preview.claim_link_count} claim links affected. ${if (preview.self_binding_affected) "Your explicit self binding is affected." else ""}", links = false)
                    Text("Original names, evidence and saved requests remain. Undo restores the mapping; history records both decisions.")
                    Button(controller::reviewMerge, enabled = editable, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Review this merge") }
                }
            }
        }
    }
    s.preview?.let { pending ->
        val body = adaJson.parseToJsonElement(pending.body) as JsonObject
        val label = body["label"]?.jsonPrimitive?.content
        AlertDialog(onDismissRequest = controller::cancelPreview,
            title = { Text("Confirm ${pending.action.replace('_', ' ')}") },
            text = { Column(Modifier.verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                Text("Scope: ${s.scopes.items.firstOrNull { it.id == pending.scopeId }?.name ?: "original owned scope"}")
                label?.let { SafeChatText("Exact name: $it", links = false) }
                s.selected?.let { Text("Selected entity: ${it.label}") }
                s.claims.items.firstOrNull { it.id == s.selectedClaim }?.let { Text("Original subject: ${it.subject}") }
                Text("This is an explicit identity annotation. It changes no ownership, permissions, original evidence or prior request sources.")
                if (pending.action == "create" && s.resolution?.state != "absent") Text("A matching or ambiguous name already exists. This creates a separate identity.", color = MaterialTheme.colorScheme.error)
            } },
            confirmButton = { TextButton(controller::confirm, enabled = editable, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("entity-confirm")) { Text("Confirm change") } },
            dismissButton = { TextButton(controller::cancelPreview, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Keep editing") } })
    }
    if (discard) AlertDialog(onDismissRequest = { discard = false }, title = { Text("Discard local recovery?") }, text = { Text("Any committed remote change remains. Check its saved operation before knowingly reviewing a new change.") }, confirmButton = { TextButton({ discard = false; controller.discard() }) { Text("Discard local recovery") } }, dismissButton = { TextButton({ discard = false }) { Text("Keep saved change") } })
}
