package dev.ada.assistant.audio

import android.Manifest
import android.app.*
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.media.*
import android.os.*
import androidx.core.app.NotificationCompat
import dev.ada.assistant.MainActivity
import dev.ada.assistant.R
import dev.ada.assistant.BuildConfig
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.data.HttpAdaApi
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.concurrent.atomic.AtomicBoolean

/** Explicit visible-start foreground mic. A wake emits only a nonprivate cue/open notification. */
class HelloAdaService : Service() {
    companion object {
        const val STOP="dev.ada.assistant.STOP_HELLO_ADA"
        private const val CHANNEL="ada-hello-ada-v1"
        private const val NOTIFICATION=3201
        private val mutable=MutableStateFlow("Not armed")
        val status=mutable.asStateFlow()
        // Aggregate diagnostics only in the separate public validation package.
        @Volatile internal var publicFrames=0L
            private set
        @Volatile internal var publicPeak=0f
            private set
    }
    private val handler=Handler(Looper.getMainLooper())
    private val running=AtomicBoolean()
    private var record: AudioRecord?=null
    private var cpu: PowerManager.WakeLock?=null
    private var nextCue=0L
    @Volatile private var generation=0L
    private val auth=CoroutineScope(SupervisorJob()+Dispatchers.IO)
    private var authJob:Job?=null
    override fun onBind(intent: Intent?) = null
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if(intent?.action==STOP) { WakeAuthority.revoke(); stopSelf(); return START_NOT_STICKY }
        val authority=WakeAuthority.current()
        if(intent==null || authority==null || checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED ||
            (Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)) { stopSelf(); return START_NOT_STICKY }
        if(running.get()) return START_NOT_STICKY
        val key=++generation
        val runtime=LocalSpeechFactory.create(this)
        if(!runtime.installed || !VoiceAudioCoordinator.acquire(this,VoiceAudioCoordinator.Use.Wake) { stopListening("Paused for other audio; re-arm when ready",key) }) { stopSelf(); return START_NOT_STICKY }
        try {
            getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL,"Hello Ada microphone",NotificationManager.IMPORTANCE_LOW))
            if(Build.VERSION.SDK_INT>=29) startForeground(NOTIFICATION,notification("Starting local wake microphone…"),ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
            else startForeground(NOTIFICATION,notification("Starting local wake microphone…"))
            running.set(true); mutable.value="Starting local wake microphone…"
            if(BuildConfig.DEBUG && packageName.startsWith("dev.ada.validation.")) {publicFrames=0; publicPeak=0f}
            WakeAuthority.stopped={ handler.post { stopListening("Not armed",key) } }
            cpu=getSystemService(PowerManager::class.java).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"ADA:HelloAda").apply { setReferenceCounted(false); acquire((authority.expiresAt-System.currentTimeMillis()).coerceAtMost(900_000)) }
            Thread({ listen(runtime,authority,key) },"ada-local-wake").start()
            if(authority.persistent) authJob=auth.launch {
                val sessions=WakeSessionMaintainer(HttpAdaApi(),AndroidSessionStore(applicationContext),BuildConfig.DEBUG)
                while(isActive && running.get() && WakeAuthority.sameLease(authority)) {
                    val current=WakeAuthority.current() ?: break
                    val renewed=try { sessions.verify(current) } catch (_:Exception) { null }
                    if(renewed==null || !WakeAuthority.extend(current,renewed)) {
                        handler.post { stopListening("Not armed · sign in and re-arm",key) }; break
                    }
                    handler.post { if(key==generation && running.get()) cpu?.acquire(900000) }
                    delay(30000)
                }
            }
        } catch (_: Exception) { stopListening("Wake unavailable; open ADA to retry") }
        return START_NOT_STICKY
    }
    private fun notification(message: String): Notification {
        val open=PendingIntent.getActivity(this,3201,Intent(this,MainActivity::class.java),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val stop=PendingIntent.getService(this,3202,Intent(this,HelloAdaService::class.java).setAction(STOP),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        return NotificationCompat.Builder(this,CHANNEL).setSmallIcon(R.drawable.ic_ada_notification).setContentTitle("Hello Ada")
            .setContentText(message).setContentIntent(open).setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setOngoing(true).setSilent(true).addAction(0,"Stop listening",stop).build()
    }
    private fun listen(runtime: LocalSpeechRuntime, grant: WakeAuthority.Grant, key: Long) {
        var microphone: AudioRecord?=null
        try {
            runtime.wakeDetector().use { detector ->
                val minimum=AudioRecord.getMinBufferSize(16000,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT)
                require(minimum>0)
                microphone=AudioRecord.Builder().setAudioSource(MediaRecorder.AudioSource.VOICE_RECOGNITION)
                    .setAudioFormat(AudioFormat.Builder().setSampleRate(16000).setChannelMask(AudioFormat.CHANNEL_IN_MONO).setEncoding(AudioFormat.ENCODING_PCM_16BIT).build())
                    .setBufferSizeInBytes(maxOf(6400,minimum)).build()
                synchronized(this) { if(!running.get()) return; record=microphone; microphone!!.startRecording() }
                handler.post {if(key==generation && running.get()) {mutable.value="Armed · local wake only"; getSystemService(NotificationManager::class.java).notify(NOTIFICATION,notification("Listening locally for Hello Ada"))}}
                val pcm=ShortArray(320)
                var route:Int?=null
                while(running.get() && WakeAuthority.sameLease(grant)) {
                    require(!getSystemService(AudioManager::class.java).isMicrophoneMute)
                    if(Build.VERSION.SDK_INT>=29) require(microphone!!.activeRecordingConfiguration?.isClientSilenced!=true)
                    microphone!!.routedDevice?.id?.let { id -> require(route==null || route==id); route=id }
                    val count=microphone!!.read(pcm,0,pcm.size,AudioRecord.READ_BLOCKING)
                    if(!running.get()) break
                    require(count>0)
                    val samples=FloatArray(count) { pcm[it]/32768f }; pcm.fill(0)
                    if(BuildConfig.DEBUG && packageName.startsWith("dev.ada.validation.")) {publicFrames+=count; publicPeak=maxOf(publicPeak,samples.maxOf {kotlin.math.abs(it)})}
                    val wake=try { detector.accept(samples) } finally { samples.fill(0f) }
                    if(wake) handler.post { cue(key) }
                }
            }
        } catch (_: SecurityException) { /* Active permission removal stops this lease. */ }
        catch (_: Exception) { /* No audio, recognizer output or private error text logged. */ }
        finally {
            synchronized(this) { if(record===microphone) record=null }
            try { microphone?.stop() } catch (_: Exception) { }; microphone?.release()
            handler.post { stopListening("Not armed · reopen ADA to re-arm",key) }
        }
    }
    private fun cue(key: Long) {
        if(key!=generation) return
        if(!running.get() || WakeAuthority.current()==null || SystemClock.elapsedRealtime()<nextCue) return
        nextCue=SystemClock.elapsedRealtime()+5000
        mutable.value="Hello Ada detected · unlock and open ADA to record"
        getSystemService(NotificationManager::class.java).notify(NOTIFICATION,notification("Hello Ada heard · open ADA to continue"))
        @Suppress("DEPRECATION") val vibrator=getSystemService(VIBRATOR_SERVICE) as? Vibrator
        vibrator?.vibrate(VibrationEffect.createOneShot(80,VibrationEffect.DEFAULT_AMPLITUDE))
    }
    private fun stopListening(message: String, key: Long?=null) {
        if(key!=null && key!=generation) return
        generation++; running.set(false); mutable.value=message
        WakeAuthority.revoke()
        authJob?.cancel(); authJob=null
        synchronized(this) { try { record?.stop() } catch (_: Exception) { } }
        cpu?.let { if(it.isHeld) it.release() }; cpu=null
        VoiceAudioCoordinator.release(this)
        stopForeground(STOP_FOREGROUND_REMOVE); stopSelf()
    }
    override fun onTaskRemoved(rootIntent: Intent?) { WakeAuthority.revoke(); stopListening("Not armed · reopen ADA to re-arm"); super.onTaskRemoved(rootIntent) }
    override fun onDestroy() { WakeAuthority.stopped=null; stopListening("Not armed"); auth.cancel(); super.onDestroy() }
}
