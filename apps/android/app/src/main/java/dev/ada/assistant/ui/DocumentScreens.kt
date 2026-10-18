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
            if (state.screen != DocumentScreen.Browse) TextButton(onClick = { focus.clearFocus(); controller.back() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Back to documents") }
            AdaSectionHeading(when (state.screen) {
                DocumentScreen.Browse -> "Documents"; DocumentScreen.Edit -> "Import a document"; DocumentScreen.Preview -> "Review document upload"
                DocumentScreen.Detail -> "Document version"; DocumentScreen.Versions -> "Immutable versions"
            })
            Text("Imported text and Markdown are untrusted evidence. Uploading creates no explicit user assertion.", style = MaterialTheme.typography.bodyMedium)
        }
        item {
            state.validation?.let { Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.testTag("document-validation")) }
            state.fault?.let { failure -> Text(if (failure == ApiFailure.TooLarge) "The server rejected a document size or retained-data limit. Review the upload details below." else failure.message(), color = MaterialTheme.colorScheme.error) }
            state.notice?.let { Text(it, modifier = Modifier.testTag("document-notice")) }
        }
        if (state.pending != null) item { DocumentPending(state, controller) }
        when (state.screen) {
            DocumentScreen.Browse -> {
                item {
                    Text("Owned scope", style = MaterialTheme.typography.titleMedium)
                    state.scopes.items.forEach { scope ->
                        Row {
                            RadioButton(state.scopeId == scope.id, onClick = { controller.selectScope(scope.id) }, enabled = !state.saving)
                            TextButton(onClick = { controller.selectScope(scope.id) }, enabled = !state.saving, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-scope-${scope.id}")) { Text(scope.name) }
                        }
                    }
                    if (state.scopes.hasMore) TextButton(onClick = controller::loadMoreScopes, enabled = !state.scopes.loading) { Text("More scopes") }
                    Button(onClick = { controller.beginUpload() }, enabled = state.enabled && state.scopeId != null && state.pending == null && !state.saving,
                        modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-new")) { Text("Import text / Markdown") }
                    TextButton(onClick = controller::refreshUploads, enabled = !state.uploads.loading, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh upload status") }
                }
                if (state.scopes.loading || state.uploads.loading) item { CircularProgressIndicator() }
                items(state.uploads.items, key = { it.id }) { receipt -> DocumentReceiptCard(receipt) { controller.openUpload(receipt) } }
                if (state.uploads.hasMore && !state.uploads.loading) item { TextButton(onClick = controller::loadMoreUploads) { Text("More uploads") } }
                if (!state.uploads.loading && state.scopeId != null && state.uploads.items.isEmpty()) item { Text("No uploads in this scope.") }
            }
            DocumentScreen.Edit -> item {
                val draft = state.draft
                Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
                    draft.sourceId?.let { Text("New immutable version of the selected document. Previous versions remain available.") }
                    Text("UTF-8 .txt, .md or .markdown only · ${state.uploadLimit / 1024} KiB maximum on this device. PDF and compressed files are unavailable.")
                    OutlinedButton(onClick = {
                        controller.beginFileSelection()?.let { selection -> fileSelection = selection; focus.clearFocus(); picker.launch(arrayOf("text/plain", "text/markdown", "text/x-markdown", "application/octet-stream")) }
                    }, enabled = !state.saving && fileSelection == null, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-file")) { Text("Choose text / Markdown file") }
                    OutlinedTextField(draft.filename, { controller.updateDraft(draft.copy(filename = it)) }, label = { Text("Display filename") }, singleLine = true,
                        modifier = Modifier.fillMaxWidth().testTag("document-filename"))
                    Row {
                        TextButton(onClick = { controller.updateDraft(draft.copy(mediaType = "text/plain")) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (draft.mediaType == "text/plain") "Text selected" else "Text") }
                        TextButton(onClick = { controller.updateDraft(draft.copy(mediaType = "text/markdown")) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (draft.mediaType == "text/markdown") "Markdown selected" else "Markdown") }
                    }
                    OutlinedTextField(draft.text, { controller.updateDraft(draft.copy(text = it)) }, label = { Text("Exact UTF-8 document text") }, minLines = 4, maxLines = 10,
                        supportingText = { Text("File content or pasted text is preserved literally, including line endings and Unicode.") }, modifier = Modifier.fillMaxWidth().testTag("document-text"))
                    OutlinedTextField(draft.availableFrom, { controller.updateDraft(draft.copy(availableFrom = it)) }, label = { Text("Available from (optional)") }, singleLine = true,
                        supportingText = { Text("Timezone-bearing instant. Blank uses the upload time.") }, modifier = Modifier.fillMaxWidth().testTag("document-from"))
                    OutlinedTextField(draft.availableTo, { controller.updateDraft(draft.copy(availableTo = it)) }, label = { Text("Available until (optional, exclusive)") }, singleLine = true,
                        modifier = Modifier.fillMaxWidth().testTag("document-to"))
                    Button(onClick = { controller.preview(); focus.clearFocus() }, enabled = !state.saving && draft.text.isNotBlank(),
                        modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-preview")) { Text("Review upload") }
                }
            }
            DocumentScreen.Preview -> state.preview?.let { pending -> item {
                Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
                    SafeChatText(pending.filename, links = false)
                    Text("Scope: ${state.scopes.items.firstOrNull { it.id == pending.scopeId }?.name ?: "Selected owned scope"}")
                    Text("${pending.mediaType} · ${pending.rawBytes().size} exact bytes")
                    Text("Availability: ${pending.availableFrom ?: "upload time"} until ${pending.availableTo ?: "open"} (exclusive)")
                    Text("Exact imported text", style = MaterialTheme.typography.titleMedium)
                    SafeChatText(documentText(pending.rawBytes()), Modifier.testTag("document-preview-text").semantics(mergeDescendants = true) {}, links = false)
                    Text("Review this exact text and scope before upload. Embedded instructions are imported content and grant no permissions.")
                    DocumentTechnicalDetails("Scope: ${pending.scopeId}\nSource: ${pending.sourceId}\nUpload: ${pending.uploadId}\nRaw SHA-256: ${documentHash(pending.rawBytes())}", pending.uploadId, "document-preview-details")
                    Button(onClick = controller::savePreview, enabled = state.pending == null && !state.saving,
                        modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-upload")) { Text("Upload reviewed document") }
                    OutlinedButton(onClick = controller::editPreview, enabled = state.pending == null && !state.saving,
                        modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Edit before uploading") }
                }
            } }
            DocumentScreen.Detail -> {
                state.detail?.let { receipt -> item {
                    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        DocumentReceiptCard(receipt)
                        TextButton(onClick = controller::refreshDetail, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Check this version’s status") }
                        OutlinedButton(onClick = controller::showVersions, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-versions")) { Text("All immutable versions") }
                        OutlinedButton(onClick = { controller.beginUpload(reupload = true) }, enabled = state.pending == null && !state.saving,
                            modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-reupload")) { Text("Upload a new version") }
                        if (receipt.state == "failed") Text("Ingestion failed. No partial chunks from this version are searchable.")
                        if (state.detailLoading) CircularProgressIndicator()
                        state.version?.let { version ->
                            Text("Exact parsed text", style = MaterialTheme.typography.titleMedium)
                            SafeChatText(version.content, Modifier.testTag("document-version-text").semantics(mergeDescendants = true) {}, links = false)
                            DocumentTechnicalDetails("Version: ${version.id}\nText SHA-256: ${version.content_hash}\nRaw SHA-256: ${receipt.raw_hash}\nImported trust: ${version.trust_class}", version.id, "document-version-details")
                        }
                    }
                } }
                items(state.chunks.items, key = { it.id }) { chunk ->
                    Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        Text("Chunk ${chunk.ordinal} · lines ${chunk.line_start}–${chunk.line_end}")
                        SafeChatText(chunk.quote, links = false)
                        DocumentTechnicalDetails("Chunk: ${chunk.id}\nExact code-point span ${chunk.span_start}–${chunk.span_end} (end exclusive)\nQuote SHA-256: ${chunk.quote_hash}", chunk.id, "document-chunk-details-${chunk.id}")
                    } }
                }
                if (state.chunks.hasMore) item { TextButton(onClick = controller::loadMoreChunks, enabled = !state.chunks.loading) { Text("More exact chunks") } }
            }
            DocumentScreen.Versions -> {
                if (state.versions.loading) item { CircularProgressIndicator() }
                items(state.versions.items, key = { it.id }) { receipt -> DocumentReceiptCard(receipt) { controller.openUpload(receipt) } }
                if (state.versions.hasMore) item { TextButton(onClick = controller::loadMoreVersions, enabled = !state.versions.loading) { Text("More versions") } }
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
            Text("Available from ${displayInstant(receipt.available_from)}", style = MaterialTheme.typography.bodySmall)
            Text(receipt.available_to?.let { "Until ${displayInstant(it)} (exclusive)" } ?: "No availability end", style = MaterialTheme.typography.bodySmall)
            if (open != null) TextButton(onClick = open, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-open-${receipt.id}")) { Text("Open exact version") }
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
            state.pendingReceipt?.let { Text("Observed status: ${it.state}") }
            if (state.saving) CircularProgressIndicator()
            OutlinedButton(onClick = controller::checkPending, enabled = !state.saving && state.enabled,
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-check")) { Text("Check saved upload") }
            OutlinedButton(onClick = controller::resumePending, enabled = !state.saving && state.enabled,
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("document-resume")) { Text("Resume with original bytes and IDs") }
            TextButton(onClick = { discard = true }, enabled = !state.saving, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("document-discard")) { Text("Discard local upload recovery") }
        }
    }
    if (discard) AlertDialog(onDismissRequest = { discard = false }, title = { Text("Discard local upload recovery?") },
        text = { Text("Any remote upload and its versions remain. The exact input is kept for review; a future upload allocates a new ID. Review status before knowingly creating another version.") },
        confirmButton = { TextButton(onClick = { discard = false; controller.discardPending() }) { Text("Discard local recovery") } },
        dismissButton = { TextButton(onClick = { discard = false }) { Text("Keep original upload") } })
}

@Composable
private fun DocumentTechnicalDetails(text: String, identity: Any, tag: String) {
    var open by remember(identity) { mutableStateOf(false) }
    TextButton(onClick = { open = !open }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag(tag)) { Text(if (open) "Hide technical details" else "Technical details") }
    if (open) SafeChatText(text, links = false)
}
