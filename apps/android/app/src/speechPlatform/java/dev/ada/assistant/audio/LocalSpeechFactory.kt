package dev.ada.assistant.audio

import android.content.Context

/** Normal builds contain no additional model/runtime until the native acceptance gate closes. */
object LocalSpeechFactory {
    fun create(context: Context): LocalSpeechRuntime = object : LocalSpeechRuntime {
        override val available = false
        override val installed = false
        override val modelDigest = ""
        override fun install(): Unit = error("Local speech is not included in this build")
        override fun remove() = Unit
        override fun recognizer(): StreamingSpeechDecoder = error("Local speech unavailable")
        override fun wakeDetector(): WakeWordDecoder = error("Local speech unavailable")
        override fun synthesizer(): LocalVoiceSynthesizer = error("Local speech unavailable")
    }
}
