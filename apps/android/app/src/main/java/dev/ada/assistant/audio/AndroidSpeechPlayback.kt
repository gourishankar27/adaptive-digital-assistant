package dev.ada.assistant.audio

import android.content.Context
import android.media.AudioAttributes
import android.os.Handler
import android.os.Looper
import android.speech.tts.*
import dev.ada.assistant.ui.SpeechPlayback
import dev.ada.assistant.ui.SpeechVoice
import java.util.UUID

/** Only installed voices that do not require a network connection are offered. */
class AndroidSpeechPlayback(context: Context, private val diagnostic: ((String) -> Unit)? = null) : SpeechPlayback {
    private val handler = Handler(Looper.getMainLooper())
    private val app = context.applicationContext
    private var engine: TextToSpeech? = null
    private var voices = emptyMap<String, Voice>()
    private var callback: ((String?) -> Unit)? = null
    private var key = 0L
    private var closed = false
    private val audio = AudioSession(context, diagnostic) { finish("Playback was interrupted. Tap Read reply to start again.") }
    override fun initialize(ready: (List<SpeechVoice>) -> Unit) {
        engine = TextToSpeech(app) { result -> handler.post {
            if (closed) return@post
            val tts = engine
            if (result != TextToSpeech.SUCCESS || tts == null) { ready(emptyList()); return@post }
            try {
                voices = tts.voices.orEmpty().filter { !it.isNetworkConnectionRequired && TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED !in it.features.orEmpty() }.associateBy { it.name }
                if (tts.setAudioAttributes(speechAudioAttributes()) != TextToSpeech.SUCCESS) {
                    voices = emptyMap(); ready(emptyList()); return@post
                }
                ready(voices.values.sortedBy { it.name }.map { SpeechVoice(it.name, "${it.locale.toLanguageTag()} · ${it.name}", it.locale.toLanguageTag()) })
            } catch (_: Exception) { voices = emptyMap(); ready(emptyList()) }
        } }
    }
    override fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit) {
        stop(); callback = finished
        val tts = engine; val selected = voices[voice]
        if (tts == null || selected == null || closed || text.isBlank() || text.length > 12000 || speed !in listOf(.75f, 1f, 1.25f, 1.5f)) { finish("An installed on-device playback voice is unavailable."); return }
        try {
            // Recheck after initialization: a system voice can be removed or changed in Settings.
            val current = tts.voices.orEmpty().firstOrNull { it.name == voice }
            if (current == null || current.isNetworkConnectionRequired || TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED in current.features.orEmpty()) {
                finish("The selected offline voice is no longer installed. Text remains available."); return
            }
            if (!audio.acquire() || tts.setVoice(current) != TextToSpeech.SUCCESS || tts.setSpeechRate(speed) != TextToSpeech.SUCCESS) { finish("Playback could not acquire audio. Text remains available."); return }
            val run = key; val id = UUID.randomUUID().toString()
            val chunks = speechChunks(text, TextToSpeech.getMaxSpeechInputLength().coerceAtMost(4000))
            tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(utteranceId: String?) { handler.post { if (run == key && utteranceId?.startsWith("$id-") == true) diagnostic?.invoke("utterance_started") } }
                override fun onDone(utteranceId: String?) { handler.post { if (run == key && utteranceId == "$id-${chunks.lastIndex}") finish(null) } }
                @Deprecated("Platform callback") override fun onError(utteranceId: String?) { handler.post { if (run == key && utteranceId?.startsWith("$id-") == true) finish("Playback failed. Text remains available.") } }
                override fun onError(utteranceId: String?, errorCode: Int) { onError(utteranceId) }
            })
            chunks.forEachIndexed { index, chunk -> if (tts.speak(chunk, if (index == 0) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD, null, "$id-$index") == TextToSpeech.ERROR) { finish("Playback failed. Text remains available."); return } }
        } catch (_: Exception) { finish("Playback failed. Text remains available.") }
    }
    private fun finish(message: String?) { val done = callback; stop(); done?.invoke(message) }
    override fun stop() { key++; callback = null; try { engine?.stop() } catch (_: Exception) { }; audio.release() }
    override fun close() { closed = true; stop(); engine?.shutdown(); engine = null; voices = emptyMap(); handler.removeCallbacksAndMessages(null) }
}

internal fun speechChunks(text: String, maximum: Int): List<String> {
    require(maximum >= 2 && text.length <= 12000)
    val chunks = mutableListOf<String>(); var offset = 0
    while (offset < text.length) {
        var end = (offset + maximum).coerceAtMost(text.length)
        if (end < text.length && text[end - 1].isHighSurrogate()) end--
        chunks += text.substring(offset, end); offset = end
    }
    return chunks
}
