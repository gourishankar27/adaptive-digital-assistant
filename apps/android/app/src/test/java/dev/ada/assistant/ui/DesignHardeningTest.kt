package dev.ada.assistant.ui

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import androidx.compose.ui.graphics.luminance
import org.junit.Assert.*
import org.junit.Test

class DesignHardeningTest {
    private fun contrast(a: Color, b: Color) = (maxOf(a.luminance(), b.luminance()) + .05f) / (minOf(a.luminance(), b.luminance()) + .05f)

    @Test fun mutedTextAndFunctionalInputBoundaryRemainReadableAcrossAllEightSchemes() {
        ThemePalette.entries.forEach { palette -> listOf(false, true).forEach { dark ->
            val c = palette.colorScheme(dark)
            listOf(c.background, c.surface, c.surfaceVariant, c.surfaceContainerHigh, c.surfaceContainerHighest).forEach {
                assertTrue("${palette.label}/$dark muted text", contrast(c.onSurfaceVariant, it) >= 4.5f)
                assertTrue("${palette.label}/$dark inline link", contrast(c.primary, it) >= 4.5f)
            }
            val glass = palette.glassColor(dark).compositeOver(c.background)
            assertTrue("${palette.label}/$dark composer boundary", contrast(c.outline, glass) >= 3f)
        } }
    }

    @Test fun fencedCodeDoesNotApplyMonospaceToFollowingProseOrChangeLiteralText() {
        val text = "```kotlin\r\nval sample = \"😀\"\r\n```\r\nThis paragraph remains ordinary text."
        val ranges = fencedCodeRanges(text)
        assertEquals(1, ranges.size)
        assertTrue(text.substring(ranges.single()).startsWith("```kotlin"))
        assertFalse(ranges.single().contains(text.indexOf("This paragraph")))
    }

    @Test fun multipleAndUnclosedCodeFencesHaveBoundedLiteralDisplaySpans() {
        assertTrue(fencedCodeRanges("Plain text and `inline code`.").isEmpty())
        val text = "Before\n```\none\n```\nBetween\n```\ntwo"
        val ranges = fencedCodeRanges(text)
        assertEquals(2, ranges.size)
        assertFalse(ranges.any { text.indexOf("Between") in it })
        assertEquals(text.lastIndex, ranges.last().last)
    }

    @Test fun unknownProtocolValuesNeverImplyCompletedWork() {
        assertEquals("Completed", statusLabel("completed"))
        assertEquals("Outcome unconfirmed", statusLabel(null))
        assertTrue(statusLabel("future-server-state").startsWith("Unrecognized"))
        assertEquals("search index rebuild", jobLabel("lexical_rebuild"))
        assertEquals("Step by step", preferenceLabel("stepwise"))
    }

    @Test fun explicitAppearanceChoicesStayExplicitUntilSystemFollowingIsSelected() {
        assertFalse(AppearanceSettings(dark = false).effectiveDark(true))
        assertTrue(AppearanceSettings(dark = true).effectiveDark(false))
        assertFalse(AppearanceSettings(dark = true, followSystem = true).effectiveDark(false))
        assertTrue(AppearanceSettings(dark = false, followSystem = true).effectiveDark(true))
        assertFalse(AppearanceSettings().followSystem)
        assertFalse(AppearanceSettings().reduceMotion)
    }
}
