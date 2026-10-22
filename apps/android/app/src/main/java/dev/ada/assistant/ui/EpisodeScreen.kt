package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import java.time.Instant
import java.util.UUID

@Composable fun EpisodeScreen(controller: EpisodeController, conversation: ConversationDto?, scopeName: String? = null) {
    val s by controller.state.collectAsStateWithLifecycle()
    var discard by remember { mutableStateOf(false) }
    var activatedConversation by remember { mutableStateOf<UUID?>(null) }
    LaunchedEffect(conversation?.id, s.enabled, s.busy) {
        if (s.enabled && !s.busy && activatedConversation != conversation?.id) {
            activatedConversation = conversation?.id
            controller.activate(conversation)
        }
    }
    LazyColumn(Modifier.fillMaxSize().testTag("episode-list"), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item { AdaSectionHeading("History & episodes")
            Text("Generated summaries help you navigate. They are interpretations, not remembered truth. Facts still need original evidence.")
            Text(if (conversation == null) "Open a conversation to choose its scope." else "Scope: ${scopeName ?: "Saved conversation scope"}")
            if (s.busy) AdaLoading("Checking summaries and jobs")
            s.fault?.let { AdaFailureNotice(it) }
            s.notice?.let { AdaNotice(it) }
            AdaOutlinedButton(controller::refresh, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("episode-refresh")) { Text("Refresh episodes and jobs") }
        }
        s.journal?.let { p -> item {
            Text("Saved submission", style = MaterialTheme.typography.titleMedium)
            Text("Server: ${p.identity.server}")
            AdaTechnicalDetails("Saved scope: ${p.scopeId}\nJob: ${s.job?.id}\nKind: ${s.previewKind ?: s.job?.kind}\nState: ${s.job?.status}\nCreated UTC milliseconds: ${s.job?.created_at}")
            s.job?.let { j -> Text("${jobLabel(j.kind).replaceFirstChar(Char::titlecase)}: ${statusLabel(j.status)} · attempt ${j.attempt}/3", Modifier.testTag("episode-job-state"))
                Text("Created: ${displayInstant(j.created_at)}\nStarted: ${j.started_at?.let(::displayInstant) ?: "Not started"}\nFinished: ${j.finished_at?.let(::displayInstant) ?: "Not finished"}\nAttempt elapsed: ${j.elapsed_ms?.let { "$it ms" } ?: "Not recorded"}") }
            if (s.job == null) Text("Outcome unconfirmed. Check before retrying the exact same submission.")
            AdaOutlinedButton(controller::retry, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("episode-retry")) { Text("Retry identical submission") }
            AdaTextButton({ discard = true }, enabled = !s.busy) { Text("Discard local reservation") }
        } }
        if (s.journal == null) {
            item { Text("Select up to four complete messages", style = MaterialTheme.typography.titleMedium)
                Text("First 50 events in this conversation; completed requests only. No message is silently shortened.")
                if (s.events.isEmpty()) Text("No completed messages available for selection.") }
            items(s.events, key = { it.id }) { event -> Card { Row(Modifier.padding(8.dp)) {
                Checkbox(event.id in s.selected, { controller.toggle(event.id) }, enabled = !s.busy,
                    modifier = Modifier.semantics { contentDescription = "Select ${event.role} message ${s.events.indexOf(event) + 1}" }.testTag("episode-event-${event.role}"))
                Column(Modifier.weight(1f)) { Text("${event.role} · ${event.trust_class}"); SelectionContainer { Text(event.content) } }
            } } }
            item { AdaButton({ controller.preview("episode") }, enabled = s.canGenerate && !s.busy && s.selected.isNotEmpty(), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("episode-preview")) { Text("Preview summary job") }
                AdaOutlinedButton({ controller.preview("proposals") }, enabled = s.canGenerate && !s.busy && s.selected.isNotEmpty()) { Text("Preview memory suggestion job") }
                AdaOutlinedButton({ controller.preview("lexical_rebuild") }, enabled = s.enabled && !s.busy) { Text("Preview search index rebuild") }
                if (!s.canGenerate) Text("Summary generation is unavailable on this server. Existing episodes remain readable.") }
        }
        item { Text("Episodes in this scope", style = MaterialTheme.typography.titleMedium); if (s.episodes.isEmpty()) Text("No published episodes on this page.") }
        items(s.episodes, key = { it.id }) { ep -> Card { Column(Modifier.padding(AdaSpacing.medium)) {
            Text("Generated summary · ${ep.tags.joinToString(", ")}")
            Text("${displayInstant(ep.range_start)} to ${displayInstant(ep.range_end)} (end excluded)")
            AdaButton({ controller.open(ep) }, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("episode-open")) { Text("Read summary and original sources") }
        } } }
        s.episode?.let { ep -> item { Card { Column(Modifier.padding(AdaSpacing.medium)) {
            Text("Generated interpretation", style = MaterialTheme.typography.titleMedium)
            Text("${ep.summary_version} · ${ep.model}")
            ep.sections.forEach { section -> SelectionContainer { Text(section.text) }; Text(section.support.joinToString("; ") { pin -> "[S${ep.sources.indexOfFirst { it.evidence.source_version_id == pin.source_version_id } + 1}] code points ${pin.span_start}–${pin.span_end}" }) }
            ep.omissions.forEach { Text("Omission: $it") }
            ep.sources.forEachIndexed { index, src -> HorizontalDivider(); Text("[S${index + 1}] Original ${src.source_origin} · ${src.trust_class}")
                SelectionContainer { Text(src.evidence.quote) }
                AdaOutlinedButton({ controller.original(src) }, enabled = !s.busy) { Text("Open exact original version") }
            }
        } } } }
        s.original?.let { source -> item { SelectionContainer { Text(source.content) } } }
        item { Text("Maintenance jobs in this scope", style = MaterialTheme.typography.titleMedium)
            if (s.jobs.isEmpty()) Text("No jobs on this page.") }
        items(s.jobs, key = { it.id }) { j -> Text("${jobLabel(j.kind).replaceFirstChar(Char::titlecase)}: ${statusLabel(j.status)} · attempt ${j.attempt}\nCreated ${displayInstant(j.created_at)} · elapsed ${j.elapsed_ms?.let { "$it ms" } ?: "Not recorded"}") }
        item { Row { AdaOutlinedButton({ controller.page(-1) }, enabled = !s.busy && s.offset > 0) { Text("Previous page") }
            AdaOutlinedButton({ controller.page(1) }, enabled = !s.busy && (s.episodes.size == 25 || s.jobs.size == 25)) { Text("Next page") } } }
    }
    if (s.preview != null) AlertDialog(onDismissRequest = controller::dismissPreview,
        title = { Text("Queue ${jobLabel(s.previewKind)}?") }, text = { Column(Modifier.heightIn(max = 300.dp).verticalScroll(rememberScrollState())) {
            Text("Scope: ${s.scopeId}\nThis explicit job creates generated content or pending suggestions. It cannot endorse memory, delete evidence or rewrite chat.")
            s.preview!!.forEach { Text("${it.trust_class}: ${it.content}") }
        } }, confirmButton = { AdaTextButton(controller::queue, enabled = !s.busy, modifier = Modifier.testTag("episode-queue")) { Text("Queue job") } }, dismissButton = { AdaTextButton(controller::dismissPreview) { Text("Back") } })
    if (discard) AlertDialog(onDismissRequest = { discard = false }, title = { Text("Discard local reservation?") }, text = { Text("This removes only recovery on this device. A queued or running server job continues; evidence and results are retained.") }, confirmButton = { AdaTextButton({ discard = false; controller.discard() }) { Text("Discard local reservation") } }, dismissButton = { AdaTextButton({ discard = false }) { Text("Keep reservation") } })
}
