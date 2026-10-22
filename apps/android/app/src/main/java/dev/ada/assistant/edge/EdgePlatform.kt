package dev.ada.assistant.edge

import android.app.ActivityManager
import android.content.*
import android.os.*
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import dev.ada.assistant.BuildConfig
import dev.ada.assistant.data.SessionIdentity
import dev.ada.assistant.data.documentHash
import java.io.File
import java.io.InputStream
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.MessageDigest
import java.security.Signature
import java.security.spec.ECGenParameterSpec
import java.util.Base64
import java.util.UUID
import kotlinx.coroutines.*

const val EDGE_MODEL_ID="Qwen/Qwen3-0.6B-GGUF"
const val EDGE_MODEL_DIGEST="9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031"
const val EDGE_MODEL_BYTES=639446688L
const val EDGE_RUNTIME="llama.cpp-620d2225cc436ab0b001e3200e590e3b286ef9ab"
// Both measured candidates failed the frozen reply quality gate. No user activation.
const val EDGE_QUALITY_APPROVED=false
data class NativeDraft(val text:String,val truncated:Boolean,val elapsed:Long,val pssKiB:Int,val isolatedUid:Int=-1,val internetAllowed:Boolean=false) { override fun toString()="NativeDraft(redacted)" }

interface DraftPlatform {
    val supported:Boolean
    fun modelPresent():Boolean
    suspend fun generate(text:String):NativeDraft
    fun publicKey(who:SessionIdentity,create:Boolean=false):String?
    fun sign(who:SessionIdentity,message:ByteArray):String
}
class EdgePlatform(context:Context) : DraftPlatform {
    private val app=context.applicationContext
    private val model=File(app.filesDir,"edge/qwen3-0.6b-q8.gguf")
    override val supported:Boolean get()=BuildConfig.EDGE_RUNTIME && Build.VERSION.SDK_INT>=28 && "arm64-v8a" in Build.SUPPORTED_ABIS
    override fun modelPresent()=model.isFile && model.length()==EDGE_MODEL_BYTES
    suspend fun importModel(stream:InputStream)=withContext(Dispatchers.IO) {
        require(supported)
        model.parentFile!!.mkdirs()
        require(model.parentFile!!.usableSpace>=EDGE_MODEL_BYTES*2)
        val partial=File(model.parentFile,"candidate.part")
        try {
            val digest=MessageDigest.getInstance("SHA-256");var size=0L
            stream.use { input -> partial.outputStream().use { output ->
                val buffer=ByteArray(262144)
                while(true) { ensureActive();val count=input.read(buffer);if(count<0)break;size+=count;require(size<=EDGE_MODEL_BYTES);digest.update(buffer,0,count);output.write(buffer,0,count) }
            } }
            require(size==EDGE_MODEL_BYTES && digest.digest().joinToString("") { "%02x".format(it) }==EDGE_MODEL_DIGEST)
            require(partial.renameTo(model))
        } finally { partial.delete() }
    }
    fun removeModel() { require(!model.exists() || model.delete()) }
    private fun alias(who:SessionIdentity)="ada-edge-"+documentHash((who.server+"\n"+who.owner).toByteArray())
    private fun keys()=KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    override fun publicKey(who:SessionIdentity,create:Boolean):String? {
        val alias=alias(who);var store=keys()
        if(!store.containsAlias(alias) && create) {
            KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC,"AndroidKeyStore").apply { initialize(KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY).setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1")).setDigests(KeyProperties.DIGEST_SHA256).build()) }.generateKeyPair()
            store=keys()
        }
        return store.getCertificate(alias)?.publicKey?.encoded?.let { Base64.getEncoder().encodeToString(it) }
    }
    override fun sign(who:SessionIdentity,message:ByteArray):String {
        val key=keys().getKey(alias(who),null) as java.security.PrivateKey
        return Base64.getEncoder().encodeToString(Signature.getInstance("SHA256withECDSA").apply { initSign(key);update(message) }.sign())
    }
    override suspend fun generate(text:String):NativeDraft=withContext(Dispatchers.Main) {
        require(supported && modelPresent() && text.toByteArray().size in 1..1500)
        val memory=ActivityManager.MemoryInfo();app.getSystemService(ActivityManager::class.java).getMemoryInfo(memory)
        require(!memory.lowMemory && memory.availMem>=1024L*1024*1024)
        if(Build.VERSION.SDK_INT>=29) require(app.getSystemService(PowerManager::class.java).currentThermalStatus<PowerManager.THERMAL_STATUS_MODERATE)
        val battery=app.registerReceiver(null,IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        require((battery?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE,Int.MAX_VALUE) ?: Int.MAX_VALUE)<420)
        withContext(Dispatchers.IO) { require(model.inputStream().use { MessageDigest.getInstance("SHA-256").let { digest -> val buffer=ByteArray(262144);while(true){ensureActive();val n=it.read(buffer);if(n<0)break;digest.update(buffer,0,n)};digest.digest().joinToString(""){ b -> "%02x".format(b) } } }==EDGE_MODEL_DIGEST) }
        val prompt="<|im_start|>system\nWrite a short draft message in the user's first person. Return only the message, at most two short sentences. Follow every constraint. Use only supplied information. Do not invent reasons, identity, dates or commitments. Never claim an external action has happened. /no_think<|im_end|>\n<|im_start|>user\n$text /no_think<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        val request=UUID.randomUUID().toString();val deferred=CompletableDeferred<NativeDraft>()
        val descriptor=ParcelFileDescriptor.open(model,ParcelFileDescriptor.MODE_READ_ONLY)
        val reply=Messenger(Handler(Looper.getMainLooper()) { message ->
            val data=message.data
            if(data.getString("request")==request && !deferred.isCompleted) {
                if(data.containsKey("error")) deferred.completeExceptionally(java.io.IOException("Local draft unavailable"))
                else {
                    val result=NativeDraft(data.getString("text").orEmpty(),data.getBoolean("truncated"),data.getLong("elapsed"),data.getInt("pss"),data.getInt("uid",-1),data.getBoolean("internet",true))
                    if(result.pssKiB>768*1024 || result.elapsed>20000 || result.text.isBlank() || result.isolatedUid<0 || result.isolatedUid==Process.myUid() || result.internetAllowed) deferred.completeExceptionally(java.io.IOException("Local resource limit reached")) else deferred.complete(result)
                }
            };true
        })
        val connection=object:ServiceConnection {
            override fun onServiceConnected(name:ComponentName,service:IBinder) {
                try { Messenger(service).send(Message.obtain(null,1).apply { replyTo=reply;data=Bundle().apply { putString("request",request);putByteArray("prompt",prompt.toByteArray());putParcelable("model",descriptor) } }) }
                catch(_:Exception) { deferred.completeExceptionally(java.io.IOException("Local service unavailable")) }
            }
            override fun onServiceDisconnected(name:ComponentName) { deferred.completeExceptionally(java.io.IOException("Local service stopped")) }
            override fun onBindingDied(name:ComponentName) { deferred.completeExceptionally(java.io.IOException("Local service stopped")) }
            override fun onNullBinding(name:ComponentName) { deferred.completeExceptionally(java.io.IOException("Local service unavailable")) }
        }
        var bound=false
        try { bound=app.bindService(Intent(app,NativeDraftService::class.java),connection,Context.BIND_AUTO_CREATE);require(bound);withTimeout(25000){deferred.await()} }
        finally { if(bound)app.unbindService(connection);descriptor.close() }
    }
}
