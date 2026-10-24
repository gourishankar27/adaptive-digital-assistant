package dev.ada.assistant

import android.app.Activity
import android.os.Bundle
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.EditText
import android.widget.ScrollView
import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
import dev.ada.assistant.ui.CaptureListener
import dev.ada.assistant.data.*
import java.util.UUID
import dev.ada.assistant.audio.*
import dev.ada.assistant.ui.VOICE_PREVIEW_TEXT
import kotlinx.coroutines.*

/** Separate validation packages only. Fixed public samples, no credentials/private history. */
class PrivateVoiceReviewActivity : Activity() {
    private var player: NeuralSpeechPlayback?=null
    private lateinit var status: TextView
    private var capture: ContinuousSpeechCapture?=null
    private lateinit var words: EditText
    private var runtime: LocalSpeechRuntime?=null
    private val review=CoroutineScope(SupervisorJob()+Dispatchers.Main)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if(!packageName.startsWith("dev.ada.validation.")) { finish(); return }
        window.setFlags(WindowManager.LayoutParams.FLAG_SECURE,WindowManager.LayoutParams.FLAG_SECURE)
        val runtime=LocalSpeechFactory.create(applicationContext).also { this.runtime=it }
        val layout=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(24,64,24,24) }
        status=TextView(this).apply { text="Public local voice review · no private data\nChoose a sample when ready. Stop is independent of server generation."; textSize=20f }
        layout.addView(status)
        player=NeuralSpeechPlayback(this,runtime)
        for((id,label) in listOf(1 to "Bella",2 to "Nicole",3 to "Sarah",4 to "Sky")) {
            layout.addView(Button(this).apply { text="Play $label"; isEnabled=runtime.installed
                setOnClickListener {
                    status.text="Playing $label · local neural public sample"
                    player?.play(VOICE_PREVIEW_TEXT,"neural/$id",1f) { error -> status.text=if(error==null) "$label finished" else "$label stopped or interrupted" }
                }
            })
        }
        layout.addView(Button(this).apply { text="Stop sample"; setOnClickListener { player?.stop(); status.text="Stopped" } })
        words=EditText(this).apply { hint="Editable public transcript · nothing is sent or saved"; minLines=2; maxLines=4 }
        layout.addView(words)
        capture=ContinuousSpeechCapture(this,runtime)
        layout.addView(Button(this).apply { text="Record public phrase"; setOnClickListener {
            if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO),32); return@setOnClickListener }
            player?.stop(); status.text="Starting public local microphone test…"
            capture?.start("en-US",object:CaptureListener {
                override fun ready() { status.text="Recording until Stop · silence does not end capture" }
                override fun ended() { status.text="Stopped · finishing public transcript" }
                override fun partial(text:String) { words.setText(text) }
                // Explicit public, memory-only fixture. Production uses authenticated encrypted checkpoints.
                override fun checkpoint(segments:List<TranscriptSegmentDto>,duration:Long,saved:(Boolean)->Unit) { saved(true) }
                override fun result(text:String) { words.setText(text); status.text="Public transcript ready · editable · nothing sent" }
                override fun failed(code:String) { status.text="Public recording stopped ($code) · nothing sent" }
            })
        } })
        layout.addView(Button(this).apply { text="Stop recording"; setOnClickListener { capture?.stop() } })
        val wakeState=TextView(this).apply {text="Wake not armed";textSize=18f}
        layout.addView(wakeState)
        review.launch {HelloAdaService.status.collect {wakeState.text=it}}
        layout.addView(Button(this).apply { text="Arm public Hello Ada test"; setOnClickListener {
            val permissions=mutableListOf(Manifest.permission.RECORD_AUDIO)
            if(android.os.Build.VERSION.SDK_INT>=33) permissions+=Manifest.permission.POST_NOTIFICATIONS
            if(permissions.any { checkSelfPermission(it)!=PackageManager.PERMISSION_GRANTED }) { requestPermissions(permissions.toTypedArray(),33); return@setOnClickListener }
            capture?.cancel(); player?.stop()
            WakeAuthority.arm(WakeAuthority.Grant(SessionIdentity("https://validation.invalid/",UUID(0,32)),UUID(0,32),UUID(0,32),0,System.currentTimeMillis()+900000))
            ContextCompat.startForegroundService(this@PrivateVoiceReviewActivity,Intent(this@PrivateVoiceReviewActivity,HelloAdaService::class.java))
            status.text="Wait for Armed below before saying Hello Ada · Home/lock allowed · Stop ends it · no private access"
        } })
        layout.addView(Button(this).apply { text="Stop wake listening"; setOnClickListener { WakeAuthority.revoke(); stopService(Intent(this@PrivateVoiceReviewActivity,HelloAdaService::class.java)); status.text="Wake listening stopped" } })
        layout.addView(Button(this).apply { text="Finish review"; setOnClickListener { player?.stop(); capture?.cancel(); WakeAuthority.revoke(); finish() } })
        setContentView(ScrollView(this).apply { addView(layout) })
    }
    override fun onPause() { player?.stop(); capture?.cancel(); super.onPause() }
    override fun onDestroy() { review.cancel(); player?.close(); capture?.close(); if(isFinishing) WakeAuthority.revoke(); super.onDestroy() }
}
