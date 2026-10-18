package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.security.MessageDigest
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.encodeToString

data class CuriosityState(val supported: Boolean = false, val busy: Boolean = false, val policy: CuriosityPolicyDto? = null,
    val questions: List<CuriosityQuestionDto> = emptyList(), val pending: List<CuriosityPending> = emptyList(),
    val receipts: Map<UUID, CuriosityReceiptDto> = emptyMap(), val originals: List<SourceVersionDto> = emptyList(),
    val inspected: SourceVersionDto? = null, val answer: RequestDto? = null, val notice: String? = null) {
    override fun toString() = "CuriosityState(redacted)"
}

class CuriosityController(private val api: AdaApi, private val store: SessionStore, private val scope: CoroutineScope,
    private val unauthorized: () -> Unit) {
    private val mutable = MutableStateFlow(CuriosityState())
    val state = mutable.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private var visibility = 0L
    private var selectedScope: UUID? = null
    private var selectedConversation: UUID? = null
    private val jobs = mutableSetOf<Job>()
    private val offered = mutableSetOf<UUID>()
    private var cooldown = 0L
    private fun update(block: (CuriosityState) -> CuriosityState) { mutable.value = block(mutable.value) }
    private fun current(epoch: Long) = generation == epoch && identity != null
    fun reset() { generation++; visibility++; jobs.toList().forEach { it.cancel() }; jobs.clear(); offered.clear()
        identity = null; connection = null; selectedScope = null; selectedConversation = null; cooldown = 0; mutable.value = CuriosityState() }
    private fun work(block: suspend (ConnectionCredential, SessionIdentity, Long) -> Unit) {
        val c = connection ?: return
        val owner = identity ?: return
        val epoch = generation
        scope.launch(start = CoroutineStart.UNDISPATCHED) {
            try { if (current(epoch)) block(c, owner, epoch) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(epoch)) update { it.copy(busy = false, notice = "The optional question could not be confirmed. Text chat remains available; check saved deliveries before retrying.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accept(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        if (result is ApiResult.Success) return result.value
        val fault = (result as ApiResult.Failure).reason
        if (fault == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (fault is ApiFailure.Busy) cooldown = System.currentTimeMillis() + (fault.retryAfterSeconds ?: 3).coerceIn(0, 300) * 1000L
        if (fault is ApiFailure.Http && fault.status == 429) cooldown = System.currentTimeMillis() + 60000
        update { it.copy(busy = false, notice = "This question is unavailable, paused or unconfirmed. Check the saved delivery; no automatic retry was made.") }
        return null
    }
    fun setVerifiedSession(c: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = c; identity = owner
        update { it.copy(supported = caps.curiosity_protocol == "ada-curiosity-v1") }
        if (!state.value.supported) return
        work { conn, who, epoch ->
            val journal = store.curiosityJournal(who)
            if (!current(epoch)) return@work
            update { it.copy(pending = journal?.operations ?: emptyList()) }
            // Reopen only reads policy/receipts. It never generates or resends a question.
            refreshPolicy(conn, epoch)
            journal?.operations?.forEach { if (current(epoch)) check(conn, who, it, epoch) }
        }
    }
    private suspend fun refreshPolicy(c: ConnectionCredential, epoch: Long) {
        val p = accept(api.curiosityPolicy(c), epoch) ?: return
        require(p.version == "ada-curiosity-v1" && p.revision >= 0 && !p.settings.notifications_enabled && p.day_boundary == "UTC")
        require(p.settings.topics.keys == curiosityTopics.toSet() && p.inbox_daily_limit == 2 && p.interview_daily_limit == 10)
        if (current(epoch) && p.revision >= (state.value.policy?.revision ?: 0)) update { it.copy(policy = p, questions = if (p.settings.enabled) it.questions else emptyList(), busy = false) }
    }
    fun activate(scopeId: UUID?, conversationId: UUID? = null) {
        selectedScope = scopeId; selectedConversation = conversationId; visibility++
        update { it.copy(questions = emptyList(), originals = emptyList(), inspected = null, answer = null) }
        refresh()
    }
    fun refresh() { if (!state.value.supported) return; work { c, _, epoch -> refreshPolicy(c, epoch); load(c, epoch) } }
    private suspend fun load(c: ConnectionCredential, epoch: Long) {
        val scopeId = selectedScope ?: return
        val conv = selectedConversation
        val sequence = visibility
        val revision = state.value.policy?.revision ?: return
        val rows = accept(if (conv != null) api.curiosityConversation(c, conv) else api.curiosityQuestions(c, scopeId), epoch) ?: return
        require(rows.size <= 100 && rows.all { it.version == "ada-curiosity-v1" && it.scope_id == scopeId && (conv == null || it.conversation_id == conv || it.opened_conversation_id == conv) })
        rows.forEach { q -> q.source?.let { pin -> require(pin.scope_id == q.scope_id && pin.trust_class == "user_explicit" && pin.content_hash.matches(Regex("[a-f0-9]{64}")) && pin.span_start >= 0 && pin.span_end > pin.span_start && pin.span_end - pin.span_start <= 600) } }
        if (current(epoch) && sequence == visibility && revision == state.value.policy?.revision && state.value.policy?.settings?.enabled == true) update { it.copy(questions = rows, busy = false) }
    }
    private suspend fun pending(who: SessionIdentity, epoch: Long) {
        val journal = store.curiosityJournal(who)
        if (current(epoch)) update { it.copy(pending = journal?.operations ?: emptyList()) }
    }
    private fun queue(operation: CuriosityPending) {
        val owner = identity ?: return
        if (!state.value.supported || (operation.kind == "create" && System.currentTimeMillis() < cooldown)) return
        validateCuriosityJournal(CuriosityJournal(owner, listOf(operation)))
        update { it.copy(busy = true, notice = null) }
        work { c, who, epoch ->
            store.saveCuriosityOperation(who, operation)
            if (!current(epoch)) return@work
            pending(who, epoch); submit(c, who, operation, epoch)
        }
    }
    private suspend fun acknowledge(c: ConnectionCredential, who: SessionIdentity, op: CuriosityPending, receipt: CuriosityReceiptDto, epoch: Long) {
        require(receipt.version == "ada-curiosity-v1" && receipt.operation_id == op.operationId)
        require(receipt.action == op.kind)
        if (op.questionId != null) require(receipt.question_id == op.questionId)
        if (op.kind == "answer") require(receipt.request_id == adaJson.decodeFromString<CuriosityAnswerDto>(op.body).request_id)
        if (op.kind == "open") require(receipt.conversation_id == adaJson.decodeFromString<CuriosityOpenDto>(op.body).conversation_id)
        if (!current(epoch)) return
        update { it.copy(receipts = it.receipts + (op.operationId to receipt), busy = false,
            notice = when (receipt.state) {
                "not_offered" -> "No suitable question was offered. You can keep chatting normally."
                "rejected" -> "This answer was not recorded. Review or shorten it before sending a new answer."
                else -> null
            }) }
        if (receipt.state in setOf("completed", "created", "not_offered", "rejected")) {
            store.removeCuriosityOperation(who, op.operationId)
            if (!current(epoch)) return
            pending(who, epoch)
            if (op.kind == "answer" && receipt.state == "completed" && receipt.request_id != null) {
                val answer = accept(api.request(c, receipt.request_id), epoch)
                if (current(epoch) && selectedScope == op.scopeId && answer?.request_id == receipt.request_id && answer.conversation_id == receipt.conversation_id) update { it.copy(answer = answer) }
            }
        }
        refreshPolicy(c, epoch); load(c, epoch)
    }
    private suspend fun submit(c: ConnectionCredential, who: SessionIdentity, op: CuriosityPending, epoch: Long) {
        val result = api.curiosityWrite(c, op)
        if (!current(epoch)) return
        val receipt = accept(result, epoch)
        if (receipt != null) acknowledge(c, who, op, receipt, epoch)
        else if (result is ApiResult.Failure && result.reason in setOf(ApiFailure.Validation, ApiFailure.Conflict, ApiFailure.TooLarge)) {
            // Answer admission follows its durable intent. Resolve that receipt
            // before deciding whether the rejection recorded an operation.
            if (op.kind == "answer") {
                val saved = api.curiosityReceipt(c, op.operationId)
                if (!current(epoch)) return
                if (saved is ApiResult.Success) {
                    acknowledge(c, who, op, saved.value, epoch); return
                }
                if (saved !is ApiResult.Failure || saved.reason != ApiFailure.NotFound) {
                    accept(saved, epoch); return
                }
            }
            store.removeCuriosityOperation(who, op.operationId); pending(who, epoch); refreshPolicy(c, epoch)
        }
    }
    private suspend fun check(c: ConnectionCredential, who: SessionIdentity, op: CuriosityPending, epoch: Long) {
        val result = api.curiosityReceipt(c, op.operationId)
        val receipt = accept(result, epoch) ?: return
        acknowledge(c, who, op, receipt, epoch)
    }
    fun check(op: CuriosityPending) { work { c, who, epoch -> check(c, who, op, epoch) } }
    fun retry(op: CuriosityPending) { if (op.kind != "create" || System.currentTimeMillis() >= cooldown) work { c, who, epoch -> submit(c, who, op, epoch) } }
    fun save(settings: CuriositySettingsDto) {
        val p = state.value.policy ?: return
        val id = UUID.randomUUID()
        visibility++
        if (!settings.enabled) update { it.copy(questions = emptyList(), originals = emptyList(), inspected = null) }
        queue(CuriosityPending(id, "policy", body = adaJson.encodeToString(CuriosityPolicyWriteDto(id, p.revision, settings))))
    }
    fun off() { state.value.policy?.settings?.let { save(it.copy(enabled = false)) } }
    fun create(scopeId: UUID, topic: String, interview: Boolean = false, original: SourceVersionDto? = null) {
        val p = state.value.policy ?: return
        if (!p.settings.enabled || state.value.busy) return
        val pin = original?.let { CuriosityPinInputDto(it.id, 0, minOf(600, it.content.codePointCount(0, it.content.length))) }
        val id = UUID.randomUUID()
        queue(CuriosityPending(id, "create", scopeId, body = adaJson.encodeToString(CuriosityCreateDto(id, p.revision, topic = topic, intent = if (interview) "interview" else "normal", source = pin))))
    }
    fun afterReply(conversation: ConversationDto, requestId: UUID) {
        val p = state.value.policy ?: return
        if (!p.settings.enabled || !p.settings.chat_enabled || !offered.add(requestId)) return
        val id = UUID.randomUUID()
        queue(CuriosityPending(id, "create", conversation.scope_id, body = adaJson.encodeToString(CuriosityCreateDto(id, p.revision, "chat", request_id = requestId))))
    }
    fun action(q: CuriosityQuestionDto, action: String) {
        val id = UUID.randomUUID()
        visibility++
        update { it.copy(questions = it.questions.filterNot { old -> old.id == q.id }) }
        queue(CuriosityPending(id, "action", q.scope_id, q.id, adaJson.encodeToString(CuriosityActionDto(id, action))))
    }
    fun open(q: CuriosityQuestionDto, profile: UUID) { val id = UUID.randomUUID()
        queue(CuriosityPending(id, "open", q.scope_id, q.id, adaJson.encodeToString(CuriosityOpenDto(id, UUID.randomUUID(), profile)))) }
    fun answer(q: CuriosityQuestionDto, text: String) { if (text.isBlank() || state.value.busy || state.value.pending.any { it.kind == "answer" && it.questionId == q.id } || q.answer_request_id != null) return
        if (text.codePointCount(0, text.length) > 4000) {
            update { it.copy(notice = "Please shorten your answer to 4000 characters or fewer.") }; return
        }
        val id = UUID.randomUUID()
        queue(CuriosityPending(id, "answer", q.scope_id, q.id, adaJson.encodeToString(CuriosityAnswerDto(id, UUID.randomUUID(), text)))) }
    fun originals(scopeId: UUID) { work { c, _, epoch ->
        val sequence = visibility
        val rows = accept(api.sources(c, scopeId, 50, 0), epoch) ?: return@work
        require(rows.all { it.scope_id == scopeId })
        if (current(epoch) && sequence == visibility) update { it.copy(originals = rows.filter { source -> source.trust_class == "user_explicit" }) }
    } }
    fun inspect(q: CuriosityQuestionDto) { val pin = q.source ?: return
        val sequence = visibility
        work { c, _, epoch ->
            val source = accept(api.source(c, pin.source_version_id), epoch) ?: return@work
            require(source.id == pin.source_version_id && source.scope_id == q.scope_id && source.trust_class == "user_explicit")
            val hash = MessageDigest.getInstance("SHA-256").digest(source.content.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
            require(hash == pin.content_hash && source.content_hash == hash)
            require(source.content.substring(source.content.offsetByCodePoints(0, pin.span_start), source.content.offsetByCodePoints(0, pin.span_end)) == pin.quote)
            if (current(epoch) && sequence == visibility && selectedScope == q.scope_id) update { it.copy(inspected = source) }
        }
    }
}
