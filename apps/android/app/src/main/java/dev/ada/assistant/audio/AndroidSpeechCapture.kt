package dev.ada.assistant.audio

import android.content.Context
import android.content.BroadcastReceiver
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.media.*
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.*
import androidx.core.content.ContextCompat
import dev.ada.assistant.ui.*

/** No system/network fallback, model download, raw audio file or background service. */
class AndroidSpeechCapture(private val context: Context) : SpeechCapture {
    override val availability: SpeechAvailability get() = when {
        !context.packageManager.hasSystemFeature(PackageManager.FEATURE_MICROPHONE) -> SpeechAvailability.NoMicrophone
        Build.VERSION.SDK_INT < 31 -> SpeechAvailability.UnsupportedDevice
        !SpeechRecognizer.isOnDeviceRecognitionAvailable(context) -> SpeechAvailability.NoEngine
        else -> SpeechAvailability.Available
    }
    override val version = "Android ${Build.VERSION.RELEASE} API ${Build.VERSION.SDK_INT}".filter { it.code in 32..126 }.take(120)
    private val handler = Handler(Looper.getMainLooper())
    private var recognizer: SpeechRecognizer? = null
    private var listener: CaptureListener? = null
    private var key = 0L
    private val audio = AudioSession(context) { fail("interrupted") }
    override fun start(language: String, listener: CaptureListener) {
        cancel(); this.listener = listener
        val run = key
        if (availability != SpeechAvailability.Available) { fail("unavailable"); return }
        try {
            if (!VoiceAudioCoordinator.acquire(this,VoiceAudioCoordinator.Use.Capture) { fail("interrupted") } || !audio.acquire()) { fail("interrupted"); return }
            if (Build.VERSION.SDK_INT < 31) { fail("unavailable"); return }
            val engine = SpeechRecognizer.createOnDeviceSpeechRecognizer(context)
            recognizer = engine
            engine.setRecognitionListener(object : RecognitionListener {
                private fun active() = run == key
                override fun onReadyForSpeech(params: Bundle?) { if (active()) this@AndroidSpeechCapture.listener?.ready() }
                override fun onEndOfSpeech() { if (active()) this@AndroidSpeechCapture.listener?.ended() }
                override fun onResults(results: Bundle?) {
                    if (!active()) return
                    val text = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
                    val callback = this@AndroidSpeechCapture.listener
                    cancel()
                    if (text.isNullOrBlank()) callback?.failed("no_match") else callback?.result(text)
                }
                override fun onError(error: Int) { if (active()) fail(when(error) {
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "permission_lost"
                    SpeechRecognizer.ERROR_LANGUAGE_NOT_SUPPORTED, SpeechRecognizer.ERROR_LANGUAGE_UNAVAILABLE -> "language_unavailable"
                    SpeechRecognizer.ERROR_NO_MATCH, SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "no_match"
                    else -> "recognition_failed"
                }) }
                override fun onBeginningOfSpeech() = Unit
                override fun onRmsChanged(rmsdB: Float) = Unit
                override fun onBufferReceived(buffer: ByteArray?) = Unit // Never retain/export audio.
                override fun onPartialResults(partialResults: Bundle?) {
                    if (active()) partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()?.let { this@AndroidSpeechCapture.listener?.partial(it) }
                }
                override fun onEvent(eventType: Int, params: Bundle?) = Unit
            })
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE, language)
                .putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
                .putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            if (Build.VERSION.SDK_INT >= 33) {
                engine.checkRecognitionSupport(intent, context.mainExecutor, object : RecognitionSupportCallback {
                    override fun onSupportResult(support: RecognitionSupport) {
                        if (run != key) return
                        if (support.installedOnDeviceLanguages.none { it.equals(language, ignoreCase = true) }) fail("language_unavailable")
                        else try { engine.startListening(intent) } catch (_: Exception) { fail("recognition_failed") }
                    }
                    override fun onError(error: Int) { if (run == key) fail(if (error == SpeechRecognizer.ERROR_LANGUAGE_NOT_SUPPORTED || error == SpeechRecognizer.ERROR_LANGUAGE_UNAVAILABLE) "language_unavailable" else "support_unavailable") }
                })
            } else engine.startListening(intent)
        } catch (_: SecurityException) { fail("permission_lost") }
        catch (_: Exception) { fail("recognition_failed") }
    }
    private fun fail(code: String) { val callback = listener; cancel(); callback?.failed(code) }
    override fun stop() { try { recognizer?.stopListening() } catch (_: Exception) { fail("recognition_failed") } }
    override fun cancel() {
        key++; listener = null
        recognizer?.let { try { it.cancel(); it.destroy() } catch (_: Exception) { /* Text remains available. */ } }
        recognizer = null; audio.release(); VoiceAudioCoordinator.release(this)
    }
    override fun close() { cancel(); handler.removeCallbacksAndMessages(null) }
}

