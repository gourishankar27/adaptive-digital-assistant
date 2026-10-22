package dev.ada.assistant.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.semantics
import dev.ada.assistant.data.DocumentCitationDto
import java.util.UUID

@Composable
fun DocumentSourceCard(card: DocumentCitationDto, requestId: UUID) {
    var details by remember(requestId, card.chunk_id) { mutableStateOf(false) }
    Card(Modifier.fillMaxWidth().testTag("source-card-${card.label}")) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text("Source [${card.label}]", style = MaterialTheme.typography.titleMedium)
            Text(if (card.origin == "imported_document" && card.trust_class == "imported_untrusted")
                "Imported document · untrusted evidence · version ${card.source_version}" else "Unrecognized imported evidence", style = MaterialTheme.typography.bodyMedium)
            SafeChatText(card.filename, links = false)
            Text("Lines ${card.line_start}–${card.line_end}", style = MaterialTheme.typography.labelLarge)
            Text("Exact document excerpt", style = MaterialTheme.typography.labelLarge)
            SafeChatText(card.evidence.quote, Modifier.testTag("source-quote-${card.label}").semantics(mergeDescendants = true) {}, links = false)
            Text("Available from ${displayInstant(card.available_from)}", style = MaterialTheme.typography.bodySmall)
            Text(card.available_to?.let { "Available until ${displayInstant(it)} (exclusive)" } ?: "No availability end", style = MaterialTheme.typography.bodySmall)
            Text("Imported text is not a user assertion. Availability describes this version, not whether its statements are true.", style = MaterialTheme.typography.bodySmall)
            AdaTextButton(onClick = { details = !details }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (details) "Hide source details" else "Source details") }
            if (details) SafeChatText("Request: $requestId\nSource: ${card.source_id}\nVersion: ${card.source_version_id}\nUpload: ${card.upload_id}\nChunk: ${card.chunk_id}\nScope: ${card.scope_id}\nOrigin: ${card.origin}\nTrust: ${card.trust_class}\nCode-point span: ${card.evidence.span_start}–${card.evidence.span_end}\nText SHA-256: ${card.evidence.content_hash}\nRaw SHA-256: ${card.raw_hash}\nPublished UTC milliseconds: ${card.published_at}", links = false)
        }
    }
}
