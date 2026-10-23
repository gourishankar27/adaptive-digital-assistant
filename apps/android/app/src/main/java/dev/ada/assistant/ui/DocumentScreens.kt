package dev.ada.assistant.ui

import android.provider.OpenableColumns
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import java.io.ByteArrayOutputStream
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun DocumentScreens(controller: DocumentController) {
    val state by controller.state.collectAsStateWithLifecycle()
    val focus = LocalFocusManager.current
    val context = LocalContext.current
    val work = rememberCoroutineScope()
    var fileSelection by remember(controller) { mutableStateOf<DocumentFileSelection?>(null) }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        val selection = fileSelection
        if (uri != null && selection != null && controller.isFileSelectionCurrent(selection)) work.launch {
            val selected = withContext(Dispatchers.IO) {
                runCatching {
                    val resolver = context.contentResolver
                    val name = resolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE), null, null, null)?.use { cursor ->
                        require(cursor.moveToFirst())
                        val sizeColumn = cursor.getColumnIndex(OpenableColumns.SIZE)
                        if (sizeColumn >= 0 && !cursor.isNull(sizeColumn)) require(cursor.getLong(sizeColumn) <= selection.limit)
                        cursor.getString(cursor.getColumnIndexOrThrow(OpenableColumns.DISPLAY_NAME))
                    } ?: error("Missing display name")
                    val bytes = resolver.openInputStream(uri)?.use { stream ->
                        val result = ByteArrayOutputStream(); val buffer = ByteArray(4096)
                        while (true) {
                            val count = stream.read(buffer); if (count < 0) break
                            require(result.size() + count <= selection.limit); result.write(buffer, 0, count)
                        }
                        result.toByteArray()
                    } ?: error("Missing stream")
                    name to bytes
                }.getOrNull()
            }
            if (selected != null) controller.chooseFile(selection, selected.first, selected.second) else controller.fileFailed(selection)
            if (fileSelection === selection) fileSelection = null
        } else fileSelection = null
    }
    LazyColumn(Modifier.fillMaxSize().testTag("documents-list"),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium),
        verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item {
            if (state.screen != DocumentScreen.Browse) AdaTextButton(onClick = { focus.clearFocus(); controller.back() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Back to documents") }
            AdaSectionHeading(when (state.screen) {
                DocumentScreen.Browse -> "Documents"; DocumentScreen.Edit -> "Import a document"; DocumentScreen.Preview -> "Review document upload"
                DocumentScreen.Detail -> "Document version"; DocumentScreen.Versions -> "Immutable versions"
            })
            Text("Imported text and Markdown are untrusted evidence. Uploading creates no explicit user assertion.", style = MaterialTheme.typography.bodyMedium)
        }
        item {
            state.validation?.let { AdaNotice(it, Modifier.testTag("document-validation"), error = true) }
            state.fault?.let { failure -> AdaNotice(if (failure == ApiFailure.TooLarge) "The server rejected a document size or retained-data limit. Review the upload details below." else failure.message(), error = true) }
            state.notice?.let { AdaNotice(it, Modifier.testTag("document-notice")) }
        }
        if (state.pending != null) item { DocumentPending(state, controller) }
        when (state.screen) {
            DocumentScreen.Browse -> {
                item {
                    Text("Owned scope", style = MaterialTheme.typography.titleMedium)
                    state.scopes.items.forEach { scope ->
                        AdaChoice(state.scopeId == scope.id, scope.name, { controller.selectScope(scope.id) }, Modifier.testTag("document-scope-${scope.id}"), enabled = !state.saving)
                    }
                    if (state.scopes.hasMore) AdaTextButton(onClick = controller::loadMoreScopes, enabled = !state.scopes.loading) { Text("More scopes") }
                    AdaButton(onClick = { controller.beginUpload() }, enabled = state.enabled && state.scopeId != null && state.pending == null && !state.saving,
                        modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-new")) { Text(if(state.pdfEnabled) "Import document" else "Import text / Markdown") }
                    AdaTextButton(onClick = controller::refreshUploads, enabled = !state.uploads.loading, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh upload status") }
                }
                if (state.scopes.loading || state.uploads.loading) item { AdaLoading("Checking document status") }
                items(state.uploads.items, key = { it.id }) { receipt -> DocumentReceiptCard(receipt) { controller.openUpload(receipt) } }
                if (state.uploads.hasMore && !state.uploads.loading) item { AdaTextButton(onClick = controller::loadMoreUploads) { Text("More uploads") } }
                if (!state.uploads.loading && state.scopeId != null && state.uploads.items.isEmpty()) item { Text("No uploads in this scope.") }
            }
            DocumentScreen.Edit -> item {
                val draft = state.draft
                Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
                    draft.sourceId?.let { Text("New immutable version of the selected document. Previous versions remain available.") }
                    Text("UTF-8 text/Markdown${if (state.pdfEnabled) " or text PDF" else ""} · ${state.uploadLimit / 1024} KiB maximum. Scanned PDFs/OCR and archives are unavailable.")
                    AdaOutlinedButton(onClick = {
                        controller.beginFileSelection()?.let { selection -> fileSelection = selection; focus.clearFocus(); picker.launch(if(state.pdfEnabled) arrayOf("application/pdf", "text/plain", "text/markdown") else arrayOf("text/plain", "text/markdown", "text/x-markdown", "application/octet-stream")) }
                    }, enabled = !state.saving && fileSelection == null, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-file")) { Text(if(state.pdfEnabled) "Choose text / Markdown / PDF file" else "Choose text / Markdown file") }
                    OutlinedTextField(draft.filename, { controller.updateDraft(draft.copy(filename = it)) }, label = { Text("Display filename") }, singleLine = true,
                        modifier = Modifier.fillMaxWidth().testTag("document-filename"))
                    Row {
                        AdaChoiceChip(draft.mediaType == "text/plain", "Text", { controller.updateDraft(draft.copy(mediaType = "text/plain")) })
                        AdaChoiceChip(draft.mediaType == "text/markdown", "Markdown", { controller.updateDraft(draft.copy(mediaType = "text/markdown")) })
                    }
                    if(draft.mediaType != "application/pdf") OutlinedTextField(draft.text, { controller.updateDraft(draft.copy(text = it)) }, label = { Text("Exact UTF-8 document text") }, minLines = 4, maxLines = 10,
                        supportingText = { Text("File content or pasted text is preserved literally, including line endings and Unicode.") }, modifier = Modifier.fillMaxWidth().testTag("document-text"))
                    OutlinedTextField(draft.availableFrom, { controller.updateDraft(draft.copy(availableFrom = it)) }, label = { Text("Available from (optional)") }, singleLine = true,
                        supportingText = { Text("Timezone-bearing instant. Blank uses the upload time.") }, modifier = Modifier.fillMaxWidth().testTag("document-from"))
                    OutlinedTextField(draft.availableTo, { controller.updateDraft(draft.copy(availableTo = it)) }, label = { Text("Available until (optional, exclusive)") }, singleLine = true,
                        modifier = Modifier.fillMaxWidth().testTag("document-to"))
                    AdaButton(onClick = { controller.preview(); focus.clearFocus() }, enabled = !state.saving && (draft.text.isNotBlank() || draft.binaryBase64 != null),
                        modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-preview")) { Text("Review upload") }
                }
            }
            DocumentScreen.Preview -> state.preview?.let { pending -> item {
                Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
                    SafeChatText(pending.filename, links = false)
                    Text("Scope: ${state.scopes.items.firstOrNull { it.id == pending.scopeId }?.name ?: "Selected owned scope"}")
                    Text("${pending.mediaType} · ${pending.rawBytes().size} exact bytes")
                    Text("Availability: ${pending.availableFrom ?: "upload time"} until ${pending.availableTo ?: "open"} (exclusive)")
                    Text(if(pending.mediaType=="application/pdf") "Selected original PDF" else "Exact imported text", style = MaterialTheme.typography.titleMedium)
                    if(pending.mediaType == "application/pdf") Text("Exact binary PDF selected. Original bytes are retained; text/page extraction happens after upload. No OCR.",Modifier.testTag("document-preview-text")) else SafeChatText(documentText(pending.rawBytes()), Modifier.testTag("document-preview-text").semantics(mergeDescendants = true) {}, links = false)
                    Text("Review ${if (pending.mediaType == "application/pdf") "the selected file" else "this exact text"} and scope before upload. Embedded instructions are imported content and grant no permissions.")
                    DocumentTechnicalDetails("Scope: ${pending.scopeId}\nSource: ${pending.sourceId}\nUpload: ${pending.uploadId}\nRaw SHA-256: ${documentHash(pending.rawBytes())}", pending.uploadId, "document-preview-details")
                    AdaButton(onClick = controller::savePreview, enabled = state.pending == null && !state.saving,
                        modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-upload")) { Text("Upload reviewed document") }
                    AdaOutlinedButton(onClick = controller::editPreview, enabled = state.pending == null && !state.saving,
                        modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Edit before uploading") }
                }
            } }
            DocumentScreen.Detail -> {
                state.detail?.let { receipt -> item {
                    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        DocumentReceiptCard(receipt)
                        AdaTextButton(onClick = controller::refreshDetail, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Check this version’s status") }
                        AdaOutlinedButton(onClick = controller::showVersions, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-versions")) { Text("All immutable versions") }
                        AdaOutlinedButton(onClick = { controller.beginUpload(reupload = true) }, enabled = state.pending == null && !state.saving,
                            modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-reupload")) { Text("Upload a new version") }
                        if (receipt.state == "failed") Text("Ingestion failed. No partial chunks from this version are searchable.")
                        if (state.detailLoading) AdaLoading("Checking document status")
                        state.version?.let { version ->
                            version.extraction?.let { Text("${it.pages.size} extracted PDF pages · OCR disabled"); it.warnings.forEach { warning -> Text(warning) } }
                            Text("Exact parsed text", style = MaterialTheme.typography.titleMedium)
                            SafeChatText(version.content, Modifier.testTag("document-version-text").semantics(mergeDescendants = true) {}, links = false)
                            DocumentTechnicalDetails("Version: ${version.id}\nText SHA-256: ${version.content_hash}\nRaw SHA-256: ${receipt.raw_hash}\nImported trust: ${version.trust_class}", version.id, "document-version-details")
                        }
                    }
                } }
                items(state.chunks.items, key = { it.id }) { chunk ->
                    Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        Text("${chunk.pdf?.let { "PDF page ${it.page} · " } ?: ""}Chunk ${chunk.ordinal} · extracted lines ${chunk.line_start}–${chunk.line_end}")
                        SafeChatText(chunk.quote, links = false)
                        DocumentTechnicalDetails("Chunk: ${chunk.id}\nExact code-point span ${chunk.span_start}–${chunk.span_end} (end exclusive)\nQuote SHA-256: ${chunk.quote_hash}", chunk.id, "document-chunk-details-${chunk.id}")
                    } }
                }
                if (state.chunks.hasMore) item { AdaTextButton(onClick = controller::loadMoreChunks, enabled = !state.chunks.loading) { Text("More exact chunks") } }
            }
            DocumentScreen.Versions -> {
                if (state.versions.loading) item { AdaLoading("Checking document status") }
                items(state.versions.items, key = { it.id }) { receipt -> DocumentReceiptCard(receipt) { controller.openUpload(receipt) } }
                if (state.versions.hasMore) item { AdaTextButton(onClick = controller::loadMoreVersions, enabled = !state.versions.loading) { Text("More versions") } }
            }
        }
    }
}

@Composable
private fun DocumentReceiptCard(receipt: DocumentUploadDto, open: (() -> Unit)? = null) {
    Card(Modifier.fillMaxWidth().testTag("document-receipt-${receipt.id}")) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            SafeChatText(receipt.filename, links = false)
            Text("Imported document · version ${receipt.version} · ${when (receipt.state) { "ready" -> "Ready"; "processing" -> "Processing"; "failed" -> "Failed"; else -> "Unrecognized state" }}")
            Text("${receipt.raw_size} bytes · ${receipt.chunk_count} chunks", style = MaterialTheme.typography.bodySmall)
            if(receipt.state=="failed") Text(documentFailureText(receipt.error_code))
            Text("Available from ${displayInstant(receipt.available_from)}", style = MaterialTheme.typography.bodySmall)
            Text(receipt.available_to?.let { "Until ${displayInstant(it)} (exclusive)" } ?: "No availability end", style = MaterialTheme.typography.bodySmall)
            if (open != null) AdaTextButton(onClick = open, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-open-${receipt.id}")) { Text("Open exact version") }
        }
    }
}

@Composable
private fun DocumentPending(state: DocumentState, controller: DocumentController) {
    val pending = state.pending ?: return
    var discard by remember(pending.uploadId) { mutableStateOf(false) }
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text("Saved document upload", style = MaterialTheme.typography.titleMedium)
            SafeChatText(pending.filename, links = false)
            Text("Original scope: ${state.scopes.items.firstOrNull { it.id == pending.scopeId }?.name ?: "Saved owned scope"}")
            state.pendingReceipt?.let { Text("Observed status: ${statusLabel(it.state)}");if(it.state=="failed")Text(documentFailureText(it.error_code)) }
            if (state.saving) AdaLoading("Checking document status")
            AdaOutlinedButton(onClick = controller::checkPending, enabled = !state.saving && state.enabled,
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-check")) { Text("Check saved upload") }
            AdaOutlinedButton(onClick = controller::resumePending, enabled = !state.saving && state.enabled && state.pendingReceipt?.state!="failed",
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-resume")) { Text("Resume with original bytes and IDs") }
            AdaTextButton(onClick = { discard = true }, enabled = !state.saving, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-discard")) { Text("Discard local upload recovery") }
        }
    }
    if (discard) AlertDialog(onDismissRequest = { discard = false }, title = { Text("Discard local upload recovery?") },
        text = { Text("Any remote upload and its versions remain. The exact input is kept for review; a future upload allocates a new ID. Review status before knowingly creating another version.") },
        confirmButton = { AdaTextButton(onClick = { discard = false; controller.discardPending() }) { Text("Discard local recovery") } },
        dismissButton = { AdaTextButton(onClick = { discard = false }) { Text("Keep original upload") } })
}

private fun documentFailureText(code:String?):String=when(code) {
    "pdf_ocr_required"->"This PDF has a scanned or blank page. OCR is unavailable; choose a PDF with selectable text on every page."
    "pdf_encrypted"->"Encrypted PDFs are unsupported. Choose an unencrypted text PDF."
    "pdf_active_content"->"This PDF contains unsupported links, forms, attachments or active content. Choose a plain text PDF."
    "pdf_page_limit","pdf_text_limit"->"This PDF exceeds the page or extracted-text limit. Choose a smaller section."
    "pdf_parser_busy"->"The PDF parser was busy. This attempt was retained as failed; review it before starting a new upload."
    else->"This version could not be imported safely. Its original bytes are retained and no partial text is searchable. Choose corrected bytes in an explicitly new upload."
}

@Composable
private fun DocumentTechnicalDetails(text: String, identity: Any, tag: String) {
    var open by remember(identity) { mutableStateOf(false) }
    AdaTextButton(onClick = { open = !open }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag(tag)) { Text(if (open) "Hide technical details" else "Technical details") }
    if (open) SafeChatText(text, links = false)
}
