@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.security.MessageDigest
import java.time.OffsetDateTime
import java.util.Base64
import java.util.UUID
import kotlinx.serialization.Serializable

const val MOBILE_DOCUMENT_MAX_BYTES = 64 * 1024

@Serializable data class DocumentUploadDto(
    val id: UUID, val source_id: UUID, val scope_id: UUID, val source_version_id: UUID,
    val version: Int, val filename: String, val media_type: String, val raw_hash: String,
    val raw_size: Int, val available_from: Long, val available_to: Long? = null,
    val state: String, val error_code: String? = null, val created_at: Long,
    val published_at: Long? = null,
    val input_hash: String? = null, val chunk_count: Int = 0,
    val origin: String = "imported_document", val trust_class: String = "imported_untrusted",
)
@Serializable data class DocumentVersionDto(
    val id: UUID, val source_id: UUID, val scope_id: UUID, val version: Int, val content: String,
    val content_hash: String, val trust_class: String, val created_at: Long, val upload: DocumentUploadDto,
)
@Serializable data class DocumentChunkDto(
    val id: UUID, val source_id: UUID, val source_version_id: UUID, val scope_id: UUID,
    val upload_id: UUID, val ordinal: Int, val span_start: Int, val span_end: Int, val quote: String,
    val content_hash: String, val quote_hash: String, val line_start: Int, val line_end: Int,
)
@Serializable data class DocumentCitationDto(
    val label: String, val origin: String, val trust_class: String, val scope_id: UUID, val source_id: UUID,
    val source_version_id: UUID, val upload_id: UUID, val chunk_id: UUID, val source_version: Int,
    val filename: String, val media_type: String, val raw_hash: String, val available_from: Long,
    val available_to: Long? = null, val published_at: Long, val line_start: Int, val line_end: Int,
    val evidence: EvidenceDto,
)
@Serializable data class DocumentCandidateDto(
    val chunk_id: UUID, val source_version_id: UUID, val channels: List<String>, val decision: String,
    val score: Double? = null, val term_coverage: Int? = null,
)

/** An immutable owner/scope-bound upload, never a filesystem pathname or authorization. */
@Serializable data class PendingDocument(
    val identity: SessionIdentity, val scopeId: UUID, val uploadId: UUID, val sourceId: UUID,
    val filename: String, val mediaType: String, val rawBase64: String,
    val availableFrom: String? = null, val availableTo: String? = null,
) {
    fun rawBytes(): ByteArray = Base64.getDecoder().decode(rawBase64)
    override fun toString() = "PendingDocument(redacted)"
}

fun documentHash(bytes: ByteArray): String = MessageDigest.getInstance("SHA-256").digest(bytes)
    .joinToString("") { "%02x".format(it) }

/** Strict UTF-8 preserves CRLF, combining characters and the exact imported text. */
fun documentText(bytes: ByteArray): String = Charsets.UTF_8.newDecoder()
    .onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT)
    .decode(ByteBuffer.wrap(bytes)).toString()

fun validateDocument(pending: PendingDocument) {
    try {
        require(pending.filename.codePointCount(0, pending.filename.length) in 1..120)
        require(pending.filename.isNotBlank() && pending.filename == pending.filename.trim())
        require(pending.filename.none { it.code < 32 || it.code == 127 || it in "\\/:*?\"<>|" })
        require(pending.filename !in setOf(".", "..") && !pending.filename.startsWith('.'))
        val extension = pending.filename.substringAfterLast('.', "").lowercase()
        require((pending.mediaType == "text/plain" && extension == "txt") ||
            (pending.mediaType == "text/markdown" && extension in setOf("md", "markdown")))
        require(pending.rawBase64.length <= (MOBILE_DOCUMENT_MAX_BYTES + 2) / 3 * 4)
        val bytes = pending.rawBytes()
        require(bytes.size in 1..MOBILE_DOCUMENT_MAX_BYTES)
        require(Base64.getEncoder().encodeToString(bytes) == pending.rawBase64)
        val text = documentText(bytes)
        require(text.isNotBlank() && text.none { it == '\u0000' })
        listOfNotNull(pending.availableFrom, pending.availableTo).forEach { require(normalizeUtcMillis(it) == it) }
        if (pending.availableFrom != null && pending.availableTo != null) {
            require(OffsetDateTime.parse(pending.availableFrom).toInstant() < OffsetDateTime.parse(pending.availableTo).toInstant())
        }
    } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
}

fun verifyDocumentReceipt(pending: PendingDocument, receipt: DocumentUploadDto): Boolean = runCatching {
    validateDocument(pending)
    require(receipt.id == pending.uploadId && receipt.source_id == pending.sourceId && receipt.scope_id == pending.scopeId)
    require(receipt.filename == pending.filename && receipt.media_type == pending.mediaType)
    val bytes = pending.rawBytes()
    require(receipt.raw_size == bytes.size && receipt.raw_hash == documentHash(bytes))
    require(receipt.version > 0 && receipt.state in setOf("processing", "ready", "failed"))
    require(receipt.origin == "imported_document" && receipt.trust_class == "imported_untrusted")
    require(validDocumentState(receipt))
    pending.availableFrom?.let { require(receipt.available_from == OffsetDateTime.parse(it).toInstant().toEpochMilli()) }
    require(receipt.available_to == pending.availableTo?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() })
    true
}.getOrDefault(false)

private fun validDocumentState(receipt: DocumentUploadDto): Boolean =
    when (receipt.state) {
        "ready" -> receipt.published_at != null && receipt.error_code == null && receipt.chunk_count in 1..512
        "processing" -> receipt.published_at == null && receipt.error_code == null && receipt.chunk_count == 0
        "failed" -> receipt.published_at == null && !receipt.error_code.isNullOrBlank() && receipt.chunk_count == 0
        else -> false
    }

fun verifyDocumentVersion(version: DocumentVersionDto, receipt: DocumentUploadDto): Boolean = runCatching {
    require(version.id == receipt.source_version_id && version.source_id == receipt.source_id && version.scope_id == receipt.scope_id)
    require(version.version == receipt.version && version.upload == receipt && receipt.state == "ready")
    require(validDocumentState(receipt) && version.content_hash == receipt.raw_hash)
    require(version.trust_class == "imported_untrusted" && version.content_hash == documentHash(version.content.toByteArray(Charsets.UTF_8)))
    true
}.getOrDefault(false)

fun verifyDocumentChunk(chunk: DocumentChunkDto, version: DocumentVersionDto): Boolean = runCatching {
    require(chunk.source_version_id == version.id && chunk.source_id == version.source_id && chunk.scope_id == version.scope_id && chunk.upload_id == version.upload.id)
    require(chunk.content_hash == version.content_hash && chunk.span_start >= 0 && chunk.span_end > chunk.span_start)
    val start = codePointToUtf16Offset(version.content, chunk.span_start)
    val end = codePointToUtf16Offset(version.content, chunk.span_end)
    require(version.content.substring(start, end) == chunk.quote && documentHash(chunk.quote.toByteArray(Charsets.UTF_8)) == chunk.quote_hash)
    require(chunk.line_start == version.content.substring(0, start).count { it == '\n' } + 1)
    require(chunk.line_end == chunk.line_start + chunk.quote.dropLast(1).count { it == '\n' })
    true
}.getOrDefault(false)
