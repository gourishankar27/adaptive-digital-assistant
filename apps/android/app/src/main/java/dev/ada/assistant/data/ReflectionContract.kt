@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable

@Serializable data class ReflectionSettingsDto(val enabled: Boolean = false, val scope_ids: List<UUID> = emptyList(),
    val source_types: List<String> = listOf("user_notes"), val automatic_completed_turns: Boolean = false,
    val lookback_days: Int = 7, val timezone: String = "UTC", val allowed_start: Int = 0, val allowed_end: Int = 60,
    val job_kinds: List<String> = listOf("report", "question"), val question_topic: String = "work",
    val allow_empty: Boolean = true, val idle_seconds: Int = 900, val nightly_seconds: Int = 600,
    val max_jobs: Int = 3, val unit_seconds: Int = 20, val minimum_memory_percent: Int = 10,
    val minimum_disk_mib: Int = 1024, val maximum_thermal_c: Int = 80)
@Serializable data class ReflectionPolicyDto(val version: String, val revision: Int, val settings: ReflectionSettingsDto,
    val globally_enabled: Boolean, val scheduling_consent: Boolean, val summary_generation: Boolean,
    val last_decision: String? = null, val foreground_idle_seconds: Int)
@Serializable data class ReflectionPolicyWriteDto(val operation_id: UUID, val expected_revision: Int, val settings: ReflectionSettingsDto)
@Serializable data class ReflectionFindingDto(val category: String, val text: String, val support: List<SourcePinDto>, val claim_ids: List<UUID> = emptyList()) { override fun toString() = "ReflectionFindingDto(redacted)" }
@Serializable data class ReflectionQuestionDto(val topic: String, val template_key: String, val text: String, val source: CuriositySourceDto? = null) { override fun toString() = "ReflectionQuestionDto(redacted)" }
@Serializable data class ReflectionSummaryDto(val sections: List<EpisodeSectionDto>, val tags: List<String>, val omissions: List<String>) { override fun toString() = "ReflectionSummaryDto(redacted)" }
@Serializable data class ReflectionContentDto(val findings: List<ReflectionFindingDto>? = null, val question: ReflectionQuestionDto? = null, val summary: ReflectionSummaryDto? = null) { override fun toString() = "ReflectionContentDto(redacted)" }
@Serializable data class ReflectionArtifactDto(val version: String, val id: UUID, val scope_id: UUID, val run_id: UUID,
    val kind: String, val state: String, val provenance: String, val rationale: String, val content: ReflectionContentDto? = null,
    val sources: List<EpisodeSourceDto>, val omissions: Map<String, Int>, val created_at: Long, val elapsed_ms: Long,
    val model_elapsed_ms: Long? = null, val episode_id: UUID? = null, val question_id: UUID? = null,
    val conversation_id: UUID? = null, val unavailable_reason: String? = null) { override fun toString() = "ReflectionArtifactDto(redacted)" }
@Serializable data class ReflectionRunDto(val id: UUID, val scope_id: UUID, val kind: String, val state: String,
    val attempt: Int, val reason: String? = null, val artifact_id: UUID? = null, val created_at: Long,
    val finished_at: Long? = null, val elapsed_ms: Long? = null, val charged_ms: Long)
@Serializable data class ReflectionActionDto(val operation_id: UUID, val action: String,
    val conversation_id: UUID? = null, val personality_id: UUID? = null)
@Serializable data class ReflectionReceiptDto(val version: String, val operation_id: UUID, val action: String,
    val state: String, val revision: Int? = null, val artifact_id: UUID? = null, val episode_id: UUID? = null,
    val question_id: UUID? = null, val conversation_id: UUID? = null, val created_at: Long)
@Serializable data class ReflectionPending(val operationId: UUID, val kind: String, val body: String, val artifactId: UUID? = null) { override fun toString() = "ReflectionPending(redacted)" }
@Serializable data class ReflectionJournal(val identity: SessionIdentity, val operations: List<ReflectionPending>) { override fun toString() = "ReflectionJournal(redacted)" }
fun ReflectionPending.turnsReflectionOff() = kind == "policy" && !adaJson.decodeFromString<ReflectionPolicyWriteDto>(body).settings.enabled
fun validateReflectionJournal(j: ReflectionJournal) {
    require(j.operations.size <= 8 && j.operations.map { it.operationId }.distinct().size == j.operations.size)
    j.operations.forEach { op ->
        require(op.body.length in 1..16000)
        val key = if (op.kind == "policy") {
            require(op.artifactId == null)
            val b = adaJson.decodeFromString<ReflectionPolicyWriteDto>(op.body)
            require(b.expected_revision >= 0 && b.settings.scope_ids.size <= 4)
            require(!b.settings.enabled || b.settings.scope_ids.isNotEmpty())
            b.operation_id
        } else {
            require(op.kind == "action" && op.artifactId != null)
            val b = adaJson.decodeFromString<ReflectionActionDto>(op.body)
            require(b.action in setOf("keep", "dismiss", "open_question"))
            require((b.action == "open_question") == (b.conversation_id != null && b.personality_id != null))
            b.operation_id
        }
        require(key == op.operationId)
    }
    require(j.operations.count { !it.turnsReflectionOff() } <= 7)
}
fun reflectionPath(op: ReflectionPending) = if (op.kind == "policy") "reflection/policy" else "reflection/artifacts/${requireNotNull(op.artifactId)}/actions"
