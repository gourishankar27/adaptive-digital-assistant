@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import java.security.MessageDigest
import java.time.OffsetDateTime
import java.time.ZoneOffset
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.PrimitiveSerialDescriptor
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonDecoder
import kotlinx.serialization.json.JsonEncoder
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.decodeFromJsonElement
import kotlinx.serialization.json.encodeToJsonElement

object UuidSerializer : KSerializer<UUID> {
    override val descriptor = PrimitiveSerialDescriptor("UUID", PrimitiveKind.STRING)
    override fun serialize(encoder: Encoder, value: UUID) = encoder.encodeString(value.toString())
    override fun deserialize(decoder: Decoder): UUID {
        val text = decoder.decodeString()
        require(text.matches(Regex("[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")))
        return UUID.fromString(text)
    }
}

val adaJson = Json { ignoreUnknownKeys = true; explicitNulls = false; encodeDefaults = true }

// Wire enums are strings so future values remain visible and cannot be silently coerced.
@Serializable data class MeDto(val id: UUID, val name: String, val data_epoch: Long = 0)
@Serializable data class CapabilitiesDto(
    val api_version: String, val chat: Boolean, val streaming: Boolean, val tools: Boolean,
    val structured_memory: Boolean, val memory_writes: String, val memory_in_chat: Boolean,
    val memory_retrieval: String, val memory_citations: Boolean, val retrieval_traces: Boolean,
    val chat_prompt_version: String, val automatic_memory_extraction: Boolean,
    val historical_memory_queries: Boolean, val private_project_scopes: Boolean,
    val shared_scopes: Boolean, val edge_inference: Boolean, val personality_isolation: Boolean,
    val authority: String, val provider: String, val model: String,
    val document_ingestion: String = "unsupported", val document_uploads: Boolean = false,
    val document_retrieval: Boolean = false, val document_citations: Boolean = false,
    val document_max_bytes: Int = 0,
    val scoped_entities: Boolean = false, val entity_writes: Boolean = false, val entity_resolution: String = "unsupported",
    val memory_proposals: String = "unsupported", val memory_review: Boolean = false, val memory_provenance: String = "legacy",
    val agent_tools: String = "unsupported", val agent_protocol: String = "unsupported", val agent_registry: List<String> = emptyList(),
    val episodes: String = "unsupported", val consolidation_jobs: String = "unsupported",
    val consolidation_generation: Boolean = false, val consolidation_worker: Boolean = false,
    val interaction_preferences: String = "unsupported", val session_expression: String = "unsupported", val automatic_affect_inference: Boolean = false,
    val interaction_learning: String = "unsupported",
    val stream_protocol: String = "unsupported", val generation_cancellation: Boolean = false,
    val voice_input: String = "unsupported", val voice_audio_uploads: Boolean = false,
    val device_credentials: String = "unsupported", val private_deletion: String = "unsupported",
    val answer_quality: String = "unsupported", val calendar_windows: String = "unsupported",
    val quality_prompt_version: String? = null,
)
@Serializable data class PersonalitySnapshotDto(
    val name: String, val style: String, val warmth: String, val detail: String,
)
@Serializable data class PersonalityDto(
    val id: UUID, val name: String, val style: String, val warmth: String, val detail: String,
)
@Serializable data class ConversationDto(
    val id: UUID, val title: String, val scope_id: UUID, val scope_kind: String,
    val personality: PersonalitySnapshotDto, val prompt_version: String, val revision: Int,
    val created_at: Long,
)
@Serializable data class EventDto(
    val id: UUID, val role: String, val content: String, val trust_class: String,
    val request_id: UUID, val request_status: String, val created_at: Long,
    val source_version_id: UUID,
)
@Serializable data class ScopeDto(val id: UUID, val name: String, val kind: String, val created_at: Long)
@Serializable data class EvidenceDto(
    val source_version_id: UUID, val span_start: Int, val span_end: Int,
    val quote: String, val content_hash: String,
)
@Serializable data class SourceVersionDto(
    val id: UUID, val source_id: UUID, val scope_id: UUID, val version: Int,
    val content: String, val content_hash: String, val trust_class: String, val created_at: Long,
)
@Serializable data class ClaimDto(
    val id: UUID, val scope_id: UUID, val subject: String, val predicate: String, val value: String,
    val kind: String, val status: String, val valid_from: Long, val valid_to: Long? = null,
    val superseded_by: UUID? = null, val created_at: Long, val origin: String, val evidence: EvidenceDto,
    val subject_entity_id: UUID? = null,
    val provenance: ReviewProvenanceDto? = null,
)
@Serializable data class CitationDto(
    val label: String, val claim_id: UUID, val scope_id: UUID, val subject: String,
    val predicate: String, val value: String, val kind: String, val valid_from: Long,
    val valid_to: Long? = null, val origin: String, val evidence: EvidenceDto,
    val source_id: UUID, val source_version: Int, val conflict: Boolean,
    val subject_entity_id: UUID? = null, val entity: EntityChoiceDto? = null,
    val provenance: ReviewProvenanceDto? = null,
)
@Serializable data class RequestDto(
    val request_id: UUID, val conversation_id: UUID, val status: String,
    val response: String? = null, val error_code: String? = null, val attempt: Int,
    val provider: String, val model: String, val input_tokens: Int? = null,
    val output_tokens: Int? = null, val citations: List<CitationDto> = emptyList(),
    val citation_warnings: List<String> = emptyList(),
    val document_citations: List<DocumentCitationDto> = emptyList(),
    val continuity_citations: List<ContinuityCardDto> = emptyList(),
) {
    val observedState: ObservedRequestState get() = when (status) {
        "running" -> ObservedRequestState.Running
        "completed" -> ObservedRequestState.Completed
        "failed" -> ObservedRequestState.Failed
        else -> ObservedRequestState.Unknown
    }
}
enum class ObservedRequestState { Running, Completed, Failed, Unknown }
@Serializable data class RetrievalPlanDto(
    val enabled: Boolean, val reason: String, val time_mode: String, val as_of: Long? = null,
    val query_terms: List<String>, val expanded_terms: List<String>, val subject_keys: List<String>,
    val overview: Boolean, val prompt_version: String? = null,
    val entity_resolution: List<EntityResolutionDto> = emptyList(),
    val entity_resolution_truncated: Boolean = false,
)
@Serializable data class RetrievalDto(
    val version: String, val scope_id: UUID, val plan: RetrievalPlanDto,
    val candidates: List<RetrievalCandidateDto>, val selected: List<CitationDto>, val budget: RetrievalBudgetDto,
    val retrieval_ms: Long,
    val document_selected: List<DocumentCitationDto> = emptyList(), val document_candidates: List<DocumentCandidateDto> = emptyList(),
)
@Serializable data class TraceDto(
    val request_id: UUID, val conversation_id: UUID, val created_at: Long,
    val version: String, val scope_id: UUID, val plan: RetrievalPlanDto,
    val candidates: List<RetrievalCandidateDto>, val selected: List<CitationDto>, val budget: RetrievalBudgetDto,
    val retrieval_ms: Long,
    val document_selected: List<DocumentCitationDto> = emptyList(), val document_candidates: List<DocumentCandidateDto> = emptyList(),
)
@Serializable data class PromptUpgradeDto(
    val id: UUID, val prompt_version: String, val revision: Int,
)
@Serializable data class RetrievalCandidateDto(
    val claim_id: UUID, val channels: List<String>, val decision: String,
    val score: Double? = null, val term_coverage: Int? = null,
)
@Serializable data class RetrievalBudgetDto(
    val memory_limit_bytes: Long, val memory_used_bytes: Long, val selected_limit: Int,
    val candidate_limit_per_channel: Int, val candidate_pool_truncated: Boolean,
    val prompt_limit_bytes: Long? = null, val prompt_used_bytes: Long? = null,
    val history_pairs: Int? = null, val history_pairs_omitted: Int? = null,
)
@Serializable data class PersonalityInputDto(
    val name: String = "ADA", val style: String = "conversational", val warmth: String = "warm",
    val detail: String = "balanced",
)
@Serializable data class ConversationInputDto(
    val personality_id: UUID, val title: String = "New conversation", val scope_id: UUID? = null,
)
@Serializable data class ChatInputDto(
    val request_id: UUID, val content: String, val as_of: String? = null, val use_memory: Boolean = true,
    val use_documents: Boolean = false,
)
@Serializable data class ScopeInputDto(val name: String, val kind: String = "project")
@Serializable data class NoteInputDto(val source_id: UUID, val content: String)
@Serializable data class ClaimInputDto(
    val claim_id: UUID, val source_version_id: UUID, val span_start: Int, val span_end: Int,
    val subject: String, val predicate: String, val value: String, val kind: String = "fact",
    val valid_from: String? = null, val valid_to: String? = null,
)
@Serializable data class SupersedeInputDto(
    val claim_id: UUID, val source_version_id: UUID, val span_start: Int, val span_end: Int,
    val value: String, val effective_at: String? = null, val valid_to: String? = null,
)
@Serializable data class RetrieveInputDto(
    val query: String, val as_of: String? = null, val limit: Int = 8, val budget_bytes: Int = 2200,
)
@Serializable data class ErrorEnvelopeDto(val detail: ErrorDetailDto)
@Serializable data class ValidationIssueDto(val type: String, val loc: List<JsonPrimitive>, val msg: String)
@Serializable(with = ErrorDetailSerializer::class)
sealed interface ErrorDetailDto {
    data class Code(val code: String) : ErrorDetailDto
    data class Validation(val issues: List<ValidationIssueDto>) : ErrorDetailDto
}
object ErrorDetailSerializer : KSerializer<ErrorDetailDto> {
    override val descriptor = PrimitiveSerialDescriptor("ErrorDetail", PrimitiveKind.STRING)
    override fun deserialize(decoder: Decoder): ErrorDetailDto {
        val element = (decoder as JsonDecoder).decodeJsonElement()
        return when (element) {
            is JsonPrimitive -> {
                require(element.isString)
                ErrorDetailDto.Code(element.content)
            }
            is JsonArray -> ErrorDetailDto.Validation(adaJson.decodeFromJsonElement(element))
            else -> throw kotlinx.serialization.SerializationException("Invalid error detail shape")
        }
    }
    override fun serialize(encoder: Encoder, value: ErrorDetailDto) {
        (encoder as JsonEncoder).encodeJsonElement(when (value) {
            is ErrorDetailDto.Code -> JsonPrimitive(value.code)
            is ErrorDetailDto.Validation -> adaJson.encodeToJsonElement(value.issues)
        })
    }
}

