@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.security.MessageDigest
import java.util.UUID
import kotlinx.serialization.Serializable

const val VOICE_PROTOCOL = "ada-reviewed-voice-v1"

@Serializable data class TranscriptInputDto(val transcript_id: UUID, val engine_id: String,
    val engine_version: String, val language: String, val duration_ms: Long, val original_text: String) {
    override fun toString() = "TranscriptInput(redacted)"
}
@Serializable data class ReviewedVoiceInputDto(val request_id: UUID, val content: String,
    val transcript: TranscriptInputDto, val review: String = "approve", val as_of: String? = null,
    val use_memory: Boolean = true, val use_documents: Boolean = false) {
    override fun toString() = "ReviewedVoiceInput(redacted)"
    companion object {
        fun from(message: PendingMessage) = ReviewedVoiceInputDto(message.body.request_id, message.body.content,
            requireNotNull(message.voiceTranscript), as_of = message.body.as_of,
            use_memory = message.body.use_memory, use_documents = message.body.use_documents)
    }
}
@Serializable data class VoiceDraft(val identity: SessionIdentity, val conversationId: UUID,
    val scopeId: UUID, val transcript: TranscriptInputDto, val reviewedText: String,
    val approved: Boolean = false) {
    override fun toString() = "VoiceDraft(redacted)"
}
@Serializable data class VoiceLineageDto(val request_id: UUID, val conversation_id: UUID, val scope_id: UUID,
    val transcript_id: UUID, val engine_id: String, val engine_version: String, val engine_metadata: String,
    val language: String, val duration_ms: Long, val original_text: String, val original_hash: String,
    val original_origin: String, val original_trust: String, val reviewed_text: String, val reviewed_hash: String,
    val reviewed_origin: String, val endorsement_source_version_id: UUID, val approved_at: Long,
    val audio_storage: String, val audio_sha256: String? = null) {
    override fun toString() = "VoiceLineage(redacted)"
    fun validate(conversation: UUID, scope: UUID) {
        require(conversation_id == conversation && scope_id == scope && approved_at >= 0)
        validateTranscript(TranscriptInputDto(transcript_id, engine_id, engine_version, language, duration_ms, original_text))
        require(original_origin == "asr_generated" && original_trust == "generated_interpretation" &&
            reviewed_origin == "user_reviewed" && engine_metadata == "client_reported" &&
            audio_storage == "not_received_by_server" && audio_sha256 == null)
        require(voiceTextValid(reviewed_text) && original_hash == voiceHash(original_text) && reviewed_hash == voiceHash(reviewed_text))
    }
}
fun CapabilitiesDto.hasVoiceInput() = voice_input == VOICE_PROTOCOL && !voice_audio_uploads && hasStreaming()
fun voiceTextValid(text: String): Boolean {
    if (text.isBlank() || text.contains('\u0000') || text.codePointCount(0, text.length) > 4000) return false
    var index = 0
    while (index < text.length) {
        val c = text[index++]
        if (c.isLowSurrogate()) return false
        if (c.isHighSurrogate() && (index >= text.length || !text[index++].isLowSurrogate())) return false
    }
    return true
}
fun voiceLanguageValid(language: String) = language.length <= 35 && Regex("[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8}){0,4}").matches(language)
fun validateTranscript(transcript: TranscriptInputDto) {
    require(transcript.engine_id == "android_on_device" && transcript.engine_version.length in 1..120 &&
        transcript.engine_version.all { it.code in 32..126 } && voiceLanguageValid(transcript.language) &&
        transcript.duration_ms in 1..60_000 && voiceTextValid(transcript.original_text))
}
fun validateVoiceDraft(draft: VoiceDraft) {
    validateTranscript(draft.transcript)
    require(voiceTextValid(draft.reviewedText))
}
fun voiceHash(text: String) = MessageDigest.getInstance("SHA-256").digest(text.toByteArray(Charsets.UTF_8))
    .joinToString("") { (it.toInt() and 255).toString(16).padStart(2, '0') }

/** Playback is plain completed reply text; private traces/ASR input are never passed here. */
fun safeSpeechText(response: String): String {
    val clean = response.replace(Regex("<think>.*?(?:</think>|$)", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL)), "")
        .replace(Regex("```.*?(?:```|$)", RegexOption.DOT_MATCHES_ALL), "")
        .replace(Regex("\\[([^]]+)]\\([^)]*\\)"), "$1")
        .replace(Regex("https?://\\S+"), "")
        .replace(Regex("`[^`]*`|<[^>]*>|\\[[MDC][1-9][0-9]*]"), "")
        .replace(Regex("[\\s]+"), " ").trim()
    return clean.take(12000).let { if (it.lastOrNull()?.isHighSurrogate() == true) it.dropLast(1) else it }
}
