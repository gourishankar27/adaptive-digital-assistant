package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import java.time.Instant
import java.time.ZoneId
import java.util.UUID

@OptIn(ExperimentalLayoutApi::class)
@Composable fun ReflectionScreen(controller: ReflectionController, scopes: List<ScopeDto>, profiles: List<PersonalityDto>, continueConversation: (UUID) -> Unit) {
    val s by controller.state.collectAsStateWithLifecycle()
    var discard by remember { mutableStateOf<ReflectionArtifactDto?>(null) }
    var profile by remember(profiles) { mutableStateOf(profiles.firstOrNull()?.id) }
    discard?.let { row -> AdaConfirmation("Discard this draft?", "The original sources remain saved. Use explicit content deletion to erase evidence.", "Discard", { discard = null }, { controller.action(row, "dismiss"); discard = null }, "reflection-discard") }
    LazyColumn(Modifier.fillMaxSize().testTag("reflection-screen"), contentPadding = PaddingValues(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item {
            AdaSectionHeading("While you were away")
            Text("Optional local drafts from selected material. Review sources and uncertainty before relying on them. These jobs do not learn model weights or accept facts.")
            s.notice?.let { AdaNotice(it) }
            if (s.busy) AdaLoading("Checking reflection")
            AdaOutlinedButton(controller::refresh, Modifier.testTag("reflection-refresh")) { Text("Refresh") }
            s.policy?.let { policy ->
                if (!policy.globally_enabled) AdaNotice("Idle work is stopped by server configuration. Review remains available.")
                if (!policy.scheduling_consent) AdaNotice("Enable separate automation consent in Reminders & inbox before enabling idle reflection.")
                Text("Last decision: ${policy.last_decision?.replace('_', ' ') ?: "No jobs considered"}. ADA idle: ${policy.foreground_idle_seconds}s.")
                if (policy.settings.enabled) AdaOutlinedButton({ controller.save(policy.settings.copy(enabled = false)) }, Modifier.testTag("reflection-off")) { Text("Stop idle reflection") }
                AdaSettingsGroup("Consent and input policy", "reflection-policy") { ReflectionEditor(policy, scopes, controller::save, s.busy) }
            }
        }
        if (s.pending.isNotEmpty()) item { AdaSettingsGroup("Unconfirmed changes", "reflection-pending") { s.pending.forEach { op ->
            Text("Saved change awaiting confirmation")
            AdaTextButton({ controller.check(op) }) { Text("Check saved result") }
            AdaTextButton({ controller.retry(op) }, enabled = !s.busy) { Text("Retry original change") }
        } } }
        item { AdaSettingsGroup("Profile for opening a question", "reflection-profile") { profiles.forEach { row -> AdaChoice(profile == row.id, row.name, { profile = row.id }) } } }
        if (s.artifacts.isEmpty()) item { Text("No review drafts on this page. An empty queue can be a useful result.") }
        items(s.artifacts, key = { it.id }) { row ->
            Surface(shape = MaterialTheme.shapes.medium, color = MaterialTheme.colorScheme.surfaceContainerLow) {
                Column(Modifier.fillMaxWidth().padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    AdaSectionHeading(if (row.kind == "summary") "Generated summary · unendorsed" else if (row.kind == "question") "Optional question draft" else "Selected-material report")
                    Text("Scope: ${scopes.firstOrNull { it.id == row.scope_id }?.name ?: row.scope_id}")
                    Text("${row.state} · ${Instant.ofEpochMilli(row.created_at)} · ${row.elapsed_ms} ms")
                    Text("Reason: ${row.rationale.replace('_', ' ')}")
                    row.model_elapsed_ms?.let { Text("Model wall time: $it ms; GPU time is not measured.") }
                    row.unavailable_reason?.let { AdaNotice("Source or epoch changed. Content is withheld.") }
                    row.content?.let { content ->
                        content.findings?.let { findings -> if (findings.isEmpty()) Text("No useful findings in the selected sources."); findings.forEach { Text(it.text) } }
                        content.question?.let { Text(it.text) }
                        content.summary?.let { summary -> summary.sections.forEach { Text(it.text) }; summary.omissions.forEach { Text("Omitted: $it") } }
                    }
                    Text("Selection omissions: ${row.omissions.entries.joinToString { "${it.key.replace('_', ' ')}: ${it.value}" }}")
                    AdaSettingsGroup("Inspect original sources (${row.sources.size})", "reflection-sources-${row.id}") {
                        row.sources.forEach { source ->
                            Text("${source.source_origin} · ${source.trust_class} · version ${source.source_version}")
                            Text("Source ${source.evidence.source_version_id}")
                            Text("SHA-256: ${source.evidence.content_hash}")
                            Text(source.evidence.quote)
                            source.conversation_id?.let { id -> AdaTextButton({ continueConversation(id) }) { Text("Open source conversation") } }
                        }
                    }
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        if (row.state == "pending" && row.content != null) {
                            if (row.kind == "question") AdaTextButton({ controller.action(row, "open_question", profile) }, enabled = profile != null && !s.busy, modifier = Modifier.testTag("reflection-open-question")) { Text("Open question to answer") }
                            else AdaTextButton({ controller.action(row, "keep") }, enabled = !s.busy, modifier = Modifier.testTag("reflection-keep")) { Text(if (row.kind == "summary") "Keep as generated episode" else "Keep report") }
                        }
                        if (row.state != "dismissed") AdaTextButton({ discard = row }, enabled = !s.busy) { Text("Discard") }
                        row.conversation_id?.let { id -> AdaTextButton({ continueConversation(id) }) { Text("Continue conversation") } }
                    }
                }
            }
        }
        item {
            AdaSettingsGroup("Skipped, cancelled and completed jobs", "reflection-runs") { s.runs.forEach { row -> Text("${row.kind}: ${row.state} · ${row.reason?.replace('_', ' ') ?: "Completed"} · attempt ${row.attempt} · reserved ${row.charged_ms} ms") } }
            FlowRow { AdaTextButton({ controller.page(false) }, enabled = s.offset > 0 && !s.busy) { Text("Previous page") }; AdaTextButton({ controller.page(true) }, enabled = (s.artifacts.size == 100 || s.runs.size == 100) && !s.busy) { Text("Next page") } }
        }
    }
}

