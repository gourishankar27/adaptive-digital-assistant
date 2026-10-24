@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable

const val LONG_VOICE_PROTOCOL = "ada-long-reviewed-voice-v1"
const val LONG_VOICE_ENGINE = "sherpa_zipformer_en_v1"
const val LONG_VOICE_TEXT = 32768
const val LONG_VOICE_DURATION = 7_200_000L

@Serializable data class TranscriptSegmentDto(val id: UUID, val sequence: Int, val end_ms: Long, val text: String, val sha256: String) {
    override fun toString() = "TranscriptSegment(redacted)"
}
@Serializable data class LongTranscriptDto(val transcript_id: UUID, val engine_id: String, val engine_version: String,
    val model_sha256: String, val language: String, val duration_ms: Long, val segments: List<TranscriptSegmentDto>) {
    override fun toString() = "LongTranscript(redacted)"
}
@Serializable data class LongReviewedVoiceInputDto(val request_id: UUID, val content: String, val transcript: LongTranscriptDto,
    val reviewed_text: String, val context_start: Int, val context_end: Int, val data_epoch: Long,
    val review: String = "approve", val as_of: String? = null, val use_memory: Boolean = true, val use_documents: Boolean = false, val conversation_style: String = "listen") {
    override fun toString() = "LongReviewedVoiceInput(redacted)"
}
fun CapabilitiesDto.hasLongVoice() = long_voice_input == LONG_VOICE_PROTOCOL && hasVoiceInput()
@Serializable data class LongVoiceLineageDto(val protocol: String, val request_id: UUID, val conversation_id: UUID,
    val scope_id: UUID, val transcript: LongTranscriptDto, val reviewed_text: String, val reviewed_hash: String,
    val context_start: Int, val context_end: Int, val endorsement_source_version_id: UUID,
    val original_trust: String, val reviewed_origin: String, val engine_metadata: String, val audio_storage: String, val approved_at: Long) {
    override fun toString() = "LongVoiceLineage(redacted)"
    fun validate(cid: UUID, sid: UUID) {
        require(protocol==LONG_VOICE_PROTOCOL && conversation_id==cid && scope_id==sid && approved_at>=0)
        require(original_trust=="generated_interpretation" && reviewed_origin=="user_reviewed" && engine_metadata=="client_reported" && audio_storage=="not_received_by_server")
        validateTranscript(TranscriptInputDto(transcript.transcript_id,transcript.engine_id,transcript.engine_version,transcript.language,transcript.duration_ms,
            transcript.segments.joinToString(" ") { it.text },transcript.model_sha256,transcript.segments))
        require(voiceTextValid(reviewed_text,LONG_VOICE_TEXT) && voiceHash(reviewed_text)==reviewed_hash)
        require(context_start>=0 && context_end>context_start && context_end<=reviewed_text.codePointCount(0,reviewed_text.length) && context_end-context_start<=4000)
    }
}
fun TranscriptInputDto.isLong() = engine_id == LONG_VOICE_ENGINE
fun VoiceDraft.contextText(): String? {
    if (!transcript.isLong()) return reviewedText
    if (reviewedText.codePointCount(0, reviewedText.length) <= 4000) return reviewedText.takeIf { voiceTextValid(it) }
    val start = contextStart ?: return null; val end = contextEnd ?: return null
    if (start < 0 || end <= start || end > reviewedText.codePointCount(0, reviewedText.length)) return null
    return reviewedText.substring(reviewedText.offsetByCodePoints(0,start), reviewedText.offsetByCodePoints(0,end)).takeIf { voiceTextValid(it) }
}
fun longVoiceRequest(message: PendingMessage): LongReviewedVoiceInputDto {
    val t = requireNotNull(message.voiceTranscript); require(t.isLong()); validateTranscript(t)
    val reviewed = requireNotNull(message.longReviewedText)
    val start = message.longContextStart
    val end = start + message.body.content.codePointCount(0,message.body.content.length)
    require(message.longConversationStyle in setOf("listen","questions","suggestions"))
    require(voiceTextValid(reviewed, LONG_VOICE_TEXT))
    require(start >= 0 && end <= reviewed.codePointCount(0, reviewed.length))
    require(reviewed.substring(reviewed.offsetByCodePoints(0,start), reviewed.offsetByCodePoints(0,end)) == message.body.content)
    return LongReviewedVoiceInputDto(message.body.request_id,message.body.content,
        LongTranscriptDto(t.transcript_id,t.engine_id,t.engine_version,requireNotNull(t.modelSha256),t.language,t.duration_ms,t.segments),
        reviewed,start,end,requireNotNull(message.longDataEpoch),as_of=message.body.as_of,use_memory=message.body.use_memory,use_documents=message.body.use_documents,conversation_style=message.longConversationStyle)
}
