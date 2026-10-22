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
    val primary = MaterialTheme.colorScheme.primary
    val text = remember(content, destinations, primary, uriHandler) {
        androidx.compose.ui.text.buildAnnotatedString {
            append(content)
            fencedCodeRanges(content).forEach { range ->
                addStyle(androidx.compose.ui.text.SpanStyle(fontFamily = FontFamily.Monospace), range.first, range.last + 1)
            }
            destinations.forEach { destination ->
                var from = 0
                while (from < content.length) {
                    val start = content.indexOf(destination, from)
                    if (start < 0) break
                    addLink(androidx.compose.ui.text.LinkAnnotation.Url(destination,
                        styles = androidx.compose.ui.text.TextLinkStyles(style = androidx.compose.ui.text.SpanStyle(color = primary, textDecoration = androidx.compose.ui.text.style.TextDecoration.Underline)),
                        linkInteractionListener = { runCatching { uriHandler.openUri(destination) } }), start, start + destination.length)
                    from = start + destination.length
                }
            }
        }
    }
    SelectionContainer(modifier) { Text(text, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.fillMaxWidth()) }

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

/** UTF-16 display spans only; the original text/quotes and API code-point spans never change. */
internal fun fencedCodeRanges(content: String): List<IntRange> {
    val result = mutableListOf<IntRange>()
    var start: Int? = null
    Regex("(?m)^[ \t]{0,3}```[^\r\n]*(?:\r?\n|$)").findAll(content).forEach { match ->
        val opening = start
        if (opening == null) start = match.range.first
        else { result += opening..match.range.last; start = null }
    }
    start?.let { if (it < content.length) result += it..content.lastIndex }
    return result
}
