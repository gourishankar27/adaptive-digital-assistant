@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import dev.ada.assistant.edge.EDGE_MODEL_ID
import dev.ada.assistant.edge.EDGE_MODEL_DIGEST
import dev.ada.assistant.edge.EDGE_RUNTIME

const val EDGE_PROTOCOL="ada-device-drafts-v1"
@Serializable data class EdgeDeviceDto(val version:String=EDGE_PROTOCOL,val id:UUID,val revision:Int,val last_sequence:Int,
    val label:String,val public_key:String,val revoked_at:Long?=null,val created_at:Long,
    val enrollment_id:UUID?=null,val revocation_id:UUID?=null) { override fun toString()="EdgeDevice(redacted)" }
@Serializable data class EdgeEnrollDto(val operation_id:UUID,val label:String,val public_key:String,val review:String="confirm") { override fun toString()="EdgeEnroll(redacted)" }
@Serializable data class EdgeRevokeDto(val operation_id:UUID,val expected_revision:Int,val review:String="confirm") { override fun toString()="EdgeRevoke(redacted)" }
@Serializable data class EdgeSyncDto(val proposal_id:UUID,val device_id:UUID,val device_revision:Int,val sequence:Int,
    val prompt:String,val prompt_hash:String,val output:String,val signature:String,val sources:List<SourcePinDto> = emptyList(),
    val task:String="offline_reply",val model_id:String=EDGE_MODEL_ID,val model_digest:String=EDGE_MODEL_DIGEST,val runtime:String=EDGE_RUNTIME) { override fun toString()="EdgeSync(redacted)" }
@Serializable data class EdgeProposalDto(val version:String=EDGE_PROTOCOL,val id:UUID,val scope_id:UUID,val device_id:UUID,
    val sequence:Int,val task:String,val model_id:String,val model_digest:String,val runtime:String,val output:String,
    val sources:List<SourcePinDto>,val trust_class:String,val state:String,val created_at:Long,val prompt_hash:String="") { override fun toString()="EdgeProposal(redacted)" }
@Serializable data class EdgePending(val operationId:UUID,val kind:String,val deviceId:UUID,val body:String,val scopeId:UUID?=null) { override fun toString()="EdgePending(redacted)" }
@Serializable data class EdgeLocalDraft(val scopeId:UUID,val prompt:String,val output:String,val truncated:Boolean,
    val proposalId:UUID,val createdAt:Long,val modelId:String=EDGE_MODEL_ID,val modelDigest:String=EDGE_MODEL_DIGEST,val runtime:String=EDGE_RUNTIME) { override fun toString()="EdgeLocalDraft(redacted)" }
@Serializable data class EdgeJournal(val identity:SessionIdentity,val operations:List<EdgePending> = emptyList(),
    val draft:EdgeLocalDraft?=null,val lastProposal:UUID?=null) { override fun toString()="EdgeJournal(redacted)" }
fun edgeSigningMessage(scope:UUID,body:EdgeSyncDto):ByteArray {
    val sources=body.sources.joinToString("\n") { "${it.source_version_id}:${it.version}:${it.content_hash}:${it.span_start}:${it.span_end}" }
    return listOf(EDGE_PROTOCOL,scope.toString(),body.proposal_id.toString(),body.device_id.toString(),body.device_revision.toString(),body.sequence.toString(),body.task,body.model_id,body.model_digest,body.runtime,body.prompt_hash,voiceHash(body.output),voiceHash(sources)).joinToString("\n").toByteArray(Charsets.US_ASCII)
}
fun validateEdgeJournal(j:EdgeJournal) {
    require(j.operations.size<=4 && j.operations.map{it.operationId}.distinct().size==j.operations.size)
    j.draft?.let { require(it.modelId==EDGE_MODEL_ID && it.modelDigest==EDGE_MODEL_DIGEST && it.runtime==EDGE_RUNTIME && voiceTextValid(it.prompt) && voiceTextValid(it.output) && it.prompt.toByteArray().size in 1..1500 && it.output.toByteArray().size in 1..12000) }
    j.operations.forEach { p ->
        require(p.body.toByteArray().size in 1..24000)
        when(p.kind) {
            "enroll" -> { val b=adaJson.decodeFromString<EdgeEnrollDto>(p.body);require(b.operation_id==p.operationId && b.review=="confirm" && b.label.isNotBlank() && b.public_key.length in 80..256) }
            "revoke" -> { val b=adaJson.decodeFromString<EdgeRevokeDto>(p.body);require(b.operation_id==p.operationId && b.expected_revision>0 && b.review=="confirm") }
            "sync" -> { val b=adaJson.decodeFromString<EdgeSyncDto>(p.body);require(p.scopeId!=null && b.proposal_id==p.operationId && b.device_id==p.deviceId && b.sequence>0 && b.device_revision>0 && b.prompt_hash==voiceHash(b.prompt) && b.model_id==EDGE_MODEL_ID && b.model_digest==EDGE_MODEL_DIGEST && b.runtime==EDGE_RUNTIME && b.sources.size<=4 && b.signature.length in 80..192) }
            else -> error("Unsupported edge operation")
        }
    }
}
fun edgePath(p:EdgePending)=when(p.kind) {
    "enroll" -> "edge/devices/${p.deviceId}"
    "revoke" -> "edge/devices/${p.deviceId}/revoke"
    "sync" -> "scopes/${requireNotNull(p.scopeId)}/edge/proposals/${p.operationId}"
    else -> error("Unsupported edge operation")
}
