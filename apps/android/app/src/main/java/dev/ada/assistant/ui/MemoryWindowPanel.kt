package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import java.time.OffsetDateTime
import java.time.ZoneId

@Composable
fun MemoryWindowPanel(state: MemoryState, controller: MemoryController) {
    var expanded by remember(state.scopeId) { mutableStateOf(false) }
    var query by remember(state.scopeId) { mutableStateOf("") }
    var expression by remember(state.scopeId) { mutableStateOf("yesterday") }
    var timezone by remember(state.scopeId) { mutableStateOf(ZoneId.systemDefault().id) }
    var reference by remember(state.scopeId) { mutableStateOf(OffsetDateTime.now().withNano(0).toString()) }
    AdaTextButton({ expanded = !expanded }, Modifier.heightIn(min = AdaSpacing.touch).testTag("memory-window-toggle")) { Text("Explore a calendar interval") }
    if (!expanded) return
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Read-only lookup of saved assertions over a whole interval. Nothing is sent to chat or saved as new memory.")
        OutlinedTextField(query, { query = it }, label = { Text("Memory question") }, modifier = Modifier.fillMaxWidth().testTag("window-query"))
        Row {
            listOf("yesterday", "last week").forEach { option ->
                AdaChoiceChip(expression == option, option.replaceFirstChar(Char::titlecase), { expression = option })
            }
        }
        Text("Last week means the previous Monday-to-Monday calendar week.")
        OutlinedTextField(timezone, { timezone = it }, label = { Text("Timezone (IANA name)") }, modifier = Modifier.fillMaxWidth().testTag("window-timezone"))
        OutlinedTextField(reference, { reference = it }, label = { Text("Reference date/time with offset") }, modifier = Modifier.fillMaxWidth().testTag("window-reference"))
        AdaButton({ controller.retrieveWindow(query, expression, timezone, reference) }, enabled = query.isNotBlank() && !state.windowLoading,
            modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("window-search")) { Text("Resolve and find assertions") }
        if (state.windowLoading) AdaLoading("Resolving the memory interval")
        state.window?.let { result ->
            val time = result.resolution
            if (time.state != "resolved") Text(when (time.reason) {
                "timezone_and_reference_required" -> "Enter a timezone and a reference date/time before searching."
                "unknown_timezone" -> "Use a recognized timezone name, such as America/Phoenix."
                "ambiguous_or_missing_local_boundary" -> "This interval starts or ends at a repeated or missing local midnight. Review an explicit dated memory view instead of guessing."
                else -> "Choose Yesterday or Last week and review the timezone/reference date."
            }, Modifier.testTag("window-clarification"))
            else Text("${time.local_start} until ${time.local_end} (end excluded)", Modifier.testTag("window-resolved"))
            Text(result.guidance)
            if (time.state == "resolved" && result.selected.isEmpty()) Text("No exact assertions supplied by this bounded lookup. This does not prove you never recorded them.")
            if (result.candidate_pool_truncated || result.omitted_groups > 0 || result.invalid_groups > 0) Text("Some evidence was omitted. Narrow the question or review memory history; no partial conflicting group was presented.")
            result.selected.forEach { card ->
                Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small)) {
                    Text("${card.subject} · ${card.predicate}: ${card.value}")
                    Text("Valid ${displayInstant(card.valid_from)} until ${card.valid_to?.let(::displayInstant) ?: "open"}")
                    SafeChatText(card.evidence.quote, links = false)
                    if (card.conflict) Text("Different values in this interval need comparison or clarification.")
                    AdaTextButton({ controller.openClaim(card.claim_id) }) { Text("Review source or correct explicitly") }
                } }
            }
        }
    }
}
