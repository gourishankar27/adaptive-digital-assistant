@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject

val selectedAgentTools = setOf("calculator", "memory_lookup", "source_lookup")
@Serializable data class AgentInputDto(val run_id: UUID, val task: String, val protocol_version: String = "ada-agent-v1", val allowed_tools: List<String>, val as_of: String? = null) {
    override fun toString() = "AgentInputDto(redacted)"
}
@Serializable data class AgentApprovalDto(val approval_id: UUID, val preview_hash: String, val argument_hash: String, val tool_version: String)
@Serializable data class AgentRecoverDto(val operation_id: UUID, val generation: Int)
@Serializable data class ToolReceiptDto(val id: UUID, val approval_id: UUID, val owner_id: UUID, val run_id: UUID, val scope_id: UUID, val step_id: UUID, val tool: String? = null, val tool_version: String? = null, val argument_hash: String? = null, val preview_hash: String? = null, val outcome: String, val origin: String, val trust_class: String, val result: JsonObject? = null, val error_code: String? = null, val created_at: Long) {
    override fun toString() = "ToolReceiptDto(redacted)"
}
@Serializable data class AgentStepDto(val id: UUID, val number: Int, val attempt: Int, val status: String, val tool: String? = null, val tool_version: String? = null, val arguments: JsonObject? = null, val argument_hash: String? = null, val preview_hash: String? = null, val expires_at: Long? = null, val receipt: ToolReceiptDto? = null) {
    override fun toString() = "AgentStepDto(redacted)"
}
@Serializable data class AgentRunDto(val id: UUID, val owner_id: UUID, val scope_id: UUID, val conversation_id: UUID, val protocol_version: String, val status: String, val response: String? = null, val error_code: String? = null, val provider: String, val model: String, val generation: Int, val lease_until: Long? = null, val created_at: Long, val finished_at: Long? = null, val as_of: Long, val steps: List<AgentStepDto>) {
    override fun toString() = "AgentRunDto(redacted)"
}
@Serializable data class AgentOperation(val kind: String, val id: UUID, val stepId: UUID? = null, val body: String) {
    override fun toString() = "AgentOperation(redacted)"
}
/** Exact create reservation and optional exact approval/recovery survive lost delivery. */
@Serializable data class AgentJournal(val identity: SessionIdentity, val scopeId: UUID, val conversationId: UUID, val runId: UUID, val body: String, val operation: AgentOperation? = null) {
    override fun toString() = "AgentJournal(redacted)"
}
private val agentJournalJson = Json { ignoreUnknownKeys = false }
fun validateAgentJournal(p: AgentJournal) {
    require(p.body.toByteArray(Charsets.UTF_8).size <= 18000)
    val input = agentJournalJson.decodeFromString<AgentInputDto>(p.body)
    require(input.run_id == p.runId && input.protocol_version == "ada-agent-v1")
    require(input.task.isNotBlank() && input.task.codePointCount(0, input.task.length) in 1..4000 && validAgentUnicode(input.task))
    require(input.allowed_tools.size in 1..3 && input.allowed_tools.distinct() == input.allowed_tools && input.allowed_tools.all { it in selectedAgentTools })
    input.as_of?.let { require(normalizeUtcMillis(it) != null) }
    p.operation?.let { op ->
        require(op.body.length <= 1000)
        when (op.kind) {
            "approve", "revoke" -> {
                val a = agentJournalJson.decodeFromString<AgentApprovalDto>(op.body)
                require(op.stepId != null && a.approval_id == op.id && a.preview_hash.matches(Regex("[a-f0-9]{64}")) && a.argument_hash.matches(Regex("[a-f0-9]{64}")) && a.tool_version in setOf("calculator-v1", "memory-lookup-v1", "source-lookup-v1"))
            }
            "recover" -> { val r = agentJournalJson.decodeFromString<AgentRecoverDto>(op.body); require(op.stepId == null && r.operation_id == op.id && r.generation > 0) }
            else -> error("Invalid agent operation")
        }
    }
}
private fun validAgentUnicode(text: String): Boolean {
    var i = 0
    while (i < text.length) {
        val c = text[i]
        if (c.isHighSurrogate()) { if (i + 1 == text.length || !text[i + 1].isLowSurrogate()) return false; i += 2 }
        else { if (c.isLowSurrogate() || c == '\u0000') return false; i++ }
    }
    return true
}
fun CapabilitiesDto.hasAgentTools() = agent_tools == "approval_read_only_v1" && agent_protocol == "ada-agent-v1" && agent_registry.toSet() == selectedAgentTools
