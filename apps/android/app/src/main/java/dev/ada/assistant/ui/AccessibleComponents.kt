package dev.ada.assistant.ui

import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material3.*
import androidx.compose.material3.Button as MaterialButton
import androidx.compose.material3.OutlinedButton as MaterialOutlinedButton
import androidx.compose.material3.TextButton as MaterialTextButton
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.focusProperties
import androidx.compose.ui.platform.LocalWindowInfo
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.*
import dev.ada.assistant.data.ApiFailure

/** Reserve real layout space, in addition to Material's expanded hit area. */
@Composable fun AdaTextButton(onClick: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true, content: @Composable RowScope.() -> Unit) {
    MaterialTextButton(onClick, modifier.heightIn(min = AdaSpacing.touch), enabled, content = content)
}
@Composable fun AdaButton(onClick: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true, content: @Composable RowScope.() -> Unit) {
    MaterialButton(onClick, modifier.heightIn(min = AdaSpacing.touch), enabled, content = content)
}
@Composable fun AdaOutlinedButton(onClick: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true, content: @Composable RowScope.() -> Unit) {
    MaterialOutlinedButton(onClick, modifier.heightIn(min = AdaSpacing.touch), enabled, content = content)
}

/** Durable, human-readable feedback; no exception names or private error bodies. */
@Composable fun AdaNotice(message: String, modifier: Modifier = Modifier, error: Boolean = false) {
    val focus = remember { FocusRequester() }
    LaunchedEffect(message, error) { if (error) focus.requestFocus() }
    Surface(
        color = if (error) MaterialTheme.colorScheme.errorContainer else MaterialTheme.colorScheme.secondaryContainer,
        contentColor = if (error) MaterialTheme.colorScheme.onErrorContainer else MaterialTheme.colorScheme.onSecondaryContainer,
        shape = MaterialTheme.shapes.medium,
    ) {
        Text(message, style = MaterialTheme.typography.bodyMedium,
            modifier = modifier.fillMaxWidth().padding(AdaSpacing.medium)
                .then(if (error) Modifier.focusRequester(focus).focusable() else Modifier)
                .semantics { liveRegion = LiveRegionMode.Polite })
    }
}

@Composable fun AdaFailureNotice(failure: ApiFailure, modifier: Modifier = Modifier) {
    val message = failure.message() + if (failure is ApiFailure.Busy && failure.retryAfterSeconds != null)
        " Wait at least ${failure.retryAfterSeconds} seconds before retrying." else ""
    AdaNotice(message, modifier, error = true)
}

@Composable fun AdaLoading(label: String, modifier: Modifier = Modifier) {
    Column(modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        LinearProgressIndicator(Modifier.fillMaxWidth().semantics { contentDescription = label })
        Text(label, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.clearAndSetSemantics {})
    }
}

@Composable fun AdaSettingsHeading(title: String) {
    Text(title, style = MaterialTheme.typography.titleMedium, modifier = Modifier.semantics { heading() })
}

@Composable fun AdaSettingsGroup(title: String, tag: String, content: @Composable () -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    Surface(color = MaterialTheme.colorScheme.surfaceContainerLow, shape = MaterialTheme.shapes.medium) {
        Column(Modifier.fillMaxWidth().padding(AdaSpacing.small)) {
            AdaTextButton({ expanded = !expanded }, Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag(tag)
                .semantics { heading(); stateDescription = if (expanded) "Expanded" else "Collapsed" }) {
                Text(title, Modifier.weight(1f), style = MaterialTheme.typography.titleMedium)
                AdaIconGlyph(if (expanded) AdaIcon.Close else AdaIcon.Expand)
            }
            if (expanded) Column(Modifier.padding(AdaSpacing.small), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) { content() }
        }
    }
}

@Composable fun AdaChoice(selected: Boolean, label: String, onClick: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true) {
    Row(modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)
        .selectable(selected, enabled = enabled, role = Role.RadioButton, onClick = onClick)
        .padding(AdaSpacing.small), verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        RadioButton(selected, onClick = null, enabled = enabled)
        Text(label, style = MaterialTheme.typography.bodyLarge)
    }
}

@Composable fun AdaChoiceChip(selected: Boolean, label: String, onClick: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true) {
    FilterChip(selected, onClick, label = { Text(label) }, enabled = enabled,
        modifier = modifier.heightIn(min = AdaSpacing.touch).semantics { role = Role.RadioButton })
}

@Composable fun AdaToggle(checked: Boolean, label: String, change: (Boolean) -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true, switch: Boolean = false) {
    Row(modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)
        .toggleable(checked, enabled = enabled, role = if (switch) Role.Switch else Role.Checkbox, onValueChange = change),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        if (switch) Switch(checked, onCheckedChange = null, enabled = enabled)
        else Checkbox(checked, onCheckedChange = null, enabled = enabled)
        Text(label, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable fun AdaTechnicalDetails(text: String) {
    var expanded by remember { mutableStateOf(false) }
    AdaTextButton({ expanded = !expanded }, Modifier.heightIn(min = AdaSpacing.touch).semantics { stateDescription = if (expanded) "Expanded" else "Collapsed" }) {
        Text(if (expanded) "Hide technical details" else "Show technical details")
    }
    if (expanded) SafeChatText(text, links = false)
}

@Composable fun AdaConfirmation(title: String, explanation: String, confirmLabel: String, dismiss: () -> Unit, confirm: () -> Unit, tag: String) {
    val cancelFocus = remember { FocusRequester() }
    AlertDialog(onDismissRequest = dismiss, modifier = Modifier.testTag("$tag-dialog"),
        title = { Text(title) }, text = { Text(explanation) },
        confirmButton = { AdaTextButton(confirm, Modifier.heightIn(min = AdaSpacing.touch).testTag("$tag-confirm")) { Text(confirmLabel) } },
        dismissButton = {
            val focusedWindow = LocalWindowInfo.current.isWindowFocused
            LaunchedEffect(focusedWindow) {
                if (focusedWindow) { withFrameNanos {}; cancelFocus.requestFocus() }
            }
            AdaTextButton(dismiss, Modifier.heightIn(min = AdaSpacing.touch).focusProperties { canFocus = true }
                .focusRequester(cancelFocus).testTag("$tag-cancel")) { Text("Cancel") }
        })
}
