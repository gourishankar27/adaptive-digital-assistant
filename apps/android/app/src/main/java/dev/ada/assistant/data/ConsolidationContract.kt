@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable data class ConsolidationInputDto(val job_id: UUID, val kind: String, val sources: List<SourcePinDto> = emptyList())
@Serializable data class ConsolidationJournal(val identity: SessionIdentity, val scopeId: UUID, val jobId: UUID, val body: String) {
    override fun toString() = "ConsolidationJournal(redacted)"
}
@Serializable data class ConsolidationReceiptDto(val id: UUID, val job_id: UUID, val outcome: String, val attempt: Int, val episode_id: UUID? = null, val extraction_id: UUID? = null, val proposal_ids: List<UUID>, val indexed_claims: Int? = null, val indexed_chunks: Int? = null, val error_code: String? = null, val created_at: Long)
@Serializable data class ConsolidationJobDto(val id: UUID, val owner_id: UUID, val scope_id: UUID, val kind: String, val version: String, val status: String, val checkpoint: String, val attempt: Int, val model: String, val lease_until: Long? = null, val created_at: Long, val started_at: Long? = null, val finished_at: Long? = null, val elapsed_ms: Long? = null, val error_code: String? = null, val receipt: ConsolidationReceiptDto? = null)
@Serializable data class EpisodeSectionDto(val text: String, val support: List<SourcePinDto>) {
    override fun toString() = "EpisodeSectionDto(redacted)"
}
@Serializable data class EpisodeSourceDto(val source_id: UUID, val source_version: Int, val source_origin: String, val trust_class: String, val evidence: EvidenceDto, val conversation_id: UUID? = null, val event_id: UUID? = null, val created_at: Long, val source_created_at: Long, val available_from: Long? = null, val available_to: Long? = null, val published_at: Long? = null) {
    override fun toString() = "EpisodeSourceDto(redacted)"
}
@Serializable data class EpisodeDto(val id: UUID, val owner_id: UUID, val scope_id: UUID, val job_id: UUID, val summary_version: String, val model: String, val trust_class: String, val sections: List<EpisodeSectionDto>, val tags: List<String>, val omissions: List<String>, val sources: List<EpisodeSourceDto>, val range_start: Long, val range_end: Long, val created_at: Long) {
    override fun toString() = "EpisodeDto(redacted)"
}
fun CapabilitiesDto.hasEpisodes() = episodes == "source_linked_v1" && consolidation_jobs == "bounded_jobs_v1"
private val consolidationJournalJson = Json { ignoreUnknownKeys = false }
fun validateConsolidationJournal(p: ConsolidationJournal) {
    require(p.body.toByteArray(Charsets.UTF_8).size <= 4096)
    val b = consolidationJournalJson.decodeFromString<ConsolidationInputDto>(p.body)
    require(b.job_id == p.jobId && b.kind in setOf("episode", "proposals", "lexical_rebuild"))
    require(if (b.kind == "lexical_rebuild") b.sources.isEmpty() else b.sources.size in 1..4)
    require(b.sources.map { it.source_version_id }.distinct().size == b.sources.size)
    b.sources.forEach { require(it.version > 0 && it.content_hash.matches(Regex("[a-f0-9]{64}")) && it.span_start >= 0 && it.span_end > it.span_start) }
}
