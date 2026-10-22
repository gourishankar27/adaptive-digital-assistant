@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.io.IOException
import java.security.MessageDigest
import java.util.UUID
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

private class JournalDisk : SessionDisk {
    var bytes: ByteArray? = null
    var failWrite = false
    override fun read(maxBytes: Int): ByteArray? = bytes?.copyOf()?.also {
        if (it.size > maxBytes) throw IOException("Synthetic bound exceeded")
    }
    override fun write(bytes: ByteArray) {
        if (failWrite) throw IOException("Synthetic commit failure")
        this.bytes = bytes.copyOf()
    }
    override fun delete() { bytes = null }
}
private class JournalKeys : SessionKeys {
    var key: SecretKey? = null
    override fun existing() = key
    override fun create(): SecretKey = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey().also { key = it }
    override fun delete() { key = null }
}
@Serializable private data class LegacyJournalRecord(
    val version: Int = 1, val credential: StoredCredential, val pending: PendingMessage,
)

class MemoryJournalTest {
    private val identity = SessionIdentity("https://ada.example/", UUID.fromString("00000000-0000-4000-8000-000000000001"))
    private val scope = UUID.fromString("00000000-0000-4000-8000-000000000002")
    private val claimId = UUID.fromString("00000000-0000-4000-8000-000000000003")
    private val sourceId = UUID.fromString("00000000-0000-4000-8000-000000000004")
    private val versionId = UUID.fromString("00000000-0000-4000-8000-000000000005")
    private val text = "Synthetic 😀 evidence\r\n e\u0301 தமிழ்  "
    private fun hash(content: String) = MessageDigest.getInstance("SHA-256").digest(content.toByteArray(Charsets.UTF_8))
        .joinToString("") { "%02x".format(it) }
    private fun source(content: String = text) = SourceVersionDto(versionId, sourceId, scope, 1, content, hash(content), "user_explicit", 1000L)
    private fun reserved(note: String = text) = PendingMemory(MemoryReservation(identity, scope, claimId,
        note = NoteInputDto(sourceId, note), subject = "user", predicate = "language", value = "Tamil", kind = "preference"))
    private fun chat() = PendingMessage(identity, UUID.randomUUID(), ChatInputDto(UUID.randomUUID(), "Synthetic original chat"))
    private fun store(disk: JournalDisk, keys: JournalKeys) = EncryptedSessionStore(disk, AesGcmSessionCipher(keys), false)
    private suspend fun initialize(store: SessionStore) = store.saveCredential(StoredCredential(identity, "synthetic-journal-token"))
    private suspend fun rejected(expected: SessionStoreFailure, block: suspend () -> Unit) {
        try { block(); fail("Unsafe journal transition accepted") } catch (error: SessionStorageException) {
            assertEquals(expected, error.failure)
            assertNull(error.cause)
            assertFalse(error.toString().contains(text))
            assertFalse(error.toString().contains("synthetic-journal-token"))
        }
    }

