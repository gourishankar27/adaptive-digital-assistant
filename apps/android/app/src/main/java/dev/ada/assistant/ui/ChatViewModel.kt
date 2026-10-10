package dev.ada.assistant.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.ada.assistant.data.*
import java.time.OffsetDateTime
import java.time.format.DateTimeParseException
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/** Recovery state is client intent, never authorization. Every restored identity is verified by ADA. */
class ChatViewModel(
    private val api: AdaApi, private val store: SessionStore, private val allowDebugHttp: Boolean,
    private val pollDelaysMs: List<Long> = listOf(0, 1000, 2000, 4000, 8000, 16000),
) : ViewModel() {
    private val mutableState = MutableStateFlow(ChatState())
    val state = mutableState.asStateFlow()
    val memory = MemoryController(api, store, viewModelScope) { expire() }
    private var credential: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private val jobs = mutableSetOf<Job>()
    private var pollJob: Job? = null
    private val storage = Mutex()
    private var cleanupJob: Job? = null
    private var cleanupFailed = false
    private val drafts = mutableMapOf<UUID, Draft>()
    private var selection = 0L
    private var sourceSelection = 0L
    private var retryNotBefore = 0L
    private data class Draft(val text: String = "", val memory: Boolean = true, val at: String = "")

    init { require(pollDelaysMs.isNotEmpty() && pollDelaysMs.size <= 12 && pollDelaysMs.all { it in 0..60_000 }) }
    private fun update(block: (ChatState) -> ChatState) { mutableState.value = block(mutableState.value) }
    private fun launchWork(block: suspend () -> Unit): Job {
        val launchedEpoch = generation
        return viewModelScope.launch {
        try { block() }
        catch (cancelled: CancellationException) { throw cancelled }
        catch (_: Exception) {
            if (current(launchedEpoch)) update { it.copy(connecting = false, creating = false, creatingProfile = false,
                upgrading = false, sourceLoading = false, traceLoading = false,
                conversations = it.conversations.copy(loading = false), profiles = it.profiles.copy(loading = false),
                scopes = it.scopes.copy(loading = false), events = it.events.copy(loading = false),
                pending = it.pending?.let { pending -> if (pending.phase == PendingPhase.Submitting) pending.copy(phase = PendingPhase.Unknown) else pending },
                fault = ApiFailure.IncompatibleContract, notice = "The operation could not be completed safely. Reconnect or refresh before continuing.") }
        }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun current(epoch: Long) = epoch == generation
    private fun resetMemory() {
        memory.reset()
        generation++; selection++; sourceSelection++
        jobs.toList().forEach { it.cancel() }; jobs.clear(); pollJob = null
        credential = null; identity = null; drafts.clear(); retryNotBefore = 0
    }
    private fun expire(reason: ApiFailure? = ApiFailure.Unauthorized, notice: String? = null) {
        resetMemory()
        mutableState.value = ChatState(fault = reason, notice = notice)
        clearDurably(reportSuccess = reason == null)
    }
    private fun clearDurably(reportSuccess: Boolean = false) {
        val previous = cleanupJob
        val epoch = generation
        // A subsequent Connect or Activity teardown must not cancel a requested logout.
        cleanupJob = viewModelScope.launch(NonCancellable) {
            previous?.join()
            try {
                storage.withLock { store.clear() }; cleanupFailed = false
                if (reportSuccess && current(epoch) && mutableState.value.account == null) update {
                    it.copy(notice = "Disconnected. Private drafts, sources and recovery state were cleared.")
                }
            } catch (_: Exception) {
                cleanupFailed = true
                if (current(epoch) && mutableState.value.account == null) update { it.copy(connecting = false,
                    fault = ApiFailure.IncompatibleContract,
                    notice = "Private data is hidden, but encrypted recovery data could not be removed. Resolve device storage before reconnecting.") }
            }
        }
    }
    private suspend fun awaitCleanup(): Boolean {
        cleanupJob?.join()
        if (!cleanupFailed) return true
        return try { storage.withLock { store.clear() }; cleanupFailed = false; true }
        catch (_: Exception) { false }
    }
    fun logout() = expire(reason = null, notice = "Disconnecting. Private data is hidden while encrypted recovery state is removed.")
    fun disconnect() = logout()

    fun restore() {
        resetMemory(); mutableState.value = ChatState(connecting = true)
        val epoch = generation
        launchWork {
            if (!awaitCleanup()) { if (current(epoch)) expire(ApiFailure.IncompatibleContract, "Private recovery storage could not be cleared safely. Resolve device storage before reconnecting."); return@launchWork }
            val saved = try { storage.withLock { store.readCredential() } } catch (_: Exception) { null }
            if (!current(epoch)) return@launchWork
            if (saved == null) {
                storage.withLock { if (current(epoch)) store.clear() }
                update { it.copy(connecting = false, notice = "Connect with a current token. Unusable encrypted state is discarded.") }
                return@launchWork
            }
            establish(saved.identity.server, saved.token, epoch, expectedOwner = saved.identity.owner)
        }
    }

    fun connect(server: String, token: String) {
        resetMemory(); mutableState.value = ChatState(connecting = true)
        // An explicit connection is an account/server switch. Restore is the
        // separate identity-verified path that retains a recovery journal.
        clearDurably()
        val epoch = generation
        launchWork { establish(server, token, epoch) }
    }
    fun rotateCredential(server: String, token: String) {
        val previous = identity ?: run { connect(server, token); return }
        val normalized = ConnectionCredential.parse(server, token, allowDebugHttp)?.server?.toString()
        if (normalized != previous.server) { connect(server, token); return }
        resetMemory(); mutableState.value = ChatState(connecting = true)
        val epoch = generation
        launchWork { establish(server, token, epoch, expectedOwner = previous.owner) }
    }

    private suspend fun establish(server: String, token: String, epoch: Long, expectedOwner: UUID? = null) {
        if (!awaitCleanup()) {
            if (current(epoch)) expire(ApiFailure.IncompatibleContract, "Secure cleanup could not be confirmed. Resolve device storage before connecting.")
            return
        }
        if (!current(epoch)) return
        val connection = ConnectionCredential.parse(server, token, allowDebugHttp)
        if (connection == null) {
            storage.withLock { if (current(epoch)) store.clear() }
            if (current(epoch)) update { it.copy(connecting = false, fault = ApiFailure.Validation) }
            return
        }
        val normalized = connection.server.toString()
        storage.withLock {
            if (!current(epoch)) return
            if (store.readCredential()?.identity?.server?.let { it != normalized } == true) store.clear()
        }
        val user = value(api.me(connection), epoch) ?: return
        if (!current(epoch)) return
        if (expectedOwner != null && user.id != expectedOwner) {
            expire(ApiFailure.Unauthorized, "The stored account does not match this token. Connect again; old recovery data was cleared.")
            return
        }
        val features = value(api.capabilities(connection), epoch) ?: return
        if (!current(epoch)) return
        if (features.api_version != "v1" || features.authority != "server" || !features.chat) {
            expire(ApiFailure.IncompatibleContract); return
        }
        val verified = SessionIdentity(normalized, user.id)
        val savedPending = try {
            storage.withLock {
                if (!current(epoch)) return
                store.saveCredential(StoredCredential(verified, token))
                store.pending(verified)
            }
        } catch (_: Exception) {
            if (current(epoch)) expire(ApiFailure.IncompatibleContract, "Secure storage is unavailable. Reconnect after resolving the device storage issue.")
            return
        }
        if (!current(epoch)) return
        credential = connection; identity = verified
        memory.setVerifiedSession(connection, verified, features)
        update { it.copy(connecting = false, account = AccountSummary(normalized, user.id, user.name, features.provider, features.model),
            capabilities = features, destination = ChatDestination.Conversations,
            fault = null, notice = null,
            useMemory = features.memory_in_chat,
            pending = savedPending?.let { message -> PendingState(message, PendingPhase.Unknown) },
            submittedMessages = savedPending?.let { mapOf(it.body.request_id to it) } ?: emptyMap()) }
        refreshConversations(); refreshProfiles(); refreshScopes()
        if (savedPending != null) {
            openConversation(savedPending.conversationId)
            reconcile()
        }
    }

    private fun failure(result: ApiResult.Failure, epoch: Long) {
        if (!current(epoch)) return
        if (result.reason == ApiFailure.Unauthorized) { expire(); return }
        update { it.copy(connecting = false, fault = result.reason) }
    }
    private fun <T> value(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        return when (result) {
            is ApiResult.Success -> result.value
            is ApiResult.Failure -> { failure(result, epoch); null }
        }
    }
    private fun sessionWork(block: suspend (ConnectionCredential, Long) -> Unit) {
        val connection = credential ?: return
        val epoch = generation
        launchWork { if (current(epoch)) block(connection, epoch) }
    }
    fun navigate(destination: ChatDestination) {
        if (mutableState.value.account == null) return
        if (destination == ChatDestination.Memory) {
            if (mutableState.value.capabilities?.structured_memory != true) return
            memory.activate()
        }
        update { it.copy(destination = destination, fault = null) }
    }
    fun back() {
        if (mutableState.value.destination == ChatDestination.Memory && memory.back()) return
        navigate(when (mutableState.value.destination) {
        ChatDestination.Retrieval -> ChatDestination.Sources
        ChatDestination.Sources -> if (mutableState.value.conversation == null) ChatDestination.Conversations else ChatDestination.Chat
        else -> ChatDestination.Conversations
        })
    }

    private fun <T> merge(old: List<T>, page: List<T>, id: (T) -> UUID): List<T> {
        val rows = linkedMapOf<UUID, T>()
        old.forEach { rows[id(it)] = it }; page.forEach { rows[id(it)] = it }
        return rows.values.toList()
    }
    fun refreshConversations() = loadConversations(true)
    fun loadMoreConversations() = loadConversations(false)
    private fun loadConversations(refresh: Boolean) {
        val page = mutableState.value.conversations
        if (page.loading || (!refresh && !page.hasMore)) return
        val offset = if (refresh) 0 else page.nextOffset
        update { it.copy(conversations = page.copy(loading = true), fault = null) }
        sessionWork { connection, epoch ->
            val response = api.conversations(connection, PAGE_SIZE, offset)
            if (!current(epoch)) return@sessionWork
            val rows = value(response, epoch)
            if (!current(epoch)) return@sessionWork
            update { it.copy(conversations = if (rows == null) it.conversations.copy(loading = false) else ChatPage(
                merge(if (refresh) emptyList() else it.conversations.items, rows) { row -> row.id }, false, rows.size == PAGE_SIZE, offset + rows.size)) }
        }
    }
    fun refreshProfiles() = loadProfiles(true)
    fun loadMoreProfiles() = loadProfiles(false)
    private fun loadProfiles(refresh: Boolean) {
        val page = mutableState.value.profiles
        if (page.loading || (!refresh && !page.hasMore)) return
        val offset = if (refresh) 0 else page.nextOffset
        update { it.copy(profiles = page.copy(loading = true)) }
        sessionWork { connection, epoch ->
            val rows = value(api.personalities(connection, PAGE_SIZE, offset), epoch)
            if (!current(epoch)) return@sessionWork
            update { it.copy(profiles = if (rows == null) it.profiles.copy(loading = false) else ChatPage(
                merge(if (refresh) emptyList() else it.profiles.items, rows) { row -> row.id }, false, rows.size == PAGE_SIZE, offset + rows.size)) }
        }
    }
    fun refreshScopes() = loadScopes(true)
    fun loadMoreScopes() = loadScopes(false)
    private fun loadScopes(refresh: Boolean) {
        val page = mutableState.value.scopes
        if (page.loading || (!refresh && !page.hasMore)) return
        val offset = if (refresh) 0 else page.nextOffset
        update { it.copy(scopes = page.copy(loading = true)) }
        sessionWork { connection, epoch ->
            val rows = value(api.scopes(connection, PAGE_SIZE, offset), epoch)
            if (!current(epoch)) return@sessionWork
            update { it.copy(scopes = if (rows == null) it.scopes.copy(loading = false) else ChatPage(
                merge(if (refresh) emptyList() else it.scopes.items, rows) { row -> row.id }, false, rows.size == PAGE_SIZE, offset + rows.size)) }
        }
    }

    fun openConversation(id: UUID) {
        val version = ++selection
        val draft = drafts[id] ?: Draft(memory = mutableState.value.capabilities?.memory_in_chat == true)
        update { it.copy(conversation = null, events = ChatPage(loading = true), destination = ChatDestination.Chat,
            draft = draft.text, useMemory = draft.memory, asOf = draft.at, fault = null, notice = null) }
        sessionWork { connection, epoch ->
            val result = api.conversation(connection, id)
            if (!current(epoch) || version != selection) return@sessionWork
            val row = value(result, epoch)
            if (!current(epoch)) return@sessionWork
            if (row == null || row.id != id) {
                update { it.copy(conversation = null, events = ChatPage(), destination = ChatDestination.Conversations,
                    fault = if (row == null) it.fault else ApiFailure.IncompatibleContract) }
                return@sessionWork
            }
            update { it.copy(conversation = row, events = ChatPage()) }
            refreshEvents()
        }
    }
    fun refreshEvents() = loadEvents(true)
    fun loadMoreEvents() = loadEvents(false)
    private fun loadEvents(refresh: Boolean) {
        val row = mutableState.value.conversation ?: return
        val page = mutableState.value.events
        if (page.loading || (!refresh && !page.hasMore)) return
        val offset = if (refresh) 0 else page.nextOffset
        val version = selection
        update { it.copy(events = page.copy(loading = true)) }
        sessionWork { connection, epoch ->
            val result = api.events(connection, row.id, PAGE_SIZE, offset)
            if (!current(epoch) || version != selection) return@sessionWork
            val events = value(result, epoch)
            if (!current(epoch)) return@sessionWork
            if (events == null && result is ApiResult.Failure && result.reason in listOf(ApiFailure.Forbidden, ApiFailure.NotFound)) {
                update { it.copy(conversation = null, events = ChatPage(), sources = emptyMap(), trace = null, destination = ChatDestination.Conversations) }
                return@sessionWork
            }
            update { it.copy(events = if (events == null) it.events.copy(loading = false) else ChatPage(
                merge(if (refresh) emptyList() else it.events.items, events) { event -> event.id }, false, events.size == PAGE_SIZE, offset + events.size)) }
        }
    }

    fun beginCreate() {
        update { it.copy(destination = ChatDestination.NewConversation, createTitle = "",
            createProfileId = it.createProfileId?.takeIf { selected -> it.selectedProfile?.id == selected || it.profiles.items.any { row -> row.id == selected } }
                ?: it.profiles.items.firstOrNull()?.id,
            createScopeId = null, creationUncertain = false, fault = null, notice = null) }
        refreshProfiles(); refreshScopes()
    }
    fun updateCreateTitle(title: String) = update { it.copy(createTitle = title) }
    fun acknowledgeProfileReview() = update { it.copy(profileUncertain = false,
        notice = "After reviewing the style list, a new creation is a conscious action and may duplicate an earlier uncertain outcome.") }
    fun acknowledgeConversationReview() = update { it.copy(creationUncertain = false,
        notice = "After reviewing conversations, a new creation is a conscious action and may duplicate an earlier uncertain outcome.") }
    fun selectProfile(id: UUID) {
        val row = state.value.profiles.items.firstOrNull { it.id == id }
            ?: state.value.selectedProfile?.takeIf { it.id == id } ?: return
        update { it.copy(createProfileId = id, selectedProfile = row) }
    }
    fun selectScope(id: UUID?) = update { it.copy(createScopeId = id) }
    fun updateProfileDraft(body: PersonalityInputDto) {
        if (!state.value.creatingProfile) update { it.copy(profileDraft = body) }
    }
    fun createProfile(name: String, style: String = "conversational", warmth: String = "warm", detail: String = "balanced") {
        val current = mutableState.value
        if (current.account == null || current.creatingProfile || current.profileUncertain) return
        if (name.isBlank() || name.codePointCount(0, name.length) > 40 || !name.matches(Regex("[\\p{L}\\p{N}_ .-]+")) ||
            style !in listOf("direct", "conversational", "formal") || warmth !in listOf("reserved", "warm") || detail !in listOf("concise", "balanced", "detailed")) {
            update { it.copy(fault = ApiFailure.Validation) }; return
        }
        update { it.copy(creatingProfile = true, fault = null, notice = null) }
        sessionWork { connection, epoch ->
            val result = api.createPersonality(connection, PersonalityInputDto(name, style, warmth, detail))
            if (!current(epoch)) return@sessionWork
            when (result) {
                is ApiResult.Success -> {
                    update { it.copy(creatingProfile = false, createProfileId = result.value.id, selectedProfile = result.value,
                        notice = "The style was created and selected for a new conversation.") }
                    refreshProfiles()
                }
                is ApiResult.Failure -> {
                    failure(result, epoch); if (!current(epoch)) return@sessionWork
                    val unknown = ambiguous(result.reason)
                    update { it.copy(creatingProfile = false, profileUncertain = unknown,
                        notice = if (unknown) "The style creation outcome is unknown. Refresh styles and choose the created style before trying a new creation." else null) }
                    if (unknown) refreshProfiles()
                }
            }
        }
    }
    fun createConversation() {
        val current = mutableState.value
        if (current.account == null || current.creating || current.creationUncertain) return
        val profile = current.createProfileId
        if (profile == null || current.createTitle.isBlank() || current.createTitle.codePointCount(0, current.createTitle.length) > 120) {
            update { it.copy(fault = ApiFailure.Validation) }; return
        }
        val body = ConversationInputDto(profile, current.createTitle, current.createScopeId)
        update { it.copy(creating = true, fault = null, notice = null) }
        sessionWork { connection, epoch ->
            val result = api.createConversation(connection, body)
            if (!current(epoch)) return@sessionWork
            when (result) {
                is ApiResult.Success -> {
                    update { it.copy(creating = false) }; refreshConversations(); refreshScopes(); openConversation(result.value.id)
                }
                is ApiResult.Failure -> {
                    failure(result, epoch); if (!current(epoch)) return@sessionWork
                    val unknown = ambiguous(result.reason)
                    update { it.copy(creating = false, creationUncertain = unknown,
                        notice = if (unknown) "Creation may have succeeded. Refresh conversations and inspect the list before consciously starting another creation." else null) }
                    if (unknown) refreshConversations()
                }
            }
        }
    }
    fun upgradePrompt() {
        val row = mutableState.value.conversation ?: return
        if (mutableState.value.upgrading) return
        update { it.copy(upgrading = true, fault = null, notice = null) }
        sessionWork { connection, epoch ->
            val result = api.upgradePrompt(connection, row.id)
            if (!current(epoch)) return@sessionWork
            value(result, epoch)
            if (!current(epoch)) return@sessionWork
            openConversation(row.id); refreshConversations()
            // Refresh resets transient feedback; publish the explicit operation's result afterward.
            update { it.copy(upgrading = false, notice = if (result is ApiResult.Success) "Prompt updated for future replies. Completed answers and saved style remain unchanged."
                else "Prompt update was not confirmed. Refresh the conversation; an active request or changed history may require waiting.") }
        }
    }

    private fun saveDraft() {
        mutableState.value.conversation?.id?.let { drafts[it] = Draft(mutableState.value.draft, mutableState.value.useMemory, mutableState.value.asOf) }
    }
    fun updateDraft(text: String) { update { it.copy(draft = text, fault = null) }; saveDraft() }
    fun updateMemory(enabled: Boolean) { update { it.copy(useMemory = enabled && it.capabilities?.memory_in_chat == true) }; saveDraft() }
    fun updateAsOf(instant: String) { update { it.copy(asOf = instant) }; saveDraft() }
    private fun normalizedTime(value: String): String? {
        if (value.isBlank()) return null
        val parsed = OffsetDateTime.parse(value)
        require(parsed.nano % 1_000_000 == 0)
        val utc = parsed.toInstant()
        require(utc.atOffset(java.time.ZoneOffset.UTC).year in 1..9999)
        return utc.toString()
    }
    fun send() {
        val current = mutableState.value
        val verified = identity ?: return
        val row = current.conversation ?: return
        if (current.pending != null || current.capabilities?.chat != true) return
        val content = current.draft
        if ((current.useMemory && current.capabilities?.memory_in_chat != true) ||
            (current.asOf.isNotBlank() && current.capabilities?.historical_memory_queries != true)) { invalidDraft(); return }
        val at = try { normalizedTime(current.asOf) } catch (_: DateTimeParseException) { invalidDraft(); return }
            catch (_: IllegalArgumentException) { invalidDraft(); return }
        if (content.isBlank() || content.codePointCount(0, content.length) > 4000 || content.contains('\u0000') ||
            !validUnicode(content)) { invalidDraft(); return }
        val message = PendingMessage(verified, row.id, ChatInputDto(UUID.randomUUID(), content, at, current.useMemory))
        // Reserve synchronously before starting a coroutine so a second tap cannot race persistence.
        update { it.copy(pending = PendingState(message, PendingPhase.Journaling), fault = null, notice = null) }
        val epoch = generation
        launchWork {
            try {
                storage.withLock { if (!current(epoch)) return@launchWork; store.savePending(message) }
            } catch (_: Exception) {
                if (current(epoch)) update { it.copy(pending = null, notice = "The request was not sent because secure recovery storage could not be saved.") }
                return@launchWork
            }
            if (!current(epoch)) return@launchWork
            if (drafts[row.id] == Draft(current.draft, current.useMemory, current.asOf)) {
                drafts[row.id] = Draft("", current.useMemory, current.asOf)
                if (mutableState.value.conversation?.id == row.id && mutableState.value.draft == content) update { it.copy(draft = "") }
            }
            update { it.copy(submittedMessages = it.submittedMessages + (message.body.request_id to message)) }
            submit(message, epoch)
        }
    }
    private fun invalidDraft() = update { it.copy(fault = ApiFailure.Validation, notice = "Use 1–4000 Unicode characters and a timezone-aware instant with millisecond precision.") }
    private fun validUnicode(text: String): Boolean {
        var index = 0
        while (index < text.length) {
            val character = text[index++]
            if (character.isLowSurrogate()) return false
            if (character.isHighSurrogate() && (index >= text.length || !text[index++].isLowSurrogate())) return false
        }
        return true
    }
    private suspend fun submit(message: PendingMessage, epoch: Long) {
        val connection = credential ?: return
        if (!current(epoch) || identity != message.identity) return
        update { it.copy(pending = PendingState(message, PendingPhase.Submitting), fault = null) }
        when (val result = api.send(connection, message.conversationId, message.body)) {
            is ApiResult.Success -> consume(result.value, message, epoch)
            is ApiResult.Failure -> {
                if (!current(epoch)) return
                failure(result, epoch); if (!current(epoch)) return
                if (result.reason == ApiFailure.TooLarge || result.reason == ApiFailure.Validation) {
                    storage.withLock { if (current(epoch)) store.removePending(message.identity, message.body.request_id) }
                    if (!current(epoch)) return
                    if (mutableState.value.conversation?.id == message.conversationId && mutableState.value.draft.isEmpty()) {
                        update { it.copy(draft = message.body.content) }; saveDraft()
                    }
                    update { it.copy(pending = null, submittedMessages = it.submittedMessages - message.body.request_id,
                        notice = "The input was rejected. Edit the draft before submitting a new request.") }
                } else {
                    val phase = if (result.reason == ApiFailure.Conflict) PendingPhase.Conflict else PendingPhase.Unknown
                    update { it.copy(pending = PendingState(message, phase, failure = result.reason, code = result.code),
                        notice = if (phase == PendingPhase.Conflict) "The saved request or conversation changed. Refresh history and check the original request before retrying." else "The request outcome is unknown. Checking its original ID does not submit a second message.") }
                    if (result.reason == ApiFailure.Conflict && mutableState.value.conversation?.id == message.conversationId) refreshEvents()
                    val wait = (result.reason as? ApiFailure.Busy)?.retryAfterSeconds
                    if (wait != null) retryNotBefore = deadline(wait)
                    // This server ID represents different bytes/options. Its status
                    // cannot be presented as the answer to this local reservation.
                    if (result.code != "idempotency_key_reused") reconcile()
                }
            }
        }
    }
    private fun deadline(seconds: Long): Long {
        val now = System.currentTimeMillis()
        return if (seconds > (Long.MAX_VALUE - now) / 1000) Long.MAX_VALUE else now + seconds.coerceAtLeast(0) * 1000
    }
    private suspend fun consume(response: RequestDto, message: PendingMessage, epoch: Long) {
        if (!current(epoch)) return
        val conflictCode = mutableState.value.pending?.code
        if (response.request_id != message.body.request_id || response.conversation_id != message.conversationId) {
            update { it.copy(pending = PendingState(message, PendingPhase.Unknown, failure = ApiFailure.IncompatibleContract), fault = ApiFailure.IncompatibleContract) }
            reconcile(); return
        }
        when (response.observedState) {
            ObservedRequestState.Completed -> {
                if (response.response == null) {
                    update { it.copy(pending = PendingState(message, PendingPhase.Unknown, failure = ApiFailure.IncompatibleContract)) }
                    reconcile(); return
                }
                // Remove only this identity/UUID, after the completed response can be reconciled.
                update { it.copy(sources = it.sources + (response.request_id to response), pending = PendingState(message, PendingPhase.Blocked, response)) }
                try { storage.withLock { if (current(epoch)) store.removePending(message.identity, message.body.request_id) } }
                catch (_: Exception) {
                    if (current(epoch)) update { it.copy(notice = "The answer was received, but recovery storage could not be cleared. Check the same request again before sending another message.") }
                    return
                }
                if (!current(epoch)) return
                update { it.copy(pending = null, fault = null, notice = null) }
                if (mutableState.value.conversation?.id == message.conversationId) refreshEvents()
                refreshConversations()
            }
            ObservedRequestState.Failed -> update { it.copy(pending = PendingState(message,
                if (conflictCode == "retry_history_changed") PendingPhase.Conflict else PendingPhase.Failed, response, code = conflictCode),
                notice = if (conflictCode == "retry_history_changed") "The conversation changed, so this failed request cannot be retried with its old context. Refresh history and consciously start a new message."
                    else "Generation failed. Retry uses the original message, request ID and options.") }
            ObservedRequestState.Running -> update { it.copy(pending = PendingState(message, PendingPhase.Running, response, code = conflictCode), notice = "ADA is generating. Leaving this screen stops no server work.") }
            ObservedRequestState.Unknown -> update { it.copy(pending = PendingState(message, PendingPhase.Unknown, response, code = conflictCode), notice = "The server reported an unfamiliar request state. Keep the original ID and check again.") }
        }
        if (response.observedState in listOf(ObservedRequestState.Running, ObservedRequestState.Unknown)) reconcile()
    }
    fun reconcile() {
        if (pollJob?.isActive == true) return
        if (mutableState.value.pending?.code == "idempotency_key_reused") return
        val message = mutableState.value.pending?.message ?: return
        val connection = credential ?: return
        val epoch = generation
        pollJob = launchWork {
            val start = System.currentTimeMillis()
            val budget = 60_000L
            for (pause in pollDelaysMs) {
                val required = maxOf(pause, (retryNotBefore - System.currentTimeMillis()).coerceAtLeast(0))
                if (required > budget || System.currentTimeMillis() - start + required > budget) {
                    update { it.copy(notice = "ADA requested a longer wait. Check the original request after the retry interval; it was not submitted again.") }; break
                }
                if (required > 0) delay(required)
                if (!current(epoch) || identity != message.identity || mutableState.value.pending?.message?.body?.request_id != message.body.request_id) return@launchWork
                when (val result = api.request(connection, message.body.request_id)) {
                    is ApiResult.Success -> {
                        consume(result.value, message, epoch)
                        if (!current(epoch) || mutableState.value.pending == null || mutableState.value.pending?.phase in listOf(PendingPhase.Failed, PendingPhase.Conflict, PendingPhase.Blocked)) return@launchWork
                    }
                    is ApiResult.Failure -> {
                        failure(result, epoch); if (!current(epoch)) return@launchWork
                        if (result.reason == ApiFailure.NotFound) {
                            update { it.copy(pending = PendingState(message, PendingPhase.Missing, failure = result.reason), notice = "No request with this ID is available to the verified account. You may explicitly submit the saved message with its same ID.") }; return@launchWork
                        }
                        if (result.reason == ApiFailure.Forbidden) {
                            update { it.copy(pending = PendingState(message, PendingPhase.Blocked, failure = result.reason), events = ChatPage(), sources = emptyMap(), trace = null) }; return@launchWork
                        }
                        val wait = (result.reason as? ApiFailure.Busy)?.retryAfterSeconds
                        if (wait != null) retryNotBefore = deadline(wait)
                        update { it.copy(pending = PendingState(message, PendingPhase.Unknown, failure = result.reason)) }
                    }
                }
            }
        }
    }
    fun retry() = explicitSubmit(PendingPhase.Failed)
    fun resubmitSamePayload() = explicitSubmit(PendingPhase.Missing)
    /** Explicitly leave a known failed/rejected/absent local reservation; never cancel server work. */
    fun discardPending() {
        val pending = mutableState.value.pending ?: return
        if (pending.phase !in listOf(PendingPhase.Failed, PendingPhase.Missing, PendingPhase.Conflict)) return
        pollJob?.cancel(); pollJob = null
        val epoch = generation
        update { it.copy(pending = pending.copy(phase = PendingPhase.Blocked)) }
        launchWork {
            try { storage.withLock { if (current(epoch)) store.removePending(pending.message.identity, pending.message.body.request_id) } }
            catch (_: Exception) {
                if (current(epoch)) update { it.copy(pending = pending, notice = "Secure recovery state could not be cleared. Check the saved request before continuing.") }
                return@launchWork
            }
            if (!current(epoch)) return@launchWork
            update { it.copy(pending = null, submittedMessages = it.submittedMessages - pending.message.body.request_id,
                draft = if (it.conversation?.id == pending.message.conversationId && it.draft.isEmpty()) pending.message.body.content else it.draft,
                notice = "The previous request was not canceled or rewritten. Edit the draft and Send to consciously create a new request ID.") }
            saveDraft()
        }
    }
    private fun explicitSubmit(required: PendingPhase) {
        val pending = mutableState.value.pending ?: return
        if (pending.phase != required || identity != pending.message.identity) return
        if (System.currentTimeMillis() < retryNotBefore) { update { it.copy(notice = "Wait for the server's retry interval before trying again.") }; return }
        pollJob?.cancel(); pollJob = null
        update { it.copy(pending = pending.copy(phase = PendingPhase.Submitting), fault = null) }
        val epoch = generation
        val connection = credential ?: return
        launchWork {
            val owner = value(api.me(connection), epoch) ?: run {
                if (current(epoch)) update { it.copy(pending = pending.copy(phase = PendingPhase.Blocked), notice = "Reconnection could not be verified. The saved request was not submitted again.") }
                return@launchWork
            }
            if (owner.id != pending.message.identity.owner) { expire(); return@launchWork }
            try { storage.withLock { if (!current(epoch)) return@launchWork; store.savePending(pending.message) } }
            catch (_: Exception) {
                if (current(epoch)) update { it.copy(pending = pending.copy(phase = PendingPhase.Blocked), notice = "Secure recovery storage could not be verified. The saved request was not submitted again.") }
                return@launchWork
            }
            submit(pending.message, epoch)
        }
    }
    fun openSources(requestId: UUID, label: String? = null) {
        val version = ++sourceSelection
        update { it.copy(destination = ChatDestination.Sources, sourceRequestId = requestId, sourceLabel = label,
            sourceLoading = !it.sources.containsKey(requestId), trace = null, traceMissing = false, fault = null) }
        if (mutableState.value.sources.containsKey(requestId)) return
        sessionWork { connection, epoch ->
            val result = api.request(connection, requestId)
            if (!current(epoch) || version != sourceSelection) return@sessionWork
            val row = value(result, epoch)
            if (!current(epoch)) return@sessionWork
            update { it.copy(sourceLoading = false, sources = if (row != null && row.request_id == requestId) it.sources + (requestId to row) else it.sources,
                fault = if (row != null && row.request_id != requestId) ApiFailure.IncompatibleContract else it.fault) }
        }
    }
    fun loadTrace() {
        val id = mutableState.value.sourceRequestId ?: return
        if (mutableState.value.traceLoading) return
        val version = sourceSelection
        update { it.copy(destination = ChatDestination.Retrieval, traceLoading = true, traceMissing = false, fault = null) }
        sessionWork { connection, epoch ->
            val result = api.trace(connection, id)
            if (!current(epoch) || version != sourceSelection) return@sessionWork
            val row = value(result, epoch)
            if (!current(epoch)) return@sessionWork
            update { it.copy(traceLoading = false, trace = row?.takeIf { trace -> trace.request_id == id },
                traceMissing = result is ApiResult.Failure && result.reason == ApiFailure.NotFound,
                fault = if (row != null && row.request_id != id) ApiFailure.IncompatibleContract else it.fault) }
        }
    }
    private fun ambiguous(reason: ApiFailure) = reason == ApiFailure.Timeout || reason == ApiFailure.Unreachable || reason == ApiFailure.IncompatibleContract || reason is ApiFailure.Http || reason == ApiFailure.Provider
    companion object { private const val PAGE_SIZE = 50 }
}
