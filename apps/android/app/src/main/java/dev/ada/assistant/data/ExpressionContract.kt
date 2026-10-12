@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*

@Serializable data class PreferenceValuesDto(val verbosity: String? = null, val initiative: String? = null,
    val formality: String? = null, val humor: String? = null, val cadence: String? = null)
@Serializable data class PreferenceDto(val target_kind: String, val target_id: UUID, val revision: Int,
    val values: PreferenceValuesDto, val receipt_id: UUID? = null)
@Serializable data class ExpressionVectorDto(val warmth: Int, val focus: Int, val energy: Int,
    val playfulness: Int, val concern: Int)
@Serializable data class ExpressionDto(val policy_version: String, val conversation_id: UUID,
    val profile_id: UUID, val scope_id: UUID, val active: Boolean, val binding_revision: Int,
    val preferences: PreferenceValuesDto, val origins: Map<String, String>, val dynamic_enabled: Boolean,
    val session_id: UUID? = null, val turn: Int, val vector: ExpressionVectorDto,
    val defaults: ExpressionVectorDto, val expires_at: Long? = null, val expired: Boolean,
    val last_request_id: UUID? = null, val source_receipts: Map<String, UUID?> = emptyMap())
@Serializable data class PreferenceWriteDto(val operation_id: UUID, val expected_revision: Int,
    val values: PreferenceValuesDto, val dynamic_enabled: Boolean? = null)
@Serializable data class ExpressionResetDto(val operation_id: UUID, val session_id: UUID)
@Serializable data class ExpressionSignalDto(val operation_id: UUID, val session_id: UUID,
    val source_request_id: UUID, val reviewed: Boolean = true, val reason: String = "user_selected",
    val vector: Map<String, Int>)
@Serializable data class ExpressionReceiptDto(val operation_id: UUID, val action: String,
    val target_kind: String, val target_id: UUID, val created_at: Long,
    val preference: PreferenceDto? = null, val expression: ExpressionDto? = null,
    val reason: String = "explicit_settings", val source_request_id: UUID? = null)
@Serializable data class ExpressionJournal(val identity: SessionIdentity, val operationId: UUID,
    val action: String, val targetKind: String, val targetId: UUID, val body: String) {
    override fun toString() = "ExpressionJournal(redacted)"
}

val preferenceChoices = linkedMapOf("verbosity" to listOf("concise", "balanced", "detailed"),
    "initiative" to listOf("respond", "suggest"), "formality" to listOf("casual", "neutral", "formal"),
    "humor" to listOf("none", "light"), "cadence" to listOf("direct", "stepwise"))
fun validatePreferences(values: PreferenceValuesDto) {
    val entries = listOf(values.verbosity, values.initiative, values.formality, values.humor, values.cadence)
    preferenceChoices.values.zip(entries).forEach { (choices, value) -> require(value == null || value in choices) }
}
fun validateExpression(value: ExpressionDto) {
    require(value.policy_version == "ada-expression-v1" && value.turn >= 0 && value.binding_revision >= 0)
    validatePreferences(value.preferences)
    require(listOf(value.preferences.verbosity, value.preferences.initiative, value.preferences.formality, value.preferences.humor, value.preferences.cadence).all { it != null })
    for (v in listOf(value.vector, value.defaults)) require(listOf(v.warmth, v.focus, v.energy, v.playfulness, v.concern).all { it in 0..100 })
    require(value.origins.keys == preferenceChoices.keys && value.origins.values.all { it in setOf("personality", "account", "scope", "profile", "conversation") })
    require(value.source_receipts.keys == preferenceChoices.keys)
    require(value.origins.all { (key, origin) -> (origin == "personality") == (value.source_receipts[key] == null) })
}
fun validateExpressionJournal(journal: ExpressionJournal) {
    require(journal.targetKind in setOf("account", "scope", "profile", "conversation"))
    require(journal.targetKind != "account" || journal.targetId == journal.identity.owner)
    require(journal.body.toByteArray().size <= 4096)
    val raw = adaJson.parseToJsonElement(journal.body).jsonObject
    require(raw["operation_id"]?.jsonPrimitive?.content == journal.operationId.toString())
    when (journal.action) {
        "preferences" -> {
            require(raw.keys.all { it in setOf("operation_id", "expected_revision", "values", "dynamic_enabled") })
            require(raw["values"]!!.jsonObject.keys.all { it in preferenceChoices })
            val input = adaJson.decodeFromString<PreferenceWriteDto>(journal.body)
            require(input.expected_revision >= 0)
            require(input.dynamic_enabled == null || journal.targetKind == "conversation")
            validatePreferences(input.values)
        }
        "reset" -> {
            require(journal.targetKind == "conversation" && raw.keys == setOf("operation_id", "session_id"))
            adaJson.decodeFromString<ExpressionResetDto>(journal.body)
        }
        "signal" -> {
            require(journal.targetKind == "conversation" && raw.keys == setOf("operation_id", "session_id", "source_request_id", "reviewed", "reason", "vector"))
            val input = adaJson.decodeFromString<ExpressionSignalDto>(journal.body)
            require(input.reviewed && input.reason == "user_selected" && input.vector.isNotEmpty())
            require(input.vector.keys.all { it in setOf("warmth", "focus", "energy", "playfulness", "concern") } && input.vector.values.all { it in -1000..1000 })
        }
        else -> error("Unsupported expression action")
    }
}
