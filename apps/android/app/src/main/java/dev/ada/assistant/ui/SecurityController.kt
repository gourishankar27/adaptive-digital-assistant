package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

class SecurityState(val enabled: Boolean = false, val busy: Boolean = false,
    val status: SecurityStatusDto? = null, val devices: List<DeviceCredentialDto> = emptyList(),
    val preview: DeletionPreviewDto? = null, val pending: SecurityJournal? = null,
    val deletion: DeletionDto? = null, val issued: CredentialIssueDto? = null, val notice: String? = null) {
    override fun toString() = "SecurityState(redacted)"
}

/** Exact encrypted reservation before POST; recovery performs GET only until an explicit tap. */
class SecurityController(private val api: AdaApi, private val store: SessionStore,
    private val scope: CoroutineScope, private val unauthorized: () -> Unit,
    private val install: (String, String) -> Unit, private val erased: () -> Unit) {
    private val mutable = MutableStateFlow(SecurityState())
    val state = mutable.asStateFlow()
    private val history = MutableStateFlow<List<DeletionDto>>(emptyList())
    val deletionHistory = history.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private var job: Job? = null
    private var retryAt = 0L
    fun reset() { generation++; job?.cancel(); job = null; connection = null; identity = null; retryAt = 0; mutable.value = SecurityState(); history.value = emptyList() }
    fun setVerifiedSession(c: ConnectionCredential, i: SessionIdentity, features: CapabilitiesDto) {
        reset(); connection = c; identity = i
        mutable.value = SecurityState(enabled = features.device_credentials == "ada-device-credentials-v1" && features.private_deletion == "ada-private-deletion-v1")
        if (state.value.enabled) refresh()
    }
    private fun work(action: suspend (ConnectionCredential, SessionIdentity) -> Unit) {
        val c = connection ?: return; val i = identity ?: return
        if (!state.value.enabled || state.value.busy || System.currentTimeMillis() < retryAt) return
        val epoch = generation
        val previous = state.value
        mutable.value = SecurityState(true, true, previous.status, previous.devices, previous.preview, previous.pending, previous.deletion, previous.issued)
        job = scope.launch {
            try { action(c, i) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (generation == epoch) feedback("The outcome is unknown. Refresh using the saved operation before retrying.") }
            finally { if (generation == epoch) {
                val s = state.value; mutable.value = SecurityState(s.enabled, false, s.status, s.devices, s.preview, s.pending, s.deletion, s.issued, s.notice)
            } }
        }
    }
    private fun feedback(message: String) { val s = state.value; mutable.value = SecurityState(s.enabled, s.busy, s.status, s.devices, s.preview, s.pending, s.deletion, s.issued, message) }
    private suspend fun <T> value(result: ApiResult<T>): T? {
        currentCoroutineContext().ensureActive()
        return when (result) {
        is ApiResult.Success -> result.value
        is ApiResult.Failure -> {
            if (result.reason == ApiFailure.Unauthorized) unauthorized()
            else {
                if (result.reason is ApiFailure.Busy) retryAt = System.currentTimeMillis() + (result.reason.retryAfterSeconds ?: 3).coerceIn(1, 3600) * 1000
                feedback("Operation unavailable (${result.reason.javaClass.simpleName}). Refresh before retrying; no new operation was submitted.")
            }; null
        }
        }
    }
    fun refresh() = work { c, i ->
        val status = value(api.securityStatus(c)) ?: return@work
        if (status.owner_id != i.owner || status.retention != "until_explicit_owner_deletion") { unauthorized(); return@work }
        val devices = value(api.credentials(c)) ?: return@work
        val pending = store.securityJournal(i)
        currentCoroutineContext().ensureActive()
        if (c.dataEpoch != null && status.data_epoch != c.dataEpoch && pending?.kind != "delete") { unauthorized(); return@work }
        history.value = value(api.deletions(c)) ?: return@work
        var deletion: DeletionDto? = null
        var retained = pending
        if (pending?.kind == "delete") {
            when (val result = api.deletion(c, pending.operation)) {
                is ApiResult.Success -> {
                    deletion = result.value
                    if (deletion.id != pending.operation) { unauthorized(); return@work }
                    if (deletion.status == "completed") { erased(); return@work }
                }
                is ApiResult.Failure -> if (result.reason != ApiFailure.NotFound) { value(result); return@work }
            }
        } else if (pending != null && devices.any { it.id == pending.operation }) {
            store.removeSecurityJournal(i, pending.operation); retained = null
        }
        mutable.value = SecurityState(true, true, status, devices, pending = retained, deletion = deletion,
            notice = if (pending != null && retained == null) "Issued credential found. Its secret cannot be recovered. Revoke it and explicitly enroll another device if delivery was lost." else null)
    }
    fun enroll(label: String, rotate: UUID? = null) = work { c, i ->
        if (state.value.pending != null || label.trim().length !in 1..80 || state.value.status?.enrollment_enabled != true) return@work
        val pending = SecurityJournal(i, if (rotate == null) "enroll" else "rotate", UUID.randomUUID(), label.trim(), rotate)
        store.saveSecurityJournal(pending)
        currentCoroutineContext().ensureActive()
        val s = state.value; mutable.value = SecurityState(true, true, s.status, s.devices, pending = pending)
        issue(c, i, pending)
    }
    private suspend fun issue(c: ConnectionCredential, i: SessionIdentity, pending: SecurityJournal) {
        val issued = value(api.issueCredential(c, pending)) ?: return
        if (issued.credential.id != pending.operation) { unauthorized(); return }
        store.removeSecurityJournal(i, pending.operation)
        currentCoroutineContext().ensureActive()
        val s = state.value
        mutable.value = SecurityState(true, true, s.status, s.devices, issued = issued,
            notice = if (issued.token == null) "Metadata recovered; the one-time secret is unavailable. Revoke this credential and enroll explicitly again." else "One-time secret: save it in your password manager. Keep an independent recovery credential before rotating.")
        if (pending.kind == "rotate" && s.status?.current_credential_id == pending.credential && issued.token != null) install(i.server, issued.token)
    }
    fun useIssued() { val issued = state.value.issued ?: return; val i = identity ?: return; issued.token?.let { install(i.server, it) } }
    fun revoke(id: UUID) = work { c, _ ->
        if (value(api.revokeCredential(c, id)) != null) {
            if (state.value.status?.current_credential_id == id) unauthorized() else feedback("Credential revoked. Refresh the device list.")
        }
    }
    fun preview() = work { c, _ ->
        if (state.value.pending != null) return@work
        val preview = value(api.deletionPreview(c)) ?: return@work
        val s = state.value; mutable.value = SecurityState(true, true, s.status, s.devices, preview = preview)
    }
    fun confirm() = work { c, i ->
        val preview = state.value.preview ?: return@work
        if (state.value.pending != null || state.value.status?.deletion_worker_enabled != true) return@work
        val pending = SecurityJournal(i, "delete", UUID.randomUUID(), preview = preview.id)
        store.saveSecurityJournal(pending)
        currentCoroutineContext().ensureActive()
        val s = state.value; mutable.value = SecurityState(true, true, s.status, s.devices, pending = pending)
        delete(c, pending)
    }
    private suspend fun delete(c: ConnectionCredential, pending: SecurityJournal) {
        val result = value(api.deleteContent(c, pending)) ?: return
        if (result.id != pending.operation) { unauthorized(); return }
        if (result.status == "completed") { erased(); return }
        val s = state.value; mutable.value = SecurityState(true, true, s.status, s.devices, pending = pending, deletion = result,
            notice = "Deletion ${result.status}. Refresh to check its durable status. Backups and offline devices may retain copies.")
    }
    fun retrySaved() = work { c, i ->
        val pending = state.value.pending ?: return@work
        if (pending.kind == "delete") delete(c, pending) else issue(c, i, pending)
    }
    fun forgetReservation() = work { _, i ->
        val pending = state.value.pending ?: return@work
        if (state.value.deletion?.status in setOf("queued", "running")) return@work
        store.removeSecurityJournal(i, pending.operation)
        val s = state.value; mutable.value = SecurityState(true, true, s.status, s.devices, notice = "Local reservation cleared. This does not undo any server operation; refresh the list before starting again.")
    }
}
