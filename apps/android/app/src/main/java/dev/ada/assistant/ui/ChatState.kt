package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID

enum class ChatDestination { Connect, Conversations, NewConversation, Chat, Sources, Retrieval, Settings }
enum class PendingPhase { Journaling, Submitting, Unknown, Running, Failed, Missing, Conflict, Blocked }
data class ChatPage<T>(
    val items: List<T> = emptyList(), val loading: Boolean = false,
    val hasMore: Boolean = false, val nextOffset: Int = 0,
)
data class PendingState(
    val message: PendingMessage, val phase: PendingPhase,
    val response: RequestDto? = null, val failure: ApiFailure? = null, val code: String? = null,
)
data class ChatState(
    val destination: ChatDestination = ChatDestination.Connect,
    val account: AccountSummary? = null, val capabilities: CapabilitiesDto? = null,
    val connecting: Boolean = false,
    val conversations: ChatPage<ConversationDto> = ChatPage(),
    val profiles: ChatPage<PersonalityDto> = ChatPage(), val scopes: ChatPage<ScopeDto> = ChatPage(),
    val conversation: ConversationDto? = null, val events: ChatPage<EventDto> = ChatPage(),
    val draft: String = "", val useMemory: Boolean = true, val asOf: String = "",
    val pending: PendingState? = null, val sources: Map<UUID, RequestDto> = emptyMap(),
    val submittedMessages: Map<UUID, PendingMessage> = emptyMap(),
    val sourceRequestId: UUID? = null, val sourceLabel: String? = null,
    val sourceLoading: Boolean = false, val trace: TraceDto? = null,
    val traceLoading: Boolean = false, val traceMissing: Boolean = false,
    val fault: ApiFailure? = null, val notice: String? = null,
    val createTitle: String = "", val createProfileId: UUID? = null, val createScopeId: UUID? = null,
    val creating: Boolean = false, val creationUncertain: Boolean = false,
    val creatingProfile: Boolean = false, val profileUncertain: Boolean = false,
    val upgrading: Boolean = false,
)
