@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.Serializable

@Serializable
class PasswordLoginInput(val username: String, val password: String) {
    override fun toString() = "PasswordLoginInput(redacted)"
}
@Serializable
class RefreshLoginInput(val refresh_token: String) {
    override fun toString() = "RefreshLoginInput(redacted)"
}
@Serializable
class PasswordChangeInput(val current_password: String, val new_password: String) {
    override fun toString() = "PasswordChangeInput(redacted)"
}
@Serializable
class PasswordSessionDto(val access_token: String, val refresh_token: String, val session_id: UUID,
    val access_expires_at: Long, val expires_at: Long) {
    override fun toString() = "PasswordSessionDto(redacted)"
}
@Serializable
data class LoginSessionDto(val id: UUID, val label: String, val created_at: Long, val expires_at: Long, val revoked_at: Long?)
@Serializable
data class AuthAcknowledgementDto(val status: String)
