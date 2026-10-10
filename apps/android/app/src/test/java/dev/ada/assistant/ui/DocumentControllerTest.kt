package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.time.OffsetDateTime
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

private val docScope = UUID.randomUUID()
private val docOtherScope = UUID.randomUUID()
private val docIdentity = SessionIdentity("https://ada.test/", UUID.randomUUID())
private val docConnection = ConnectionCredential.parse(docIdentity.server, "synthetic-document-token", false)!!
private val docFeatures = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(
    document_ingestion = "text_markdown_v1", document_uploads = true, document_retrieval = true, document_citations = true, document_max_bytes = 256 * 1024,
)
private class UploadStore : SessionStore {
    var saved: PendingDocument? = null
    var failSave = false; var failRemove = false
    val operations = mutableListOf<String>()
    override suspend fun readCredential(): StoredCredential? = null
    override suspend fun saveCredential(credential: StoredCredential) = Unit
    override suspend fun clear() { saved = null }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = null
    override suspend fun savePending(message: PendingMessage) = Unit
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) = Unit
    override suspend fun documentPending(identity: SessionIdentity) = saved?.takeIf { it.identity == identity }
    override suspend fun saveDocumentPending(pending: PendingDocument) {
        if (failSave) throw SessionStorageException()
        assertTrue(saved == null || saved == pending); saved = pending; operations += "reserve"
    }
    override suspend fun removeDocumentPending(identity: SessionIdentity, uploadId: UUID) {
        if (failRemove) throw SessionStorageException()
        if (saved?.identity == identity && saved?.uploadId == uploadId) saved = null
        operations += "remove"
    }
}
private fun unsupportedDocumentApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) {
    _, method, _ -> error("Unexpected test call: ${method.name}")
} as AdaApi
private class UploadApi(val store: UploadStore) : AdaApi by unsupportedDocumentApi() {
    val posts = mutableListOf<PendingDocument>(); val rows = mutableMapOf<UUID, DocumentUploadDto>(); val bodies = mutableMapOf<UUID, String>()
    var failure: ApiResult.Failure? = null; var lostDelivery = false; var mismatch = false
    var listCall: suspend (UUID) -> ApiResult<List<DocumentUploadDto>> = { scope -> ApiResult.Success(rows.values.filter { it.scope_id == scope }) }
    override suspend fun scopes(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(
        ScopeDto(docScope, "Synthetic first scope", "project", 1), ScopeDto(docOtherScope, "Synthetic second scope", "project", 1)))
    override suspend fun documentUploads(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int) = listCall(scope)
    override suspend fun documentUpload(connection: ConnectionCredential, id: UUID): ApiResult<DocumentUploadDto> = rows[id]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun documentVersions(connection: ConnectionCredential, source: UUID, limit: Int, offset: Int) = ApiResult.Success(rows.values.filter { it.source_id == source })
    override suspend fun uploadDocument(connection: ConnectionCredential, pending: PendingDocument): ApiResult<DocumentUploadDto> {
        assertEquals(pending, store.saved); posts += pending; store.operations += "post"
        failure?.let { return it }
        val receipt = rows[pending.uploadId] ?: DocumentUploadDto(pending.uploadId, pending.sourceId, pending.scopeId, UUID.randomUUID(),
            rows.values.count { it.source_id == pending.sourceId } + 1, pending.filename, pending.mediaType, documentHash(pending.rawBytes()), pending.rawBytes().size,
            pending.availableFrom?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() } ?: 1791504000000L,
            pending.availableTo?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() }, "ready", created_at = 1791504000000L, published_at = 1791504000001L, chunk_count = 1)
        rows[receipt.id] = receipt; bodies[receipt.source_version_id] = documentText(pending.rawBytes())
        return if (lostDelivery) ApiResult.Failure(ApiFailure.Timeout) else ApiResult.Success(if (mismatch) receipt.copy(filename = "changed.txt") else receipt)
    }
    override suspend fun documentVersion(connection: ConnectionCredential, id: UUID): ApiResult<DocumentVersionDto> {
        val row = rows.values.single { it.source_version_id == id }; val text = bodies[id]!!
        return ApiResult.Success(DocumentVersionDto(id, row.source_id, row.scope_id, row.version, text, documentHash(text.toByteArray()), "imported_untrusted", row.created_at, row))
    }
    override suspend fun documentChunks(connection: ConnectionCredential, id: UUID, limit: Int, offset: Int) = ApiResult.Success(emptyList<DocumentChunkDto>())
}

