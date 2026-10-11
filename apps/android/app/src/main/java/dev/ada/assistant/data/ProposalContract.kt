@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject

@Serializable data class SourcePinDto(val source_version_id: UUID, val version: Int, val content_hash: String, val span_start: Int, val span_end: Int)
@Serializable data class ProposalCandidateDto(
    val subject: String, val predicate: String, val value: String, val kind: String,
    val valid_from: String? = null, val valid_to: String? = null,
    val subject_entity_id: UUID? = null, val support: List<SourcePinDto>, val confidence: Double? = null,
)
@Serializable data class SupportingEvidenceDto(val source_id: UUID, val source_version: Int, val source_origin: String, val trust_class: String, val evidence: EvidenceDto)
@Serializable data class ReviewProvenanceDto(val version: String, val origin: String, val proposal_id: UUID, val review_id: UUID, val model: String, val extractor_version: String, val support: List<SupportingEvidenceDto>)
@Serializable data class ProposalConflictDto(val id: UUID, val value: String, val valid_from: Long, val valid_to: Long? = null, val status: String, val write_hash: String, val subject_entity_id: UUID? = null)
@Serializable data class ProposalDto(
    val id: UUID, val scope_id: UUID, val extraction_id: UUID, val status: String, val revision: Int,
    val candidate: ProposalCandidateDto, val original_candidate: ProposalCandidateDto,
    val model: String, val extractor_version: String, val validation: JsonObject,
    val support: List<SupportingEvidenceDto>, val conflicts: List<ProposalConflictDto>, val review_hash: String,
    val rejection_reason: String? = null, val review_id: UUID? = null, val created_at: Long,
)
@Serializable data class ExtractionInputDto(val extraction_id: UUID, val sources: List<SourcePinDto>)
@Serializable data class ExtractionDto(val id: UUID, val scope_id: UUID, val state: String, val model: String, val extractor_version: String, val validation: JsonObject, val error_code: String? = null, val proposal_ids: List<UUID>, val created_at: Long)
@Serializable data class ProposalEditDto(val revision: Int, val review_hash: String, val candidate: ProposalCandidateDto)
@Serializable data class ProposalReviewDto(val review_id: UUID, val revision: Int, val review_hash: String, val decision: String, val annotation: String, val candidate: ProposalCandidateDto, val replace_claim_id: UUID? = null)
@Serializable data class ReviewReceiptDto(val id: UUID, val proposal_id: UUID, val scope_id: UUID, val principal_id: UUID, val decision: String, val revision: Int, val review_hash: String, val claim_id: UUID? = null, val endorsement_source_version_id: UUID? = null, val created_at: Long)

/** Exact operation plus a separate interruption-safe unsent review draft. */
@Serializable data class PendingProposal(val identity: SessionIdentity, val scopeId: UUID, val operationId: UUID, val proposalId: UUID? = null, val kind: String, val body: String) {
    override fun toString() = "PendingProposal(redacted)"
}
@Serializable data class ProposalDraft(val identity: SessionIdentity, val proposal: ProposalDto, val candidate: ProposalCandidateDto, val annotation: String = "", val replaceClaimId: UUID? = null) {
    override fun toString() = "ProposalDraft(redacted)"
}

fun validateProposalPending(p: PendingProposal) {
    try {
        require(p.body.toByteArray(Charsets.UTF_8).size <= 32768)
        val strict = Json { ignoreUnknownKeys = false }
        when (p.kind) {
            "extract" -> { val b = strict.decodeFromString<ExtractionInputDto>(p.body); require(b.extraction_id == p.operationId && p.proposalId == null && b.sources.size in 1..4); b.sources.forEach { validatePin(it) } }
            "edit" -> { val b = strict.decodeFromString<ProposalEditDto>(p.body); require(p.proposalId != null && b.revision >= 1 && b.review_hash.matches(Regex("[a-f0-9]{64}"))); validateCandidate(b.candidate) }
            "review" -> { val b = strict.decodeFromString<ProposalReviewDto>(p.body); require(p.proposalId != null && b.review_id == p.operationId && b.revision >= 1 && b.review_hash.matches(Regex("[a-f0-9]{64}"))); require(b.decision in setOf("accept", "reject")); validatePrivateText(b.annotation, 1000); validateCandidate(b.candidate) }
            else -> error("Invalid operation")
        }
    } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
}
fun validatePin(p: SourcePinDto) { require(p.version >= 1 && p.span_start >= 0 && p.span_end > p.span_start && p.content_hash.matches(Regex("[a-f0-9]{64}"))) }
fun validatePrivateText(value: String, max: Int) { require(value.isNotBlank()); validateDraftText(value, max) }
private fun validateDraftText(value: String, max: Int) {
    require(value.codePointCount(0, value.length) <= max)
    documentText(value.toByteArray(Charsets.UTF_8))
    var i = 0
    while (i < value.length) { val c = value[i]; require(c != '\u0000' && !c.isLowSurrogate()); if (c.isHighSurrogate()) { require(i + 1 < value.length && value[i + 1].isLowSurrogate()); i++ }; i++ }
}
fun validateCandidate(c: ProposalCandidateDto) {
    validatePrivateText(c.subject, 160); validatePrivateText(c.predicate, 160); validatePrivateText(c.value, 1000)
    require(c.kind in setOf("fact", "preference", "decision") && c.support.size in 1..4); c.support.forEach { validatePin(it) }
    require(c.confidence == null || (c.confidence.isFinite() && c.confidence in 0.0..1.0))
    c.valid_from?.let { require(normalizeUtcMillis(it) != null) }; c.valid_to?.let { require(normalizeUtcMillis(it) != null) }
    if (c.valid_from != null && c.valid_to != null) require(java.time.OffsetDateTime.parse(c.valid_to) > java.time.OffsetDateTime.parse(c.valid_from))
}
fun validateProposalDraft(d: ProposalDraft) {
    try {
        require(d.proposal.revision >= 1 && d.proposal.review_hash.matches(Regex("[a-f0-9]{64}")))
        require(d.proposal.status == "pending")
        require(d.candidate.support == d.proposal.candidate.support)
        // Partial form fields may be empty, but malformed Unicode never survives a restart.
        for (value in listOf(d.candidate.subject, d.candidate.predicate, d.candidate.value, d.annotation)) {
            validateDraftText(value, 1000)
        }
        listOfNotNull(d.candidate.valid_from, d.candidate.valid_to, d.candidate.kind).forEach { validateDraftText(it, 64) }
        require(d.replaceClaimId == null || d.proposal.conflicts.any { it.id == d.replaceClaimId && it.status == "active" })
    } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
}

/** Recover an exact edit even when the server normalizes UTC offsets and trims fields. */
fun sameProposalCandidate(a: ProposalCandidateDto, b: ProposalCandidateDto): Boolean = try {
    fun normalized(c: ProposalCandidateDto) = c.copy(subject = c.subject.trim(), predicate = c.predicate.trim(), value = c.value.trim(),
        valid_from = c.valid_from?.let(::normalizeUtcMillis), valid_to = c.valid_to?.let(::normalizeUtcMillis))
    normalized(a) == normalized(b)
} catch (_: Exception) { false }

fun ReviewProvenanceDto.reviewOriginLabel(): String =
    if (version == "review-v1" && origin == "user_reviewed") "User reviewed · explicit endorsement"
    else "Unrecognized review provenance"
