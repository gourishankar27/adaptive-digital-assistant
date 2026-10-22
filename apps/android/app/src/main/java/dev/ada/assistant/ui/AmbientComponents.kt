package dev.ada.assistant.ui

import android.animation.ValueAnimator
import android.database.ContentObserver
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import androidx.compose.animation.core.*
import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.boundsInWindow
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.*
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import dev.ada.assistant.data.ApiFailure
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

enum class AdaPresenceState(val label: String) {
    Idle("Idle"), Listening("Listening"), Thinking("Processing"), Speaking("Speaking"),
    Acting("Running a task"), Unconfirmed("Waiting for confirmation"), Offline("Server unavailable"), Error("Needs attention")
}

/** Presentation only: unknown delivery is never presented as confirmed model execution. */
fun adaPresenceState(chat: ChatState, voice: VoiceState = VoiceState(), acting: Boolean = false): AdaPresenceState = when {
    voice.playing -> AdaPresenceState.Speaking
    voice.phase == VoicePhase.Recording -> AdaPresenceState.Listening
    chat.fault in setOf(ApiFailure.Unreachable, ApiFailure.Dns, ApiFailure.ServerNotReady) -> AdaPresenceState.Offline
    chat.fault != null || voice.phase in setOf(VoicePhase.Error, VoicePhase.Denied) -> AdaPresenceState.Error
    chat.pending?.phase in setOf(PendingPhase.Failed, PendingPhase.Conflict, PendingPhase.Blocked) -> AdaPresenceState.Error
    acting -> AdaPresenceState.Acting
    voice.phase == VoicePhase.Transcribing || chat.pending?.phase == PendingPhase.Running -> AdaPresenceState.Thinking
    chat.connecting || chat.pending != null || voice.playbackLoading -> AdaPresenceState.Unconfirmed
    else -> AdaPresenceState.Idle
}

@Composable
fun AdaBackground(modifier: Modifier = Modifier, quiet: Boolean = false, content: @Composable BoxScope.() -> Unit) {
    val colors = MaterialTheme.colorScheme
    val visuals = LocalAdaVisuals.current
    Box(modifier.fillMaxSize().background(colors.background).drawBehind {
        val strength = if (quiet) .045f else .10f
        drawRect(Brush.radialGradient(listOf(colors.primary.copy(alpha = strength), Color.Transparent), center = Offset(size.width * .1f, 0f), radius = size.maxDimension * .8f))
        if (!quiet) drawRect(Brush.radialGradient(listOf(visuals.listening.copy(alpha = .035f), Color.Transparent), center = Offset(size.width, size.height * .55f), radius = size.maxDimension * .65f))
    }, content = content)
}

/** A single owner of safe system insets; the background alone reaches the screen edges. */
@Composable
fun AdaAppFrame(content: @Composable () -> Unit) {
    AdaBackground(quiet = true) {
        Scaffold(containerColor = Color.Transparent, contentColor = MaterialTheme.colorScheme.onBackground, contentWindowInsets = WindowInsets.safeDrawing) { insets ->
            Box(Modifier.fillMaxSize().padding(insets).consumeWindowInsets(insets)) { content() }
        }
    }
}

@Composable
fun AdaGlassSurface(modifier: Modifier = Modifier, boundary: Boolean = false, content: @Composable () -> Unit) {
    val visuals = LocalAdaVisuals.current
    Surface(modifier, shape = MaterialTheme.shapes.large, color = visuals.glass,
        contentColor = MaterialTheme.colorScheme.onSurface, border = BorderStroke(AdaLayout.border, if (boundary) MaterialTheme.colorScheme.outline else visuals.edge), content = content)
}

@Composable
private fun ambientMotionAllowed(): Boolean {
    val context = LocalContext.current
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    var active by remember(lifecycle) { mutableStateOf(lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) }
    var enabled by remember(context) { mutableStateOf(ValueAnimator.areAnimatorsEnabled()) }
    DisposableEffect(context, lifecycle) {
        val listener = LifecycleEventObserver { _, _ -> active = lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED) }
        val observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
            override fun onChange(selfChange: Boolean) { enabled = ValueAnimator.areAnimatorsEnabled() }
        }
        lifecycle.addObserver(listener)
        context.contentResolver.registerContentObserver(Settings.Global.getUriFor(Settings.Global.ANIMATOR_DURATION_SCALE), false, observer)
        onDispose { lifecycle.removeObserver(listener); context.contentResolver.unregisterContentObserver(observer) }
    }
    return active && enabled && LocalAdaMotionEnabled.current
}

