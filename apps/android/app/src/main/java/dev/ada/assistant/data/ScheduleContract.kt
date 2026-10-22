@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable

@Serializable data class ScheduleDefinitionDto(val kind: String = "reminder", val text: String = "",
    val topic: String? = null, val source: CuriosityPinInputDto? = null, val timezone: String,
    val start_local: String, val frequency: String = "once", val count: Int = 1, val fold: String = "reject",
    val gap: String = "skip", val allowed_start: Int = 480, val allowed_end: Int = 1320,
    val expires_at: String, val channel: String = "inbox") { override fun toString() = "ScheduleDefinitionDto(redacted)" }
@Serializable data class SchedulePolicyDto(val version: String, val revision: Int, val enabled: Boolean,
    val globally_enabled: Boolean, val notice_channel: String, val background_push: Boolean)
@Serializable data class SchedulePolicyWriteDto(val operation_id: UUID, val expected_revision: Int, val enabled: Boolean)
@Serializable data class SchedulePreviewDto(val operation_id: UUID, val definition: ScheduleDefinitionDto) { override fun toString() = "SchedulePreviewDto(redacted)" }
@Serializable data class ScheduleConfirmDto(val operation_id: UUID, val preview_id: UUID, val expected_generation: Int, val consent_revision: Int)
@Serializable data class ScheduleActionDto(val operation_id: UUID, val expected_generation: Int, val action: String, val until: String? = null)
@Serializable data class ScheduleInboxActionDto(val operation_id: UUID, val action: String, val until: String? = null)
@Serializable data class ScheduleOpenDto(val operation_id: UUID, val conversation_id: UUID, val personality_id: UUID)
@Serializable data class SchedulePlanDto(val at: Long, val local: String)
@Serializable data class ScheduleReceiptDto(val version: String, val operation_id: UUID, val action: String,
    val state: String, val schedule_id: UUID? = null, val item_id: UUID? = null, val conversation_id: UUID? = null,
    val generation: Int? = null, val consent_revision: Int? = null, val definition: ScheduleDefinitionDto? = null,
    val source: CuriositySourceDto? = null,
    val occurrences: List<SchedulePlanDto>? = null, val timezone_data: String? = null,
    val preview_expires_at: Long? = null, val created_at: Long) { override fun toString() = "ScheduleReceiptDto(redacted)" }
@Serializable data class ScheduleDto(val version: String, val id: UUID, val scope_id: UUID, val generation: Int,
    val state: String, val reason: String? = null, val definition: ScheduleDefinitionDto? = null, val next_at: Long? = null,
    val snoozed_until: Long? = null, val delivered: Int, val missed: Int, val consent_revision: Int,
    val origin_kind: String, val created_at: Long, val updated_at: Long) { override fun toString() = "ScheduleDto(redacted)" }
@Serializable data class ScheduleOccurrenceDto(val id: UUID, val schedule_id: UUID, val generation: Int,
    val scheduled_for: Long, val state: String, val reason: String? = null, val attempt: Int,
    val lease_until: Long? = null, val item_id: UUID? = null)
@Serializable data class ScheduleInboxDto(val version: String, val id: UUID, val scope_id: UUID,
    val schedule_id: UUID, val occurrence_id: UUID, val kind: String, val text: String? = null,
    val question_id: UUID? = null, val state: String, val available_at: Long, val expires_at: Long,
    val acknowledged_at: Long? = null, val opened_conversation_id: UUID? = null, val created_at: Long) {
    override fun toString() = "ScheduleInboxDto(redacted)"
}
@Serializable data class SchedulePending(val operationId: UUID, val kind: String, val body: String,
    val scopeId: UUID? = null, val scheduleId: UUID? = null, val itemId: UUID? = null, val expectedGeneration: Int = 0) {
    override fun toString() = "SchedulePending(redacted)"
}
@Serializable data class ScheduleJournal(val identity: SessionIdentity, val operations: List<SchedulePending>) {
    override fun toString() = "ScheduleJournal(redacted)"
}
fun SchedulePending.turnsSchedulingOff() = kind == "policy" && !adaJson.decodeFromString<SchedulePolicyWriteDto>(body).enabled
fun validateScheduleJournal(journal: ScheduleJournal) {
    require(journal.operations.size <= 8 && journal.operations.map { it.operationId }.distinct().size == journal.operations.size)
    journal.operations.forEach { op ->
        require(op.body.length in 1..16000)
        val id = when (op.kind) {
            "policy" -> { require(op.scopeId == null && op.scheduleId == null && op.itemId == null); adaJson.decodeFromString<SchedulePolicyWriteDto>(op.body).operation_id }
            "preview" -> { require(op.scopeId != null && op.itemId == null); val b = adaJson.decodeFromString<SchedulePreviewDto>(op.body)
                require(b.definition.count in 1..100 && b.definition.channel == "inbox" && b.definition.kind in setOf("reminder", "curiosity_question")); b.operation_id }
            "confirm" -> { require(op.scheduleId != null && op.itemId == null); adaJson.decodeFromString<ScheduleConfirmDto>(op.body).operation_id }
            "action" -> { require(op.scheduleId != null && op.itemId == null); val b = adaJson.decodeFromString<ScheduleActionDto>(op.body)
                require(b.action in setOf("pause", "reauthorize", "delete", "snooze")); b.operation_id }
            "inbox_action" -> { require(op.itemId != null); val b = adaJson.decodeFromString<ScheduleInboxActionDto>(op.body)
                require(b.action in setOf("acknowledge", "dismiss", "snooze")); b.operation_id }
            "open" -> { require(op.itemId != null); adaJson.decodeFromString<ScheduleOpenDto>(op.body).operation_id }
            else -> error("Unsupported schedule operation")
        }
        require(id == op.operationId)
    }
    require(journal.operations.count { !it.turnsSchedulingOff() } <= 7)
}
fun schedulePath(op: SchedulePending) = when (op.kind) {
    "policy" -> "scheduling/policy"
    "preview" -> "scopes/${requireNotNull(op.scopeId)}/schedules/preview"
    "confirm" -> "schedules/${requireNotNull(op.scheduleId)}/confirm"
    "action" -> "schedules/${requireNotNull(op.scheduleId)}/actions"
    "inbox_action" -> "scheduling/inbox/${requireNotNull(op.itemId)}/actions"
    "open" -> "scheduling/inbox/${requireNotNull(op.itemId)}/open"
    else -> error("Unsupported schedule operation")
}
