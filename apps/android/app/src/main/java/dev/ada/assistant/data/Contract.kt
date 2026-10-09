@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
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
@Serializable data class MeDto(val id: UUID, val name: String)
@Serializable data class CapabilitiesDto(
    val api_version: String, val chat: Boolean, val streaming: Boolean, val tools: Boolean,
    val structured_memory: Boolean, val memory_writes: String, val memory_in_chat: Boolean,
    val memory_retrieval: String, val memory_citations: Boolean, val retrieval_traces: Boolean,
    val chat_prompt_version: String, val automatic_memory_extraction: Boolean,
    val historical_memory_queries: Boolean, val private_project_scopes: Boolean,
    val shared_scopes: Boolean, val edge_inference: Boolean, val personality_isolation: Boolean,
    val authority: String, val provider: String, val model: String,
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
)
@Serializable data class CitationDto(
    val label: String, val claim_id: UUID, val scope_id: UUID, val subject: String,
    val predicate: String, val value: String, val kind: String, val valid_from: Long,
    val valid_to: Long? = null, val origin: String, val evidence: EvidenceDto,
    val source_id: UUID, val source_version: Int, val conflict: Boolean,
)
@Serializable data class RequestDto(
    val request_id: UUID, val conversation_id: UUID, val status: String,
    val response: String? = null, val error_code: String? = null, val attempt: Int,
    val provider: String, val model: String, val input_tokens: Int? = null,
    val output_tokens: Int? = null, val citations: List<CitationDto> = emptyList(),
    val citation_warnings: List<String> = emptyList(),
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
)
@Serializable data class RetrievalDto(
    val version: String, val scope_id: UUID, val plan: RetrievalPlanDto,
    val candidates: List<RetrievalCandidateDto>, val selected: List<CitationDto>, val budget: RetrievalBudgetDto,
    val retrieval_ms: Long,
)
@Serializable data class TraceDto(
    val request_id: UUID, val conversation_id: UUID, val created_at: Long,
    val version: String, val scope_id: UUID, val plan: RetrievalPlanDto,
    val candidates: List<RetrievalCandidateDto>, val selected: List<CitationDto>, val budget: RetrievalBudgetDto,
    val retrieval_ms: Long,
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
