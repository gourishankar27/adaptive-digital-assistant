@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable

const val WORK_PROTOCOL = "ada-work-v1"
@Serializable data class WorkFieldsDto(val kind: String, val description: String, val status: String = "planned",
    val goal_id: UUID? = null, val origin_request_id: UUID? = null, val due_local: String? = null, val timezone: String? = null,
    val fold: String = "reject", val pins: List<SourcePinDto> = emptyList()) { override fun toString() = "WorkFields(redacted)" }
@Serializable data class WorkSourceDto(val source_id: UUID, val source_version: Int, val source_origin: String,
    val trust_class: String, val evidence: EvidenceDto) { override fun toString() = "WorkSource(redacted)" }
@Serializable data class WorkItemDto(val version: String, val id: UUID, val scope_id: UUID, val revision: Int,
    val fields: WorkFieldsDto, val origin_conversation_id: UUID? = null, val due_at: Long? = null, val overdue: Boolean, val provenance: String,
    val sources: List<WorkSourceDto>, val source_unavailable: String? = null, val schedule_id: UUID? = null,
    val question_id: UUID? = null, val created_at: Long, val updated_at: Long) { override fun toString() = "WorkItem(redacted)" }
@Serializable data class WorkWriteDto(val operation_id: UUID, val expected_revision: Int, val fields: WorkFieldsDto,
    val review: String = "confirm", val preview_hash: String? = null, val reminder_choice: String = "none") { override fun toString() = "WorkWrite(redacted)" }
@Serializable data class WorkPreviewDto(val version: String, val preview_hash: String, val due_at: Long? = null,
    val sources: List<WorkSourceDto>, val provenance: String, val reminder: String, val reminder_choice: String = "none") { override fun toString() = "WorkPreview(redacted)" }
@Serializable data class WorkRevisionDto(val revision: Int, val fields: WorkFieldsDto, val created_at: Long) { override fun toString() = "WorkRevision(redacted)" }
@Serializable data class WorkProjectDto(val operation_id: UUID, val name: String) { override fun toString() = "WorkProject(redacted)" }
@Serializable data class WorkBriefInputDto(val operation_id: UUID, val scope_ids: List<UUID>, val item_ids: List<UUID>,
    val day: String, val timezone: String) { override fun toString() = "WorkBriefInput(redacted)" }
@Serializable data class WorkBriefItemDto(val label: String, val task: WorkItemDto, val overdue: Boolean,
    val due_on_day: Boolean, val changes: List<String>) { override fun toString() = "WorkBriefItem(redacted)" }
@Serializable data class WorkBriefDto(val version: String, val id: UUID, val scope_ids: List<UUID>, val day: String,
    val timezone: String, val items: List<WorkBriefItemDto>, val needs_decision: Int, val generated_by: String,
    val factual_evidence: Boolean, val created_at: Long, val timezone_data: String = "unrecorded") { override fun toString() = "WorkBrief(redacted)" }
@Serializable data class WorkFollowupDto(val operation_id: UUID, val expected_revision: Int,
    val policy_revision: Int, val topic: String, val review: String = "confirm")
@Serializable data class WorkReminderPreviewDto(val operation_id: UUID, val expected_revision: Int,
    val definition: ScheduleDefinitionDto) { override fun toString() = "WorkReminderPreview(redacted)" }
@Serializable data class WorkReminderConfirmDto(val operation_id: UUID, val expected_revision: Int, val preview_id: UUID,
    val consent_revision: Int, val schedule_id: UUID, val expected_generation: Int, val review: String = "confirm")
@Serializable data class WorkReceiptDto(val version: String, val operation_id: UUID, val action: String, val state: String,
    val item_id: UUID? = null, val scope_id: UUID? = null, val revision: Int? = null, val question_id: UUID? = null,
    val schedule_id: UUID? = null, val brief_id: UUID? = null, val schedule_preview: ScheduleReceiptDto? = null,
    val created_at: Long) { override fun toString() = "WorkReceipt(redacted)" }
@Serializable data class WorkPending(val operationId: UUID, val kind: String, val body: String,
    val scopeId: UUID? = null, val itemId: UUID? = null) { override fun toString() = "WorkPending(redacted)" }
@Serializable data class WorkJournal(val identity: SessionIdentity, val operations: List<WorkPending>) { override fun toString() = "WorkJournal(redacted)" }
fun validateWorkJournal(j: WorkJournal) {
    require(j.operations.size <= 4 && j.operations.map { it.operationId }.distinct().size == j.operations.size)
    j.operations.forEach { op ->
        require(op.body.toByteArray(Charsets.UTF_8).size in 1..24000)
        val id = when (op.kind) {
            "save" -> { require(op.scopeId != null && op.itemId != null); val b = adaJson.decodeFromString<WorkWriteDto>(op.body)
                require(b.reminder_choice in setOf("none","review_after_save")); require(b.expected_revision >= 0 && b.review == "confirm" && b.preview_hash?.matches(Regex("[a-f0-9]{64}")) == true)
                require(b.fields.kind in setOf("goal","task") && b.fields.status in setOf("planned","done","deferred","unknown","dismissed"))
                require(voiceTextValid(b.fields.description) && b.fields.description.codePointCount(0,b.fields.description.length) <= 1000 && b.fields.pins.size <= 4); b.operation_id }
            "project" -> { require(op.scopeId != null && op.itemId == null); val b = adaJson.decodeFromString<WorkProjectDto>(op.body); require(b.name.isNotBlank() && b.name.length <= 120); b.operation_id }
            "brief" -> { val b = adaJson.decodeFromString<WorkBriefInputDto>(op.body); require(b.item_ids.size in 1..30 && b.scope_ids.size in 1..4 && b.item_ids.distinct() == b.item_ids && b.scope_ids.distinct() == b.scope_ids); b.operation_id }
            "followup" -> { require(op.itemId != null); val b = adaJson.decodeFromString<WorkFollowupDto>(op.body); require(b.expected_revision > 0 && b.policy_revision > 0 && b.topic in setOf("work","routines") && b.review == "confirm"); b.operation_id }
            "reminder_preview" -> { require(op.itemId != null); val b = adaJson.decodeFromString<WorkReminderPreviewDto>(op.body); require(b.expected_revision > 0 && b.definition.kind == "reminder"); b.operation_id }
            "reminder_confirm" -> { require(op.itemId != null); val b = adaJson.decodeFromString<WorkReminderConfirmDto>(op.body); require(b.expected_revision > 0 && b.consent_revision > 0 && b.review == "confirm"); b.operation_id }
            else -> error("Unknown work operation")
        }
        require(id == op.operationId)
    }
}
fun workPath(op: WorkPending): String = when (op.kind) {
    "save" -> "scopes/${requireNotNull(op.scopeId)}/work/${requireNotNull(op.itemId)}"
    "project" -> "work/projects/${requireNotNull(op.scopeId)}"
    "brief" -> "work/briefs"
    "followup" -> "work/${requireNotNull(op.itemId)}/followup"
    "reminder_preview" -> "work/${requireNotNull(op.itemId)}/reminder-preview"
    "reminder_confirm" -> "work/${requireNotNull(op.itemId)}/reminder-confirm"
    else -> error("Unknown work operation")
}
