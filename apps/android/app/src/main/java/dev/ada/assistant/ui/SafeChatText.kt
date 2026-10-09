package dev.ada.assistant.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import java.net.URI

/** Text stays text: no HTML, script execution, command actions or remote previews. */
@Composable
fun SafeChatText(content: String, modifier: Modifier = Modifier, links: Boolean = true) {
    val uriHandler = LocalUriHandler.current
    val destinations = remember(content, links) { if (links) safeChatLinks(content) else emptyList() }
    Column(modifier, verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        SelectionContainer {
            Text(
                content,
                style = MaterialTheme.typography.bodyLarge,
                // Fenced code remains selectable literal text, including its original delimiters.
                fontFamily = if (content.startsWith("```")) FontFamily.Monospace else null,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        destinations.forEach { destination ->
            val host = remember(destination) { URI(destination).host }
            TextButton(
                onClick = { runCatching { uriHandler.openUri(destination) } },
                modifier = Modifier.heightIn(min = AdaSpacing.touch).semantics {
                    contentDescription = "Open external link to $host in your browser"
                },
            ) { Text("Open link to $host") }
        }
    }
}

/** Only explicit user clicks open HTTP(S) destinations; embedded credentials are rejected. */
internal fun safeChatLinks(content: String): List<String> =
    Regex("https?://[^\\s<>]+", RegexOption.IGNORE_CASE).findAll(content)
        .map { it.value.trimEnd('.', ',', ';', ')', ']', '}', '"', '\'') }
        .filter { candidate ->
            runCatching {
                val uri = URI(candidate)
                uri.scheme.lowercase() in setOf("https", "http") &&
                    !uri.host.isNullOrBlank() && uri.userInfo == null &&
                    candidate.none { it.isISOControl() }
            }.getOrDefault(false)
        }.distinct().take(8).toList()
