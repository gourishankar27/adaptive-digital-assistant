package dev.ada.assistant.audio

import java.io.ByteArrayInputStream
import java.security.MessageDigest
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test

/** No model/runtime download or native execution: these are hostile metadata/stream fixtures. */
class LocalSpeechManifestTest {
    private val bytes = "synthetic inert model".toByteArray()
    private fun hash(value: ByteArray) = MessageDigest.getInstance("SHA-256").digest(value).joinToString("") { "%02x".format(it) }
    private fun manifest() = LocalSpeechManifest(
        modelId = "synthetic-en-v1", adapterId = "test.asr.v1", task = SpeechTask.Asr,
        runtimeRevision = "test-runtime-1", minimumApi = 26, abis = listOf("arm64-v8a"),
        languages = listOf("en-US"), quantization = "int8", licenseReview = "synthetic-review-1",
        files = listOf(SpeechModelFile("model.onnx", bytes.size.toLong(), hash(bytes), "Apache-2.0")),
    )
    private fun check(value: LocalSpeechManifest = manifest(), content: ByteArray = bytes) {
        val raw = Json.encodeToString(value).toByteArray()
        val result = verifyLocalSpeechBundle(raw, hash(raw)) { ByteArrayInputStream(content) }
        assertEquals(value, result)
    }
    private fun rejected(block: () -> Unit) {
        try { block(); fail("Hostile bundle accepted") } catch (_: IllegalArgumentException) { }
    }
    @Test fun pinnedManifestAndEveryExactByteAreVerifiedWithoutActivatingAnything() { check() }
    @Test fun manifestCannotAuthorizeItsOwnDigestOrExecutablePlugin() {
        val raw = Json.encodeToString(manifest()).toByteArray()
        rejected { verifyLocalSpeechBundle(raw, "0".repeat(64)) { error("Must reject before opening files") } }
        for (name in listOf("engine.so", "plugin.dex", "program.exe", "script.py")) {
            rejected { check(manifest().copy(files = listOf(manifest().files.single().copy(path = name)))) }
        }
    }
    @Test fun windowsAndArchiveTraversalAndAmbiguousPathsAreRejectedBeforeReading() {
        for (name in listOf("../model.onnx", "/model.onnx", "C:/model.onnx", "a\\model.onnx", "a//model.onnx", "./model.onnx", "CON.txt", "aux.onnx", "a /model.onnx", "a/model.onnx.", "a:stream.onnx")) {
            val raw = Json.encodeToString(manifest().copy(files = listOf(manifest().files.single().copy(path = name)))).toByteArray()
            rejected { verifyLocalSpeechBundle(raw, hash(raw)) { error("Must reject before opening files") } }
        }
        rejected { check(manifest().copy(files = listOf(manifest().files.single(), manifest().files.single().copy(path = "MODEL.onnx")))) }
    }
    @Test fun corruptPartialOversizedAndTrailingDataNeverVerify() {
        for (value in listOf(bytes.dropLast(1).toByteArray(), bytes + 0, ByteArray(bytes.size))) rejected { check(content = value) }
        rejected { check(manifest().copy(files = listOf(manifest().files.single().copy(bytes = Long.MAX_VALUE)))) }
        rejected { check(manifest().copy(files = emptyList())) }
    }
    @Test fun unknownVersionsFieldsLanguagesAndRuntimeMetadataFailClosed() {
        for (value in listOf(manifest().copy(version = 2), manifest().copy(adapterId = "shell/exec"),
            manifest().copy(minimumApi = 0), manifest().copy(abis = listOf("unknown")),
            manifest().copy(languages = listOf("en_US")), manifest().copy(licenseReview = ""))) rejected { check(value) }
        val raw = Json.encodeToString(manifest()).dropLast(1).plus(",\"entrypoint\":\"evil.so\"}").toByteArray()
        rejected { verifyLocalSpeechBundle(raw, hash(raw)) { error("Must reject unknown fields") } }
    }
    @Test fun metadataNeverCreatesActivationPermissionOnAnyDevice() {
        val value = manifest()
        assertEquals(SpeechModelReadiness.AwaitingDeviceValidation, value.readiness(36, "arm64-v8a", "en-US"))
        assertEquals(SpeechModelReadiness.Unsupported, value.readiness(25, "arm64-v8a", "en-US"))
        assertEquals(SpeechModelReadiness.Unsupported, value.readiness(36, "x86_64", "en-US"))
        assertEquals(SpeechModelReadiness.Unsupported, value.readiness(36, "arm64-v8a", "hi-IN"))
    }
}
