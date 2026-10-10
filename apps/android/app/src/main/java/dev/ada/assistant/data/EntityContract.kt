@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import java.nio.charset.CodingErrorAction
import java.nio.CharBuffer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonPrimitive

@Serializable data class EntityChoiceDto(val id: UUID, val label: String, val kind: String)
@Serializable data class EntityDto(
    val id: UUID, val scope_id: UUID, val label: String, val kind: String, val normalized_key: String,
    val revision: Int, val redirect_id: UUID? = null, val created_at: Long, val is_self: Boolean,
    val origin: String = "user_confirmed",
)
@Serializable data class EntityAliasDto(
    val id: UUID, val scope_id: UUID, val entity_id: UUID, val label: String,
    val normalized_key: String, val canonical: Boolean, val created_at: Long, val valid_to: Long? = null,
    val origin: String = "user_confirmed",
)
@Serializable data class EntityLinkDto(val claim_id: UUID, val entity_id: UUID? = null, val original_subject: String)
@Serializable data class EntityOperationDto(
    val id: UUID, val scope_id: UUID, val action: String, val created_at: Long,
    val entity: EntityDto? = null, val alias: EntityAliasDto? = null, val link: EntityLinkDto? = null,
)
@Serializable data class EntityResolutionDto(
    val state: String, val name: String? = null, val entity_id: UUID? = null,
    val candidates: List<EntityChoiceDto>, val alias_ids: List<UUID>, val explicitly_selected: Boolean = false,
    val truncated: Boolean = false, val policy: String = "nfkc_casefold_whitespace_v1",
)
@Serializable data class EntityResolveInputDto(val name: String? = null, val self_reference: Boolean = false, val selected_id: UUID? = null, val as_of: String? = null)
@Serializable data class EntityMergePreviewDto(
    val source: EntityDto, val target: EntityDto, val alias_count: Int, val claim_link_count: Int,
    val self_binding_affected: Boolean, val preview_token: String,
)
@Serializable data class PendingEntity(
    val identity: SessionIdentity, val scopeId: UUID, val operationId: UUID,
    val action: String, val path: String, val body: String,
) { override fun toString() = "PendingEntity(redacted)" }

private val entityActions = setOf("create", "alias", "retire_alias", "rename", "self", "link", "merge", "undo_merge")
fun validateEntityPending(pending: PendingEntity) {
    try {
        require(pending.action in entityActions && pending.body.toByteArray(Charsets.UTF_8).size in 1..8192)
        val uuid = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        val expected = when (pending.action) {
            "create" -> "scopes/${pending.scopeId}/entities"
            "self" -> "scopes/${pending.scopeId}/entities/self"
            "retire_alias" -> "entity-aliases/$uuid/retire"
            "link" -> "claims/$uuid/entity"
            "alias" -> "entities/$uuid/aliases"
            "undo_merge" -> "entities/$uuid/undo-merge"
            else -> "entities/$uuid/${pending.action}"
        }
        require(Regex(expected).matches(pending.path))
        val body = adaJson.parseToJsonElement(pending.body) as JsonObject
        require(body["operation_id"]?.jsonPrimitive?.content == pending.operationId.toString())
        require(body.values.all { it is JsonPrimitive || it == JsonNull })
        body.values.filterIsInstance<JsonPrimitive>().filter { it.isString }.forEach {
            require('\u0000' !in it.content)
            Charsets.UTF_8.newEncoder().onMalformedInput(CodingErrorAction.REPORT)
                .onUnmappableCharacter(CodingErrorAction.REPORT).encode(CharBuffer.wrap(it.content))
        }
    } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
}

fun verifyEntityOperation(pending: PendingEntity, receipt: EntityOperationDto): Boolean = runCatching {
    validateEntityPending(pending)
    require(receipt.id == pending.operationId && receipt.scope_id == pending.scopeId && receipt.action == pending.action)
    receipt.entity?.let { require(it.scope_id == pending.scopeId && it.origin == "user_confirmed" && it.revision >= 0) }
    receipt.alias?.let { require(it.scope_id == pending.scopeId && it.origin == "user_confirmed") }
    val body = adaJson.parseToJsonElement(pending.body) as JsonObject
    fun text(key: String) = body[key]?.takeIf { it != JsonNull }?.jsonPrimitive?.content
    val pathId = pending.path.split('/').getOrNull(1)
    when (pending.action) {
        "create" -> require(receipt.entity?.id.toString() == text("entity_id") && receipt.entity?.label == text("label") && receipt.entity?.kind == text("kind"))
        "alias" -> require(receipt.alias?.id.toString() == text("alias_id") && receipt.alias?.entity_id.toString() == pathId && receipt.alias?.label == text("label"))
        "rename" -> require(receipt.entity?.id.toString() == pathId && receipt.entity?.label == text("label"))
        "self" -> require(receipt.entity?.id.toString() == text("entity_id") && receipt.entity?.is_self == true)
        "merge" -> require(receipt.entity?.id.toString() == pathId && receipt.entity?.redirect_id.toString() == text("target_id"))
        "undo_merge" -> require(receipt.entity?.id.toString() == pathId && receipt.entity != null && receipt.entity.redirect_id == null)
        "retire_alias" -> require(receipt.alias?.id.toString() == pathId && receipt.alias?.valid_to != null)
        "link" -> require(receipt.link?.claim_id.toString() == pathId && receipt.link != null && receipt.link.entity_id?.toString() == text("entity_id"))
    }
    true
}.getOrDefault(false)
