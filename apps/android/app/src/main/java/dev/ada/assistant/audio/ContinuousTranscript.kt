package dev.ada.assistant.audio

import dev.ada.assistant.data.*
import java.util.UUID

/** Endpoints commit an internal segment, never the recording/turn. No PCM is retained. */
class ContinuousTranscript {
    private val rows = mutableListOf<TranscriptSegmentDto>()
    fun segments(): List<TranscriptSegmentDto> = rows.toList()
    fun text(partial: String = ""): String = (rows.map { it.text } + partial.takeIf { it.isNotBlank() }.orEmpty()).filter { it.isNotEmpty() }.joinToString(" ")
    fun commit(text: String, endMs: Long): Boolean {
        if (text.isBlank()) return false
        require(rows.size < 512 && voiceTextValid(text,LONG_VOICE_TEXT))
        val next = text(text)
        require(voiceTextValid(next,LONG_VOICE_TEXT))
        require(endMs in 1..LONG_VOICE_DURATION && (rows.lastOrNull()?.end_ms ?: 0) <= endMs)
        rows += TranscriptSegmentDto(UUID.randomUUID(),rows.size,endMs,text,voiceHash(text))
        return true
    }
}

interface StreamingSpeechDecoder : AutoCloseable {
    fun accept(samples: FloatArray)
    fun ready(): Boolean
    fun decode()
    fun text(): String
    fun endpoint(): Boolean
    fun reset()
    fun finish()
}
interface WakeWordDecoder : AutoCloseable { fun accept(samples: FloatArray): Boolean }
interface LocalVoiceSynthesizer : AutoCloseable {
    val sampleRate: Int
    fun generate(text: String, voice: Int, speed: Float, cancelled: () -> Boolean): FloatArray
}

interface LocalSpeechRuntime {
    val available: Boolean
    val installed: Boolean
    val modelDigest: String
    fun install()
    fun remove()
    fun recognizer(): StreamingSpeechDecoder
    fun wakeDetector(): WakeWordDecoder
    fun synthesizer(): LocalVoiceSynthesizer
}
