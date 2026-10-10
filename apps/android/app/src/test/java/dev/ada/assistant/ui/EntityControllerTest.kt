package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test

private val entityScope = UUID.randomUUID()
private val entityOther = UUID.randomUUID()
private val entityIdentity = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val entityConnection = ConnectionCredential.parse(entityIdentity.server, "synthetic-entity-token", false)!!
private val entityCaps = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(scoped_entities = true, entity_writes = true, entity_resolution = "explicit_aliases_v1")
private class IdentityStore : SessionStore {
    var saved: PendingEntity? = null
    var failSave = false; var failRemove = false
    val events = mutableListOf<String>()
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) = Unit
    override suspend fun clear() { saved = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) = Unit
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) = Unit
    override suspend fun entityPending(identity: SessionIdentity) = saved?.takeIf { it.identity == identity }
    override suspend fun saveEntityPending(pending: PendingEntity) { if (failSave) throw SessionStorageException(); assertTrue(saved == null || saved == pending); saved = pending; events += "reserve" }
    override suspend fun removeEntityPending(identity: SessionIdentity, operationId: UUID) { if (failRemove) throw SessionStorageException(); if (saved?.identity == identity && saved?.operationId == operationId) saved = null; events += "remove" }
}
private fun unexpectedEntityApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ -> error("Unexpected call: ${method.name}") } as AdaApi
private class IdentityApi(val store: IdentityStore) : AdaApi by unexpectedEntityApi() {
    val posts = mutableListOf<PendingEntity>(); val receipts = mutableMapOf<UUID, EntityOperationDto>()
    var loss = false; var mismatch = false; var failure: ApiResult.Failure? = null
    var listCall: suspend (UUID) -> ApiResult<List<EntityDto>> = { scope -> ApiResult.Success(receipts.values.mapNotNull { it.entity }.filter { it.scope_id == scope }) }
    override suspend fun scopes(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(ScopeDto(entityScope, "Synthetic one", "project", 1), ScopeDto(entityOther, "Synthetic two", "project", 1)))
    override suspend fun entities(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int) = listCall(scope)
    override suspend fun claims(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int, history: Boolean, asOf: String?) = ApiResult.Success(emptyList<ClaimDto>())
    override suspend fun resolveEntity(connection: ConnectionCredential, scope: UUID, body: EntityResolveInputDto) = ApiResult.Success(EntityResolutionDto("absent", body.name, candidates = emptyList(), alias_ids = emptyList()))
    override suspend fun entityOperation(connection: ConnectionCredential, id: UUID): ApiResult<EntityOperationDto> = receipts[id]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun writeEntity(connection: ConnectionCredential, pending: PendingEntity): ApiResult<EntityOperationDto> {
        assertEquals(pending, store.saved); posts += pending; store.events += "post"; failure?.let { return it }
        val body = adaJson.parseToJsonElement(pending.body).jsonObject
        val receipt = receipts.getOrPut(pending.operationId) { EntityOperationDto(pending.operationId, pending.scopeId, "create", 1, EntityDto(UUID.fromString(body["entity_id"]!!.jsonPrimitive.content), pending.scopeId, body["label"]!!.jsonPrimitive.content, "person", "synthetic", 0, created_at = 1, is_self = false)) }
        return if (loss) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(if (mismatch) receipt.copy(scope_id = entityOther) else receipt)
    }
}