/** Foreground-only transient audio focus. Route changes and focus loss never auto-resume. */
internal class AudioSession(private val context: Context, private val diagnostic: ((String) -> Unit)? = null, private val interrupted: () -> Unit) {
    private val manager = context.getSystemService(AudioManager::class.java)
    private val handler = Handler(Looper.getMainLooper())
    private var active = false
    private var routes = emptySet<Int>()
    private var receiverRegistered = false
    private var devicesRegistered = false
    private var focus: AudioFocusRequest? = null
    private val lease = FocusLease()
    private val noisy = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (active && intent?.action == AudioManager.ACTION_AUDIO_BECOMING_NOISY) interrupted()
        }
    }
    private val deviceCallback = object : AudioDeviceCallback() {
        override fun onAudioDevicesAdded(addedDevices: Array<out AudioDeviceInfo>) = changed()
        override fun onAudioDevicesRemoved(removedDevices: Array<out AudioDeviceInfo>) = changed()
        private fun changed() {
            val current = (manager.getDevices(AudioManager.GET_DEVICES_INPUTS) + manager.getDevices(AudioManager.GET_DEVICES_OUTPUTS)).map { it.id }.toSet()
            if (active && current != routes) interrupted()
        }
    }
    fun acquire(): Boolean {
        release()
        val generation = lease.begin()
        val request = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
            .setAudioAttributes(speechAudioAttributes())
            .setOnAudioFocusChangeListener({ change ->
                if (active && lease.accepts(generation) && change < 0) {
                    diagnostic?.invoke(when (change) {
                        AudioManager.AUDIOFOCUS_LOSS -> "focus_loss"
                        AudioManager.AUDIOFOCUS_LOSS_TRANSIENT -> "focus_transient_loss"
                        else -> "focus_duck_loss"
                    })
                    interrupted()
                }
            }, handler).setWillPauseWhenDucked(true).build()
        focus = request
        try {
            if (manager.requestAudioFocus(request) != AudioManager.AUDIOFOCUS_REQUEST_GRANTED) {
                diagnostic?.invoke("focus_request_rejected")
                release(); return false
            }
            diagnostic?.invoke("focus_request_granted")
            active = true
            routes = (manager.getDevices(AudioManager.GET_DEVICES_INPUTS) + manager.getDevices(AudioManager.GET_DEVICES_OUTPUTS)).map { it.id }.toSet()
            manager.registerAudioDeviceCallback(deviceCallback, handler); devicesRegistered = true
            ContextCompat.registerReceiver(context, noisy, IntentFilter(AudioManager.ACTION_AUDIO_BECOMING_NOISY), ContextCompat.RECEIVER_NOT_EXPORTED)
            receiverRegistered = true
            return true
        } catch (_: Exception) { release(); return false }
    }
    fun release() {
        active = false; lease.end()
        if (devicesRegistered) { devicesRegistered = false; try { manager.unregisterAudioDeviceCallback(deviceCallback) } catch (_: Exception) { } }
        if (receiverRegistered) { receiverRegistered = false; try { context.unregisterReceiver(noisy) } catch (_: Exception) { } }
        val previous = focus; focus = null
        if (previous != null) try { manager.abandonAudioFocusRequest(previous) } catch (_: Exception) { }
    }
}

internal fun speechAudioAttributes(): AudioAttributes = AudioAttributes.Builder()
    .setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build()
