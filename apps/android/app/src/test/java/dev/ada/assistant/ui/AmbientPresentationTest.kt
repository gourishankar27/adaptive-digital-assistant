package dev.ada.assistant.ui

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import dev.ada.assistant.data.ApiFailure
import dev.ada.assistant.data.PendingMessage
import dev.ada.assistant.data.ChatInputDto
import dev.ada.assistant.data.SessionIdentity
import java.util.UUID
import org.junit.Assert.*
import org.junit.Test

class AmbientPresentationTest {
    private fun contrast(a: Color, b: Color): Float {
        val first = a.luminance(); val second = b.luminance()
        return (maxOf(first, second) + .05f) / (minOf(first, second) + .05f)
    }
    @Test fun allPalettesKeepReadableTextAndControlContrastInBothModes() {
        ThemePalette.entries.forEach { palette -> listOf(false, true).forEach { dark ->
            val c = palette.colorScheme(dark)
            listOf(c.onSurface to c.surface, c.onSurfaceVariant to c.surface, c.onBackground to c.background,
                c.onPrimary to c.primary, c.onPrimaryContainer to c.primaryContainer, c.onSecondary to c.secondary,
                c.onTertiary to c.tertiary, c.inverseOnSurface to c.inverseSurface, c.onErrorContainer to c.errorContainer).forEach { (text, surface) ->
                assertTrue("${palette.label}/dark=$dark text contrast ${contrast(text, surface)}", contrast(text, surface) >= 4.5f)
            }
        } }
    }
    @Test fun savedPaletteKeysStillResolveAndFreshInstallIsDarkAmbient() {
        assertEquals(ThemePalette.OxfordBlue, ThemePalette.fromPreference("oxford_blue"))
        assertEquals(ThemePalette.DarkRed, ThemePalette.fromPreference("dark_red"))
        assertEquals(ThemePalette.OliveGreen, ThemePalette.fromPreference("olive_green"))
        assertEquals(ThemePalette.AmbientViolet, AppearanceSettings().palette)
        assertTrue(AppearanceSettings().dark)
    }
    @Test fun presenceDoesNotInventListeningOrExecution() {
        assertEquals(AdaPresenceState.Idle, adaPresenceState(ChatState(), VoiceState(phase = VoicePhase.Permission)))
        assertEquals(AdaPresenceState.Listening, adaPresenceState(ChatState(), VoiceState(phase = VoicePhase.Recording)))
        assertEquals(AdaPresenceState.Speaking, adaPresenceState(ChatState(), VoiceState(playing = true)))
        assertEquals(AdaPresenceState.Offline, adaPresenceState(ChatState(fault = ApiFailure.Unreachable)))
        assertEquals(AdaPresenceState.Error, adaPresenceState(ChatState(fault = ApiFailure.Tls)))
        assertEquals(AdaPresenceState.Acting, adaPresenceState(ChatState(), acting = true))
    }
    @Test fun unknownDeliveryNeverLooksLikeConfirmedGeneration() {
        val message = PendingMessage(SessionIdentity("https://ada.test/", UUID.randomUUID()), UUID.randomUUID(), ChatInputDto(UUID.randomUUID(), "Public sample"))
        assertEquals(AdaPresenceState.Unconfirmed, adaPresenceState(ChatState(pending = PendingState(message, PendingPhase.Unknown))))
        assertEquals(AdaPresenceState.Thinking, adaPresenceState(ChatState(pending = PendingState(message, PendingPhase.Running))))
        assertEquals(AdaPresenceState.Error, adaPresenceState(ChatState(pending = PendingState(message, PendingPhase.Failed))))
    }
}
