package dev.ada.assistant.ui

import java.util.UUID
import dev.ada.assistant.data.ApiFailure

data class AccountSummary(val server: String, val owner: UUID, val name: String, val provider: String, val model: String)
sealed interface ConnectionState {
    data object Empty : ConnectionState
    data object Validating : ConnectionState
    data class Connected(val account: AccountSummary) : ConnectionState
    data class Error(val failure: ApiFailure) : ConnectionState
    data object InvalidInput : ConnectionState
}

/** Presentation types only: later phases wire each screen to authorized repositories. */
enum class Destination { Connect, Conversations, NewConversation, Chat, Sources, Memory, Settings }
enum class ScreenCondition {
    Empty, Loading, Loaded, Error, Refreshing, PendingCreation, Selection, Validation, Creating,
    CreationOutcomeUnknown, Ready, Sending, Running, Reconnecting, Failed, Completed, AccessLost,
    Available, UnknownLabel, MissingLegacyTrace, AccessDenied, Historical, Conflicting, Saving,
    Recovering, ChangedSettings, ProfileSaved, UpgradeConflict, LoggedOut,
}
data class ScreenDefinition(val destination: Destination, val enabledPhase: Int, val conditions: Set<ScreenCondition>)
val screenMap = listOf(
    ScreenDefinition(Destination.Connect, 3, setOf(ScreenCondition.Empty, ScreenCondition.Loading, ScreenCondition.Loaded, ScreenCondition.Error, ScreenCondition.AccessDenied, ScreenCondition.Validation)),
    ScreenDefinition(Destination.Conversations, 4, setOf(ScreenCondition.Loading, ScreenCondition.Empty, ScreenCondition.Loaded, ScreenCondition.Error, ScreenCondition.Refreshing, ScreenCondition.PendingCreation)),
    ScreenDefinition(Destination.NewConversation, 4, setOf(ScreenCondition.Selection, ScreenCondition.Validation, ScreenCondition.Creating, ScreenCondition.CreationOutcomeUnknown)),
    ScreenDefinition(Destination.Chat, 4, setOf(ScreenCondition.Loading, ScreenCondition.Ready, ScreenCondition.Sending, ScreenCondition.Running, ScreenCondition.Reconnecting, ScreenCondition.Failed, ScreenCondition.Completed, ScreenCondition.AccessLost)),
    ScreenDefinition(Destination.Sources, 4, setOf(ScreenCondition.Available, ScreenCondition.UnknownLabel, ScreenCondition.MissingLegacyTrace, ScreenCondition.AccessDenied)),
    ScreenDefinition(Destination.Memory, 7, setOf(ScreenCondition.Empty, ScreenCondition.Loading, ScreenCondition.Historical, ScreenCondition.Conflicting, ScreenCondition.Validation, ScreenCondition.Saving, ScreenCondition.Recovering)),
    ScreenDefinition(Destination.Settings, 4, setOf(ScreenCondition.Loaded, ScreenCondition.ChangedSettings, ScreenCondition.ProfileSaved, ScreenCondition.UpgradeConflict, ScreenCondition.LoggedOut)),
)

fun ApiFailure.message(): String = when (this) {
    ApiFailure.Unauthorized -> "The token was rejected. Enter a current token and connect again."
    ApiFailure.Forbidden, ApiFailure.NotFound -> "This account cannot access the requested information."
    ApiFailure.Conflict -> "The request conflicts with saved data. Refresh before continuing."
    ApiFailure.TooLarge -> "The request is too large. Keep your draft and shorten it."
    ApiFailure.Validation -> "Check the entered values and try again."
    is ApiFailure.Busy -> "ADA is busy. Wait and try again."
    ApiFailure.Provider -> "The model provider is unavailable. Try again later."
    ApiFailure.Timeout -> "The connection timed out. Check your connection and try again. A timeout does not establish whether a submitted request completed."
    ApiFailure.Unreachable -> "ADA could not be reached. Check the address, Wi-Fi or VPN, firewall, proxy and server. This error does not identify which is unavailable. Retry after restoring the connection."
    ApiFailure.Tls -> "The secure server identity could not be verified. Check the hostname, certificate trust/expiry and device clock. Do not bypass certificate checks."
    ApiFailure.Dns -> "The server name could not be resolved. Check spelling, DNS and your private network or VPN, then retry."
    ApiFailure.ServerNotReady -> "The server was reached but its database is not ready. Ask the server operator to check connectivity and migrations, then retry."
    ApiFailure.IncompatibleContract -> "This server returned an incompatible API contract. Check the server version."
    is ApiFailure.Http -> "The server could not complete the request (HTTP $status). Try again later."
}