    @Test fun noteStageSurvivesRecreationAndCannotReplaceBoundInputOrCommittedSource() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys)
        initialize(store); store.saveMemoryPending(reserved())
        assertEquals(reserved(), store(disk, keys).memoryPending(identity))
        assertFalse(checkNotNull(disk.bytes).toString(Charsets.UTF_8).contains("Synthetic"))
        assertFalse(reserved().toString().contains("Synthetic"))
        assertFalse(reserved().reservation.toString().contains("Synthetic"))
        val completedNote = reserved().copy(source = source())
        store.saveMemoryPending(completedNote)
        assertEquals(completedNote, store(disk, keys).memoryPending(identity))
        store.saveMemoryPending(completedNote) // identical replay is safe
        rejected(SessionStoreFailure.PendingConflict) { store.saveMemoryPending(reserved()) }
        rejected(SessionStoreFailure.PendingConflict) { store.saveMemoryPending(completedNote.copy(reservation = completedNote.reservation.copy(value = "Changed"))) }
        rejected(SessionStoreFailure.PendingConflict) { store.saveMemoryPending(completedNote.copy(source = source().copy(id = UUID.randomUUID()))) }
        rejected(SessionStoreFailure.PendingConflict) { store.saveMemoryPending(completedNote.copy(reservation = completedNote.reservation.copy(claimId = UUID.randomUUID()))) }
        assertEquals(completedNote, store.memoryPending(identity))
    }

    @Test fun twoIndependentJournalsPersistTogetherAndScopedRemovalCannotEraseAnotherWrite() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); val chat = chat()
        initialize(store); store.savePending(chat); store.saveMemoryPending(reserved().copy(source = source()))
        store.removeMemoryPending(identity.copy(owner = UUID.randomUUID()), claimId)
        store.removeMemoryPending(identity, UUID.randomUUID())
        assertNotNull(store.memoryPending(identity)); assertEquals(chat, store.pending(identity))
        store.removePending(identity, chat.body.request_id)
        assertNull(store.pending(identity)); assertNotNull(store.memoryPending(identity))
        store.savePending(chat); store.removeMemoryPending(identity, claimId)
        assertNull(store.memoryPending(identity)); assertEquals(chat, store.pending(identity))
    }

    @Test fun v1EncryptedCredentialAndChatUpgradeWithoutLosingPendingInput() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); val chat = chat()
        val old = LegacyJournalRecord(credential = StoredCredential(identity, "synthetic-v1-token"), pending = chat)
        disk.bytes = AesGcmSessionCipher(keys).encrypt(adaJson.encodeToString(old).toByteArray(Charsets.UTF_8))
        assertEquals(chat, store.pending(identity)); assertNull(store.memoryPending(identity))
        store.saveMemoryPending(reserved())
        assertEquals(chat, store(disk, keys).pending(identity)); assertEquals(reserved(), store(disk, keys).memoryPending(identity))
        val plaintext = AesGcmSessionCipher(keys).decrypt(checkNotNull(disk.bytes))
        try { assertTrue(plaintext.toString(Charsets.UTF_8).contains("\"version\":18")) } finally { plaintext.fill(0) }
    }

    @Test fun rotationRetainsBothJournalsButIdentitySwitchAndLogoutClearThem() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); val chat = chat()
        initialize(store); store.savePending(chat); store.saveMemoryPending(reserved())
        store.saveCredential(StoredCredential(identity, "synthetic-rotated-token"))
        assertEquals(chat, store.pending(identity)); assertEquals(reserved(), store.memoryPending(identity))
        val other = identity.copy(owner = UUID.randomUUID())
        assertNull(store.memoryPending(other))
        rejected(SessionStoreFailure.IdentityMismatch) { store.saveMemoryPending(reserved().copy(reservation = reserved().reservation.copy(identity = other))) }
        store.saveCredential(StoredCredential(other, "synthetic-other-token"))
        assertNull(store.pending(other)); assertNull(store.memoryPending(other)); assertNull(store.memoryPending(identity))
        store.saveMemoryPending(reserved().copy(reservation = reserved().reservation.copy(identity = other)))
        val otherServer = other.copy(server = "https://other.example/")
        store.saveCredential(StoredCredential(otherServer, "synthetic-other-server-token"))
        assertNull(store.memoryPending(otherServer)); assertNull(store.memoryPending(other))
        store.clear(); assertNull(disk.bytes); assertNull(keys.key)
    }

    @Test fun failureBeforeStageCommitRetainsOriginalReservationAndChat() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); val chat = chat()
        initialize(store); store.savePending(chat); store.saveMemoryPending(reserved())
        val committed = checkNotNull(disk.bytes).copyOf(); disk.failWrite = true
        rejected(SessionStoreFailure.Unavailable) { store.saveMemoryPending(reserved().copy(source = source())) }
        assertArrayEquals(committed, disk.bytes); assertEquals(reserved(), store.memoryPending(identity)); assertEquals(chat, store.pending(identity))
    }

    @Test fun existingEvidenceRequiresExactOwnedUserSourceAndCodePointQuote() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); initialize(store)
        val start = text.indexOf("😀"); val end = text.indexOf("  ")
        val evidence = EvidenceDto(versionId, text.codePointCount(0, start), text.codePointCount(0, end), text.substring(start, end), hash(text))
        val pending = PendingMemory(reserved().reservation.copy(note = null, evidence = evidence), source())
        rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending.copy(source = null)) }
        rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending.copy(source = source().copy(trust_class = "model_generated"))) }
        rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending.copy(source = source().copy(scope_id = UUID.randomUUID()))) }
        rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending.copy(source = source().copy(content_hash = "0".repeat(64)))) }
        rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending.copy(reservation = pending.reservation.copy(evidence = evidence.copy(quote = "Normalized")))) }
        rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending.copy(reservation = pending.reservation.copy(evidence = evidence.copy(span_end = evidence.span_start)))) }
        store.saveMemoryPending(pending)
        val input = pending.claimInput()
        assertEquals(evidence.span_start, input.span_start); assertEquals(evidence.span_end, input.span_end)
        assertEquals(pending, store(disk, keys).memoryPending(identity))
    }

    @Test fun invalidUnicodeBoundsAndIntervalsAreRejectedBeforeCommit() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); initialize(store)
        val invalid = listOf(
            reserved().copy(reservation = reserved().reservation.copy(note = NoteInputDto(sourceId, "\uD83D"))),
            reserved().copy(reservation = reserved().reservation.copy(note = NoteInputDto(sourceId, "x\u0000y"))),
            reserved("x".repeat(4001)),
            reserved().copy(reservation = reserved().reservation.copy(subject = "x".repeat(161))),
            reserved().copy(reservation = reserved().reservation.copy(predicate = " ")),
            reserved().copy(reservation = reserved().reservation.copy(value = "x".repeat(1001))),
            reserved().copy(reservation = reserved().reservation.copy(kind = "model_fact")),
            reserved().copy(reservation = reserved().reservation.copy(validFrom = "2026-01-01T00:00:00")),
            reserved().copy(reservation = reserved().reservation.copy(validFrom = "2026-01-01T00:00:00.0001Z")),
            reserved().copy(reservation = reserved().reservation.copy(validFrom = "2026-01-01T00:00:00Z", validTo = "2026-01-01T00:00:00Z")),
            reserved().copy(reservation = reserved().reservation.copy(validTo = "1970-01-01T00:00:00.999Z"), source = source()),
        )
        invalid.forEach { pending -> rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending) } }
        assertNull(store.memoryPending(identity))
    }

    @Test fun correctionPreservesOriginalSlotAndRejectsInvalidHalfOpenBounds() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); initialize(store)
        val old = ClaimDto(UUID.randomUUID(), scope, "user", "language", "English", "preference", "active", 1000L, 4000L,
            created_at = 1000L, origin = "user_asserted", evidence = EvidenceDto(versionId, 0, 1, "S", hash(text)))
        val correction = reserved().copy(reservation = reserved().reservation.copy(corrects = old, validFrom = "1970-01-01T00:00:02.000Z"), source = source())
        val invalid = listOf(
            correction.copy(reservation = correction.reservation.copy(validFrom = "1970-01-01T00:00:01.000Z")),
            correction.copy(reservation = correction.reservation.copy(validFrom = "1970-01-01T00:00:04.001Z")),
            correction.copy(reservation = correction.reservation.copy(validTo = "1970-01-01T00:00:02.000Z")),
            correction.copy(reservation = correction.reservation.copy(subject = "other")),
            correction.copy(reservation = correction.reservation.copy(corrects = old.copy(scope_id = UUID.randomUUID()))),
            correction.copy(reservation = correction.reservation.copy(claimId = old.id)),
            correction.copy(reservation = correction.reservation.copy(validFrom = null)), // implicit source start equals old start
        )
        invalid.forEach { pending -> rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(pending) } }
        store.saveMemoryPending(correction)
        assertEquals(claimId, correction.correctionInput().claim_id)
        assertEquals("1970-01-01T00:00:02.000Z", correction.correctionInput().effective_at)
        assertEquals(correction, store(disk, keys).memoryPending(identity))
    }

    @Test fun maximumUnicodeChatNoteOldEvidenceAndAnnotationsFitBoundedRecord() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); initialize(store)
        val content = "😀".repeat(4000)
        val old = ClaimDto(UUID.randomUUID(), scope, "😀".repeat(160), "😀".repeat(160), "😀".repeat(1000), "fact", "active", 0L,
            created_at = 0L, origin = "user_asserted", evidence = EvidenceDto(UUID.randomUUID(), 0, 4000, content, hash(content)))
        val maximum = reserved(content).copy(reservation = reserved(content).reservation.copy(subject = old.subject, predicate = old.predicate,
            value = old.value, kind = old.kind, corrects = old), source = source(content))
        store.savePending(chat().copy(body = ChatInputDto(UUID.randomUUID(), content)))
        store.saveMemoryPending(maximum)
        assertTrue(checkNotNull(disk.bytes).size <= EncryptedSessionStore.MAX_FILE_BYTES)
        assertEquals(maximum, store(disk, keys).memoryPending(identity))
        assertEquals(4000, maximum.claimInput().span_end)
    }

    @Test fun damagedKeyTamperingAndUnknownRecordVersionDestroyBothJournals() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys)
        initialize(store); store.savePending(chat()); store.saveMemoryPending(reserved())
        keys.key = null
        assertNull(store.memoryPending(identity)); assertNull(store.readCredential()); assertNull(disk.bytes)
        initialize(store); store.saveMemoryPending(reserved())
        disk.bytes!![disk.bytes!!.lastIndex] = (disk.bytes!!.last() + 1).toByte()
        assertNull(store.readCredential()); assertNull(store.memoryPending(identity)); assertNull(disk.bytes)
        initialize(store); store.savePending(chat()); store.saveMemoryPending(reserved())
        val plain = AesGcmSessionCipher(keys).decrypt(checkNotNull(disk.bytes))
        try {
            val unknown = plain.toString(Charsets.UTF_8).replace("\"version\":18", "\"version\":149")
            disk.bytes = AesGcmSessionCipher(keys).encrypt(unknown.toByteArray(Charsets.UTF_8))
        } finally { plain.fill(0) }
        assertNull(store.readCredential()); assertNull(store.pending(identity)); assertNull(store.memoryPending(identity))
        assertNull(disk.bytes); assertNull(keys.key)
    }

    @Test fun noteAcknowledgementCannotChangeSourceIdentityContentOrScope() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); initialize(store)
        store.saveMemoryPending(reserved())
        listOf(
            source().copy(source_id = UUID.randomUUID()),
            source().copy(content = "Different source input", content_hash = hash("Different source input")),
            source().copy(scope_id = UUID.randomUUID()),
            source().copy(trust_class = "model_generated"),
            source().copy(created_at = Long.MAX_VALUE),
        ).forEach { invalid -> rejected(SessionStoreFailure.InvalidPayload) { store.saveMemoryPending(reserved().copy(source = invalid)) } }
        assertEquals(reserved(), store.memoryPending(identity))
    }

    @Test fun independentStoreInstancesSerializeChatAndMemoryWithoutLostUpdates() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val first = store(disk, keys); val second = store(disk, keys); val chat = chat()
        initialize(first)
        listOf(async { first.savePending(chat) }, async { second.saveMemoryPending(reserved()) }).awaitAll()
        assertEquals(chat, first.pending(identity)); assertEquals(reserved(), second.memoryPending(identity))
        listOf(async { first.removePending(identity, chat.body.request_id) },
            async { second.saveMemoryPending(reserved().copy(source = source())) }).awaitAll()
        assertNull(first.pending(identity)); assertEquals(reserved().copy(source = source()), second.memoryPending(identity))
    }

    @Test fun maximumJsonEscapedPayloadStillFitsTheTwoJournalBound() = runTest {
        val disk = JournalDisk(); val keys = JournalKeys(); val store = store(disk, keys); initialize(store)
        val content = "\u0001".repeat(4000)
        val old = ClaimDto(UUID.randomUUID(), scope, "\u0001".repeat(160), "\u0001".repeat(160), "\u0001".repeat(1000), "fact", "active", 0L,
            created_at = 0L, origin = "user_asserted", evidence = EvidenceDto(UUID.randomUUID(), 0, 4000, content, hash(content)))
        val maximum = reserved(content).copy(reservation = reserved(content).reservation.copy(subject = old.subject, predicate = old.predicate,
            value = old.value, kind = old.kind, corrects = old), source = source(content))
        store.savePending(chat().copy(body = ChatInputDto(UUID.randomUUID(), content)))
        store.saveMemoryPending(maximum)
        assertTrue(checkNotNull(disk.bytes).size <= EncryptedSessionStore.MAX_FILE_BYTES)
        assertEquals(maximum, store(disk, keys).memoryPending(identity))
    }
}
