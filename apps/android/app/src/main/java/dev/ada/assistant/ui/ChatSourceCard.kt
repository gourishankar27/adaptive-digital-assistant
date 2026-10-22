package dev.ada.assistant.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
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
import dev.ada.assistant.data.CitationDto
import dev.ada.assistant.data.reviewOriginLabel
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle
import java.util.UUID

@Composable
fun ChatSourceCard(source: CitationDto, requestId: UUID, modifier: Modifier = Modifier) {
    var details by remember(requestId, source.claim_id) { mutableStateOf(false) }
    Card(
        modifier.fillMaxWidth().testTag("source-card-${source.label}"),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow),
    ) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
            Text("Source [${source.label}]", style = MaterialTheme.typography.titleMedium)
            source.entity?.let { SafeChatText("Explicit entity at this request: ${it.label} · ${it.kind}", links = false) }
            source.provenance?.let { provenance ->
                Text(provenance.reviewOriginLabel())
                provenance.support.forEach { support ->
                    Text("Original support · ${support.source_origin} · ${support.trust_class} · version ${support.source_version}")
                    SafeChatText(support.evidence.quote, links = false)
                }
            }
            Text(
                when (source.origin) { "user_asserted" -> "User assertion · source version ${source.source_version}"; else -> "Unrecognized origin · source version ${source.source_version}" },
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            SafeChatText("${source.subject} · ${source.predicate}: ${source.value}", links = false)
            Surface(color = MaterialTheme.colorScheme.surfaceContainerHighest, shape = MaterialTheme.shapes.medium) {
                Column(Modifier.fillMaxWidth().padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text("Exact source quote", style = MaterialTheme.typography.labelLarge)
                    SafeChatText(source.evidence.quote, Modifier.testTag("source-quote-${source.label}").semantics(mergeDescendants = true) {}, links = false)
                }
            }
            Text("Valid from ${displayInstant(source.valid_from)}", style = MaterialTheme.typography.bodyMedium)
            Text(
                source.valid_to?.let { "Valid until ${displayInstant(it)} (exclusive)" } ?: "No end to the recorded validity interval",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (source.conflict) Text("Other selected assertions have different values. Review the context.", color = MaterialTheme.colorScheme.error)
            Text("A source records provenance. It does not guarantee that an assertion or ADA’s reply is correct.", style = MaterialTheme.typography.bodySmall)
            AdaTextButton(onClick = { details = !details }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) {
                Text(if (details) "Hide source details" else "Source details")
            }
            if (details) {
                SafeChatText(
                    "Request: $requestId\nClaim: ${source.claim_id}\nScope: ${source.scope_id}\n" +
                        "Source: ${source.source_id}\nVersion: ${source.evidence.source_version_id}\n" +
                        "Origin: ${source.origin}\nCode-point span: ${source.evidence.span_start}–${source.evidence.span_end}\n" +
                        "SHA-256: ${source.evidence.content_hash}\n" +
                        "UTC milliseconds: ${source.valid_from} to ${source.valid_to ?: "open"}",
                    links = false,
                )
            }
        }
    }
}

internal fun displayInstant(milliseconds: Long): String = runCatching {
    DateTimeFormatter.ofLocalizedDateTime(FormatStyle.MEDIUM)
        .withZone(ZoneId.systemDefault()).format(Instant.ofEpochMilli(milliseconds))
}.getOrElse { "Outside the local display range; see the original UTC milliseconds in Details" }
