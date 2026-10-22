package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID

enum class DocumentScreen { Browse, Edit, Preview, Detail, Versions }
class DocumentFileSelection internal constructor(
    internal val identity: SessionIdentity, internal val scope: UUID,
    internal val sessionEpoch: Long, internal val editEpoch: Long, val limit: Int,
) { override fun toString() = "DocumentFileSelection(redacted)" }
data class DocumentDraft(
    val filename: String = "document.txt", val mediaType: String = "text/plain", val text: String = "",
    val availableFrom: String = "", val availableTo: String = "", val sourceId: UUID? = null,
    val binaryBase64: String? = null,
) { override fun toString() = "DocumentDraft(redacted)" }
data class DocumentState(
    val pdfEnabled: Boolean = false,
    val enabled: Boolean = false, val uploadLimit: Int = 0, val screen: DocumentScreen = DocumentScreen.Browse,
    val scopes: ChatPage<ScopeDto> = ChatPage(), val scopeId: UUID? = null,
    val uploads: ChatPage<DocumentUploadDto> = ChatPage(), val versions: ChatPage<DocumentUploadDto> = ChatPage(),
    val detail: DocumentUploadDto? = null, val version: DocumentVersionDto? = null,
    val chunks: ChatPage<DocumentChunkDto> = ChatPage(), val detailLoading: Boolean = false,
    val draft: DocumentDraft = DocumentDraft(), val preview: PendingDocument? = null,
    val pending: PendingDocument? = null, val pendingReceipt: DocumentUploadDto? = null, val saving: Boolean = false,
    val validation: String? = null, val fault: ApiFailure? = null, val notice: String? = null,
) { override fun toString() = "DocumentState(redacted)" }
