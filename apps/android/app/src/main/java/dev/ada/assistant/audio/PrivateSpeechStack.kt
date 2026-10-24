package dev.ada.assistant.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.os.Handler
import android.os.Looper
import dev.ada.assistant.ui.*
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

class PrivateSpeechStack(context: Context) {
    val runtime=LocalSpeechFactory.create(context.applicationContext)
    val capture=SelectableCapture(AndroidSpeechCapture(context),ContinuousSpeechCapture(context,runtime),runtime)
    val playback=SelectablePlayback(AndroidSpeechPlayback(context),NeuralSpeechPlayback(context,runtime),runtime)
}

class SelectableCapture(private val platform: SpeechCapture, private val continuous: SpeechCapture, private val runtime: LocalSpeechRuntime) : SpeechCapture {
    private var useContinuous=false
    private val active get() = if(useContinuous) continuous else platform
    override val availability get() = active.availability
    override val version get() = active.version
    override val adapterInfo get() = active.adapterInfo
    override val longForm get() = useContinuous
    override val longFormAvailable get() = runtime.installed
    override val modelSha256 get() = active.modelSha256
    override fun selectLongForm(enabled: Boolean): Boolean {
        if(enabled && !runtime.installed) return false
        cancel(); useContinuous=enabled; return true
    }
    override fun transcriptSegments() = active.transcriptSegments()
    override fun capturedDurationMs() = active.capturedDurationMs()
    override fun start(language: String, listener: CaptureListener) = active.start(language,listener)
    override fun stop() = active.stop()
    override fun cancel() { platform.cancel(); continuous.cancel() }
    override fun close() { platform.close(); continuous.close() }
}

class SelectablePlayback(private val platform: SpeechPlayback, private val neural: SpeechPlayback, private val runtime: LocalSpeechRuntime) : SpeechPlayback {
    override val adapterInfo get() = SpeechAdapterInfo("ada.local-playback.v2",SpeechTask.Tts,"Installed platform voices; optional evaluated Kokoro voices")
    override fun initialize(ready: (List<SpeechVoice>) -> Unit) {
        platform.initialize { p -> neural.initialize { n -> ready(p.map { it.copy(id="platform/${it.id}") }+n) } }
    }
    override fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit) {
        stop()
        if(voice.startsWith("neural/")) neural.play(text,voice,speed,finished)
        else if(voice.startsWith("platform/")) platform.play(text,voice.removePrefix("platform/"),speed,finished)
        else finished("voice_unavailable")
    }
    override fun stop() { platform.stop(); neural.stop() }
    override fun close() { platform.close(); neural.close() }
}

/** One <=240-character synthesis and one AudioTrack buffer at a time; no WAV/file output. */
class NeuralSpeechPlayback(context: Context, private val runtime: LocalSpeechRuntime) : SpeechPlayback {
    private val executor=Executors.newSingleThreadExecutor()
    private val handler=Handler(Looper.getMainLooper())
    private val generation=AtomicLong()
    private val audio=AudioSession(context) { fail("interrupted") }
    @Volatile private var track: AudioTrack?=null
    private var completion: ((String?) -> Unit)?=null
    override val adapterInfo get() = SpeechAdapterInfo("sherpa.kokoro.en.v019",SpeechTask.Tts,"Local evaluation; no network or voice cloning")
    override fun initialize(ready: (List<SpeechVoice>) -> Unit) = ready(if(!runtime.installed) emptyList() else listOf(
        SpeechVoice("neural/1","Bella · feminine English · local neural","en-US"),
        SpeechVoice("neural/2","Nicole · feminine English · local neural","en-US"),
        SpeechVoice("neural/3","Sarah · feminine English · local neural","en-US"),
        SpeechVoice("neural/4","Sky · feminine English · local neural","en-US")))
    override fun play(text: String, voice: String, speed: Float, finished: (String?) -> Unit) {
        stop(); val key=generation.get(); completion=finished
        val sid=voice.removePrefix("neural/").toIntOrNull()
        if(!runtime.installed || sid !in 1..4 || text.length>12000 || text.isBlank() || speed !in setOf(.75f,1f,1.25f,1.5f)) { fail("voice_unavailable"); return }
        if(!VoiceAudioCoordinator.acquire(this,VoiceAudioCoordinator.Use.Playback) { fail("interrupted") } || !audio.acquire()) { fail("interrupted"); return }
        executor.execute {
            try {
                runtime.synthesizer().use { engine ->
                    val minimum=AudioTrack.getMinBufferSize(engine.sampleRate,AudioFormat.CHANNEL_OUT_MONO,AudioFormat.ENCODING_PCM_FLOAT)
                    require(minimum>0)
                    val player=AudioTrack.Builder().setAudioAttributes(speechAudioAttributes())
                        .setAudioFormat(AudioFormat.Builder().setSampleRate(engine.sampleRate).setChannelMask(AudioFormat.CHANNEL_OUT_MONO).setEncoding(AudioFormat.ENCODING_PCM_FLOAT).build())
                        .setTransferMode(AudioTrack.MODE_STREAM).setBufferSizeInBytes(maxOf(minimum,engine.sampleRate/5*4)).build()
                    track=player
                    try {
                        require(player.state==AudioTrack.STATE_INITIALIZED)
                        player.play()
                        var at=0
                        while(at<text.length && generation.get()==key) {
                            var end=minOf(text.length,at+240)
                            if(end<text.length) { val space=text.lastIndexOf(' ',end); if(space>at+80) end=space+1 }
                            if(end<text.length && text[end-1].isHighSurrogate()) end--
                            val samples=engine.generate(text.substring(at,end),requireNotNull(sid),speed) { generation.get()!=key }
                            try {
                                var offset=0
                                while(offset<samples.size && generation.get()==key) {
                                    val written=player.write(samples,offset,minOf(2400,samples.size-offset),AudioTrack.WRITE_BLOCKING)
                                    require(written>0); offset+=written
                                }
                            } finally { samples.fill(0f) }
                            at=end
                        }
                        if(generation.get()==key) {
                            // AudioTrack writes are backpressured. Drain the small remaining hardware buffer.
                            val deadline=android.os.SystemClock.elapsedRealtime()+1500
                            var previous=player.playbackHeadPosition
                            while(generation.get()==key && android.os.SystemClock.elapsedRealtime()<deadline) {
                                Thread.sleep(50); val next=player.playbackHeadPosition
                                if(next==previous) break
                                previous=next
                            }
                        }
                    } finally { if(track===player) track=null; try { player.stop(); player.flush() } catch (_: Exception) { }; player.release() }
                }
                handler.post { if(generation.get()==key) complete(null) }
            } catch (_: Exception) { handler.post { if(generation.get()==key) complete("playback_failed") } }
        }
    }
    private fun complete(error: String?) { val callback=completion; completion=null; audio.release(); VoiceAudioCoordinator.release(this); callback?.invoke(error) }
    private fun fail(code: String) { stop(); complete(code) }
    override fun stop() {
        generation.incrementAndGet()
        try { track?.pause(); track?.flush() } catch (_: Exception) { }
        audio.release(); VoiceAudioCoordinator.release(this)
    }
    override fun close() { stop(); completion=null; executor.shutdown() }
}