/** ADA offsets count Unicode code points; reject selection boundaries inside a surrogate pair. */
fun utf16ToCodePointOffset(text: String, offset: Int): Int {
    require(offset in 0..text.length)
    require(offset == 0 || offset == text.length ||
        !(text[offset - 1].isHighSurrogate() && text[offset].isLowSurrogate()))
    return text.codePointCount(0, offset)
}

fun codePointToUtf16Offset(text: String, offset: Int): Int {
    require(offset in 0..text.codePointCount(0, text.length))
    return text.offsetByCodePoints(0, offset)
}

/** Validate exact bytes, never normalize the source or substitute a current source version. */
private fun exactSourceHash(content: String): String {
    var index = 0
    while (index < content.length) {
        val character = content[index]
        if (character.isHighSurrogate()) {
            require(index + 1 < content.length && content[index + 1].isLowSurrogate()) { "Invalid source Unicode" }
            index += 2
        } else {
            require(!character.isLowSurrogate() && character != '\u0000') { "Invalid source Unicode" }
            index++
        }
    }
    val digits = "0123456789abcdef"
    return buildString(64) {
        for (byte in MessageDigest.getInstance("SHA-256").digest(content.toByteArray(Charsets.UTF_8))) {
            val value = byte.toInt() and 255
            append(digits[value ushr 4]); append(digits[value and 15])
        }
    }
}

