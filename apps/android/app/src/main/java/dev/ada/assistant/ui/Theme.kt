package dev.ada.assistant.ui

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

object AdaSpacing { val small = 8.dp; val medium = 16.dp; val large = 24.dp; val touch = 48.dp }

enum class ThemePalette(val preferenceKey: String, val label: String, val seed: Color) {
    OxfordBlue("oxford_blue", "Oxford Blue", Color(0xFF002147)),
    DarkRed("dark_red", "Dark Red", Color(0xFF350616)),
    OliveGreen("olive_green", "Olive Green", Color(0xFF3C4C24));

    companion object {
        fun fromPreference(value: String?) = entries.firstOrNull { it.preferenceKey == value } ?: OxfordBlue
    }
}

private data class PaletteColors(
    val lightBackground: Color, val lightContainer: Color, val lightVariant: Color,
    val lightText: Color, val lightMuted: Color, val lightOutline: Color,
    val darkBackground: Color, val darkSurface: Color, val darkVariant: Color,
    val darkText: Color, val darkMuted: Color, val darkOutline: Color, val accent: Color,
)

private val OxfordColors = PaletteColors(
    Color(0xFFF5F8FD), Color(0xFFDCE8F8), Color(0xFFE1E7F0),
    Color(0xFF152235), Color(0xFF445267), Color(0xFF65758C),
    Color(0xFF081524), Color(0xFF102136), Color(0xFF26374C),
    Color(0xFFE6EDF8), Color(0xFFBAC8DC), Color(0xFF91A1B7), Color(0xFFA9C8F4),
)
private val RedColors = PaletteColors(
    Color(0xFFFFF7F9), Color(0xFFF5DAE3), Color(0xFFF0E0E5),
    Color(0xFF30141F), Color(0xFF654750), Color(0xFF886570),
    Color(0xFF1B0C12), Color(0xFF2B1720), Color(0xFF452C36),
    Color(0xFFF9E6ED), Color(0xFFDEBBC8), Color(0xFFB38D9C), Color(0xFFEAB2C7),
)
private val OliveColors = PaletteColors(
    Color(0xFFF8FAF2), Color(0xFFE1EACF), Color(0xFFE4E8DB),
    Color(0xFF222B19), Color(0xFF4E5941), Color(0xFF707E60),
    Color(0xFF12190C), Color(0xFF202A17), Color(0xFF35422A),
    Color(0xFFEDF2DF), Color(0xFFCCD7BB), Color(0xFF9EA98C), Color(0xFFBDCF9D),
)

fun ThemePalette.colorScheme(dark: Boolean): ColorScheme {
    val tones = when (this) {
        ThemePalette.OxfordBlue -> OxfordColors
        ThemePalette.DarkRed -> RedColors
        ThemePalette.OliveGreen -> OliveColors
    }
    return if (dark) darkColorScheme(
        primary = tones.accent, onPrimary = seed,
        primaryContainer = seed, onPrimaryContainer = tones.accent,
        secondary = tones.accent, onSecondary = seed,
        secondaryContainer = tones.darkVariant, onSecondaryContainer = tones.darkText,
        tertiary = tones.accent, onTertiary = seed,
        tertiaryContainer = tones.darkVariant, onTertiaryContainer = tones.darkText,
        background = tones.darkBackground, onBackground = tones.darkText,
        surface = tones.darkSurface, onSurface = tones.darkText,
        surfaceVariant = tones.darkVariant, onSurfaceVariant = tones.darkMuted,
        surfaceTint = tones.accent, outline = tones.darkOutline, outlineVariant = tones.darkVariant,
        inverseSurface = tones.lightContainer, inverseOnSurface = seed, inversePrimary = seed,
        surfaceBright = tones.darkVariant, surfaceDim = tones.darkBackground,
        surfaceContainerLowest = tones.darkBackground, surfaceContainerLow = tones.darkSurface,
        surfaceContainer = tones.darkSurface, surfaceContainerHigh = tones.darkVariant,
        surfaceContainerHighest = tones.darkVariant,
        error = Color(0xFFFFB4AB), onError = Color(0xFF690005),
        errorContainer = Color(0xFF93000A), onErrorContainer = Color(0xFFFFDAD6), scrim = Color.Black,
    ) else lightColorScheme(
        primary = seed, onPrimary = Color.White,
        primaryContainer = tones.lightContainer, onPrimaryContainer = seed,
        secondary = seed, onSecondary = Color.White,
        secondaryContainer = tones.lightVariant, onSecondaryContainer = seed,
        tertiary = seed, onTertiary = Color.White,
        tertiaryContainer = tones.lightContainer, onTertiaryContainer = seed,
        background = tones.lightBackground, onBackground = tones.lightText,
        surface = tones.lightBackground, onSurface = tones.lightText,
        surfaceVariant = tones.lightVariant, onSurfaceVariant = tones.lightMuted,
        surfaceTint = seed, outline = tones.lightOutline, outlineVariant = tones.lightVariant,
        inverseSurface = seed, inverseOnSurface = tones.lightBackground, inversePrimary = tones.accent,
        surfaceBright = tones.lightBackground, surfaceDim = tones.lightVariant,
        surfaceContainerLowest = Color.White, surfaceContainerLow = tones.lightBackground,
        surfaceContainer = tones.lightBackground, surfaceContainerHigh = tones.lightContainer,
        surfaceContainerHighest = tones.lightVariant,
        error = Color(0xFFB3261E), onError = Color.White,
        errorContainer = Color(0xFFF9DEDC), onErrorContainer = Color(0xFF410E0B), scrim = Color.Black,
    )
}

@Composable fun AdaTheme(palette: ThemePalette = ThemePalette.OxfordBlue, dark: Boolean = false, content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = palette.colorScheme(dark),
        typography = Typography(), // sp typography respects Android's system text scaling.
        shapes = Shapes(small = RoundedCornerShape(8.dp), medium = RoundedCornerShape(16.dp), large = RoundedCornerShape(24.dp)),
        content = content,
    )
}
