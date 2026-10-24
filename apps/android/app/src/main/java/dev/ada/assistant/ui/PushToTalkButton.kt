package dev.ada.assistant.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.waitForUpOrCancellation
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ripple
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.PointerInputChange
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics

/** Tap/keyboard/TalkBack open controls; only a physical held press owns capture. */
@Composable fun PushToTalkButton(
    onClick: () -> Unit,
    onHold: () -> Long?,
    onRelease: (Long, Boolean) -> Unit,
    recording: Boolean,
    modifier: Modifier = Modifier,
) {
    val interactions = remember { MutableInteractionSource() }
    val release by rememberUpdatedState(onRelease)
    val click by rememberUpdatedState(onClick)
    val hold by rememberUpdatedState(onHold)
    val colors = MaterialTheme.colorScheme
    CompositionLocalProvider(LocalContentColor provides if (recording) colors.onErrorContainer else colors.onSurfaceVariant) {
        Box(modifier.size(AdaSpacing.touch).clip(CircleShape)
            .background(if (recording) colors.errorContainer else colors.surface.copy(alpha = 0f))
            .combinedClickable(
                interactionSource = interactions, indication = ripple(), role = Role.Button,
                onClickLabel = if (recording) "Stop recording" else "Open voice controls", onClick = { click() },
                onLongClickLabel = "Hold to talk, release to finish",
                // Keyboard/accessibility have no physical Up event: use tap controls.
                onLongClick = { click() },
            ).pointerInput(Unit) {
                // combinedClickable's long-press completion does not distinguish
                // ACTION_CANCEL from Up. Own the physical sequence explicitly.
                awaitEachGesture {
                    awaitFirstDown().consume()
                    val early = withTimeoutOrNull(viewConfiguration.longPressTimeoutMillis) {
                        PressEnd(waitForUpOrCancellation())
                    }
                    if (early != null) {
                        early.up?.let { it.consume(); click() }
                    } else {
                        val key = hold()
                        var released = false
                        try {
                            val up = waitForUpOrCancellation()
                            released = up != null
                            up?.consume()
                        } finally {
                            key?.let { release(it, !released) }
                        }
                    }
                }
            }.semantics { contentDescription = if (recording) "Stop recording" else "Voice controls" },
            contentAlignment = Alignment.Center,
        ) { AdaIconGlyph(if (recording) AdaIcon.Stop else AdaIcon.Microphone) }
    }
}

private data class PressEnd(val up: PointerInputChange?)
