package dev.ada.assistant.audio

import android.content.Context
import android.system.Os
import android.system.OsConstants
import dev.ada.assistant.BuildConfig
import dev.ada.assistant.data.voiceHash
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.security.MessageDigest
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable private data class PackagedFile(val path: String, val bytes: Long, val sha256: String)
@Serializable private data class PackagedCatalogue(val version: Int, val runtime: String, val purpose: String, val files: List<PackagedFile>)

/** Only pinned APK data can be copied. No URI, archive, download, executable or external path. */
class PackagedSpeechModels(private val context: Context) {
    companion object { private val leases=Any(); private var readers=0 }
    private val root=File(context.noBackupFilesDir.canonicalFile,"private-speech-v1")
    private val staging=File(context.noBackupFilesDir.canonicalFile,"private-speech-staging-v1")
    val installed get() = root.isDirectory && File(root,"ready").isFile
    private fun catalogue(): Pair<ByteArray,PackagedCatalogue> {
        val raw=context.assets.open("speech-models/catalogue.json").use { it.readBytes() }
        require(raw.size<=256*1024 && MessageDigest.getInstance("SHA-256").digest(raw).joinToString("") { "%02x".format(it) }==BuildConfig.SPEECH_CATALOGUE_SHA)
        val model=Json.decodeFromString<PackagedCatalogue>(raw.toString(Charsets.UTF_8))
        require(model.version==1 && model.runtime=="sherpa-onnx-1.13.8" && model.purpose=="local-evaluation" && model.files.size in 1..512)
        require(model.files.all { f -> f.path.split('/').all { it.matches(Regex("[A-Za-z0-9_+.! -]+")) && it!="." && it!=".." } && f.bytes in 1..512L*1024*1024 })
        require(model.files.sumOf { it.bytes }<=600L*1024*1024)
        return raw to model
    }
    private fun checkedFile(base: File, relative: String): File {
        val file=File(base,relative)
        require(file.canonicalPath==file.absolutePath && file.canonicalPath.startsWith(base.canonicalPath+File.separator))
        return file
    }
    @Synchronized fun install() {
        if(installed) { verify(); return }
        val (_,cat)=catalogue()
        require(context.noBackupFilesDir.usableSpace>cat.files.sumOf { it.bytes }+64L*1024*1024)
        require(!VoiceAudioCoordinator.busy())
        staging.deleteRecursively(); require(staging.mkdirs())
        try {
            for(entry in cat.files) {
                val destination=checkedFile(staging,entry.path); require(destination.parentFile!!.mkdirs() || destination.parentFile!!.isDirectory)
                context.assets.open("speech-models/${entry.path}").use { source -> FileOutputStream(destination).use { output ->
                    val buffer=ByteArray(32768); var total=0L
                    while(true) { val size=source.read(buffer); if(size<0) break; total+=size; require(total<=entry.bytes); output.write(buffer,0,size) }
                    require(total==entry.bytes); output.fd.sync()
                } }
                checkBytes(destination,entry)
            }
            File(staging,"ready").writeText(BuildConfig.SPEECH_CATALOGUE_SHA)
            require(!root.exists()); require(staging.renameTo(root))
        } finally { staging.deleteRecursively() }
    }
    @Synchronized fun verify(group: String?=null) {
        require(installed && File(root,"ready").readText()==BuildConfig.SPEECH_CATALOGUE_SHA)
        catalogue().second.files.filter { group==null || it.path.startsWith("$group/") }.forEach { checkBytes(checkedFile(root,it.path),it) }
    }
    private fun checkBytes(file: File, expected: PackagedFile) {
        require(Os.lstat(file.path).st_mode and OsConstants.S_IFMT==OsConstants.S_IFREG && file.length()==expected.bytes)
        val hash=MessageDigest.getInstance("SHA-256")
        FileInputStream(file).use { source -> val buf=ByteArray(32768); var total=0L
            while(true) { val size=source.read(buf); if(size<0) break; total+=size; require(total<=expected.bytes); hash.update(buf,0,size) }
            require(total==expected.bytes)
        }
        require(hash.digest().joinToString("") { "%02x".format(it) }==expected.sha256)
    }
    fun beginUse(group: String) = synchronized(leases) { verify(group); readers++ }
    fun endUse() = synchronized(leases) { require(readers>0); readers-- }
    fun remove() = synchronized(leases) { require(!VoiceAudioCoordinator.busy() && readers==0); require(!root.exists() || root.deleteRecursively()); staging.deleteRecursively(); Unit }
    fun path(relative: String): String = checkedFile(root,relative).absolutePath
}