/** Client aid only: an authenticated server must authorize every source and write. */
fun exactEvidenceSelection(source: SourceVersionDto, scope: UUID, startUtf16: Int, endUtf16: Int): EvidenceDto {
    require(source.scope_id == scope) { "Source scope mismatch" }
    require(source.trust_class == "user_explicit") { "Source is not explicit user evidence" }
    require(exactSourceHash(source.content) == source.content_hash) { "Source content hash mismatch" }
    val start = utf16ToCodePointOffset(source.content, startUtf16)
    val end = utf16ToCodePointOffset(source.content, endUtf16)
    require(start < end) { "Select a nonempty source quote" }
    val quote = source.content.substring(startUtf16, endUtf16)
    require(quote.isNotBlank()) { "Select a nonblank source quote" }
    return EvidenceDto(source.id, start, end, quote, source.content_hash)
}

/** Exact provenance for read-only detail; this does not authorize endorsing model evidence. */
fun verifyClaimEvidence(claim: ClaimDto, source: SourceVersionDto): Boolean = runCatching {
    val evidence = claim.evidence
    require(source.id == evidence.source_version_id && source.scope_id == claim.scope_id)
    require(source.content_hash == evidence.content_hash && exactSourceHash(source.content) == source.content_hash)
    require(evidence.span_start >= 0 && evidence.span_end > evidence.span_start)
    val start = codePointToUtf16Offset(source.content, evidence.span_start)
    val end = codePointToUtf16Offset(source.content, evidence.span_end)
    require(source.content.substring(start, end) == evidence.quote && evidence.quote.isNotBlank())
    true
}.getOrDefault(false)

/** Canonical API timestamp. Valid time is separate from the returned source storage time. */
fun normalizeUtcMillis(value: String): String? {
    if (value.isBlank()) return null
    require(value.length <= 64) { "Timestamp is too long" }
    val parsed = OffsetDateTime.parse(value.trim())
    require(parsed.nano % 1_000_000 == 0) { "Timestamp requires millisecond precision" }
    val instant = parsed.toInstant()
    require(instant.atOffset(ZoneOffset.UTC).year in 1..9999) { "Timestamp is outside the server date range" }
    return instant.toString()
}