@OptIn(ExperimentalCoroutinesApi::class)
class DocumentControllerTest {
    @Before fun setup() { Dispatchers.setMain(StandardTestDispatcher()) }
    @After fun cleanup() { Dispatchers.resetMain() }
    private fun TestScope.ready(store: UploadStore = UploadStore()): Triple<DocumentController, UploadApi, UploadStore> {
        val api = UploadApi(store); val c = DocumentController(api, store, this, {})
        c.setVerifiedSession(docConnection, docIdentity, docFeatures); advanceUntilIdle(); c.activate(); advanceUntilIdle()
        return Triple(c, api, store)
    }
    private fun preview(c: DocumentController) {
        c.beginUpload(); c.updateDraft(DocumentDraft(filename = "synthetic.md", mediaType = "text/markdown", text = "Exact 😀 e\u0301\r\n日本語  "))
        c.preview(); assertNotNull(c.state.value.preview)
    }
    @Test fun durableReservationPrecedesRawPostAndDoubleTapDoesNotDuplicate() = runTest {
        val (c, api, store) = ready(); preview(c); c.savePreview(); c.savePreview(); advanceUntilIdle()
        assertEquals(listOf("reserve", "post", "remove"), store.operations); assertEquals(1, api.posts.size)
        assertNull(store.saved); assertEquals("Exact 😀 e\u0301\r\n日本語  ", c.state.value.version!!.content)
        assertEquals("imported_untrusted", c.state.value.version!!.trust_class)
    }
    @Test fun failedJournalCommitSendsNothingAndKeepsEditablePreview() = runTest {
        val (c, api, store) = ready(); preview(c); store.failSave = true; c.savePreview(); advanceUntilIdle()
        assertTrue(api.posts.isEmpty()); assertNotNull(c.state.value.preview); assertNull(c.state.value.pending)
    }
    @Test fun responseLossRestoresOriginalIdsAndBytesWithoutAutomaticPost() = runTest {
        val (c, api, store) = ready(); preview(c); api.lostDelivery = true; c.savePreview(); advanceUntilIdle()
        val original = store.saved!!; c.reset(); api.lostDelivery = false
        val restored = DocumentController(api, store, this, {}); restored.setVerifiedSession(docConnection, docIdentity, docFeatures); advanceUntilIdle()
        assertEquals(1, api.posts.size); assertEquals(original, restored.state.value.pending)
        restored.resumePending(); advanceUntilIdle()
        assertEquals(listOf(original, original), api.posts); assertEquals(1, api.rows.size); assertNull(store.saved)
    }
    @Test fun changedReceiptNeverClaimsSuccessAndFailedCleanupBlocksAnotherUpload() = runTest {
        val (c, api, store) = ready(); preview(c); api.mismatch = true; c.savePreview(); advanceUntilIdle()
        assertNotNull(c.state.value.pending); assertEquals(ApiFailure.IncompatibleContract, c.state.value.fault)
        api.mismatch = false; store.failRemove = true; c.checkPending(); advanceUntilIdle()
        assertNotNull(store.saved); c.beginUpload(); assertNotEquals(DocumentScreen.Edit, c.state.value.screen)
        store.failRemove = false; c.checkPending(); advanceUntilIdle(); assertNull(store.saved); assertEquals(1, api.posts.size)
    }
    @Test fun reuploadRetainsStableSourceAndKeepsImmutablePreviousVersion() = runTest {
        val (c, api, _) = ready(); preview(c); c.savePreview(); advanceUntilIdle(); val old = c.state.value.detail!!
        c.beginUpload(reupload = true); c.updateDraft(c.state.value.draft.copy(text = "Second immutable version")); c.preview(); c.savePreview(); advanceUntilIdle()
        val latest = c.state.value.detail!!; assertEquals(old.source_id, latest.source_id); assertEquals(2, latest.version)
        assertNotEquals(old.source_version_id, latest.source_version_id); assertEquals(2, api.rows.size)
        c.openUpload(old); advanceUntilIdle(); assertEquals("Exact 😀 e\u0301\r\n日本語  ", c.state.value.version!!.content)
    }
    @Test fun invalidUtf16OversizeAndUnsafeFilenameNeverAllocateJournalOrPost() = runTest {
        val (c, api, store) = ready(); c.beginUpload()
        for (draft in listOf(DocumentDraft(text = "\uD83D"), DocumentDraft(text = "x".repeat(MOBILE_DOCUMENT_MAX_BYTES + 1)), DocumentDraft(filename = "../bad.txt", text = "text"))) {
            c.updateDraft(draft); c.preview(); assertNull(c.state.value.preview)
        }
        assertTrue(api.posts.isEmpty()); assertNull(store.saved)
    }
    @Test fun scopeSwitchFencesLateSuccessButCurrentSessionLate401StillExpires() = runTest {
        val (c, api, _) = ready(); val deferred = CompletableDeferred<ApiResult<List<DocumentUploadDto>>>()
        api.listCall = { scope -> if (scope == docScope) withContext(NonCancellable) { deferred.await() } else ApiResult.Success(emptyList()) }
        c.refreshUploads(); runCurrent(); c.selectScope(docOtherScope); runCurrent()
        deferred.complete(ApiResult.Success(emptyList())); advanceUntilIdle(); assertEquals(docOtherScope, c.state.value.scopeId)
        var expired = false; val late = CompletableDeferred<ApiResult<List<DocumentUploadDto>>>()
        val other = DocumentController(api, UploadStore(), this, { expired = true })
        api.listCall = { scope -> if (scope == docScope) withContext(NonCancellable) { late.await() } else ApiResult.Success(emptyList()) }
        other.setVerifiedSession(docConnection, docIdentity, docFeatures); runCurrent(); other.activate(); runCurrent()
        other.selectScope(docOtherScope); runCurrent(); late.complete(ApiResult.Failure(ApiFailure.Unauthorized)); advanceUntilIdle()
        assertTrue(expired); assertNull(other.state.value.scopeId)
    }
    @Test fun capabilityGateAndRetryAfterPreventUnsupportedOrEarlyNetworkWrites() = runTest {
        val store = UploadStore(); val api = UploadApi(store); var clock = 1000L
        val c = DocumentController(api, store, this, {}, { clock })
        c.setVerifiedSession(docConnection, docIdentity, docFeatures.copy(document_uploads = false)); advanceUntilIdle(); c.activate(); c.beginUpload()
        assertFalse(c.state.value.enabled); assertTrue(c.state.value.scopes.items.isEmpty())
        c.setVerifiedSession(docConnection, docIdentity, docFeatures); advanceUntilIdle(); c.activate(); advanceUntilIdle(); preview(c)
        api.failure = ApiResult.Failure(ApiFailure.Busy(3)); c.savePreview(); advanceUntilIdle(); assertEquals(1, api.posts.size)
        c.resumePending(); advanceUntilIdle(); assertEquals(1, api.posts.size)
        clock += 3000; api.failure = null; c.resumePending(); advanceUntilIdle(); assertEquals(2, api.posts.size)
    }
    @Test fun accountAndVersionQuotasKeepExactUploadAndExplainTheReachedLimit() = runTest {
        val (c, api, store) = ready(); preview(c)
        api.failure = ApiResult.Failure(ApiFailure.TooLarge, "document_storage_quota"); c.savePreview(); advanceUntilIdle()
        val original = store.saved; assertNotNull(original); assertTrue(c.state.value.notice!!.contains("storage limit"))
        api.failure = ApiResult.Failure(ApiFailure.TooLarge, "document_version_quota"); c.resumePending(); advanceUntilIdle()
        assertEquals(original, store.saved); assertTrue(c.state.value.notice!!.contains("version limit"))
    }
    @Test fun lateFileSuccessAndFailureCannotEnterANewOwnerScopeOrEditedDraft() = runTest {
        val (c, _, _) = ready(); c.beginUpload(); val original = c.beginFileSelection()!!
        c.reset(); c.setVerifiedSession(docConnection, docIdentity.copy(owner = UUID.randomUUID()), docFeatures)
        advanceUntilIdle(); c.activate(); advanceUntilIdle(); c.beginUpload()
        c.chooseFile(original, "private-old.md", "Previous owner's synthetic bytes".toByteArray())
        c.fileFailed(original)
        assertEquals("", c.state.value.draft.text); assertNull(c.state.value.validation)
        val previousScope = c.beginFileSelection()!!; c.selectScope(docOtherScope); advanceUntilIdle(); c.beginUpload()
        c.chooseFile(previousScope, "private-old.md", "Previous scope's synthetic bytes".toByteArray())
        assertEquals("", c.state.value.draft.text)
        val previousDraft = c.beginFileSelection()!!; c.updateDraft(c.state.value.draft.copy(text = "New explicit draft"))
        c.chooseFile(previousDraft, "old.md", "Old delayed file bytes".toByteArray())
        assertEquals("New explicit draft", c.state.value.draft.text)
        val current = c.beginFileSelection()!!; c.chooseFile(current, "current.md", "Current exact 😀\r\ntext".toByteArray())
        assertEquals("Current exact 😀\r\ntext", c.state.value.draft.text)
    }
}
