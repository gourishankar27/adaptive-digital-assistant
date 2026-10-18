package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import dev.ada.assistant.data.ConversationDto

@Composable fun ResearchScreen(controller: ResearchController, conversation: ConversationDto?) {
    val s by controller.state.collectAsState()
    var confirm by remember { mutableStateOf(false) }
    if (confirm) AlertDialog(onDismissRequest = { confirm = false }, title = { Text("Approve this outgoing request?") },
        text = { Column(Modifier.verticalScroll(rememberScrollState())) {
            val preview = s.run?.calls?.lastOrNull()?.preview
            Text(preview?.disclosure ?: "Review the exact request first.")
            Text(preview?.url ?: "")
            Text("Headers: ${preview?.headers}")
        } }, confirmButton = { TextButton({ confirm = false; controller.approve() }) { Text("Approve this request only") } },
        dismissButton = { TextButton({ confirm = false }) { Text("Keep reviewing") } })
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Public research", style = MaterialTheme.typography.titleLarge)
        Text("Research uses the exact public query or URL you approve. Saved memory, chat history and files are not attached. Search snippets are not read pages.")
        s.notice?.let { Text(it, Modifier.testTag("research-notice")) }
        if (s.busy) LinearProgressIndicator(Modifier.fillMaxWidth())
        if (s.journal == null) {
            if (!s.enabled) Text("The server has not enabled an isolated web broker.")
            else {
                OutlinedTextField(s.question, { controller.edit(it, s.target, s.kind) }, label = { Text("Public research question") }, modifier = Modifier.fillMaxWidth().testTag("research-question"))
                Row {
                    TextButton({ controller.edit(s.question, s.target, "fetch") }) { Text("Public page URL${if (s.kind == "fetch") " (selected)" else ""}") }
                    if (s.searchEnabled) TextButton({ controller.edit(s.question, s.target, "search") }) { Text("Wikipedia search${if (s.kind == "search") " (selected)" else ""}") }
                }
                Text("Pilot: static Python documentation and English Wikipedia. Every page and redirect needs a separate approval; at most three outbound calls.")
                OutlinedTextField(s.target, { controller.edit(s.question, it, s.kind) }, label = { Text(if (s.kind == "fetch") "Exact HTTPS page URL" else "Exact outgoing search query") }, modifier = Modifier.fillMaxWidth().testTag("research-target"))
                Button({ conversation?.let(controller::start) }, enabled = conversation != null && !s.busy && s.question.isNotBlank() && s.target.isNotBlank(), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("research-preview")) { Text("Create preview without fetching") }
            }
        } else {
            TextButton(controller::refresh, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Check saved research") }
            if (s.journal?.operation != null || s.run == null) TextButton(controller::retry, enabled = !s.busy) { Text("Retry saved delivery explicitly") }
            s.run?.let { run ->
                Text("State: ${run.state}", Modifier.testTag("research-state"))
                Text(run.question)
                run.calls.forEach { call -> Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small)) {
                    Text("${call.preview.kind} · ${call.preview.recipient}")
                    Text(call.preview.url)
                    Text(call.preview.disclosure)
                    Text("GET · ${call.preview.max_bytes} bytes · ${call.preview.deadline_seconds} seconds network I/O · expires ${displayInstant(call.preview.expires_at)}")
                    Text("Outgoing headers: ${call.preview.headers}")
                    if (call.status == "pending_approval" && run.state == "pending_approval") Button({ confirm = true }, enabled = !s.busy && s.journal?.operation == null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("research-approve")) { Text("Review and approve") }
                    call.receipt?.let { receipt ->
                        Text("Receipt: ${receipt.state}")
                        receipt.redirect_url?.let { url -> Text(url); TextButton({ controller.next(url) }, enabled = !s.busy && run.remaining_calls > 0 && s.journal?.operation == null) { Text("Create new redirect preview") } }
                        receipt.snippets.forEach { item ->
                            Text(item.title); SafeChatText(item.snippet, links = false)
                            TextButton({ controller.next(item.url) }, enabled = !s.busy && run.remaining_calls > 0 && run.state != "completed" && s.journal?.operation == null) { Text("Preview this page separately") }
                        }
                    }
                } } }
                if (run.state in setOf("ready", "blocked", "partial") && run.citations.isNotEmpty()) Button(controller::answer, enabled = !s.busy && s.journal?.operation == null, modifier = Modifier.testTag("research-answer")) { Text("Answer from saved web evidence") }
                run.response?.let { SafeChatText(it, links = false) }
                if (run.citation_warnings.isNotEmpty()) Text("The generated answer used unknown citation labels. Check the exact saved sources.")
                run.citations.forEach { card -> Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small)) {
                    Text("[${card.label}] Untrusted public web · fetched ${displayInstant(card.retrieved_at)}")
                    Text(card.final_url); SafeChatText(card.evidence.quote, links = false)
                    Text(card.terms["license"] ?: "Review source terms")
                    if (card.extraction_truncated) Text("Only a bounded portion of extracted page text was retained.")
                    TextButton({ controller.source(card) }, enabled = !s.busy) { Text("Inspect exact saved source") }
                } } }
                if (run.state == "completed") OutlinedButton(controller::saveNote, enabled = !s.busy && s.journal?.operation == null) { Text("Save imported research note") }
                else if (run.state != "cancelled") TextButton(controller::cancel, enabled = !s.cancelling) { Text(if (s.journal?.cancelRequested == true) "Retry saved cancel" else "Cancel research") }
                Text("To edit a pending outgoing request, cancel it, close this local view and create a fresh preview. Cancellation cannot undo a request already sent.")
            }
            s.source?.let { Text("Verified snapshot (no refetch)"); SafeChatText(it.text, links = false) }
            TextButton(controller::close, enabled = !s.busy && s.journal?.operation == null && s.run?.state in setOf("completed", "cancelled")) { Text("Close local research view") }
        }
    }
}
