package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString

data class AgentState(val enabled: Boolean = false, val task: String = "", val asOf: String = "", val tools: Set<String> = setOf("calculator"), val journal: AgentJournal? = null, val run: AgentRunDto? = null, val receipt: ToolReceiptDto? = null, val busy: Boolean = false, val fault: ApiFailure? = null, val notice: String? = null) {
    override fun toString() = "AgentState(redacted)"
}
/** Restore performs GET only. Every POST first commits the exact encrypted reservation. */
class AgentController(private val api: AdaApi, private val store: SessionStore, private val scope: CoroutineScope, private val unauthorized: () -> Unit, private val now: () -> Long = System::currentTimeMillis) {
    private val mutableState = MutableStateFlow(AgentState()); val state = mutableState.asStateFlow()
    private var connection: ConnectionCredential? = null; private var identity: SessionIdentity? = null
    private var generation = 0L; private var cooldown = 0L; private val jobs = mutableSetOf<Job>()
    private fun update(change: (AgentState) -> AgentState) { mutableState.value = change(state.value) }
    fun reset() { generation++; jobs.toList().forEach { it.cancel() }; jobs.clear(); connection = null; identity = null; cooldown = 0; mutableState.value = AgentState() }
    private fun current(epoch: Long) = epoch == generation && identity != null && connection != null
    private fun work(task: suspend (ConnectionCredential, Long) -> Unit) {
        val conn = connection ?: return; val epoch = generation
        scope.launch { try { if (current(epoch)) task(conn, epoch) }
            catch (e: CancellationException) { throw e }
            catch (_: Exception) { if (current(epoch)) update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract, notice = "The outcome is unconfirmed. Check the saved run before retrying.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accepted(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        if (result is ApiResult.Success) return result.value
        val f = (result as ApiResult.Failure).reason
        if (f == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (f is ApiFailure.Busy) { val wait = (f.retryAfterSeconds ?: 3).coerceIn(0, 300); cooldown = now() + wait * 1000 }
        update { it.copy(busy = false, fault = f, notice = "The outcome is unconfirmed. Check the run or explicitly retry the saved operation. Changed or expired previews require a new run.") }; return null
    }
    fun setVerifiedSession(conn: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = conn; identity = owner; update { it.copy(enabled = caps.hasAgentTools(), busy = true) }
        work { c, epoch -> val saved = store.agentJournal(owner)
            if (!current(epoch)) return@work
            update { it.copy(journal = saved, busy = false, notice = if (saved != null) "Saved tool session restored. No operation was submitted automatically." else null) }
            if (saved != null) load(c, saved, epoch)
        }
    }
    fun task(value: String) { if (state.value.journal == null && !state.value.busy) update { it.copy(task = value) } }
    fun asOf(value: String) { if (state.value.journal == null && !state.value.busy) update { it.copy(asOf = value) } }
    fun toggleTool(name: String) { if (name in selectedAgentTools && state.value.journal == null && !state.value.busy) update { it.copy(tools = if (name in it.tools) it.tools - name else it.tools + name) } }
    fun start(conversation: ConversationDto) {
        val owner = identity ?: return; val s = state.value
        if (!s.enabled || s.busy || s.journal != null || now() < cooldown || conversation.prompt_version !in setOf("ada-baseline-v3", "ada-baseline-v4")) return
        val key = UUID.randomUUID()
        val p = try { AgentJournal(owner, conversation.scope_id, conversation.id, key, adaJson.encodeToString(AgentInputDto(key, s.task, allowed_tools = s.tools.sorted(), as_of = normalizeUtcMillis(s.asOf)))).also(::validateAgentJournal) }
        catch (_: Exception) { update { it.copy(fault = ApiFailure.Validation, notice = "Enter a task, select tools and check the optional time.") }; return }
        update { it.copy(busy = true) }
        work { conn, epoch -> store.saveAgentJournal(p); if (!current(epoch)) return@work
            update { it.copy(journal = p) }; submit(conn, p, epoch)
        }
    }
    private fun validateRun(run: AgentRunDto, p: AgentJournal) {
        require(run.id == p.runId && run.owner_id == p.identity.owner && run.scope_id == p.scopeId && run.conversation_id == p.conversationId && run.protocol_version == "ada-agent-v1" && run.generation > 0)
        require(run.steps.size <= 5 && run.steps.map { it.id }.distinct().size == run.steps.size && run.steps.all { it.number in 1..5 && it.attempt > 0 })
        run.steps.forEach { step ->
            step.receipt?.let { require(it.step_id == step.id); validateReceipt(it, p) }
            if (step.status == "pending_approval") {
                require(step.tool in selectedAgentTools && step.tool in adaJson.decodeFromString<AgentInputDto>(p.body).allowed_tools && step.arguments != null && step.expires_at != null)
                val key = UUID.randomUUID()
                validateAgentJournal(p.copy(operation = AgentOperation("approve", key, step.id, adaJson.encodeToString(AgentApprovalDto(key, step.preview_hash ?: "", step.argument_hash ?: "", step.tool_version ?: "")))))
            }
        }
    }
    private fun validateReceipt(r: ToolReceiptDto, p: AgentJournal) {
        require(r.owner_id == p.identity.owner && r.run_id == p.runId && r.scope_id == p.scopeId && r.origin == "tool_result" && r.trust_class == "untrusted_tool_output")
        require(r.outcome in setOf("completed", "failed", "unknown", "revoked"))
        require(r.outcome != "completed" || (r.result != null && r.tool in selectedAgentTools))
    }
    private suspend fun load(conn: ConnectionCredential, p: AgentJournal, epoch: Long) {
        val run = accepted(api.agentRun(conn, p.runId), epoch) ?: return
        validateRun(run, p); if (!current(epoch)) return
        update { it.copy(run = run, busy = false, fault = null) }
        // A receipt with the original nonce confirms an interrupted approval delivery.
        val op = p.operation
        if (op != null && op.kind != "recover") run.steps.firstOrNull { it.id == op.stepId }?.receipt?.takeIf { it.approval_id == op.id }?.let { finish(p, it, epoch) }
        if (op != null && run.status == "failed" && run.steps.firstOrNull { it.id == op.stepId }?.let { it.status == "failed" && it.receipt == null } == true) {
            // A terminal rejected/expired preview cannot later execute. No successful receipt is invented.
            store.saveAgentJournal(p.copy(operation = null))
            if (current(epoch)) update { it.copy(journal = p.copy(operation = null), notice = "The server rejected this preview. No tool receipt was recorded; close the failed session before requesting another.") }
        }
    }
    private suspend fun finish(p: AgentJournal, receipt: ToolReceiptDto, epoch: Long) {
        validateReceipt(receipt, p)
        val op = checkNotNull(p.operation)
        if (op.kind != "recover") {
            val a = adaJson.decodeFromString<AgentApprovalDto>(op.body)
            require(receipt.approval_id == op.id && receipt.step_id == op.stepId && receipt.preview_hash == a.preview_hash && receipt.argument_hash == a.argument_hash && receipt.tool_version == a.tool_version)
        } else require(receipt.outcome == "unknown")
        if (!current(epoch)) return
        val saved = p.copy(operation = null); store.saveAgentJournal(saved)
        if (current(epoch)) update { it.copy(journal = saved, receipt = receipt, busy = false, fault = null, notice = "A durable receipt is recorded. Read its outcome before continuing.") }
    }
    private suspend fun submit(conn: ConnectionCredential, p: AgentJournal, epoch: Long) {
        if (p.operation == null) {
            val run = accepted(api.createAgentRun(conn, p), epoch) ?: return
            validateRun(run, p); if (current(epoch)) update { it.copy(run = run, busy = false, fault = null) }
        } else {
            val r = accepted(api.agentOperation(conn, p), epoch) ?: return
            finish(p, r, epoch); if (current(epoch)) load(conn, p.copy(operation = null), epoch)
        }
    }
    fun check() { val p = state.value.journal ?: return; if (state.value.busy) return; update { it.copy(busy = true) }; work { conn, epoch -> load(conn, p, epoch) } }
    fun retry() { val p = state.value.journal ?: return; if (!state.value.enabled || state.value.busy || now() < cooldown) return; update { it.copy(busy = true) }; work { conn, epoch -> submit(conn, p, epoch) } }
    fun decide(step: AgentStepDto, approve: Boolean) {
        val s = state.value; val p = s.journal ?: return; val run = s.run ?: return
        if (!s.enabled || s.busy || p.operation != null || run.status != "pending_approval" || run.steps.none { it == step } || step.status != "pending_approval" || now() < cooldown) return
        val key = UUID.randomUUID(); val a = AgentApprovalDto(key, step.preview_hash ?: return, step.argument_hash ?: return, step.tool_version ?: return)
        reserve(p.copy(operation = AgentOperation(if (approve) "approve" else "revoke", key, step.id, adaJson.encodeToString(a))))
    }
    fun recover() {
        val s = state.value; val p = s.journal ?: return; val run = s.run ?: return
        if (!s.enabled || s.busy || p.operation != null || run.status != "running" || (run.lease_until ?: Long.MAX_VALUE) > now() || now() < cooldown) return
        val key = UUID.randomUUID(); reserve(p.copy(operation = AgentOperation("recover", key, body = adaJson.encodeToString(AgentRecoverDto(key, run.generation)))))
    }
    private fun reserve(p: AgentJournal) {
        validateAgentJournal(p); update { it.copy(busy = true) }
        work { conn, epoch -> store.saveAgentJournal(p); if (!current(epoch)) return@work; update { it.copy(journal = p) }; submit(conn, p, epoch) }
    }
    fun closeCompleted() {
        val s = state.value; val p = s.journal ?: return
        if (s.busy || p.operation != null || s.run?.status !in setOf("completed", "failed", "unknown")) return
        update { it.copy(busy = true) }; work { _, epoch -> store.removeAgentJournal(p.identity, p.runId); if (current(epoch)) update { AgentState(enabled = it.enabled) } }
    }
}
