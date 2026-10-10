@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.io.IOException
import java.util.Base64
import java.util.UUID
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

private class DocumentDisk : SessionDisk {
    var bytes: ByteArray? = null
    var failWrite = false
    override fun read(maxBytes: Int) = bytes?.copyOf()?.also { require(it.size <= maxBytes) }
    override fun write(bytes: ByteArray) { if (failWrite) throw IOException("Synthetic failure"); this.bytes = bytes.copyOf() }
    override fun delete() { bytes = null }
}
private class DocumentKeys : SessionKeys {
    var key: SecretKey? = null
    override fun existing() = key
    override fun create() = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey().also { key = it }
    override fun delete() { key = null }
}
@Serializable private data class BeforeDocuments(
    val version: Int, val credential: StoredCredential, val pending: PendingMessage?, val memoryPending: PendingMemory? = null,
)

class DocumentJournalTest {
    private val identity = SessionIdentity("https://ada.example/", UUID.randomUUID())
    private val scope = UUID.randomUUID()
    private val exact = "Synthetic 😀 e\u0301\r\nதமிழ் <script>untrusted</script>  "
    private fun reservation(text: String = exact) = PendingDocument(identity, scope, UUID.randomUUID(), UUID.randomUUID(),
        "synthetic.md", "text/markdown", Base64.getEncoder().encodeToString(text.toByteArray(Charsets.UTF_8)),
        "2026-10-09T00:00:00Z", "2026-11-09T00:00:00Z")
    private fun store(disk: DocumentDisk, keys: DocumentKeys) = EncryptedSessionStore(disk, AesGcmSessionCipher(keys), false)
    private suspend fun initialize(store: SessionStore) = store.saveCredential(StoredCredential(identity, "synthetic-document-token"))
    private suspend fun rejected(block: suspend () -> Unit) {
        try { block(); fail("Unsafe document transition accepted") }
        catch (error: SessionStorageException) { assertNull(error.cause); assertFalse(error.toString().contains(exact)) }
    }

