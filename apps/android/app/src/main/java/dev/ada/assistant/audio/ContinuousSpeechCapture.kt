package dev.ada.assistant.audio

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.AudioManager
import android.media.MediaRecorder
import android.os.Handler
import android.os.Build
import android.os.Looper
import android.os.SystemClock
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

/** App-owned 16 kHz PCM. A bounded 2 s queue fails visibly instead of dropping frames. */
class ContinuousSpeechCapture(private val context: Context, private val runtime: LocalSpeechRuntime) : SpeechCapture {
    override val longForm = true
    override val longFormAvailable get() = runtime.installed
    override val modelSha256 get() = runtime.modelDigest
    override val version = "sherpa-onnx-1.13.8"
    override val adapterInfo get() = SpeechAdapterInfo("sherpa.zipformer.en.v1",SpeechTask.Asr,"Verified local files; en-US; owner-controlled recording")
    override val availability get() = if(runtime.installed) SpeechAvailability.Available else SpeechAvailability.NoEngine
    private val handler = Handler(Looper.getMainLooper())
    private val monitor = Any()
    @Volatile private var current: Run? = null
    @Volatile private var finalSegments = emptyList<TranscriptSegmentDto>()
    @Volatile private var durationMs=1L
    private val audio = AudioSession(context) { failCurrent("interrupted") }
    private class Run(val listener: CaptureListener) {
        val active = AtomicBoolean(true)
        val recording = AtomicBoolean(true)
        val producerDone = AtomicBoolean(false)
        val queue = ArrayBlockingQueue<FloatArray>(100)
        val transcript = ContinuousTranscript()
        var record: AudioRecord? = null
        var started = 0L
        var consumedFrames = 0L
        var receivedFrames = 0L
    }
    override fun transcriptSegments() = finalSegments
    override fun capturedDurationMs() = durationMs
    override fun start(language: String, listener: CaptureListener) {
        cancel(); finalSegments = emptyList(); durationMs=1
        if(language != "en-US" || !runtime.installed) { listener.failed("language_unavailable"); return }
        if(context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) { listener.failed("permission_lost"); return }
        val run = Run(listener)
        synchronized(monitor) { if(current != null) { listener.failed("interrupted"); return }; current=run }
        if(!VoiceAudioCoordinator.acquire(this,VoiceAudioCoordinator.Use.Capture) { failCurrent("interrupted") } || !audio.acquire()) { failCurrent("interrupted"); return }
        Thread({ consume(run) },"ada-local-decoder").start()
    }
    private fun post(run: Run, action: () -> Unit) { handler.post { if(current === run && run.active.get()) action() } }
    private fun produce(run: Run) {
        var record: AudioRecord? = null
        try {
            val minimum = AudioRecord.getMinBufferSize(16000,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT)
            require(minimum > 0)
            record = AudioRecord.Builder().setAudioSource(MediaRecorder.AudioSource.VOICE_RECOGNITION)
                .setAudioFormat(AudioFormat.Builder().setSampleRate(16000).setChannelMask(AudioFormat.CHANNEL_IN_MONO).setEncoding(AudioFormat.ENCODING_PCM_16BIT).build())
                .setBufferSizeInBytes(maxOf(minimum,6400)).build()
            require(record.state == AudioRecord.STATE_INITIALIZED)
            synchronized(run) {
                if(!run.active.get() || !run.recording.get()) return
                run.record=record; run.started=SystemClock.elapsedRealtime(); record.startRecording()
            }
            post(run) { run.listener.ready() }
            val pcm = ShortArray(320)
            while(run.active.get() && run.recording.get()) {
                if(context.getSystemService(AudioManager::class.java).isMicrophoneMute) { fail(run,"permission_lost"); break }
                if(Build.VERSION.SDK_INT>=29 && record.activeRecordingConfiguration?.isClientSilenced==true) { fail(run,"interrupted"); break }
                val size = record.read(pcm,0,pcm.size,AudioRecord.READ_BLOCKING)
                if(!run.active.get() || !run.recording.get()) break
                if(size <= 0) error("Audio input stopped")
                val samples = FloatArray(size) { pcm[it]/32768f }; pcm.fill(0)
                if(!run.queue.offer(samples)) { samples.fill(0f); error("Decoder backpressure") }
                run.receivedFrames+=size
                durationMs=(run.receivedFrames*1000/16000).coerceIn(1,LONG_VOICE_DURATION)
                if(SystemClock.elapsedRealtime()-run.started >= LONG_VOICE_DURATION) stop()
            }
        } catch (_: SecurityException) { fail(run,"permission_lost") }
        catch (_: Exception) { fail(run,"capture_failed") }
        finally {
            synchronized(run) { run.record=null }
            try { record?.stop() } catch (_: Exception) { }
            record?.release(); run.recording.set(false); run.producerDone.set(true)
        }
    }
    private fun consume(run: Run) {
        try {
            runtime.recognizer().use { decoder ->
                Thread({ produce(run) },"ada-local-microphone").start()
                while(run.active.get() && (!run.producerDone.get() || run.queue.isNotEmpty())) {
                    val samples=run.queue.poll(100,TimeUnit.MILLISECONDS) ?: continue
                    try { decoder.accept(samples); run.consumedFrames+=samples.size } finally { samples.fill(0f) }
                    while(decoder.ready() && run.active.get()) decoder.decode()
                    val provisional = run.transcript.text(decoder.text())
                    post(run) { run.listener.partial(provisional) }
                    if(decoder.endpoint()) { commit(run,decoder.text()); decoder.reset() }
                }
                if(!run.active.get()) return
                decoder.accept(FloatArray(8000)); decoder.finish()
                while(decoder.ready() && run.active.get()) decoder.decode()
                commit(run,decoder.text())
                finalSegments=run.transcript.segments()
                val text=run.transcript.text()
                post(run) { val callback=run.listener; finish(run); if(text.isBlank()) callback.failed("no_match") else callback.result(text) }
            }
        } catch (_: Exception) { fail(run,"decode_or_storage_failed") }
        finally { while(true) (run.queue.poll() ?: break).fill(0f) }
    }
    private fun commit(run: Run, text: String) {
        val duration=(run.consumedFrames*1000/16000).coerceIn(1,LONG_VOICE_DURATION)
        if(!run.transcript.commit(text,duration)) return
        val done=CountDownLatch(1); var saved=false
        post(run) { run.listener.checkpoint(run.transcript.segments(),duration) { success -> saved=success; done.countDown() } }
        require(done.await(10,TimeUnit.SECONDS) && saved && run.active.get())
        finalSegments=run.transcript.segments()
    }
    override fun stop() {
        val run=current ?: return
        synchronized(run) { run.recording.set(false); try { run.record?.stop() } catch (_: Exception) { } }
        post(run) { run.listener.ended() }
    }
    private fun failCurrent(code: String) { current?.let { fail(it,code) } }
    private fun fail(run: Run, code: String) { handler.post { if(current === run) { val callback=run.listener; finish(run); callback.failed(code) } } }
    private fun finish(run: Run) {
        run.active.set(false); run.recording.set(false)
        synchronized(run) { try { run.record?.stop() } catch (_: Exception) { } }
        synchronized(monitor) { if(current === run) current=null }
        audio.release(); VoiceAudioCoordinator.release(this)
    }
    override fun cancel() { current?.let(::finish) }
    override fun close() = cancel()
}