@Composable private fun ReflectionEditor(policy: ReflectionPolicyDto, scopes: List<ScopeDto>, save: (ReflectionSettingsDto) -> Unit, busy: Boolean) {
    var draft by remember(policy.revision) { mutableStateOf(policy.settings) }
    var error by remember { mutableStateOf<String?>(null) }
    var invalid by remember(policy.revision) { mutableStateOf(emptySet<String>()) }
    val validity: (String, Boolean) -> Unit = { key, valid -> invalid = if (valid) invalid - key else invalid + key }
    Text("Select up to four owned scopes (${draft.scope_ids.size}/4).")
    scopes.forEach { row -> AdaToggle(row.id in draft.scope_ids, row.name, { checked -> draft = draft.copy(scope_ids = if (checked) (draft.scope_ids + row.id).take(4) else draft.scope_ids - row.id) }) }
    Text("Included sources")
    listOf("user_notes" to "My explicit notes", "imported_documents" to "Imported documents (untrusted)", "completed_user_turns" to "Completed user messages", "completed_model_turns" to "Completed model messages (unendorsed)").forEach { (key, label) ->
        AdaToggle(key in draft.source_types, label, { checked -> draft = draft.copy(source_types = if (checked) draft.source_types + key else draft.source_types - key) })
    }
    AdaToggle(draft.automatic_completed_turns, "Separately allow automatic selection from completed turns", { checked -> draft = draft.copy(automatic_completed_turns = checked, source_types = if (checked) draft.source_types else draft.source_types.filterNot { it.startsWith("completed_") }) })
    listOf("report" to "Reports of owner-marked open items and possible conflicts", "question" to "Optional questions (separate curiosity consent)", "summary" to "Generated episode drafts").forEach { (key, label) ->
        if (key != "summary" || policy.summary_generation) AdaToggle(key in draft.job_kinds, label, { checked -> draft = draft.copy(job_kinds = if (checked) draft.job_kinds + key else draft.job_kinds - key) })
    }
    if (!policy.summary_generation) Text("Model summary generation is disabled until this provider passes cancellation and usefulness verification.")
    OutlinedTextField(draft.timezone, { draft = draft.copy(timezone = it) }, label = { Text("IANA timezone (e.g. America/Phoenix)") }, modifier = Modifier.fillMaxWidth())
    AdaSettingsGroup("Question topic", "reflection-topic") { listOf("interests", "work", "routines", "relationships", "reflection").forEach { topic -> AdaChoice(draft.question_topic == topic, topic.replaceFirstChar { it.uppercase() }, { draft = draft.copy(question_topic = topic) }) } }
    ReflectionNumber("Lookback days (1–30)", draft.lookback_days, validity) { draft = draft.copy(lookback_days = it) }
    ReflectionNumber("Allowed start minute (0–1439)", draft.allowed_start, validity) { draft = draft.copy(allowed_start = it) }
    ReflectionNumber("Allowed end minute (1–1440, exclusive)", draft.allowed_end, validity) { draft = draft.copy(allowed_end = it) }
    ReflectionNumber("Idle seconds (900–86400)", draft.idle_seconds, validity) { draft = draft.copy(idle_seconds = it) }
    ReflectionNumber("Nightly seconds (1–600)", draft.nightly_seconds, validity) { draft = draft.copy(nightly_seconds = it) }
    ReflectionNumber("Maximum jobs per UTC day (1–3)", draft.max_jobs, validity) { draft = draft.copy(max_jobs = it) }
    ReflectionNumber("Unit seconds (1–30)", draft.unit_seconds, validity) { draft = draft.copy(unit_seconds = it) }
    ReflectionNumber("Minimum available memory % (10–90)", draft.minimum_memory_percent, validity) { draft = draft.copy(minimum_memory_percent = it) }
    ReflectionNumber("Minimum disk MiB (1024–102400)", draft.minimum_disk_mib, validity) { draft = draft.copy(minimum_disk_mib = it) }
    ReflectionNumber("Maximum measured temperature °C (40–80)", draft.maximum_thermal_c, validity) { draft = draft.copy(maximum_thermal_c = it) }
    AdaToggle(draft.allow_empty, "Allow an empty queue to do nothing", { draft = draft.copy(allow_empty = it) })
    AdaToggle(draft.enabled, "Consent to idle reflection with these selections", { draft = draft.copy(enabled = it) })
    Text("Allowed hours stay in the selected timezone. Daily job/time caps use UTC. AC power and known fresh measurements are required. Restart waits for ADA inactivity again.")
    error?.let { AdaNotice(it) }
    AdaButton({ try { ZoneId.of(draft.timezone); require(draft.allowed_start < draft.allowed_end && draft.source_types.isNotEmpty() && draft.job_kinds.isNotEmpty()); error = null; save(draft) } catch (_: Exception) { error = "Check timezone, hours, sources and job choices." } }, enabled = !busy && invalid.isEmpty() && (!draft.enabled || policy.scheduling_consent), modifier = Modifier.testTag("reflection-save")) { Text("Save reflection choices") }
}
@Composable private fun ReflectionNumber(label: String, value: Int, validity: (String, Boolean) -> Unit, change: (Int) -> Unit) {
    var text by remember(value) { mutableStateOf(value.toString()) }
    OutlinedTextField(text, { text = it; val parsed = it.toIntOrNull(); validity(label, parsed != null); parsed?.let(change) }, label = { Text(label) }, modifier = Modifier.fillMaxWidth(), singleLine = true, isError = text.toIntOrNull() == null)
}
