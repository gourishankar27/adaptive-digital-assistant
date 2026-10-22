package dev.ada.assistant.audio

import java.io.InputStream
import java.security.MessageDigest
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

const val PLATFORM_ASR_ADAPTER = "android.on-device-asr.v1"
const val PLATFORM_TTS_ADAPTER = "android.offline-tts.v1"

@Serializable enum class SpeechTask { Asr, Tts }
enum class SpeechModelReadiness { Unsupported, AwaitingDeviceValidation }

/** Local capability metadata only. Neither a voice name nor this ID attests recognition. */
data class SpeechAdapterInfo(val id: String, val task: SpeechTask, val modelStatus: String = "Managed by Android; model files are not inspected by ADA")

@Serializable data class SpeechModelFile(val path: String, val bytes: Long, val sha256: String, val license: String)

/** Versioned study contract, NOT an installer or a permission to execute model-supplied code. */
@Serializable data class LocalSpeechManifest(
    val version: Int = 1, val modelId: String, val adapterId: String, val task: SpeechTask,
    val runtimeRevision: String, val minimumApi: Int, val abis: List<String>,
    val languages: List<String>, val quantization: String, val licenseReview: String,
    val files: List<SpeechModelFile>,
) {
    fun readiness(api: Int, abi: String, language: String): SpeechModelReadiness =
        if (api < minimumApi || abi !in abis || languages.none { it.equals(language, true) }) SpeechModelReadiness.Unsupported
        else SpeechModelReadiness.AwaitingDeviceValidation
}

private val digestPattern = Regex("[0-9a-f]{64}")
private val identifierPattern = Regex("[a-zA-Z0-9][a-zA-Z0-9._-]{0,119}")
private val portableSegment = Regex("[a-zA-Z0-9][a-zA-Z0-9._-]{0,99}")
private val reservedWindowsName = Regex("(?i)(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\\..*)?")
private val speechManifestJson = Json { ignoreUnknownKeys = false; isLenient = false; coerceInputValues = false }
private const val MAX_BUNDLE_BYTES = 1024L * 1024 * 1024
private fun digest(value: ByteArray) = MessageDigest.getInstance("SHA-256").digest(value).joinToString("") { "%02x".format(it) }

/**
 * expectedManifestSha256 must come from a separately reviewed, pinned catalogue, never the
 * import itself. There are NO approved bundles or native runtimes in this release.
 * openFile must supply plain files from an isolated staging snapshot; never unpack archives,
 * follow links or pass an untrusted URI here. Reads are bounded and every stream is closed.
 * A successful check verifies metadata/bytes only; it does not install, load or activate.
 */
internal fun verifyLocalSpeechBundle(rawManifest: ByteArray, expectedManifestSha256: String, openFile: (String) -> InputStream): LocalSpeechManifest {
    require(rawManifest.size in 1..16_384 && digestPattern.matches(expectedManifestSha256))
    require(digest(rawManifest) == expectedManifestSha256)
    val manifest = speechManifestJson.decodeFromString<LocalSpeechManifest>(rawManifest.toString(Charsets.UTF_8))
    require(manifest.version == 1 && identifierPattern.matches(manifest.modelId) && identifierPattern.matches(manifest.adapterId))
    require(identifierPattern.matches(manifest.runtimeRevision) && identifierPattern.matches(manifest.licenseReview))
    require(manifest.minimumApi in 26..100 && manifest.abis.size in 1..3 && manifest.abis.distinct().size == manifest.abis.size)
    require(manifest.abis.all { it in setOf("arm64-v8a", "armeabi-v7a", "x86_64") })
    require(manifest.languages.size in 1..32 && manifest.languages.all { dev.ada.assistant.data.voiceLanguageValid(it) })
    require(manifest.quantization in setOf("fp32", "fp16", "int8", "q5_1"))
    require(manifest.files.size in 1..32)
    require(manifest.files.map { it.path.lowercase(java.util.Locale.ROOT) }.distinct().size == manifest.files.size)
    var total = 0L
    for (file in manifest.files) {
        require(file.bytes in 1..MAX_BUNDLE_BYTES && file.bytes <= MAX_BUNDLE_BYTES - total)
        total += file.bytes
        require(file.path.length <= 200 && file.path.split('/').all {
            portableSegment.matches(it) && !it.endsWith('.') && !reservedWindowsName.matches(it)
        })
        require(file.path.substringAfterLast('.').lowercase() in setOf("onnx", "bin", "txt", "json", "license"))
        require(digestPattern.matches(file.sha256) && identifierPattern.matches(file.license))
    }
    // Validate ALL paths/bounds before a single caller-supplied file can be opened.
    for (file in manifest.files) {
        val hash = MessageDigest.getInstance("SHA-256")
        val buffer = ByteArray(32 * 1024)
        var read = 0L
        openFile(file.path).use { stream ->
            while (read < file.bytes) {
                val count = stream.read(buffer, 0, minOf(buffer.size.toLong(), file.bytes - read).toInt())
                require(count > 0)
                hash.update(buffer, 0, count); read += count
            }
            require(stream.read() == -1)
        }
        require(hash.digest().joinToString("") { "%02x".format(it) } == file.sha256)
    }
    return manifest
}
