@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)
package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable

@Serializable data class DeviceCredentialDto(val id: UUID, val label: String, val created_at: Long,
    val expires_at: Long, val last_used_at: Long?, val revoked_at: Long?, val rotated_from_id: UUID?)
@Serializable class CredentialIssueDto(val credential: DeviceCredentialDto, val token: String?) {
    override fun toString() = "CredentialIssueDto(redacted)"
}
@Serializable data class CredentialInputDto(val operation_id: UUID, val label: String, val lifetime_days: Int = 30)
@Serializable data class SecurityStatusDto(val owner_id: UUID, val current_credential_id: UUID?,
    val legacy_credential: Boolean, val enrollment_enabled: Boolean, val deletion_worker_enabled: Boolean,
    val data_epoch: Long, val retention: String)
@Serializable data class DeletionPreviewDto(val id: UUID, val revision: Long, val created_at: Long,
    val expires_at: Long, val counts: Map<String, Long>, val retained: List<String>,
    val backups_may_retain_content: Boolean, val offline_clients_may_retain_content: Boolean)
@Serializable data class DeletionInputDto(val job_id: UUID, val preview_id: UUID,
    val confirmation: String = "erase_saved_content")
@Serializable data class DeletionDto(val id: UUID, val status: String, val attempt: Int,
    val created_at: Long, val finished_at: Long?, val error_code: String?, val counts: Map<String, Long>,
    val backups_may_retain_content: Boolean, val offline_clients_may_retain_content: Boolean)
@Serializable data class SecurityJournal(val identity: SessionIdentity, val kind: String,
    val operation: UUID, val label: String = "", val credential: UUID? = null, val preview: UUID? = null) {
    init {
        require(kind in setOf("enroll", "rotate", "delete"))
        require(if (kind == "delete") preview != null && label.isEmpty() && credential == null
            else label.length in 1..80 && label.none { it.code < 32 } && preview == null &&
                (kind == "enroll" || credential != null))
    }
}
