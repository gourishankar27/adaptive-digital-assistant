package dev.ada.assistant.audio

import android.app.Activity
import android.content.ComponentName
import android.content.Intent
import android.media.AudioManager
import android.os.*
import android.widget.*
import dev.ada.assistant.BuildConfig
import dev.ada.assistant.ui.SpeechVoice
import org.json.JSONArray
import org.json.JSONObject

/** Public synthetic playback only, available exclusively in the isolated validation package. */
class AudioFocusProbeActivity : Activity() {
    private var playback: AndroidSpeechPlayback? = null
    private var voices = emptyList<SpeechVoice>()
    private val handler = Handler(Looper.getMainLooper())
    private var generation = 0L
    private var pendingGain: Int? = null
    private var state = "idle"
    private val events = mutableListOf<JSONObject>()
    private lateinit var status: TextView
    private fun record(event: String) {
        val instant = SystemClock.elapsedRealtime()
        if (events.size < 32) events += JSONObject().put("event", event).put("at_ms", instant)
        java.io.File(filesDir, "native-focus-result.json").writeText(JSONObject()
            .put("state", state).put("at_ms", instant).put("events", JSONArray(events)).toString())
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!BuildConfig.APPLICATION_ID.startsWith("dev.ada.validation.")) { finish(); return }
        status = TextView(this).apply { text = "Loading installed offline English voice" }
        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; addView(status) }
        val adapter = AndroidSpeechPlayback(this) { event ->
            if (event == "utterance_started") {
                state = "speaking"; status.text = "Native engine started. Audible state needs human confirmation."
                pendingGain?.let { gain ->
                    pendingGain = null; val run = generation
                    handler.postDelayed({
                        if (run == generation && state == "speaking") {
                            record("focus_holder_launch")
                            try { startActivity(Intent().setComponent(ComponentName("dev.ada.validation.focus.debug", "dev.ada.validation.focus.FocusActivity"))
                                .putExtra("autoGain", gain).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
                            catch (_: Exception) { state = "fixture_unavailable"; record("fixture_unavailable"); status.text = "Focus fixture unavailable; inconclusive trial" }
                        }
                    }, 2000)
                }
            }
            record(event)
        }
        playback = adapter
        adapter.initialize { installed -> voices = installed.filter { it.language.equals("en-US", true) }; status.text = "Eligible offline voices: ${voices.size}" }
        fun button(label: String, gain: Int?) { layout.addView(Button(this).apply { text = label; setOnClickListener { play(gain) } }) }
        button("Play public focus sample", null)
        button("Play + full focus", AudioManager.AUDIOFOCUS_GAIN)
        button("Play + transient focus", AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
        button("Play + duck focus", AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK)
        layout.addView(Button(this).apply { text = "Stop sample"; setOnClickListener {
            generation++; pendingGain = null; handler.removeCallbacksAndMessages(null)
            adapter.stop(); state = "stopped"; record("explicit_stop"); status.text = "Native adapter explicitly stopped"
        } })
        setContentView(layout)
    }
    private fun play(gain: Int?) {
        val voice = voices.firstOrNull() ?: return
        generation++; events.clear(); pendingGain = gain; state = "play_requested"; record("explicit_play")
        status.text = "Playback requested; wait for native engine start"
        val run = generation
        playback!!.play(("The blue notebook is beside the green cup. ").repeat(40), voice.id, 1f) { error ->
            if (run == generation) {
                state = if (error == null) "completed" else "interrupted"; record(state)
                status.text = if (error == null) "Native adapter completed" else "Native adapter interruption/error callback"
            }
        }
    }
    // No pause-stop: isolate focus from MainActivity lifecycle cleanup. Debug fixture only.
    override fun onDestroy() { generation++; handler.removeCallbacksAndMessages(null); playback?.close(); playback = null; super.onDestroy() }
}
