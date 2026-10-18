@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject

@Serializable data class ResearchCreateDto(val id: UUID, val question: String, val kind: String, val target: String, val version: String = "ada-web-research-v1")
@Serializable data class ResearchActionDto(val id: UUID, val kind: String, val target: String)
@Serializable data class ResearchApprovalDto(val id: UUID, val call_id: UUID, val preview_hash: String)
@Serializable data class ResearchNoteDto(val upload_id: UUID, val source_id: UUID)
@Serializable data class ResearchPreviewDto(val id: UUID, val kind: String, val url: String, val recipient: String,
    val method: String, val disclosure: String, val preview_hash: String, val expires_at: Long,
    val max_bytes: Int, val deadline_seconds: Int, val automatic_redirects: Int, val external_writes: Boolean,
    val headers: Map<String, String>)
@Serializable data class WebEvidenceDto(val content_hash: String, val span_start: Int, val span_end: Int, val quote: String)
@Serializable data class WebCitationDto(val version: String, val label: String, val receipt_id: UUID,
    val fetched_url: String, val final_url: String, val retrieved_at: Long, val fresh_until: Long,
    val parser_version: String, val source_origin: String, val trust_class: String,
    val terms: Map<String, String>, val evidence: WebEvidenceDto, val extraction_truncated: Boolean = false)
@Serializable data class WebSnippetDto(val title: String, val url: String, val snippet: String)
@Serializable data class ResearchReceiptDto(val id: UUID, val call_id: UUID, val state: String, val code: String? = null,
    val redirect_url: String? = null, val snippets: List<WebSnippetDto> = emptyList(), val citation: WebCitationDto? = null)
@Serializable data class ResearchCallDto(val preview: ResearchPreviewDto, val status: String, val receipt: ResearchReceiptDto? = null)
@Serializable data class ResearchRunDto(val version: String, val id: UUID, val scope_id: UUID, val conversation_id: UUID,
    val question: String, val state: String, val response: String? = null, val calls: List<ResearchCallDto>,
    val citations: List<WebCitationDto>, val citation_warnings: List<String>, val created_at: Long, val remaining_calls: Int) {
    override fun toString() = "ResearchRunDto(redacted)"
}
@Serializable data class WebSnapshotDto(val citation: WebCitationDto, val text: String) {
    override fun toString() = "WebSnapshotDto(redacted)"
}
@Serializable data class ResearchOperation(val kind: String, val body: String) {
    override fun toString() = "ResearchOperation(redacted)"
}
@Serializable data class ResearchJournal(val identity: SessionIdentity, val scopeId: UUID, val conversationId: UUID,
    val runId: UUID, val createBody: String, val operation: ResearchOperation? = null, val cancelRequested: Boolean = false) {
    override fun toString() = "ResearchJournal(redacted)"
}

fun validateResearchJournal(journal: ResearchJournal) {
    require(journal.createBody.length <= 12000)
    val create = adaJson.decodeFromString<ResearchCreateDto>(journal.createBody)
    require(create.id == journal.runId && create.version == "ada-web-research-v1")
    require(create.kind in setOf("fetch", "search") && create.question.isNotBlank() && create.question.length <= 2000)
    require(create.target.isNotBlank() && create.target.length <= 2048)
    journal.operation?.let { operation ->
        require(operation.kind in setOf("approve", "cancel", "answer", "calls", "save-note") && operation.body.length <= 12000)
        val json = adaJson.decodeFromString<JsonObject>(operation.body)
        when (operation.kind) {
            "approve" -> {
                require(json.keys == setOf("id", "call_id", "preview_hash"))
                val value = adaJson.decodeFromString<ResearchApprovalDto>(operation.body)
                require(value.preview_hash.matches(Regex("[a-f0-9]{64}")))
            }
            "calls" -> {
                require(json.keys == setOf("id", "kind", "target"))
                val value = adaJson.decodeFromString<ResearchActionDto>(operation.body)
                require(value.kind in setOf("fetch", "search") && value.target.isNotBlank() && value.target.length <= 2048)
            }
            "save-note" -> { require(json.keys == setOf("upload_id", "source_id")); adaJson.decodeFromString<ResearchNoteDto>(operation.body) }
            else -> require(json.isEmpty())
        }
    }
}
