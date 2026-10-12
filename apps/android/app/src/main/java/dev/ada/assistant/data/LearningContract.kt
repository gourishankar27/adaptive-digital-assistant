@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*

@Serializable data class LearningConfigDto(val scope_id: UUID, val revision: Int, val epoch: Int,
    val status: String, val continuity_enabled: Boolean, val policy_version: String, val threshold: Int)
@Serializable data class InteractionObservationDto(val id: UUID, val owner_id: UUID, val scope_id: UUID,
    val source_request_id: UUID, val source: SourcePinDto, val evidence: SupportingEvidenceDto,
    val values: PreferenceValuesDto, val confidence_class: String, val interpretation_trust: String,
    val extraction_version: String, val purpose: String, val created_at: Long, val expires_at: Long)
@Serializable data class InteractionProposalDto(val id: UUID, val revision: Int, val values: PreferenceValuesDto,
    val status: String, val independent_count: Int, val eligible: Boolean, val observations: List<UUID>,
    val expires_at: Long, val trust_class: String)
@Serializable data class LearnedPreferenceDto(val id: UUID, val values: PreferenceValuesDto,
    val account_wide: Boolean, val receipt_id: UUID, val proposal_id: UUID, val created_at: Long,
    val observation_ids: List<UUID> = emptyList(), val reviewed_revision: Int? = null)
@Serializable data class LearningStateDto(val config: LearningConfigDto, val observations: List<InteractionObservationDto>,
    val proposals: List<InteractionProposalDto>, val learned: List<LearnedPreferenceDto>)
@Serializable data class LearningReceiptDto(val operation_id: UUID, val scope_id: UUID, val action: String,
    val revision: Int, val epoch: Int, val observation_id: UUID? = null, val proposal_id: UUID? = null,
    val decision: String? = null, val created_at: Long, val observation_ids: List<UUID> = emptyList(), val proposal_revision: Int? = null)
@Serializable data class LearningConfigWriteDto(val operation_id: UUID, val expected_revision: Int,
    val status: String, val continuity_enabled: Boolean = false)
@Serializable data class LearningObservationWriteDto(val operation_id: UUID, val source: SourcePinDto,
    val values: PreferenceValuesDto, val confidence_class: String)
@Serializable data class LearningReviewWriteDto(val operation_id: UUID, val proposal_id: UUID,
    val expected_revision: Int, val decision: String, val account_wide: Boolean = false,
    val reviewed: Boolean = true, val values: PreferenceValuesDto? = null)
@Serializable data class LearningResetWriteDto(val operation_id: UUID, val expected_revision: Int)
@Serializable data class ContinuityCardDto(val source_id: UUID, val source_version: Int,
    val source_origin: String, val trust_class: String, val evidence: EvidenceDto, val label: String,
    val episode_id: UUID, val summary_trust: String, val uncertainty: String, val omitted_source_count: Int = 0)
@Serializable data class LearningJournal(val identity: SessionIdentity, val scopeId: UUID,
    val operationId: UUID, val action: String, val body: String) {
    override fun toString() = "LearningJournal(redacted)"
}

fun preferenceMap(v: PreferenceValuesDto) = linkedMapOf("verbosity" to v.verbosity, "initiative" to v.initiative,
    "formality" to v.formality, "humor" to v.humor, "cadence" to v.cadence).filterValues { it != null }
