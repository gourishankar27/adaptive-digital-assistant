package dev.ada.assistant.ui

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

object AdaSpacing { val tiny = 4.dp; val small = 8.dp; val medium = 16.dp; val large = 24.dp; val section = 32.dp; val touch = 48.dp }
object AdaLayout { val content = 1040.dp; val reading = 840.dp; val form = 560.dp; val railAt = 840.dp; val orb = 128.dp; val presence = 64.dp; val border = 1.dp }
object AdaMotion { const val transition = 240; const val breathing = 3600; const val orbit = 18000 }

enum class ThemePalette(val preferenceKey: String, val label: String, val seed: Color) {
    AmbientViolet("ambient_violet", "ADA Ambient", Color(0xFF8A6CFF)),
    OxfordBlue("oxford_blue", "Oxford Blue", Color(0xFF002147)),
    DarkRed("dark_red", "Dark Red", Color(0xFF350616)),
    OliveGreen("olive_green", "Olive Green", Color(0xFF3C4C24));

    companion object {
        fun fromPreference(value: String?) = entries.firstOrNull { it.preferenceKey == value } ?: AmbientViolet
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
private val AmbientColors = PaletteColors(
    Color(0xFFF7F7FF), Color(0xFFE9E2FF), Color(0xFFEBEAF6),
    Color(0xFF1B1B32), Color(0xFF54566D), Color(0xFF73758E),
    Color(0xFF070816), Color(0xFF101329), Color(0xFF232640),
    Color(0xFFF6F7FF), Color(0xFFB8BDD3), Color(0xFF7E849E), Color(0xFFA48CFF),
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
        ThemePalette.AmbientViolet -> AmbientColors
        ThemePalette.OxfordBlue -> OxfordColors
        ThemePalette.DarkRed -> RedColors
        ThemePalette.OliveGreen -> OliveColors
    }
    val primaryInk = if (this == ThemePalette.AmbientViolet) Color(0xFF1C103D) else seed
    val lightPrimary = if (this == ThemePalette.AmbientViolet) Color(0xFF6249D8) else seed
    return if (dark) darkColorScheme(
        primary = tones.accent, onPrimary = primaryInk,
        primaryContainer = if (this == ThemePalette.AmbientViolet) Color(0xFF2D234F) else seed, onPrimaryContainer = tones.darkText,
        secondary = tones.accent, onSecondary = primaryInk,
        secondaryContainer = tones.darkVariant, onSecondaryContainer = tones.darkText,
        tertiary = tones.accent, onTertiary = primaryInk,
        tertiaryContainer = tones.darkVariant, onTertiaryContainer = tones.darkText,
        background = tones.darkBackground, onBackground = tones.darkText,
        surface = tones.darkSurface, onSurface = tones.darkText,
        surfaceVariant = tones.darkVariant, onSurfaceVariant = tones.darkMuted,
        surfaceTint = tones.accent, outline = tones.darkOutline, outlineVariant = tones.darkVariant,
        inverseSurface = tones.lightContainer, inverseOnSurface = primaryInk, inversePrimary = lightPrimary,
        surfaceBright = tones.darkVariant, surfaceDim = tones.darkBackground,
        surfaceContainerLowest = tones.darkBackground, surfaceContainerLow = tones.darkSurface,
        surfaceContainer = tones.darkSurface, surfaceContainerHigh = tones.darkVariant,
        surfaceContainerHighest = tones.darkVariant,
        error = Color(0xFFFFB4AB), onError = Color(0xFF690005),
        errorContainer = Color(0xFF93000A), onErrorContainer = Color(0xFFFFDAD6), scrim = Color.Black,
    ) else lightColorScheme(
        primary = lightPrimary, onPrimary = Color.White,
        primaryContainer = tones.lightContainer, onPrimaryContainer = lightPrimary,
        secondary = lightPrimary, onSecondary = Color.White,
        secondaryContainer = tones.lightVariant, onSecondaryContainer = lightPrimary,
        tertiary = lightPrimary, onTertiary = Color.White,
        tertiaryContainer = tones.lightContainer, onTertiaryContainer = lightPrimary,
        background = tones.lightBackground, onBackground = tones.lightText,
        surface = tones.lightBackground, onSurface = tones.lightText,
        surfaceVariant = tones.lightVariant, onSurfaceVariant = tones.lightMuted,
        surfaceTint = seed, outline = tones.lightOutline, outlineVariant = tones.lightVariant,
        inverseSurface = lightPrimary, inverseOnSurface = tones.lightBackground, inversePrimary = tones.accent,
        surfaceBright = tones.lightBackground, surfaceDim = tones.lightVariant,
        surfaceContainerLowest = Color.White, surfaceContainerLow = tones.lightBackground,
        surfaceContainer = tones.lightBackground, surfaceContainerHigh = tones.lightContainer,
        surfaceContainerHighest = tones.lightVariant,
        error = Color(0xFFB3261E), onError = Color.White,
        errorContainer = Color(0xFFF9DEDC), onErrorContainer = Color(0xFF410E0B), scrim = Color.Black,
    )
}

data class AdaVisuals(val dark: Boolean, val glass: Color, val edge: Color, val listening: Color, val warmth: Color)
val LocalAdaVisuals = staticCompositionLocalOf { AdaVisuals(true, Color(0xFF171A34), Color(0xFF343750), Color(0xFF68D8FF), Color(0xFFEFA5C8)) }
// Tests can freeze ambient motion. Production also checks lifecycle and system animator settings.
val LocalAdaMotionEnabled = staticCompositionLocalOf { true }
private fun adaText(size: Int, height: Int, weight: FontWeight = FontWeight.Normal) = TextStyle(fontFamily = FontFamily.SansSerif, fontSize = size.sp, lineHeight = height.sp, fontWeight = weight)
private val AdaTypography = Typography(
    displaySmall = adaText(32, 40, FontWeight.Medium), headlineLarge = adaText(30, 38, FontWeight.Medium),
    headlineMedium = adaText(26, 34, FontWeight.Medium), headlineSmall = adaText(24, 32, FontWeight.Medium),
    titleLarge = adaText(20, 28, FontWeight.Medium), titleMedium = adaText(18, 26, FontWeight.Medium), titleSmall = adaText(16, 24, FontWeight.Medium),
    bodyLarge = adaText(16, 26), bodyMedium = adaText(15, 24), bodySmall = adaText(13, 20),
    labelLarge = adaText(14, 20, FontWeight.Medium), labelMedium = adaText(13, 18, FontWeight.Medium), labelSmall = adaText(12, 18, FontWeight.Medium),
)

@Composable fun AdaTheme(palette: ThemePalette = ThemePalette.AmbientViolet, dark: Boolean = true, content: @Composable () -> Unit) {
    val scheme = palette.colorScheme(dark)
    val glass = if (dark && palette == ThemePalette.AmbientViolet) Color(0xFF171A34).copy(alpha = .86f) else if (dark) scheme.surfaceContainerHigh.copy(alpha = .88f) else scheme.surface.copy(alpha = .94f)
    val visuals = AdaVisuals(dark, glass, scheme.outline.copy(alpha = .32f), if (dark) Color(0xFF68D8FF) else Color(0xFF006581), if (dark) Color(0xFFEFA5C8) else Color(0xFF894464))
    CompositionLocalProvider(LocalAdaVisuals provides visuals) {
    MaterialTheme(
        colorScheme = scheme,
        typography = AdaTypography,
        shapes = Shapes(extraSmall = RoundedCornerShape(14.dp), small = RoundedCornerShape(16.dp), medium = RoundedCornerShape(20.dp), large = RoundedCornerShape(24.dp), extraLarge = RoundedCornerShape(24.dp)),
        content = content,
    )
    }
}
