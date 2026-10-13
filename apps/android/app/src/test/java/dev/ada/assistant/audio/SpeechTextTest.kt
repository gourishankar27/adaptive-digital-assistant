package dev.ada.assistant.audio

import dev.ada.assistant.data.safeSpeechText
import org.junit.Assert.*
import org.junit.Test

class SpeechTextTest {
    @Test fun boundedPlaybackDoesNotSplitUnicodeOrReadReasoningAndDebugBlocks() {
        assertEquals("Answer", safeSpeechText("Answer <think>hidden reasoning"))
        assertEquals("A label", safeSpeechText("A [label](https://secret.test) [D12] ```debug```"))
        val text = "x".repeat(3999) + "🫖" + "y".repeat(8000)
        val chunks = speechChunks(safeSpeechText(text), 4000)
        assertEquals(4, chunks.size); assertEquals(safeSpeechText(text), chunks.joinToString(""))
        assertTrue(chunks.all { it.length <= 4000 && it.lastOrNull()?.isHighSurrogate() != true && it.firstOrNull()?.isLowSurrogate() != true })
    }
}
