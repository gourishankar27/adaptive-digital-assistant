package dev.ada.assistant.data

import java.util.UUID
import javax.crypto.KeyGenerator
import kotlinx.serialization.json.JsonObject
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test

private class ProposalDisk : SessionDisk {
    var bytes: ByteArray? = null
    override fun read(maxBytes: Int) = bytes?.copyOf()?.also { require(it.size <= maxBytes) }
    override fun write(bytes: ByteArray) { this.bytes = bytes.copyOf() }
    override fun delete() { bytes = null }
}
class ProposalJournalTest {
    private val identity = SessionIdentity("http://127.0.0.1:8000/", UUID.randomUUID())
    private fun operation(): PendingProposal {
        val key = UUID.randomUUID(); val pin = SourcePinDto(UUID.randomUUID(), 1, "a".repeat(64), 0, 3)
        return PendingProposal(identity, UUID.randomUUID(), key, kind = "extract", body = """{"extraction_id":"$key","sources":[{"source_version_id":"${pin.source_version_id}","version":1,"content_hash":"${pin.content_hash}","span_start":0,"span_end":3}]}""")
    }
    @Test fun encryptedExactRecoveryAndIdentitySwitchPreserveLegacyChatJournal() = runTest {
        val disk = ProposalDisk(); val key = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey()
        val cipher = AesGcmSessionCipher(object : SessionKeys { override fun existing() = key; override fun create() = key; override fun delete() {} })
        val store = EncryptedSessionStore(disk, cipher, true); store.saveCredential(StoredCredential(identity, "synthetic-token"))
        val chat = PendingMessage(identity, UUID.randomUUID(), ChatInputDto(UUID.randomUUID(), "Earlier private synthetic chat")); store.savePending(chat)
        val p = operation(); store.saveProposalPending(p)
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains(p.body))
        val restored = EncryptedSessionStore(disk, cipher, true); assertEquals(p, restored.proposalPending(identity))
        restored.saveCredential(StoredCredential(identity, "replacement-token")); assertEquals(p, restored.proposalPending(identity))
        try { restored.saveProposalPending(operation()); fail("Pending overwritten") } catch (_: SessionStorageException) {}
        restored.removeProposalPending(identity, UUID.randomUUID()); assertEquals(p, restored.proposalPending(identity))
        restored.removeProposalPending(identity, p.operationId); assertNull(restored.proposalPending(identity)); assertEquals(chat, restored.pending(identity))
        restored.saveProposalPending(p); restored.saveCredential(StoredCredential(identity.copy(owner = UUID.randomUUID()), "new-account-token")); assertNull(restored.proposalPending(identity))
    }
    @Test fun keyMismatchAndUnknownFieldsNeverEnterProposalRecovery() = runTest {
        val p = operation()
        for (bad in listOf(p.copy(operationId = UUID.randomUUID()), p.copy(kind = "approve-all"), p.copy(body = p.body.dropLast(1) + ",\"owner_id\":\"forged\"}"))) {
            try { validateProposalPending(bad); fail("Invalid request accepted") } catch (_: SessionStorageException) {}
        }
    }
    @Test fun v4UpgradePersistsPartialDraftWithoutLosingEarlierEntityJournal() = runTest {
        val disk = ProposalDisk(); val key = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey()
        val cipher = AesGcmSessionCipher(object : SessionKeys { override fun existing() = key; override fun create() = key; override fun delete() {} })
        val store = EncryptedSessionStore(disk, cipher, true); store.saveCredential(StoredCredential(identity, "synthetic-token"))
        val scope = UUID.randomUUID(); val operationId = UUID.randomUUID()
        val entity = PendingEntity(identity, scope, operationId, "create", "scopes/$scope/entities", """{"operation_id":"$operationId","label":"Synthetic","kind":"person"}""")
        store.saveEntityPending(entity)
        val v4 = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":5", "\"version\":4").replace(",\"proposalPending\":null", "").replace(",\"proposalDraft\":null", "")
        disk.bytes = cipher.encrypt(v4.toByteArray())
        val restored = EncryptedSessionStore(disk, cipher, true)
        val pin = SourcePinDto(UUID.randomUUID(), 1, "a".repeat(64), 0, 3)
        val candidate = ProposalCandidateDto("Mira", "drink", "tea", "preference", "2026-10-01T00:00:00Z", support = listOf(pin))
        val proposal = ProposalDto(UUID.randomUUID(), scope, UUID.randomUUID(), "pending", 1, candidate, candidate, "synthetic", "selected-sources-v1", JsonObject(emptyMap()), emptyList(), emptyList(), "a".repeat(64), created_at = 1)
        val draft = ProposalDraft(identity, proposal, candidate.copy(value = " ", valid_to = "2026-"), "Unsent synthetic annotation")
        restored.saveProposalDraft(draft)
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains(draft.annotation))
        val reopened = EncryptedSessionStore(disk, cipher, true)
        assertEquals(entity, reopened.entityPending(identity)); assertEquals(draft, reopened.proposalDraft(identity))
        try { reopened.saveProposalDraft(draft.copy(candidate = draft.candidate.copy(valid_to = "\u0000"))); fail("Malformed Unicode saved") } catch (_: SessionStorageException) {}
        assertEquals(draft, reopened.proposalDraft(identity))
        reopened.clear(); assertNull(reopened.proposalDraft(identity)); assertNull(reopened.entityPending(identity))
    }
    @Test fun editRecoveryNormalizesExactDatesButNeverDifferentAnnotations() {
        val candidate = ProposalCandidateDto("Mira", "drink", "tea", "preference", "2026-10-01T00:00:00Z", support = listOf(SourcePinDto(UUID.randomUUID(), 1, "a".repeat(64), 0, 3)))
        assertTrue(sameProposalCandidate(candidate, candidate.copy(value = " tea ", valid_from = "2026-10-01T02:00:00+02:00")))
        assertFalse(sameProposalCandidate(candidate, candidate.copy(value = "coffee")))
        val provenance = ReviewProvenanceDto("review-v1", "user_reviewed", UUID.randomUUID(), UUID.randomUUID(), "synthetic", "selected-sources-v1", emptyList())
        assertTrue(provenance.reviewOriginLabel().startsWith("User reviewed"))
        assertEquals("Unrecognized review provenance", provenance.copy(version = "review-v2").reviewOriginLabel())
        assertEquals("Unrecognized review provenance", provenance.copy(origin = "unknown").reviewOriginLabel())
        try { validateCandidate(candidate.copy(valid_from = " ")); fail("Blank date accepted") } catch (_: IllegalArgumentException) {}
    }
}