/** Vector light and orbit. No bitmap, blur, waveform or invented audio-amplitude signal. */
@Composable
fun AdaPresence(state: AdaPresenceState, modifier: Modifier = Modifier, motion: Boolean = true, describe: Boolean = true) {
    val colors = MaterialTheme.colorScheme
    val visuals = LocalAdaVisuals.current
    val reduced = state in setOf(AdaPresenceState.Offline, AdaPresenceState.Error, AdaPresenceState.Unconfirmed)
    val view = LocalView.current
    var onScreen by remember { mutableStateOf(false) }
    val animate = motion && onScreen && ambientMotionAllowed() && !reduced
    var breath = 0f
    var orbit = 0f
    if (animate) {
        val transition = rememberInfiniteTransition(label = "ADA presence")
        val pulse by transition.animateFloat(0f, 1f, infiniteRepeatable(tween(AdaMotion.breathing, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "Presence breathing")
        breath = pulse
        if (state in setOf(AdaPresenceState.Thinking, AdaPresenceState.Acting)) {
            val angle by transition.animateFloat(0f, 360f, infiniteRepeatable(tween(AdaMotion.orbit, easing = LinearEasing)), label = "Task orbit")
            orbit = angle
        }
    }
    val targetAccent = when (state) {
        AdaPresenceState.Listening -> visuals.listening
        AdaPresenceState.Speaking -> visuals.warmth
        AdaPresenceState.Offline, AdaPresenceState.Error, AdaPresenceState.Unconfirmed -> colors.onSurfaceVariant
        else -> colors.primary
    }
    val accent = if (animate) {
        val eased by animateColorAsState(targetAccent, tween(AdaMotion.transition), label = "Presence light")
        eased
    } else targetAccent
    val semantics = if (describe) Modifier.semantics { contentDescription = "ADA presence"; stateDescription = state.label } else Modifier.clearAndSetSemantics { }
    Canvas(modifier.aspectRatio(1f).onGloballyPositioned { coordinates ->
        val bounds = coordinates.boundsInWindow()
        onScreen = bounds.width > 0 && bounds.height > 0 && bounds.bottom > 0 && bounds.top < view.height && bounds.right > 0 && bounds.left < view.width
    }.then(semantics).testTag("ada-presence-${state.name}")) {
        val radius = size.minDimension * (.27f + breath * if (state == AdaPresenceState.Listening) .018f else .007f)
        drawCircle(Brush.radialGradient(listOf(accent.copy(alpha = if (reduced) .08f else .18f), Color.Transparent), radius = size.minDimension * .49f))
        rotate(orbit + -24f) {
            drawOval(accent.copy(alpha = .30f), topLeft = Offset(size.width * .09f, size.height * .34f), size = Size(size.width * .82f, size.height * .32f), style = Stroke(1.dp.toPx()))
        }
        drawCircle(Brush.radialGradient(listOf(accent.copy(alpha = .78f), colors.primary.copy(alpha = .42f), colors.surface), center = center - Offset(radius * .38f, radius * .44f), radius = radius * 1.8f), radius = radius)
        drawCircle(accent.copy(alpha = .4f), radius, style = Stroke(.75.dp.toPx()))
        drawArc(colors.onSurface.copy(alpha = .32f), 205f, 90f, false, topLeft = center - Offset(radius * .78f, radius * .78f), size = Size(radius * 1.56f, radius * 1.56f), style = Stroke(1.dp.toPx()))
        val angle = (orbit + 22f) * PI / 180
        drawCircle(visuals.listening.copy(alpha = if (reduced) .25f else .8f), radius = 2.dp.toPx(), center = center + Offset((cos(angle) * radius * 1.38f).toFloat(), (sin(angle) * radius * .62f).toFloat()))
    }
}

@Composable
fun AdaPresenceHeading(title: String, explanation: String, state: AdaPresenceState = AdaPresenceState.Idle, compact: Boolean = false) {
    Column(Modifier.fillMaxWidth().padding(vertical = AdaSpacing.medium), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        AdaPresence(state, Modifier.size(if (compact) AdaLayout.presence else AdaLayout.orb))
        Text(title, style = MaterialTheme.typography.headlineMedium, modifier = Modifier.semantics { heading() })
        Text(explanation, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

/** Assistant reading stays unboxed; only owner messages use a quiet, tinted surface. */
@Composable
fun AdaMessageSurface(user: Boolean, modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier.fillMaxWidth(), horizontalAlignment = if (user) Alignment.End else Alignment.Start) {
        Surface(Modifier.widthIn(max = AdaLayout.reading).fillMaxWidth(if (user) .94f else 1f),
            shape = MaterialTheme.shapes.medium,
            color = if (user) MaterialTheme.colorScheme.primaryContainer.copy(alpha = .65f) else Color.Transparent,
            contentColor = MaterialTheme.colorScheme.onSurface) {
            Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small), content = content)
        }
    }
}

@Composable
fun AdaSectionHeading(title: String, explanation: String? = null) {
    Column(Modifier.padding(vertical = AdaSpacing.small), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text(title, style = MaterialTheme.typography.headlineMedium, modifier = Modifier.semantics { heading() })
        explanation?.let { Text(it, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant) }
    }
}
