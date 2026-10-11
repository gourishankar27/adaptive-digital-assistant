package dev.ada.assistant.data

import java.util.UUID
import javax.crypto.KeyGenerator
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test

private class EntityDisk : SessionDisk {
    var bytes: ByteArray? = null
    override fun read(maxBytes: Int) = bytes?.copyOf()?.also { require(it.size <= maxBytes) }
    override fun write(bytes: ByteArray) { this.bytes = bytes.copyOf() }
    override fun delete() { bytes = null }
}
class EntityJournalTest {
    private val identity = SessionIdentity("http://127.0.0.1:8000/", UUID.randomUUID())
    private fun pending() : PendingEntity {
        val scope = UUID.randomUUID(); val op = UUID.randomUUID()
        return PendingEntity(identity, scope, op, "create", "scopes/$scope/entities", """{"operation_id":"$op","entity_id":"${UUID.randomUUID()}","label":"Private synthetic entity","kind":"person"}""")
    }
    @Test fun exactEntityRecoverySurvivesTokenReplacementAndCiphertextHasNoPrivateText() = runTest {
        val disk = EntityDisk(); val key = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey()
        val cipher = AesGcmSessionCipher(object : SessionKeys { override fun existing() = key; override fun create() = key; override fun delete() {} })
        val first = EncryptedSessionStore(disk, cipher, true); first.saveCredential(StoredCredential(identity, "synthetic-token"))
        val p = pending(); first.saveEntityPending(p)
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains("Private synthetic entity"))
        val restored = EncryptedSessionStore(disk, cipher, true); assertEquals(p, restored.entityPending(identity))
        restored.saveCredential(StoredCredential(identity, "replacement-token")); assertEquals(p, restored.entityPending(identity))
        restored.removeEntityPending(identity, UUID.randomUUID()); assertEquals(p, restored.entityPending(identity))
        restored.removeEntityPending(identity, p.operationId); assertNull(restored.entityPending(identity))
    }
    @Test fun foreignIdentityAndCredentialPathsNeverEnterEntityJournal() = runTest {
        val disk = EntityDisk(); val key = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey()
        val store = EncryptedSessionStore(disk, AesGcmSessionCipher(object : SessionKeys { override fun existing() = key; override fun create() = key; override fun delete() {} }), true)
        store.saveCredential(StoredCredential(identity, "synthetic-token")); val p = pending()
        for (bad in listOf(p.copy(identity = identity.copy(owner = UUID.randomUUID())), p.copy(path = "https://example.com/credential"), p.copy(operationId = UUID.randomUUID()), p.copy(body = p.body.replace("Private synthetic entity", "\\u0000")))) {
            try { store.saveEntityPending(bad); fail("Invalid reservation accepted") } catch (_: SessionStorageException) { }
        }
        assertNull(store.entityPending(identity))
    }
    @Test fun priorV3JournalsSurviveV4UpgradeAndOnlyEntityReceiptIsCleared() = runTest {
        val disk = EntityDisk(); val key = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey()
        val cipher = AesGcmSessionCipher(object : SessionKeys { override fun existing() = key; override fun create() = key; override fun delete() {} })
        val store = EncryptedSessionStore(disk, cipher, true); store.saveCredential(StoredCredential(identity, "synthetic-token"))
        val p = pending(); val chat = PendingMessage(identity, UUID.randomUUID(), ChatInputDto(UUID.randomUUID(), "Synthetic earlier chat"))
        val memory = PendingMemory(MemoryReservation(identity, p.scopeId, UUID.randomUUID(), note = NoteInputDto(UUID.randomUUID(), "Synthetic earlier note"), subject = "Project", predicate = "setting", value = "Blue", kind = "fact"))
        val document = PendingDocument(identity, p.scopeId, UUID.randomUUID(), UUID.randomUUID(), "synthetic.txt", "text/plain", java.util.Base64.getEncoder().encodeToString("Synthetic earlier text".toByteArray()))
        store.savePending(chat); store.saveMemoryPending(memory); store.saveDocumentPending(document)
        val old = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":7", "\"version\":3").replace(",\"entityPending\":null", "").replace(",\"proposalPending\":null", "").replace(",\"proposalDraft\":null", "").replace(",\"agentJournal\":null", "").replace(",\"consolidationJournal\":null", "")
        disk.bytes = cipher.encrypt(old.toByteArray()); val upgraded = EncryptedSessionStore(disk, cipher, true)
        assertNull(upgraded.entityPending(identity)); upgraded.saveEntityPending(p); upgraded.removeEntityPending(identity, p.operationId)
        assertEquals(chat, upgraded.pending(identity)); assertEquals(memory, upgraded.memoryPending(identity)); assertEquals(document, upgraded.documentPending(identity))
    }
}