    @Test fun exactEncryptedReservationSurvivesRestartAndCannotBeOverwritten() = runTest {
        val disk = DocumentDisk(); val keys = DocumentKeys(); val store = store(disk, keys); val pending = reservation()
        initialize(store); store.saveDocumentPending(pending)
        assertEquals(pending, store(disk, keys).documentPending(identity))
        assertEquals(exact, documentText(store(disk, keys).documentPending(identity)!!.rawBytes()))
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains("Synthetic")); assertFalse(pending.toString().contains(exact))
        store.saveDocumentPending(pending)
        rejected { store.saveDocumentPending(pending.copy(filename = "changed.md")) }
        rejected { store.saveDocumentPending(pending.copy(rawBase64 = Base64.getEncoder().encodeToString("Changed".toByteArray()))) }
        rejected { store.saveDocumentPending(pending.copy(uploadId = UUID.randomUUID())) }
        assertEquals(pending, store.documentPending(identity))
    }
    @Test fun allThreeJournalsCoexistAndScopedCleanupCannotEraseAnotherReservation() = runTest {
        val disk = DocumentDisk(); val keys = DocumentKeys(); val store = store(disk, keys); initialize(store)
        val chat = PendingMessage(identity, UUID.randomUUID(), ChatInputDto(UUID.randomUUID(), "Synthetic chat"))
        val memory = PendingMemory(MemoryReservation(identity, scope, UUID.randomUUID(), note = NoteInputDto(UUID.randomUUID(), "Synthetic note"), subject = "Project", predicate = "palette", value = "Blue", kind = "fact"))
        val document = reservation(); store.savePending(chat); store.saveMemoryPending(memory); store.saveDocumentPending(document)
        store.removeDocumentPending(identity.copy(owner = UUID.randomUUID()), document.uploadId)
        store.removeDocumentPending(identity, UUID.randomUUID())
        assertEquals(document, store.documentPending(identity)); assertEquals(chat, store.pending(identity)); assertEquals(memory, store.memoryPending(identity))
        store.removeDocumentPending(identity, document.uploadId)
        assertNull(store.documentPending(identity)); assertEquals(chat, store.pending(identity)); assertEquals(memory, store.memoryPending(identity))
    }
    @Test fun v1AndV2RecordsReadAndUpgradeWithoutLosingEarlierJournals() = runTest {
        for (version in 1..2) {
            val disk = DocumentDisk(); val keys = DocumentKeys(); val store = store(disk, keys)
            val chat = PendingMessage(identity, UUID.randomUUID(), ChatInputDto(UUID.randomUUID(), "Synthetic older chat"))
            val memory = if (version == 2) PendingMemory(MemoryReservation(identity, scope, UUID.randomUUID(), note = NoteInputDto(UUID.randomUUID(), "Synthetic note"), subject = "Project", predicate = "color", value = "Blue", kind = "fact")) else null
            val before = BeforeDocuments(version, StoredCredential(identity, "synthetic-document-token"), chat, memory)
            disk.bytes = AesGcmSessionCipher(keys).encrypt(adaJson.encodeToString(before).toByteArray())
            assertEquals(chat, store.pending(identity)); assertEquals(memory, store.memoryPending(identity))
            assertNull(store.documentPending(identity)); val pending = reservation(); store.saveDocumentPending(pending)
            assertEquals(chat, store(disk, keys).pending(identity)); assertEquals(memory, store(disk, keys).memoryPending(identity))
            assertEquals(pending, store(disk, keys).documentPending(identity))
        }
    }
    @Test fun sameOwnerTokenRotationRetainsUploadWhileOwnerServerSwitchAndLogoutClearIt() = runTest {
        val disk = DocumentDisk(); val keys = DocumentKeys(); val store = store(disk, keys); val pending = reservation()
        initialize(store); store.saveDocumentPending(pending)
        store.saveCredential(StoredCredential(identity, "synthetic-rotation")); assertEquals(pending, store.documentPending(identity))
        val other = identity.copy(owner = UUID.randomUUID())
        assertNull(store.documentPending(other)); rejected { store.saveDocumentPending(pending.copy(identity = other)) }
        store.saveCredential(StoredCredential(other, "synthetic-other-token")); assertNull(store.documentPending(other))
        store.saveDocumentPending(pending.copy(identity = other))
        store.saveCredential(StoredCredential(other.copy(server = "https://other.example/"), "synthetic-other-server"))
        assertNull(store.documentPending(other)); store.clear(); assertNull(disk.bytes); assertNull(keys.key)
    }
    @Test fun malformedEncodingHostileNamesTypesBoundsAndIntervalsNeverCommit() = runTest {
        val disk = DocumentDisk(); val keys = DocumentKeys(); val store = store(disk, keys); initialize(store); val pending = reservation()
        val invalid = listOf(
            pending.copy(filename = "../private.md"), pending.copy(filename = "C:\\private.md"), pending.copy(filename = "hidden.html"),
            pending.copy(mediaType = "application/pdf"), pending.copy(filename = "bad\nname.md"),
            pending.copy(rawBase64 = Base64.getEncoder().encodeToString(byteArrayOf(0xC3.toByte(), 0x28))),
            pending.copy(rawBase64 = Base64.getEncoder().encodeToString("x\u0000y".toByteArray())),
            pending.copy(rawBase64 = Base64.getEncoder().encodeToString(ByteArray(MOBILE_DOCUMENT_MAX_BYTES + 1) { 65 })),
            pending.copy(availableFrom = "2026-10-09T00:00:00"), pending.copy(availableTo = pending.availableFrom),
        )
        for (item in invalid) rejected { store.saveDocumentPending(item) }
        assertNull(store.documentPending(identity))
    }
    @Test fun failedDiskCommitPreservesOriginalJournalAndReceiptVerificationChecksExactInput() = runTest {
        val disk = DocumentDisk(); val keys = DocumentKeys(); val store = store(disk, keys); initialize(store)
        val pending = reservation(); disk.failWrite = true; rejected { store.saveDocumentPending(pending) }
        assertNull(store.documentPending(identity)); disk.failWrite = false; store.saveDocumentPending(pending)
        val receipt = DocumentUploadDto(pending.uploadId, pending.sourceId, scope, UUID.randomUUID(), 1, pending.filename,
            pending.mediaType, documentHash(pending.rawBytes()), pending.rawBytes().size, 1791504000000L, 1794182400000L,
            "ready", created_at = 1791504000000L, published_at = 1791504000001L, chunk_count = 1)
        assertTrue(verifyDocumentReceipt(pending, receipt))
        assertFalse(verifyDocumentReceipt(pending, receipt.copy(raw_hash = "0".repeat(64))))
        assertFalse(verifyDocumentReceipt(pending, receipt.copy(state = "future_state")))
        assertFalse(verifyDocumentReceipt(pending, receipt.copy(scope_id = UUID.randomUUID())))
        assertFalse(verifyDocumentReceipt(pending, receipt.copy(filename = "changed.md")))
    }
    @Test fun receiptPublicationStatesMustBeCompleteBeforeRecoveryCleanup() {
        val pending = reservation()
        val ready = DocumentUploadDto(pending.uploadId, pending.sourceId, scope, UUID.randomUUID(), 1, pending.filename,
            pending.mediaType, documentHash(pending.rawBytes()), pending.rawBytes().size, 1791504000000L, 1794182400000L,
            "ready", created_at = 1791504000000L, published_at = 1791504000001L, chunk_count = 1)
        assertTrue(verifyDocumentReceipt(pending, ready))
        for (invalid in listOf(ready.copy(published_at = null), ready.copy(chunk_count = 0), ready.copy(error_code = "document_processing_failed"),
            ready.copy(state = "processing"), ready.copy(state = "failed", published_at = null, chunk_count = 0))) {
            assertFalse(verifyDocumentReceipt(pending, invalid))
        }
        assertTrue(verifyDocumentReceipt(pending, ready.copy(state = "processing", published_at = null, chunk_count = 0)))
        assertTrue(verifyDocumentReceipt(pending, ready.copy(state = "failed", published_at = null, chunk_count = 0, error_code = "document_processing_failed")))
    }
    @Test fun validlyHashedReplacementTextCannotMasqueradeAsTheUploadedVersion() {
        val pending = reservation()
        val receipt = DocumentUploadDto(pending.uploadId, pending.sourceId, scope, UUID.randomUUID(), 1, pending.filename,
            pending.mediaType, documentHash(pending.rawBytes()), pending.rawBytes().size, 1791504000000L, 1794182400000L,
            "ready", created_at = 1791504000000L, published_at = 1791504000001L, chunk_count = 1)
        val replacement = "Other validly hashed synthetic text"
        val version = DocumentVersionDto(receipt.source_version_id, receipt.source_id, scope, 1, replacement,
            documentHash(replacement.toByteArray()), "imported_untrusted", receipt.created_at, receipt)
        assertFalse(verifyDocumentVersion(version, receipt))
    }
}