fun singlePreference(field: String, value: String): PreferenceValuesDto {
    require(value in requireNotNull(preferenceChoices[field]))
    return when(field) { "verbosity" -> PreferenceValuesDto(verbosity = value); "initiative" -> PreferenceValuesDto(initiative = value);
        "formality" -> PreferenceValuesDto(formality = value); "humor" -> PreferenceValuesDto(humor = value); else -> PreferenceValuesDto(cadence = value) }
}
fun validateLearningState(s: LearningStateDto, owner: SessionIdentity, scope: UUID) {
    require(s.config.scope_id == scope && s.config.policy_version == "ada-learning-v1" && s.config.status in setOf("off", "enrolled", "paused") && s.config.threshold in 3..10 && s.config.revision >= 0 && s.config.epoch >= 0)
    require(s.observations.size <= 200 && s.proposals.size <= 12 && s.learned.size <= 5)
    s.observations.forEach { o ->
        require(o.owner_id == owner.owner && o.scope_id == scope && o.interpretation_trust == "unreviewed_interpretation" && o.extraction_version == "ada-learning-v1" && o.purpose == "interaction_preference" && o.confidence_class in setOf("explicit_statement", "repeated_observation", "weak_inference") && o.expires_at > o.created_at)
        validatePreferences(o.values); require(preferenceMap(o.values).size == 1 && o.evidence.trust_class == "user_explicit" && o.evidence.evidence.source_version_id == o.source.source_version_id)
        require(o.evidence.evidence.content_hash == o.source.content_hash && o.evidence.evidence.span_start == o.source.span_start && o.evidence.evidence.span_end == o.source.span_end)
    }
    s.proposals.forEach { p -> validatePreferences(p.values); require(preferenceMap(p.values).size == 1 && p.revision > 0 && p.status in setOf("pending", "approved", "rejected") && p.trust_class == "unreviewed_interpretation" && p.independent_count in 0..200 && (!p.eligible || p.independent_count >= s.config.threshold) && p.observations.all { id -> s.observations.any { it.id == id } }) }
    s.learned.forEach { validatePreferences(it.values); require(preferenceMap(it.values).size == 1 && it.observation_ids.size <= 200 && it.observation_ids.all { id -> s.observations.any { o -> o.id == id } }) }
}
fun validateLearningJournal(j: LearningJournal) {
    require(j.body.toByteArray().size <= 8192)
    val raw = adaJson.parseToJsonElement(j.body).jsonObject
    require(raw["operation_id"]?.jsonPrimitive?.content == j.operationId.toString())
    when(j.action) {
        "config" -> { require(raw.keys.all { it in setOf("operation_id", "expected_revision", "status", "continuity_enabled") }); val b = adaJson.decodeFromString<LearningConfigWriteDto>(j.body); require(b.expected_revision >= 0 && b.status in setOf("off", "enrolled", "paused")) }
        "observe" -> { require(raw.keys == setOf("operation_id", "source", "values", "confidence_class")); require(raw["source"]!!.jsonObject.keys == setOf("source_version_id", "version", "content_hash", "span_start", "span_end")); val b = adaJson.decodeFromString<LearningObservationWriteDto>(j.body); validatePreferences(b.values); require(raw["values"]!!.jsonObject.keys.all { it in preferenceChoices }); require(preferenceMap(b.values).size == 1 && b.confidence_class in setOf("explicit_statement", "repeated_observation", "weak_inference")); require(b.source.version > 0 && b.source.span_start >= 0 && b.source.span_end > b.source.span_start && b.source.content_hash.matches(Regex("[a-f0-9]{64}"))) }
        "review" -> { require(raw.keys.all { it in setOf("operation_id", "proposal_id", "expected_revision", "decision", "account_wide", "reviewed", "values") }); require(raw["reviewed"]?.jsonPrimitive?.let { !it.isString && it.booleanOrNull == true } == true); val b = adaJson.decodeFromString<LearningReviewWriteDto>(j.body); require(b.reviewed && b.expected_revision > 0 && b.decision in setOf("approve", "reject")); b.values?.let { validatePreferences(it); require(preferenceMap(it).size == 1 && raw["values"]!!.jsonObject.keys.all { k -> k in preferenceChoices }) } }
        "reset" -> { require(raw.keys == setOf("operation_id", "expected_revision")); require(adaJson.decodeFromString<LearningResetWriteDto>(j.body).expected_revision >= 0) }
        else -> error("Unsupported learning action")
    }
}
