@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

val curiosityTopics = listOf("interests", "work", "routines", "relationships", "reflection")
@Serializable data class CuriositySettingsDto(val enabled: Boolean = false, val chat_enabled: Boolean = true,
    val inbox_enabled: Boolean = true, val notifications_enabled: Boolean = false, val frequency: String = "occasional",
    val depth: String = "light", val topics: Map<String, String> = curiosityTopics.associateWith { if (it in setOf("relationships", "reflection")) "blocked" else "enabled" }) {
    override fun toString() = "CuriositySettingsDto(redacted)"
}
@Serializable data class CuriosityPolicyDto(val version: String, val revision: Int, val settings: CuriositySettingsDto,
    val day_boundary: String, val inbox_daily_limit: Int, val interview_daily_limit: Int, val suppression_days: Int,
    val permanent_suppressions: Int) { override fun toString() = "CuriosityPolicyDto(redacted)" }
@Serializable data class CuriosityPolicyWriteDto(val operation_id: UUID, val expected_revision: Int, val settings: CuriositySettingsDto)
@Serializable data class CuriosityPinInputDto(val source_version_id: UUID, val span_start: Int, val span_end: Int)
@Serializable data class CuriosityCreateDto(val operation_id: UUID, val policy_revision: Int, val channel: String = "inbox",
    val intent: String = "normal", val topic: String? = null, val request_id: UUID? = null, val source: CuriosityPinInputDto? = null)
@Serializable data class CuriosityActionDto(val operation_id: UUID, val action: String)
@Serializable data class CuriosityOpenDto(val operation_id: UUID, val conversation_id: UUID, val personality_id: UUID)
@Serializable data class CuriosityAnswerDto(val operation_id: UUID, val request_id: UUID, val text: String) {
    override fun toString() = "CuriosityAnswerDto(redacted)"
}
@Serializable data class CuriositySourceDto(val source_version_id: UUID, val scope_id: UUID, val content_hash: String,
    val span_start: Int, val span_end: Int, val quote: String, val trust_class: String, val created_at: Long) {
    override fun toString() = "CuriositySourceDto(redacted)"
}
@Serializable data class CuriosityQuestionDto(val version: String, val id: UUID, val scope_id: UUID,
    val conversation_id: UUID? = null, val request_id: UUID? = null, val opened_conversation_id: UUID? = null,
    val answer_request_id: UUID? = null, val channel: String, val topic: String, val state: String,
    val text: String? = null, val reason: String? = null, val policy: Map<String, JsonElement>? = null,
    val source: CuriositySourceDto? = null, val created_at: Long, val expires_at: Long, val available_at: Long) {
    override fun toString() = "CuriosityQuestionDto(redacted)"
}
@Serializable data class CuriosityReceiptDto(val version: String, val operation_id: UUID, val action: String, val state: String,
    val reason: String? = null, val question_id: UUID? = null, val conversation_id: UUID? = null,
    val request_id: UUID? = null, val policy_revision: Int? = null, val created_at: Long)
@Serializable data class CuriosityPending(val operationId: UUID, val kind: String, val scopeId: UUID? = null,
    val questionId: UUID? = null, val body: String) { override fun toString() = "CuriosityPending(redacted)" }
@Serializable data class CuriosityJournal(val identity: SessionIdentity, val operations: List<CuriosityPending>) {
    override fun toString() = "CuriosityJournal(redacted)"
}

fun validateCuriosityJournal(journal: CuriosityJournal) {
    require(journal.operations.size <= 8 && journal.operations.map { it.operationId }.distinct().size == journal.operations.size)
    journal.operations.forEach { op ->
        require(op.body.length in 1..24000 && op.kind in setOf("policy", "create", "action", "open", "answer"))
        val id = when (op.kind) {
            "policy" -> { require(op.scopeId == null && op.questionId == null); val body = adaJson.decodeFromString<CuriosityPolicyWriteDto>(op.body)
                require(body.expected_revision >= 0 && !body.settings.notifications_enabled && body.settings.topics.keys == curiosityTopics.toSet())
                require(body.settings.topics.values.all { it in setOf("enabled", "paused", "blocked") }); body.operation_id }
            "create" -> { require(op.scopeId != null && op.questionId == null); val body = adaJson.decodeFromString<CuriosityCreateDto>(op.body)
                require(body.policy_revision > 0 && body.channel in setOf("chat", "inbox") && body.intent in setOf("normal", "interview")); body.operation_id }
            "action" -> { require(op.scopeId != null && op.questionId != null); val body = adaJson.decodeFromString<CuriosityActionDto>(op.body)
                require(body.action in setOf("skip", "not_now", "dismiss", "dont_ask_again", "pause_topic", "helpful", "unhelpful")); body.operation_id }
            "open" -> { require(op.scopeId != null && op.questionId != null); adaJson.decodeFromString<CuriosityOpenDto>(op.body).operation_id }
            else -> { require(op.scopeId != null && op.questionId != null); val body = adaJson.decodeFromString<CuriosityAnswerDto>(op.body)
                require(body.text.isNotBlank() && body.text.codePointCount(0, body.text.length) <= 4000); body.operation_id }
        }
        require(op.operationId == id)
    }
    require(journal.operations.count { !it.turnsCuriosityOff() } <= 7)
}

fun CuriosityPending.turnsCuriosityOff(): Boolean = kind == "policy" && !adaJson.decodeFromString<CuriosityPolicyWriteDto>(body).settings.enabled

fun curiosityPath(op: CuriosityPending): String = when (op.kind) {
    "policy" -> "curiosity/policy"
    "create" -> "scopes/${requireNotNull(op.scopeId)}/curiosity/questions"
    "action" -> "curiosity/questions/${requireNotNull(op.questionId)}/actions"
    "open", "answer" -> "curiosity/questions/${requireNotNull(op.questionId)}/${op.kind}"
    else -> error("Unsupported curiosity operation")
}
