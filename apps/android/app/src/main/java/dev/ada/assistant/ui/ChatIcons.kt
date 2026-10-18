package dev.ada.assistant.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import kotlin.math.cos
import kotlin.math.sin

enum class AdaIcon { Back, More, Add, Refresh, Settings, Microphone, Attach, Send, Options, Sources, Close, Stop, Expand }

/** Compact visual controls retain a full native touch target and a spoken action label. */
@Composable fun AdaIconButton(
    icon: AdaIcon,
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    val scheme = MaterialTheme.colorScheme
    val colors = when (icon) {
        AdaIcon.Send -> IconButtonDefaults.iconButtonColors(
            containerColor = scheme.primaryContainer,
            contentColor = scheme.onPrimaryContainer,
            disabledContainerColor = scheme.surfaceContainerHighest,
            disabledContentColor = scheme.onSurface.copy(alpha = .38f),
        )
        AdaIcon.Stop -> IconButtonDefaults.iconButtonColors(
            containerColor = scheme.errorContainer,
            contentColor = scheme.onErrorContainer,
            disabledContainerColor = scheme.surfaceContainerHighest,
            disabledContentColor = scheme.onSurface.copy(alpha = .38f),
        )
        else -> IconButtonDefaults.iconButtonColors()
    }
    IconButton(
        onClick = onClick,
        enabled = enabled,
        colors = colors,
        modifier = modifier.sizeIn(minWidth = 48.dp, minHeight = 48.dp).semantics { contentDescription = label },
    ) { AdaIconGlyph(icon) }
}

/** Code-native, decorative glyph; its enclosing control owns the accessible label. */
@Composable fun AdaIconGlyph(icon: AdaIcon, modifier: Modifier = Modifier) {
    val ink = LocalContentColor.current
    Canvas(modifier.size(24.dp)) {
        val stroke = Stroke(1.8f, cap = StrokeCap.Round, join = StrokeJoin.Round)
        fun line(x1: Float, y1: Float, x2: Float, y2: Float) =
            drawLine(ink, Offset(x1, y1), Offset(x2, y2), strokeWidth = 1.8f, cap = StrokeCap.Round)
        fun path(block: Path.() -> Unit) = drawPath(Path().apply(block), ink, style = stroke)
        withTransform({ scale(size.width / 24f, size.height / 24f, pivot = Offset.Zero) }) {
            when (icon) {
                AdaIcon.Back -> { line(19f, 12f, 5f, 12f); path { moveTo(11f, 6f); lineTo(5f, 12f); lineTo(11f, 18f) } }
                AdaIcon.More -> listOf(5f, 12f, 19f).forEach { drawCircle(ink, 1.6f, Offset(it, 12f)) }
                AdaIcon.Add -> { line(5f, 12f, 19f, 12f); line(12f, 5f, 12f, 19f) }
                AdaIcon.Refresh -> {
                    drawArc(ink, 38f, 292f, false, Offset(4f, 4f), Size(16f, 16f), style = stroke)
                    path { moveTo(15f, 4f); lineTo(19.5f, 4.5f); lineTo(19f, 9f) }
                }
                AdaIcon.Settings -> {
                    drawCircle(ink, 6.2f, Offset(12f, 12f), style = stroke)
                    drawCircle(ink, 2.3f, Offset(12f, 12f), style = stroke)
                    repeat(8) { index ->
                        val angle = index * Math.PI / 4.0
                        line(12f + cos(angle).toFloat() * 6.2f, 12f + sin(angle).toFloat() * 6.2f,
                            12f + cos(angle).toFloat() * 9f, 12f + sin(angle).toFloat() * 9f)
                    }
                }
                AdaIcon.Microphone -> {
                    drawRoundRect(ink, Offset(9f, 3f), Size(6f, 12f), CornerRadius(3f), style = stroke)
                    drawArc(ink, 0f, 180f, false, Offset(5f, 6f), Size(14f, 13f), style = stroke)
                    line(12f, 19f, 12f, 22f); line(8f, 22f, 16f, 22f)
                }
                AdaIcon.Attach -> path {
                    moveTo(8f, 12f); lineTo(14f, 6f); cubicTo(17f, 3f, 22f, 7f, 19f, 10f)
                    lineTo(10f, 19f); cubicTo(6f, 23f, 0f, 17f, 4f, 13f)
                    lineTo(13f, 4f); cubicTo(17f, 0f, 23f, 6f, 20f, 10f)
                }
                AdaIcon.Send -> {
                    path { moveTo(3f, 4f); lineTo(21f, 12f); lineTo(3f, 20f); lineTo(6f, 12f); close() }
                    line(6f, 12f, 15f, 12f)
                }
                AdaIcon.Options -> {
                    line(3f, 7f, 21f, 7f); line(3f, 17f, 21f, 17f)
                    drawCircle(ink, 3f, Offset(8f, 7f)); drawCircle(ink, 3f, Offset(16f, 17f))
                }
                AdaIcon.Sources -> {
                    path { moveTo(5f, 3f); lineTo(15f, 3f); lineTo(20f, 8f); lineTo(20f, 21f); lineTo(5f, 21f); close() }
                    path { moveTo(15f, 3f); lineTo(15f, 8f); lineTo(20f, 8f) }
                    line(9f, 12f, 16f, 12f); line(9f, 16f, 16f, 16f)
                }
                AdaIcon.Close -> { line(6f, 6f, 18f, 18f); line(6f, 18f, 18f, 6f) }
                AdaIcon.Stop -> drawRoundRect(ink, Offset(6f, 6f), Size(12f, 12f), CornerRadius(2f))
                AdaIcon.Expand -> path { moveTo(6f, 9f); lineTo(12f, 15f); lineTo(18f, 9f) }
            }
        }
    }
}
