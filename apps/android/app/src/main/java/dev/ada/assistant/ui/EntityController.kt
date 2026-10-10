package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.*

data class EntityState(
    val enabled: Boolean = false, val scopes: ChatPage<ScopeDto> = ChatPage(), val scopeId: UUID? = null,
    val entities: ChatPage<EntityDto> = ChatPage(), val selected: EntityDto? = null, val aliases: List<EntityAliasDto> = emptyList(),
    val claims: ChatPage<ClaimDto> = ChatPage(), val selectedClaim: UUID? = null,
    val label: String = "", val kind: String = "person", val resolution: EntityResolutionDto? = null,
    val mergePreview: EntityMergePreviewDto? = null, val preview: PendingEntity? = null,
    val pending: PendingEntity? = null, val busy: Boolean = false, val fault: ApiFailure? = null, val notice: String? = null,
) { override fun toString() = "EntityState(redacted)" }

class EntityController(
    private val api: AdaApi, private val store: SessionStore, private val workScope: CoroutineScope,
    private val unauthorized: () -> Unit, private val now: () -> Long = System::currentTimeMillis,
) {
    private val mutableState = MutableStateFlow(EntityState())
    val state = mutableState.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L; private var choice = 0L; private var detail = 0L
    private var cooldown = 0L
    private val jobs = mutableSetOf<Job>()
    private fun update(change: (EntityState) -> EntityState) { mutableState.value = change(mutableState.value) }
    fun reset() { generation++; choice++; detail++; jobs.toList().forEach { it.cancel() }; jobs.clear(); connection = null; identity = null; cooldown = 0; mutableState.value = EntityState() }
    fun setVerifiedSession(conn: ConnectionCredential, owner: SessionIdentity, caps: CapabilitiesDto) {
        reset(); connection = conn; identity = owner
        update { it.copy(enabled = caps.scoped_entities && caps.entity_writes && caps.entity_resolution == "explicit_aliases_v1", busy = true) }
        work { _, epoch -> val saved = store.entityPending(owner)
            if (current(epoch)) update { it.copy(busy = false, pending = saved?.takeIf { p -> p.identity == owner }, notice = if (saved != null) "A saved entity change needs review. Check its original operation or explicitly resume identical input." else null) }
        }
    }
    private fun current(epoch: Long) = epoch == generation && connection != null && identity != null
    private fun work(task: suspend (ConnectionCredential, Long) -> Unit) {
        val conn = connection ?: return; val epoch = generation
        workScope.launch { try { if (current(epoch)) task(conn, epoch) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(epoch)) update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract, notice = "The operation could not be confirmed safely. Keep its exact saved input.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun <T> accepted(result: ApiResult<T>, epoch: Long): T? {
        if (!current(epoch)) return null
        if (result is ApiResult.Success) return result.value
        val failure = result as ApiResult.Failure
        if (failure.reason == ApiFailure.Unauthorized) { reset(); unauthorized(); return null }
        if (failure.reason is ApiFailure.Busy) {
            val instant = now(); val wait = failure.reason.retryAfterSeconds ?: 1
            cooldown = if (wait > (Long.MAX_VALUE - instant) / 1000) Long.MAX_VALUE else instant + wait.coerceAtLeast(0) * 1000
        }
        update { it.copy(busy = false, fault = failure.reason, notice = when (failure.reason) {
            ApiFailure.Conflict -> "The identity, preview or link changed. Check the saved operation before reviewing a new change."
            ApiFailure.TooLarge -> "This scope has reached a retained entity, alias, link or audit limit. Saved input is kept for review."
            else -> if (it.pending != null) "The outcome is not confirmed. Check the original operation or explicitly resume identical input." else null
        }) }; return null
    }
    fun activate() { if (state.value.enabled) loadScopes(true) }
    fun moreScopes() = loadScopes(false)
    private fun loadScopes(refresh: Boolean) {
        val s = state.value; if (!s.enabled || s.scopes.loading || (!refresh && !s.scopes.hasMore)) return
        val offset = if (refresh) 0 else s.scopes.nextOffset; update { it.copy(scopes = it.scopes.copy(loading = true)) }
        work { conn, epoch -> val rows = accepted(api.scopes(conn, 50, offset), epoch)
            if (!current(epoch)) return@work
            update { it.copy(scopes = if (rows == null) it.scopes.copy(loading = false) else page(it.scopes, rows, offset) { r -> r.id }) }
            if (state.value.scopeId == null) rows?.firstOrNull()?.let { selectScope(it.id) }
        }
    }
    private fun <T> page(old: ChatPage<T>, rows: List<T>, offset: Int, id: (T) -> UUID): ChatPage<T> {
        val unique = linkedMapOf<UUID, T>(); if (offset != 0) old.items.forEach { unique[id(it)] = it }; rows.forEach { unique[id(it)] = it }
        return ChatPage(unique.values.toList(), false, rows.size == 50, offset + rows.size)
    }
    fun selectScope(scope: UUID) {
        if (state.value.busy || state.value.scopes.items.none { it.id == scope }) return
        choice++; detail++
        update { it.copy(scopeId = scope, entities = ChatPage(), claims = ChatPage(), selected = null, selectedClaim = null, aliases = emptyList(), label = "", resolution = null, preview = null, mergePreview = null, fault = null, notice = null) }
        refresh()
    }
    fun refresh() { loadEntities(true); loadClaims(true) }
    fun moreEntities() = loadEntities(false)
    fun moreClaims() = loadClaims(false)
    private fun loadEntities(refresh: Boolean) {
        val s = state.value; val scope = s.scopeId ?: return; val selectedScope = choice
        if (!s.enabled || s.entities.loading || (!refresh && !s.entities.hasMore)) return
        val offset = if (refresh) 0 else s.entities.nextOffset; update { it.copy(entities = it.entities.copy(loading = true)) }
        work { conn, epoch -> val rows = accepted(api.entities(conn, scope, 50, offset), epoch)
            if (!current(epoch) || selectedScope != choice) return@work
            if (rows?.any { it.scope_id != scope || it.origin != "user_confirmed" } == true) { update { it.copy(fault = ApiFailure.IncompatibleContract, entities = it.entities.copy(loading = false)) }; return@work }
            update { it.copy(entities = if (rows == null) it.entities.copy(loading = false) else page(it.entities, rows, offset) { r -> r.id }) }
        }
    }
    private fun loadClaims(refresh: Boolean) {
        val s = state.value; val scope = s.scopeId ?: return; val selectedScope = choice
        if (!s.enabled || s.claims.loading || (!refresh && !s.claims.hasMore)) return
        val offset = if (refresh) 0 else s.claims.nextOffset; update { it.copy(claims = it.claims.copy(loading = true)) }
        work { conn, epoch -> val rows = accepted(api.claims(conn, scope, 50, offset), epoch)
            if (!current(epoch) || selectedScope != choice) return@work
            if (rows?.any { it.scope_id != scope } == true) { update { it.copy(fault = ApiFailure.IncompatibleContract, claims = it.claims.copy(loading = false)) }; return@work }
            update { it.copy(claims = if (rows == null) it.claims.copy(loading = false) else page(it.claims, rows, offset) { r -> r.id }) }
        }
    }
    fun selectEntity(id: UUID) {
        if (state.value.busy) return
        val row = state.value.entities.items.firstOrNull { it.id == id } ?: return
        val picked = ++detail; update { it.copy(selected = row, aliases = emptyList(), label = "", resolution = null, preview = null, mergePreview = null, fault = null) }
        work { conn, epoch -> val rows = accepted(api.entityAliases(conn, id), epoch)
            if (!current(epoch) || picked != detail) return@work
            if (rows?.any { it.entity_id != id || it.scope_id != row.scope_id } == true) update { it.copy(fault = ApiFailure.IncompatibleContract) }
            else if (rows != null) update { it.copy(aliases = rows) }
        }
    }
    fun selectClaim(id: UUID) { if (!state.value.busy && state.value.claims.items.any { it.id == id }) update { it.copy(selectedClaim = id) } }
    fun label(value: String) { if (!state.value.busy) { detail++; update { it.copy(label = if (value.codePointCount(0, value.length) <= 160) value else value.substring(0, value.offsetByCodePoints(0, 160)), resolution = null, preview = null, mergePreview = null) } } }
    fun kind(value: String) { if (value in setOf("person", "project", "object", "other") && !state.value.busy) update { it.copy(kind = value, preview = null) } }
    fun resolve(selected: UUID? = null) {
        val s = state.value; val scope = s.scopeId ?: return; if (!s.enabled || s.label.isBlank() || s.busy) return
        val picked = detail; update { it.copy(busy = true, fault = null) }
        work { conn, epoch -> val result = accepted(api.resolveEntity(conn, scope, EntityResolveInputDto(name = s.label, selected_id = selected)), epoch)
            if (current(epoch) && picked == detail) update { it.copy(busy = false, resolution = result) }
        }
    }
    private fun review(action: String, path: String, fields: Map<String, JsonElement>) {
        val s = state.value; val owner = identity ?: return; val scope = s.scopeId ?: return
        if (!s.enabled || s.busy || s.pending != null) return
        val op = UUID.randomUUID(); val body = JsonObject(fields + ("operation_id" to JsonPrimitive(op.toString()))).toString()
        val pending = PendingEntity(owner, scope, op, action, path, body)
        try { validateEntityPending(pending); update { it.copy(preview = pending, fault = null) } }
        catch (_: Exception) { update { it.copy(fault = ApiFailure.Validation) } }
    }
    fun reviewCreate() {
        val s = state.value; val scope = s.scopeId ?: return
        if (s.label.isBlank() || s.resolution == null) { update { it.copy(notice = "Check this name for existing or ambiguous entities before reviewing creation.") }; return }
        review("create", "scopes/$scope/entities", mapOf("entity_id" to JsonPrimitive(UUID.randomUUID().toString()), "label" to JsonPrimitive(s.label), "kind" to JsonPrimitive(s.kind)))
    }
    fun reviewAlias() { val s = state.value; val row = s.selected ?: return; if (row.redirect_id != null || s.label.isBlank()) return
        review("alias", "entities/${row.id}/aliases", mapOf("alias_id" to JsonPrimitive(UUID.randomUUID().toString()), "label" to JsonPrimitive(s.label))) }
    fun reviewRename() { val s = state.value; val row = s.selected ?: return; if (row.redirect_id != null || s.label.isBlank()) return
        review("rename", "entities/${row.id}/rename", mapOf("label" to JsonPrimitive(s.label), "expected_revision" to JsonPrimitive(row.revision))) }
    fun reviewRetire(id: UUID) { if (state.value.aliases.none { it.id == id && !it.canonical && it.valid_to == null }) return; review("retire_alias", "entity-aliases/$id/retire", emptyMap()) }
    fun reviewSelf() { val row = state.value.selected ?: return; if (row.kind != "person" || row.redirect_id != null) return; review("self", "scopes/${row.scope_id}/entities/self", mapOf("entity_id" to JsonPrimitive(row.id.toString()))) }
    fun reviewLink(clear: Boolean = false) { val s = state.value; val claim = s.claims.items.firstOrNull { it.id == s.selectedClaim } ?: return; val row = s.selected
        if (!clear && (row == null || row.redirect_id != null)) return
        review("link", "claims/${claim.id}/entity", mapOf("entity_id" to (if (clear) JsonNull else JsonPrimitive(row!!.id.toString())), "expected_entity_id" to (claim.subject_entity_id?.let { JsonPrimitive(it.toString()) } ?: JsonNull))) }
    fun previewMerge(target: UUID) { val s = state.value; val row = s.selected ?: return; val picked = detail
        if (s.busy || row.redirect_id != null || row.id == target || s.entities.items.none { it.id == target && it.kind == row.kind && it.redirect_id == null }) return
        update { it.copy(busy = true) }
        work { conn, epoch -> val result = accepted(api.entityMergePreview(conn, row.id, target), epoch)
            if (current(epoch) && picked == detail) {
                if (result != null && (result.source.id != row.id || result.target.id != target || result.source.scope_id != s.scopeId || result.target.scope_id != s.scopeId)) update { it.copy(busy = false, fault = ApiFailure.IncompatibleContract) }
                else update { it.copy(busy = false, mergePreview = result) }
            }
        }
    }
    fun reviewMerge() { val preview = state.value.mergePreview ?: return; review("merge", "entities/${preview.source.id}/merge", mapOf("target_id" to JsonPrimitive(preview.target.id.toString()), "preview_token" to JsonPrimitive(preview.preview_token))) }
    fun reviewUndo() { val row = state.value.selected ?: return; if (row.redirect_id != null) review("undo_merge", "entities/${row.id}/undo-merge", emptyMap()) }
    fun cancelPreview() { update { it.copy(preview = null) } }
    fun confirm() {
        val s = state.value; val pending = s.preview ?: return
        if (s.busy || s.pending != null || pending.identity != identity || now() < cooldown) return
        update { it.copy(preview = null, pending = pending, busy = true, fault = null) }
        work { conn, epoch ->
            try { store.saveEntityPending(pending) } catch (_: Exception) { if (current(epoch)) update { it.copy(pending = null, preview = pending, busy = false, notice = "Nothing was sent because encrypted recovery could not be saved.") }; return@work }
            if (current(epoch)) finish(accepted(api.writeEntity(conn, pending), epoch), pending, epoch)
        }
    }
    fun checkPending() = recover(false)
    fun resumePending() = recover(true)
    private fun recover(send: Boolean) {
        val pending = state.value.pending ?: return; if (!state.value.enabled || state.value.busy || pending.identity != identity || now() < cooldown) return
        update { it.copy(busy = true, fault = null) }
        work { conn, epoch -> finish(accepted(if (send) api.writeEntity(conn, pending) else api.entityOperation(conn, pending.operationId), epoch), pending, epoch) }
    }
    private suspend fun finish(receipt: EntityOperationDto?, pending: PendingEntity, epoch: Long) {
        if (!current(epoch)) return
        update { it.copy(busy = false) }; if (receipt == null) return
        if (!verifyEntityOperation(pending, receipt)) { update { it.copy(fault = ApiFailure.IncompatibleContract, notice = "The receipt does not match the saved identity change. Keep its exact input.") }; return }
        try { store.removeEntityPending(pending.identity, pending.operationId) } catch (_: Exception) { if (current(epoch)) update { it.copy(notice = "The change committed; local recovery cleanup needs attention. Check the same operation.") }; return }
        if (!current(epoch)) return
        update { it.copy(pending = null, label = "", resolution = null, selected = null, aliases = emptyList(), mergePreview = null, notice = "Explicit identity change recorded. Original evidence and saved request sources remain unchanged.") }
        refresh()
    }
    fun discard() { val pending = state.value.pending ?: return; if (state.value.busy || pending.identity != identity) return; update { it.copy(busy = true) }
        work { _, epoch -> store.removeEntityPending(pending.identity, pending.operationId); if (current(epoch)) update { it.copy(busy = false, pending = null, notice = "Local recovery discarded. Any committed remote change remains; refresh before reviewing a new operation.") } }
    }
}
