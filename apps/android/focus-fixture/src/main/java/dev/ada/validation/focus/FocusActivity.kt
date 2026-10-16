package dev.ada.validation.focus

import android.app.Activity
import android.media.*
import android.os.*
import android.widget.*

/** Separate UID; no microphone, Internet, storage or account permission. */
class FocusActivity : Activity() {
    private lateinit var manager: AudioManager
    private lateinit var status: TextView
    private var focus: AudioFocusRequest? = null
    private var autoGain = 0
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        manager = getSystemService(AudioManager::class.java)
        autoGain = intent.getIntExtra("autoGain", 0).takeIf { it in 1..3 } ?: 0
        status = TextView(this).apply { text = "Foreground audio focus fixture. No audio is captured." }
        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; addView(status) }
        listOf("Request full focus" to AudioManager.AUDIOFOCUS_GAIN,
            "Request transient focus" to AudioManager.AUDIOFOCUS_GAIN_TRANSIENT,
            "Request duck focus" to AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK).forEach { (label, gain) ->
            layout.addView(Button(this).apply { text = label; setOnClickListener { acquire(gain) } })
        }
        layout.addView(Button(this).apply { text = "Release focus"; setOnClickListener { release(); status.text = "Focus released" } })
        setContentView(layout)
    }
    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus && autoGain != 0) {
            val gain = autoGain; autoGain = 0
            Handler(Looper.getMainLooper()).postDelayed({ if (hasWindowFocus() && !isFinishing) acquire(gain) }, 200)
        }
    }
    private fun acquire(gain: Int) {
        release()
        val request = AudioFocusRequest.Builder(gain).setAudioAttributes(AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
            .setOnAudioFocusChangeListener { status.text = "Fixture focus callback: $it" }.build()
        focus = request
        val result = manager.requestAudioFocus(request)
        status.text = if (result == AudioManager.AUDIOFOCUS_REQUEST_GRANTED) "OS focus granted · foreground UID" else "OS focus rejected · inconclusive interruption test"
        java.io.File(filesDir, "focus-result.json").writeText("{\"gain\":$gain,\"outcome\":$result,\"at_ms\":${SystemClock.elapsedRealtime()}}")
    }
    private fun release() { focus?.let { manager.abandonAudioFocusRequest(it) }; focus = null }
    override fun onPause() { release(); super.onPause() }
}
