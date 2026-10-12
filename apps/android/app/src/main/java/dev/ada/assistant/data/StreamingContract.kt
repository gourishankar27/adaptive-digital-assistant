@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.contentOrNull

@Serializable data class StreamStatusDto(
    val request_id: UUID, val conversation_id: UUID, val attempt: Int,
    val available: Boolean, val stream_state: String, val sequence: Int,
    val replay_after: Int, val provisional: String, val result: RequestDto,
)
@Serializable data class StreamEventDto(
    val request_id: UUID, val attempt: Int, val sequence: Int, val type: String,
    val payload: JsonObject, val created_at: Long,
)
@Serializable data class CancelInputDto(val attempt: Int)
@Serializable data class CancelReceiptDto(
    val request_id: UUID, val attempt: Int, val outcome: String,
    val observed_state: String, val created_at: Long,
)
fun CapabilitiesDto.hasStreaming() = streaming && generation_cancellation && stream_protocol == "ada-stream-v1"
private val streamStates = setOf("running", "cancel_requested", "completed", "failed", "cancelled", "interrupted")
fun StreamStatusDto.validate(request: UUID, conversation: UUID) {
    require(request_id == request && conversation_id == conversation && result.request_id == request && result.conversation_id == conversation)
    require(attempt == result.attempt && attempt in 1..1000000 && sequence >= 0 && replay_after in 0..sequence)
    require(stream_state in streamStates && provisional.toByteArray(Charsets.UTF_8).size <= 65536 && provisional.validStreamUnicode())
    require(if (stream_state in setOf("running", "cancel_requested")) result.status == "running" else if (stream_state == "completed") result.status == "completed" && result.response != null else result.status == "failed")
}
private fun String.validStreamUnicode(): Boolean {
    if (contains('\u0000')) return false
    var i = 0
    while (i < length) { val c = this[i++]; if (c.isLowSurrogate()) return false; if (c.isHighSurrogate() && (i >= length || !this[i++].isLowSurrogate())) return false }
    return true
}
class StreamGap : Exception()
/** Provisional state only; this never constructs confirmed source cards. */
class StreamAccumulator(checkpoint: StreamStatusDto) {
    val request = checkpoint.request_id
    val attempt = checkpoint.attempt
    var sequence = checkpoint.sequence; private set
    var text = checkpoint.provisional; private set
    var state = checkpoint.stream_state; private set
    fun accept(event: StreamEventDto) {
        require(event.request_id == request && event.attempt == attempt && event.sequence > 0 && event.created_at >= 0)
        require(event.type in streamStates + setOf("started", "delta", "status"))
        if (event.sequence <= sequence) return
        if (event.sequence != sequence + 1) throw StreamGap()
        require(state in setOf("running", "cancel_requested"))
        if (event.type == "delta") {
            require(state == "running" && event.payload.keys == setOf("text"))
            val value = (event.payload["text"] as? JsonPrimitive)?.takeIf { it.isString }?.contentOrNull ?: error("Invalid delta")
            require(value.validStreamUnicode() && value.toByteArray(Charsets.UTF_8).size <= 4096)
            require((text + value).toByteArray(Charsets.UTF_8).size <= 65536)
            text += value
        } else {
            require(event.payload.keys.all { it in setOf("legacy_status", "error_code") })
            if (event.type in streamStates) state = event.type
        }
        sequence = event.sequence
    }
}
