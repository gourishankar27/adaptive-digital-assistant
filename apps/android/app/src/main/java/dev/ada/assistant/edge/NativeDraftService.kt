package dev.ada.assistant.edge

import android.app.Service
import android.content.Intent
import android.os.*
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.util.concurrent.atomic.AtomicBoolean

internal object NativeDraftBridge {
    external fun generate(fd: Int, prompt: ByteArray): ByteArray
}

/** Runs under a separate isolated UID, with no app storage, Keystore or network permission. */
class NativeDraftService : Service() {
    private val busy=AtomicBoolean(false)
    private val handler=Handler(Looper.getMainLooper())
    private val messenger=Messenger(Handler(Looper.getMainLooper()) { message ->
        if(message.what!=1 || !busy.compareAndSet(false,true)) return@Handler true
        val reply=message.replyTo ?: return@Handler true
        val data=message.data
        data.classLoader=ParcelFileDescriptor::class.java.classLoader
        @Suppress("DEPRECATION") val model=data.getParcelable<ParcelFileDescriptor>("model")
        val prompt=data.getByteArray("prompt")
        val request=data.getString("request")
        val watchdog=Runnable { Process.killProcess(Process.myPid()) }
        handler.postDelayed(watchdog,22_000)
        Thread {
            val result=Bundle()
            result.putString("request",request)
            try {
                require(model!=null && prompt!=null && prompt.size in 1..2000)
                System.loadLibrary("ada_edge")
                val started=SystemClock.elapsedRealtime()
                val output=NativeDraftBridge.generate(model.fd,prompt)
                require(output.size in 2..12001)
                val text=Charsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(output,1,output.size-1)).toString()
                require(text.isNotBlank() && !text.contains("<think>") && !text.contains('\u0000'))
                result.putString("text",text);result.putBoolean("truncated",output[0].toInt()!=1)
                result.putLong("elapsed",SystemClock.elapsedRealtime()-started)
                result.putInt("pss",Debug.getPss().coerceAtMost(Int.MAX_VALUE.toLong()).toInt())
                result.putInt("uid",Process.myUid())
                result.putBoolean("internet",checkSelfPermission(android.Manifest.permission.INTERNET)==android.content.pm.PackageManager.PERMISSION_GRANTED)
            } catch(_:Throwable) { result.putString("error","Local draft unavailable or resource limit reached") }
            finally { model?.close();handler.removeCallbacks(watchdog) }
            try { reply.send(Message.obtain(null,2).apply { this.data=result }) } catch(_:Exception) { }
        }.start()
        true
    })
    override fun onBind(intent:Intent):IBinder=messenger.binder
    override fun onUnbind(intent:Intent?):Boolean {
        // This service is manifest-isolated. Unbinding terminates its native computation.
        Process.killProcess(Process.myPid());return false
    }
}
