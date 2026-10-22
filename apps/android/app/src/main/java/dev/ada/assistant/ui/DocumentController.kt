package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.Base64
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** Private document state enters only after server and owner verification. No automatic POST on restore. */
class DocumentController(
    private val api: AdaApi, private val store: SessionStore, private val workScope: CoroutineScope,
    private val onUnauthorized: () -> Unit, private val now: () -> Long = System::currentTimeMillis,
) {
    private val mutableState = MutableStateFlow(DocumentState())
    val state = mutableState.asStateFlow()
    private var connection: ConnectionCredential? = null
    private var identity: SessionIdentity? = null
    private var generation = 0L
    private var selection = 0L
    private var detailSelection = 0L
    private var fileSelection = 0L
    private var retryNotBefore = 0L
    private val jobs = mutableSetOf<Job>()
    private fun update(block: (DocumentState) -> DocumentState) { mutableState.value = block(mutableState.value) }
    fun reset() {
        generation++; selection++; detailSelection++; fileSelection++
        jobs.toList().forEach { it.cancel() }; jobs.clear()
        connection = null; identity = null; retryNotBefore = 0
        mutableState.value = DocumentState()
    }
    fun setVerifiedSession(connection: ConnectionCredential, identity: SessionIdentity, features: CapabilitiesDto) {
        reset(); this.connection = connection; this.identity = identity
        update { it.copy(enabled = features.document_uploads && features.document_ingestion == "text_markdown_v1" && features.document_max_bytes > 0,
            uploadLimit = features.document_max_bytes.coerceIn(0, MOBILE_DOCUMENT_MAX_BYTES), pdfEnabled = features.pdf_ingestion == "ada-text-pdf-v1") }
        work { _, epoch ->
            val pending = store.documentPending(identity)
            if (current(epoch) && pending?.identity == identity) update { it.copy(pending = pending, scopeId = pending.scopeId,
                notice = "A saved document upload needs review. Check its original upload ID or explicitly resume the identical bytes.") }
        }
    }
    private fun current(epoch: Long) = generation == epoch && connection != null && identity != null
    private fun work(block: suspend (ConnectionCredential, Long) -> Unit) {
        val conn = connection ?: return; val epoch = generation
        workScope.launch {
            try { if (current(epoch)) block(conn, epoch) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (current(epoch)) update { it.copy(saving = false, detailLoading = false,
                scopes = it.scopes.copy(loading = false), uploads = it.uploads.copy(loading = false),
                versions = it.versions.copy(loading = false), chunks = it.chunks.copy(loading = false),
                fault = ApiFailure.IncompatibleContract,
                notice = "The operation could not be confirmed safely. Keep the saved upload and check its original ID.") } }
        }.also { job -> jobs += job; job.invokeOnCompletion { jobs -= job } }
    }
    private fun failed(failure: ApiResult.Failure, epoch: Long) {
        if (!current(epoch)) return
        if (failure.reason == ApiFailure.Unauthorized) { reset(); onUnauthorized(); return }
        if (failure.reason is ApiFailure.Busy) {
            val instant = now(); val seconds = failure.reason.retryAfterSeconds ?: 1
            retryNotBefore = if (seconds > (Long.MAX_VALUE - instant) / 1000) Long.MAX_VALUE else instant + seconds.coerceAtLeast(0) * 1000
        }
        update { it.copy(fault = failure.reason, notice = when (failure.code) {
            "document_upload_id_reused", "document_conflict", "document_source_id_reused" -> "The reserved upload or source ID conflicts with different input. Keep the exact reservation and review its status before a consciously new upload."
            "document_file_quota", "document_storage_quota" -> "This account has reached its retained document count or storage limit. The saved upload is kept for review."
            "document_version_quota" -> "This document has reached its retained version limit. The saved upload is kept for review."
            "document_invalid_encoding", "document_invalid_text", "document_unsupported_format" -> "The server rejected this document format or text. Review the saved input before starting a new upload."
            else -> if (it.pending != null) "The upload outcome is not confirmed. Check the original ID or explicitly resume the identical bytes." else null
        }) }
    }
    private fun accepted(result: ApiResult<*>, epoch: Long): Boolean {
        if (!current(epoch)) return false
        if (result is ApiResult.Failure && result.reason == ApiFailure.Unauthorized) { failed(result, epoch); return false }
        return true
    }
    private fun <T> value(result: ApiResult<T>, epoch: Long): T? = when {
        !current(epoch) -> null
        result is ApiResult.Success -> result.value
        result is ApiResult.Failure -> { failed(result, epoch); null }
        else -> null
    }
    private fun invalid(message: String) = update { it.copy(validation = message, fault = ApiFailure.Validation) }
    private fun <T> page(old: ChatPage<T>, rows: List<T>, offset: Int, id: (T) -> UUID): ChatPage<T> {
        val byId = linkedMapOf<UUID, T>(); if (offset != 0) old.items.forEach { byId[id(it)] = it }
        rows.forEach { byId[id(it)] = it }
        return ChatPage(byId.values.toList(), false, rows.size == PAGE_SIZE, offset + rows.size)
    }
    fun activate() { if (state.value.enabled) { refreshScopes(); if (state.value.scopeId != null) refreshUploads() } }
    fun refreshScopes() = scopes(true)
    fun loadMoreScopes() = scopes(false)
    private fun scopes(refresh: Boolean) {
        val prior = state.value.scopes
        if (!state.value.enabled || prior.loading || (!refresh && !prior.hasMore)) return
        val offset = if (refresh) 0 else prior.nextOffset
        update { it.copy(scopes = prior.copy(loading = true)) }
        work { conn, epoch ->
            val rows = value(api.scopes(conn, PAGE_SIZE, offset), epoch)
            if (!current(epoch)) return@work
            update { it.copy(scopes = if (rows == null) it.scopes.copy(loading = false) else page(it.scopes, rows, offset) { row -> row.id }) }
            if (state.value.scopeId == null) rows?.firstOrNull()?.let { selectScope(it.id) }
        }
    }
    fun selectScope(id: UUID) {
        if (state.value.saving || state.value.scopes.items.none { it.id == id }) return
        selection++; detailSelection++; fileSelection++
        update { it.copy(scopeId = id, screen = DocumentScreen.Browse, uploads = ChatPage(), versions = ChatPage(),
            detail = null, version = null, chunks = ChatPage(), draft = DocumentDraft(), preview = null, fault = null, validation = null) }
        refreshUploads()
    }
    fun refreshUploads() = uploads(true)
    fun loadMoreUploads() = uploads(false)
    private fun uploads(refresh: Boolean) {
        val s = state.value; val scope = s.scopeId ?: return
        if (!s.enabled || s.uploads.loading || (!refresh && !s.uploads.hasMore)) return
        val offset = if (refresh) 0 else s.uploads.nextOffset; val chosen = selection
        update { it.copy(uploads = s.uploads.copy(loading = true)) }
        work { conn, epoch ->
            val result = api.documentUploads(conn, scope, PAGE_SIZE, offset)
            if (!accepted(result, epoch) || chosen != selection) return@work
            val rows = value(result, epoch)
            if (!current(epoch)) return@work
            if (rows?.any { it.scope_id != scope || it.origin != "imported_document" || it.trust_class != "imported_untrusted" } == true) {
                invalid("The server returned incompatible document metadata."); update { it.copy(uploads = it.uploads.copy(loading = false)) }; return@work
            }
            update { it.copy(uploads = if (rows == null) it.uploads.copy(loading = false) else page(it.uploads, rows, offset) { row -> row.id }) }
        }
    }
    fun beginUpload(reupload: Boolean = false) {
        val s = state.value
        if (!s.enabled || s.pending != null || s.saving || s.scopeId == null) return
        val old = s.detail?.takeIf { reupload && it.scope_id == s.scopeId }
        fileSelection++
        update { it.copy(screen = DocumentScreen.Edit, draft = DocumentDraft(filename = old?.filename ?: "document.txt",
            mediaType = old?.media_type ?: "text/plain", sourceId = old?.source_id), preview = null, validation = null, fault = null, notice = null) }
    }
    fun updateDraft(draft: DocumentDraft) {
        if (state.value.screen != DocumentScreen.Edit || state.value.saving) return
        fileSelection++
        update { it.copy(draft = draft.copy(sourceId = it.draft.sourceId, binaryBase64 = if (draft.mediaType == "application/pdf") draft.binaryBase64 else null), validation = null, fault = null) }
    }
    private fun applyFile(filename: String, bytes: ByteArray) {
        if (state.value.screen != DocumentScreen.Edit || state.value.saving) return
        try {
            require(bytes.size in 1..state.value.uploadLimit)
            if (filename.endsWith(".pdf",ignoreCase=true)) {
                require(state.value.pdfEnabled && bytes.take(5).toByteArray().contentEquals("%PDF-".toByteArray()))
                updateDraft(state.value.draft.copy(filename=filename,mediaType="application/pdf",text="",binaryBase64=Base64.getEncoder().encodeToString(bytes)))
                return
            }
            val text = documentText(bytes)
            val media = if (filename.substringAfterLast('.', "").lowercase() in setOf("md", "markdown")) "text/markdown" else "text/plain"
            updateDraft(state.value.draft.copy(filename = filename, mediaType = media, text = text))
        } catch (_: Exception) { invalid("Choose a UTF-8 text or Markdown file no larger than ${state.value.uploadLimit / 1024} KiB.") }
    }
    fun beginFileSelection(): DocumentFileSelection? {
        val verified = identity ?: return null; val s = state.value; val scope = s.scopeId ?: return null
        if (!s.enabled || s.screen != DocumentScreen.Edit || s.saving || s.pending != null) return null
        return DocumentFileSelection(verified, scope, generation, ++fileSelection, s.uploadLimit)
    }
    fun isFileSelectionCurrent(selection: DocumentFileSelection): Boolean = selection.identity == identity &&
        selection.scope == state.value.scopeId && selection.sessionEpoch == generation && selection.editEpoch == fileSelection &&
        state.value.enabled && state.value.screen == DocumentScreen.Edit && !state.value.saving && state.value.pending == null
    fun chooseFile(selection: DocumentFileSelection, filename: String, bytes: ByteArray) {
        if (!isFileSelectionCurrent(selection)) return
        fileSelection++; applyFile(filename, bytes)
    }
    fun fileFailed(selection: DocumentFileSelection) {
        if (!isFileSelectionCurrent(selection)) return
        fileSelection++; invalid("The file could not be read safely. Choose UTF-8 text or Markdown within the upload limit.")
    }
    fun preview() {
        val s = state.value; val verified = identity ?: return; val scope = s.scopeId ?: return
        if (!s.enabled || s.screen != DocumentScreen.Edit || s.pending != null || s.saving) return
        try {
            val encoder = Charsets.UTF_8.newEncoder().onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
                .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT)
            val bytes = if (s.draft.mediaType == "application/pdf") {
                require(s.pdfEnabled); Base64.getDecoder().decode(requireNotNull(s.draft.binaryBase64))
            } else { val buffer = encoder.encode(java.nio.CharBuffer.wrap(s.draft.text)); ByteArray(buffer.remaining()).also { buffer.get(it) } }
            require(bytes.size <= s.uploadLimit)
            val pending = PendingDocument(verified, scope, UUID.randomUUID(), s.draft.sourceId ?: UUID.randomUUID(),
                s.draft.filename, s.draft.mediaType, Base64.getEncoder().encodeToString(bytes),
                normalizeUtcMillis(s.draft.availableFrom), normalizeUtcMillis(s.draft.availableTo))
            validateDocument(pending)
            update { it.copy(screen = DocumentScreen.Preview, preview = pending, validation = null, fault = null) }
        } catch (_: Exception) { invalid("Use a safe .txt/.md/.markdown filename, exact UTF-8 text within ${s.uploadLimit / 1024} KiB and timezone-bearing availability bounds.") }
    }
    fun editPreview() { if (!state.value.saving && state.value.pending == null) { fileSelection++; update { it.copy(screen = DocumentScreen.Edit, preview = null) } } }
    fun savePreview() {
        val s = state.value; val pending = s.preview ?: return
        if (!s.enabled || s.pending != null || s.saving || pending.identity != identity || now() < retryNotBefore) return
        update { it.copy(pending = pending, saving = true, validation = null, fault = null) }
        work { conn, epoch ->
            try { store.saveDocumentPending(pending) }
            catch (_: Exception) { if (current(epoch)) update { it.copy(pending = null, saving = false, notice = "The document was not sent because encrypted recovery storage could not be saved.") }; return@work }
            if (!current(epoch)) return@work
            submit(conn, pending, epoch)
        }
    }
    private suspend fun submit(conn: ConnectionCredential, pending: PendingDocument, epoch: Long) {
        val receipt = value(api.uploadDocument(conn, pending), epoch)
        if (!current(epoch)) return
        update { it.copy(saving = false) }
        receipt?.let { finishReceipt(pending, it, epoch) }
    }
    fun resumePending() {
        val s = state.value; val pending = s.pending ?: return
        if (!s.enabled || s.saving || pending.identity != identity || now() < retryNotBefore) return
        update { it.copy(saving = true, fault = null) }
        work { conn, epoch -> submit(conn, pending, epoch) }
    }
    fun checkPending() {
        val s = state.value; val pending = s.pending ?: return
        if (!s.enabled || s.saving || pending.identity != identity || now() < retryNotBefore) return
        update { it.copy(saving = true, fault = null) }
        work { conn, epoch ->
            val receipt = value(api.documentUpload(conn, pending.uploadId), epoch)
            if (!current(epoch)) return@work
            update { it.copy(saving = false) }; receipt?.let { finishReceipt(pending, it, epoch) }
        }
    }
    private suspend fun finishReceipt(pending: PendingDocument, receipt: DocumentUploadDto, epoch: Long) {
        if (!current(epoch) || state.value.pending != pending) return
        if (!verifyDocumentReceipt(pending, receipt)) { update { it.copy(fault = ApiFailure.IncompatibleContract, notice = "The receipt does not match this immutable upload. Keep the saved bytes and check its original ID.") }; return }
        update { it.copy(pendingReceipt = receipt) }
        if (receipt.state != "ready") {
            update { it.copy(notice = if (receipt.state == "processing") "This version is processing. Check status; incomplete text is unavailable to retrieval."
                else "This version failed ingestion. No partial version is searchable. Review its status before a consciously new upload.") }
            refreshUploads(); return
        }
        try { store.removeDocumentPending(pending.identity, pending.uploadId) }
        catch (_: Exception) { if (current(epoch)) update { it.copy(notice = "Document ready; encrypted recovery cleanup needs attention. Check the same upload before another write.") }; return }
        if (!current(epoch)) return
        update { it.copy(pending = null, pendingReceipt = null, preview = null, draft = DocumentDraft(),
            notice = "Document ready as imported, untrusted evidence. No explicit user assertion was created.") }
        openUpload(receipt); refreshUploads()
    }
    fun discardPending() {
        val s = state.value; val pending = s.pending ?: return
        if (s.saving || pending.identity != identity) return
        update { it.copy(saving = true) }
        work { _, epoch ->
            store.removeDocumentPending(pending.identity, pending.uploadId)
            if (!current(epoch)) return@work
            update { it.copy(saving = false, pending = null, pendingReceipt = null, preview = null, screen = DocumentScreen.Edit,
                draft = DocumentDraft(pending.filename, pending.mediaType, if(pending.mediaType=="application/pdf") "" else documentText(pending.rawBytes()), pending.availableFrom ?: "", pending.availableTo ?: "", pending.sourceId, if(pending.mediaType=="application/pdf") pending.rawBase64 else null),
                notice = "Local recovery was discarded. Any remote upload remains unchanged. Review versions before knowingly uploading new bytes.") }
        }
    }
    fun openUpload(receipt: DocumentUploadDto) {
        if (!state.value.enabled || receipt.scope_id != state.value.scopeId) return
        detailSelection++; val chosen = detailSelection
        update { it.copy(screen = DocumentScreen.Detail, detail = receipt, version = null, chunks = ChatPage(), detailLoading = receipt.state == "ready", validation = null, fault = null) }
        if (receipt.state != "ready") return
        work { conn, epoch ->
            val result = api.documentVersion(conn, receipt.source_version_id)
            if (!accepted(result, epoch) || chosen != detailSelection) return@work
            val version = value(result, epoch)
            if (!current(epoch)) return@work
            if (version != null && !verifyDocumentVersion(version, receipt)) { invalid("The exact document version could not be verified."); update { it.copy(detailLoading = false) }; return@work }
            update { it.copy(version = version, detailLoading = false) }; if (version != null) loadChunks(true)
        }
    }
    fun refreshDetail() {
        val old = state.value.detail ?: return; val chosen = detailSelection
        work { conn, epoch ->
            val result = api.documentUpload(conn, old.id)
            if (!accepted(result, epoch) || chosen != detailSelection) return@work
            val receipt = value(result, epoch) ?: return@work
            if (receipt.scope_id != old.scope_id || receipt.source_id != old.source_id || receipt.source_version_id != old.source_version_id) { invalid("The document receipt identity changed."); return@work }
            openUpload(receipt)
        }
    }
    fun loadMoreChunks() = loadChunks(false)
    private fun loadChunks(refresh: Boolean) {
        val s = state.value; val version = s.version ?: return
        if (s.chunks.loading || (!refresh && !s.chunks.hasMore)) return
        val offset = if (refresh) 0 else s.chunks.nextOffset; val chosen = detailSelection
        update { it.copy(chunks = s.chunks.copy(loading = true)) }
        work { conn, epoch ->
            val result = api.documentChunks(conn, version.id, PAGE_SIZE, offset)
            if (!accepted(result, epoch) || chosen != detailSelection) return@work
            val rows = value(result, epoch)
            if (!current(epoch)) return@work
            if (rows?.any { !verifyDocumentChunk(it, version) } == true) { invalid("A chunk does not match its exact source version."); update { it.copy(chunks = it.chunks.copy(loading = false)) }; return@work }
            update { it.copy(chunks = if (rows == null) it.chunks.copy(loading = false) else page(it.chunks, rows, offset) { row -> row.id }) }
        }
    }
    fun showVersions() { if (state.value.detail != null) { update { it.copy(screen = DocumentScreen.Versions, versions = ChatPage()) }; versions(true) } }
    fun loadMoreVersions() = versions(false)
    private fun versions(refresh: Boolean) {
        val s = state.value; val receipt = s.detail ?: return
        if (s.versions.loading || (!refresh && !s.versions.hasMore)) return
        val offset = if (refresh) 0 else s.versions.nextOffset; val chosen = detailSelection
        update { it.copy(versions = s.versions.copy(loading = true)) }
        work { conn, epoch ->
            val result = api.documentVersions(conn, receipt.source_id, PAGE_SIZE, offset)
            if (!accepted(result, epoch) || chosen != detailSelection) return@work
            val rows = value(result, epoch)
            if (!current(epoch)) return@work
            if (rows?.any { it.source_id != receipt.source_id || it.scope_id != receipt.scope_id } == true) { invalid("The server returned versions from another document."); update { it.copy(versions = it.versions.copy(loading = false)) }; return@work }
            update { it.copy(versions = if (rows == null) it.versions.copy(loading = false) else page(it.versions, rows, offset) { row -> row.id }) }
        }
    }
    fun back(): Boolean = when (state.value.screen) {
        DocumentScreen.Browse -> false
        DocumentScreen.Preview -> { editPreview(); true }
        DocumentScreen.Versions -> { update { it.copy(screen = DocumentScreen.Detail) }; true }
        else -> { detailSelection++; update { it.copy(screen = DocumentScreen.Browse, detail = null, version = null, chunks = ChatPage(), preview = null) }; true }
    }
    companion object { private const val PAGE_SIZE = 50 }
}