@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class EntityControllerTest {
    private fun TestScope.ready(store: IdentityStore = IdentityStore()): Triple<EntityController, IdentityApi, IdentityStore> {
        val api = IdentityApi(store); val c = EntityController(api, store, this, {})
        c.setVerifiedSession(entityConnection, entityIdentity, entityCaps); advanceUntilIdle(); c.activate(); advanceUntilIdle()
        return Triple(c, api, store)
    }
    private fun TestScope.preview(c: EntityController, label: String = "Synthetic 😀 e\u0301") { c.label(label); c.resolve(); advanceUntilIdle(); c.reviewCreate(); assertNotNull(c.state.value.preview) }
    @Test fun exactReservationPrecedesPostAndDoubleConfirmationSendsOnce() = runTest {
        val (c, api, store) = ready(); preview(c); c.confirm(); c.confirm(); advanceUntilIdle()
        assertEquals(listOf("reserve", "post", "remove"), store.events); assertEquals(1, api.posts.size); assertNull(store.saved)
    }
    @Test fun saveFailureSendsNothingAndMalformedUtf16CannotBeReserved() = runTest {
        val (c, api, store) = ready(); preview(c); store.failSave = true; c.confirm(); advanceUntilIdle()
        assertNotNull(c.state.value.preview); assertNull(store.saved); assertTrue(api.posts.isEmpty())
        c.label("\uD83D"); c.resolve(); advanceUntilIdle(); c.reviewCreate(); assertNull(c.state.value.preview)
    }
    @Test fun interruptedResultRestoresWithoutPostAndReusesExactOperation() = runTest {
        val (c, api, store) = ready(); preview(c); api.loss = true; c.confirm(); advanceUntilIdle(); val original = store.saved!!
        c.reset(); api.loss = false; val restored = EntityController(api, store, this, {})
        restored.setVerifiedSession(entityConnection, entityIdentity, entityCaps); advanceUntilIdle(); assertEquals(original, restored.state.value.pending); assertEquals(1, api.posts.size)
        restored.resumePending(); advanceUntilIdle(); assertEquals(listOf(original, original), api.posts); assertEquals(1, api.receipts.size); assertNull(store.saved)
    }
    @Test fun mismatchedReceiptAndCleanupFailureKeepJournalBlockingNewWrites() = runTest {
        val (c, api, store) = ready(); preview(c); api.mismatch = true; c.confirm(); advanceUntilIdle(); assertEquals(ApiFailure.IncompatibleContract, c.state.value.fault)
        api.mismatch = false; store.failRemove = true; c.checkPending(); advanceUntilIdle(); c.reviewCreate(); assertNull(c.state.value.preview); assertNotNull(store.saved)
        store.failRemove = false; c.checkPending(); advanceUntilIdle(); assertNull(store.saved); assertEquals(1, api.posts.size)
    }
    @Test fun capabilityAndRetryAfterGatesKeepExactInput() = runTest {
        val store = IdentityStore(); val api = IdentityApi(store); var clock = 1000L
        val c = EntityController(api, store, this, {}, { clock }); c.setVerifiedSession(entityConnection, entityIdentity, entityCaps.copy(entity_writes = false)); advanceUntilIdle(); c.activate(); assertTrue(c.state.value.scopes.items.isEmpty())
        c.setVerifiedSession(entityConnection, entityIdentity, entityCaps); advanceUntilIdle(); c.activate(); advanceUntilIdle(); preview(c)
        api.failure = ApiResult.Failure(ApiFailure.Busy(3)); c.confirm(); advanceUntilIdle(); val original = store.saved
        c.resumePending(); advanceUntilIdle(); assertEquals(1, api.posts.size)
        clock += 3000; api.failure = null; c.resumePending(); advanceUntilIdle(); assertEquals(original, api.posts.last()); assertNull(store.saved)
    }
    @Test fun scopeAndOwnerChangesFenceLateResultsWhileCurrent401Expires() = runTest {
        val (c, api, _) = ready(); val late = CompletableDeferred<ApiResult<List<EntityDto>>>()
        api.listCall = { scope -> if (scope == entityScope) withContext(NonCancellable) { late.await() } else ApiResult.Success(emptyList()) }
        c.refresh(); runCurrent(); c.selectScope(entityOther); runCurrent(); late.complete(ApiResult.Success(emptyList())); advanceUntilIdle(); assertEquals(entityOther, c.state.value.scopeId)
        var expired = false; val unauthorized = CompletableDeferred<ApiResult<List<EntityDto>>>()
        api.listCall = { scope -> if (scope == entityScope) withContext(NonCancellable) { unauthorized.await() } else ApiResult.Success(emptyList()) }
        val other = EntityController(api, IdentityStore(), this, { expired = true }); other.setVerifiedSession(entityConnection, entityIdentity, entityCaps); advanceUntilIdle(); other.activate(); runCurrent(); other.selectScope(entityOther); runCurrent()
        unauthorized.complete(ApiResult.Failure(ApiFailure.Unauthorized)); advanceUntilIdle(); assertTrue(expired); assertNull(other.state.value.scopeId)
    }
    @Test fun supplementaryNamesRespectCodePointLimitWithoutSplittingSurrogates() = runTest {
        val (c, _, _) = ready(); c.label("😀".repeat(161)); assertEquals("😀".repeat(160), c.state.value.label)
    }
    @Test fun previousOwnersLateUnauthorizedResultCannotClearNewVerifiedOwner() = runTest {
        val store = IdentityStore(); val api = IdentityApi(store); var expired = false
        val c = EntityController(api, store, this, { expired = true }); c.setVerifiedSession(entityConnection, entityIdentity, entityCaps); advanceUntilIdle(); c.activate(); advanceUntilIdle()
        val late = CompletableDeferred<ApiResult<List<EntityDto>>>()
        api.listCall = { withContext(NonCancellable) { late.await() } }; c.refresh(); runCurrent()
        api.listCall = { ApiResult.Success(emptyList()) }
        c.setVerifiedSession(entityConnection, entityIdentity.copy(owner = UUID.randomUUID()), entityCaps); runCurrent(); c.activate(); runCurrent()
        late.complete(ApiResult.Failure(ApiFailure.Unauthorized)); advanceUntilIdle()
        assertFalse(expired); assertTrue(c.state.value.enabled); assertEquals(entityScope, c.state.value.scopeId)
    }
}
