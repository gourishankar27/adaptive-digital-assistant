package dev.ada.assistant.data

import java.io.IOException
import java.util.UUID
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

/** Fakes model the disk/key boundaries only; encryption itself uses real JCE AES-GCM. */
private class MemorySessionDisk : SessionDisk {
    var bytes: ByteArray? = null
    var failWrite = false
    var failDelete = false
    override fun read(maxBytes: Int): ByteArray? {
        val data = bytes ?: return null
        if (data.size > maxBytes) throw IOException("Bound exceeded")
        return data.copyOf()
    }
    override fun write(bytes: ByteArray) {
        if (failWrite) throw IOException("Synthetic storage failure")
        this.bytes = bytes.copyOf()
    }
    override fun delete() {
        if (failDelete) throw IOException("Synthetic deletion failure")
        bytes = null
    }
}
private class MemorySessionKeys : SessionKeys {
    var key: SecretKey? = null
    var reads = 0
    override fun existing(): SecretKey? { reads++; return key }
    override fun create(): SecretKey = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey().also { key = it }
    override fun delete() { key = null }
}

class SecureSessionStoreTest {
    @Test fun passwordSessionPersistsOnlyRefreshAndKeepsOwnedJournalAcrossRotation() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(StoredCredential(identity, "synthetic-refresh-one", passwordSession = true))
        s.savePending(message())
        s.saveCredential(StoredCredential(identity, "synthetic-refresh-two", passwordSession = true))
        val reopened = store(disk, keys)
        assertTrue(reopened.readCredential()!!.passwordSession)
        assertEquals("synthetic-refresh-two", reopened.readCredential()!!.token)
        assertNull(SessionTokenStorageAdapter(reopened).load(identity.server, identity.owner))
        assertEquals(message(), reopened.pending(identity))
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains("synthetic-refresh"))
        val payload = AesGcmSessionCipher(keys).decrypt(disk.bytes!!).toString(Charsets.UTF_8)
        assertFalse(payload.contains("access_token")); assertFalse(payload.contains("synthetic-refresh-one"))
        assertTrue(payload.contains("\"version\":12"))
    }

    @Test fun releasedV10WithoutEpochOrSecurityFieldsRestoresAndUpgrades() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(credential()); s.savePending(message())
        val cipher = AesGcmSessionCipher(keys)
        val old = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":12", "\"version\":10")
            .replace(",\"dataEpoch\":0", "").replace(",\"securityJournal\":null", "")
        disk.bytes = cipher.encrypt(old.toByteArray())
        assertEquals(message(), store(disk, keys).pending(identity))
        assertEquals(0L, store(disk, keys).readCredential()!!.dataEpoch)
        store(disk, keys).saveCredential(credential())
        assertTrue(cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).contains("\"version\":12"))
    }
    @Test fun privacyEpochClearsEveryJournalAndSecurityReservationsAreEncrypted() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(credential()); s.savePending(message())
        val operation = UUID.randomUUID()
        val pending = SecurityJournal(identity, "delete", operation, preview = UUID.randomUUID())
        s.saveSecurityJournal(pending)
        assertEquals(pending, store(disk, keys).securityJournal(identity))
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains(operation.toString()))
        s.saveCredential(StoredCredential(identity, "synthetic-rotated", 0))
        assertEquals(pending, s.securityJournal(identity)); assertNotNull(s.pending(identity))
        s.saveCredential(StoredCredential(identity, "synthetic-rotated", 1))
        assertNull(s.securityJournal(identity)); assertNull(s.pending(identity)); assertNull(s.voiceDraft(identity))
        assertEquals(1L, s.readCredential()!!.dataEpoch)
    }
    @Test fun realV8CiphertextUpgradesAndLearningJournalIsEncryptedAndIdentityBound() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(credential()); s.savePending(message())
        val cipher = AesGcmSessionCipher(keys)
        val previous = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":12", "\"version\":8").replace(",\"learningJournal\":null", "")
        assertTrue(previous.contains("\"version\":8")); disk.bytes = cipher.encrypt(previous.toByteArray())
        val restored = store(disk, keys); assertEquals(message(), restored.pending(identity))
        val key = UUID.randomUUID(); val journal = LearningJournal(identity, UUID.randomUUID(), key, "config", adaJson.encodeToString(LearningConfigWriteDto(key, 0, "enrolled")))
        restored.saveLearningJournal(journal); assertEquals(journal, store(disk, keys).learningJournal(identity))
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains(key.toString()))
        restored.saveCredential(credential(token = "synthetic-rotation")); assertEquals(journal, restored.learningJournal(identity))
        restored.saveCredential(credential(SessionIdentity(identity.server, UUID.randomUUID()))); assertNull(restored.learningJournal(identity))
    }
    @Test fun realV7CiphertextUpgradesAndExpressionReservationStaysIdentityBound() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(credential()); s.savePending(message())
        val cipher = AesGcmSessionCipher(keys)
        val old = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":12", "\"version\":7").replace(",\"expressionJournal\":null", "").replace(",\"learningJournal\":null", "")
        assertTrue(old.contains("\"version\":7")); disk.bytes = cipher.encrypt(old.toByteArray())
        val restored = store(disk, keys); assertEquals(message(), restored.pending(identity))
        val id = UUID.randomUUID()
        val journal = ExpressionJournal(identity, id, "preferences", "account", identity.owner,
            adaJson.encodeToString(PreferenceWriteDto(id, 0, PreferenceValuesDto(verbosity = "concise"))))
        restored.saveExpressionJournal(journal)
        assertEquals(journal, store(disk, keys).expressionJournal(identity))
        restored.saveCredential(credential(token = "synthetic-rotated"))
        assertEquals(journal, restored.expressionJournal(identity))
        restored.saveCredential(StoredCredential(SessionIdentity(identity.server, UUID.randomUUID()), "synthetic-other"))
        assertNull(restored.expressionJournal(identity)); assertNull(restored.pending(identity))
    }
    @Test fun forgedExpressionAuthorityAndUnknownFieldsNeverReachEncryptedDisk() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys); s.saveCredential(credential())
        val id = UUID.randomUUID()
        val body = """{"operation_id":"$id","expected_revision":0,"values":{"admin":true}}"""
        try { s.saveExpressionJournal(ExpressionJournal(identity, id, "preferences", "account", identity.owner, body)); fail("forged permission accepted") }
        catch (_: SessionStorageException) { }
        assertNull(s.expressionJournal(identity))
    }
    @Test fun realV6CiphertextRemainsReadableAndUpgradesWithoutLosingChat() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(credential()); s.savePending(message())
        val cipher = AesGcmSessionCipher(keys)
        val old = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":12", "\"version\":6").replace(",\"consolidationJournal\":null", "").replace(",\"expressionJournal\":null", "").replace(",\"learningJournal\":null", "")
        assertTrue(old.contains("\"version\":6")); disk.bytes = cipher.encrypt(old.toByteArray())
        assertEquals(message(), store(disk, keys).pending(identity))
        s.saveCredential(credential(token = "synthetic-rotated"))
        assertEquals(message(), s.pending(identity)); assertTrue(cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).contains("\"version\":12"))
    }
    @Test fun consolidationReservationSurvivesEncryptedRestartAndTokenRotation() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(credential()); s.savePending(message())
        val id = UUID.randomUUID(); val p = ConsolidationJournal(identity, UUID.randomUUID(), id,
            adaJson.encodeToString(ConsolidationInputDto(id, "episode", listOf(SourcePinDto(UUID.randomUUID(), 1, "a".repeat(64), 0, 10)))))
        s.saveConsolidationJournal(p)
        assertEquals(p, store(disk, keys).consolidationJournal(identity)); assertNotNull(s.pending(identity))
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains(p.jobId.toString()))
        try { s.saveConsolidationJournal(p.copy(body = p.body.replace("episode", "proposals"))); fail("Changed input accepted") } catch (_: SessionStorageException) {}
        s.saveCredential(credential(token = "synthetic-rotated")); assertEquals(p, s.consolidationJournal(identity))
        s.removeConsolidationJournal(identity, UUID.randomUUID()); assertEquals(p, s.consolidationJournal(identity))
        s.saveCredential(credential(identity.copy(owner = UUID.randomUUID()))); assertNull(s.consolidationJournal(identity))
    }
    @Test fun agentJournalIsEncryptedExactAndClearedOnIdentityChange() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val s = store(disk, keys)
        s.saveCredential(credential())
        val run = UUID.randomUUID(); val p = AgentJournal(identity, UUID.randomUUID(), UUID.randomUUID(), run, adaJson.encodeToString(AgentInputDto(run, "synthetic-private-task", allowed_tools = listOf("calculator"))))
        s.saveAgentJournal(p); assertEquals(p, store(disk, keys).agentJournal(identity)); assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains("synthetic-private-task"))
        try { s.saveAgentJournal(p.copy(body = p.body.replace("synthetic-private-task", "changed"))); fail("Changed reservation accepted") } catch (_: SessionStorageException) {}
        val key = UUID.randomUUID(); val op = AgentOperation("approve", key, UUID.randomUUID(), adaJson.encodeToString(AgentApprovalDto(key, "a".repeat(64), "b".repeat(64), "calculator-v1")))
        s.saveAgentJournal(p.copy(operation = op)); assertEquals(op, store(disk, keys).agentJournal(identity)!!.operation)
        s.saveCredential(credential(token = "synthetic-rotated")); assertNotNull(s.agentJournal(identity))
        s.saveCredential(credential(identity.copy(owner = UUID.randomUUID()))); assertNull(s.agentJournal(identity)); assertNull(s.pending(identity))
    }
    private val identity = SessionIdentity("https://ada.example/", UUID.fromString("00000000-0000-4000-8000-000000000001"))
    private fun credential(identity: SessionIdentity = this.identity, token: String = "synthetic-only-secret") = StoredCredential(identity, token)
    private fun message(identity: SessionIdentity = this.identity, body: ChatInputDto = ChatInputDto(
        UUID.fromString("00000000-0000-4000-8000-000000000003"), "Exact 😀 text\r\n e\u0301  ", "2026-10-08T00:00:00.000Z", false,
    )) = PendingMessage(identity, UUID.fromString("00000000-0000-4000-8000-000000000002"), body)
    private fun store(disk: MemorySessionDisk, keys: MemorySessionKeys) = EncryptedSessionStore(disk, AesGcmSessionCipher(keys), false)

    @Test fun credentialsAndReservedPayloadSurviveRecreationWithNoPlaintextDisk() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys()
        val first = store(disk, keys)
        first.saveCredential(credential()); first.savePending(message())
        val bytes = checkNotNull(disk.bytes)
        assertFalse(bytes.toString(Charsets.UTF_8).contains("synthetic-only-secret"))
        assertFalse(bytes.toString(Charsets.UTF_8).contains("Exact"))
        val restored = store(disk, keys)
        assertEquals("synthetic-only-secret", restored.readCredential()?.token)
        assertEquals(message(), restored.pending(identity))
        assertFalse(credential().toString().contains("synthetic-only-secret"))
        assertFalse(message().toString().contains("Exact"))
    }

    @Test fun pendingRequiresMatchingAuthenticatedIdentityAndExactReservation() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        try { store.savePending(message()); fail("A pending request without a credential must be rejected") } catch (_: SessionStorageException) { }
        store.saveCredential(credential()); store.savePending(message())
        assertNull(store.pending(identity.copy(owner = UUID.randomUUID())))
        try { store.savePending(message(identity.copy(owner = UUID.randomUUID()))); fail("Cross-owner journal must be rejected") } catch (_: SessionStorageException) { }
        try { store.savePending(message(body = message().body.copy(use_memory = true))); fail("Changed options must be rejected") } catch (_: SessionStorageException) { }
        try { store.savePending(message(body = message().body.copy(request_id = UUID.randomUUID()))); fail("A second reservation must not overwrite the first") } catch (_: SessionStorageException) { }
        store.savePending(message()) // exact replay is allowed
        store.removePending(identity, UUID.randomUUID())
        assertEquals(message(), store.pending(identity))
        store.removePending(identity, message().body.request_id)
        assertNull(store.pending(identity))
    }

    @Test fun verifiedTokenRotationRetainsJournalButOwnerOrServerSwitchDropsIt() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        store.saveCredential(credential()); store.savePending(message())
        store.saveCredential(credential(token = "rotated-synthetic-token"))
        assertEquals(message(), store.pending(identity))
        val otherOwner = identity.copy(owner = UUID.randomUUID())
        store.saveCredential(credential(otherOwner))
        assertNull(store.pending(identity)); assertNull(store.pending(otherOwner))
        store.savePending(message(otherOwner))
        val otherServer = otherOwner.copy(server = "https://other.example/")
        store.saveCredential(credential(otherServer))
        assertNull(store.pending(otherOwner)); assertNull(store.pending(otherServer))
    }

    @Test fun failedWriteKeepsPreviousCommittedCredentialAndPending() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        store.saveCredential(credential()); store.savePending(message())
        val committed = checkNotNull(disk.bytes).copyOf()
        disk.failWrite = true
        try { store.saveCredential(credential(identity.copy(owner = UUID.randomUUID()))); fail("Write should fail") } catch (error: SessionStorageException) {
            assertNull(error.cause)
            assertFalse(error.toString().contains("synthetic-only-secret"))
            assertFalse(error.toString().contains("Exact"))
        }
        assertArrayEquals(committed, disk.bytes)
        assertEquals(identity, store.readCredential()?.identity)
        assertEquals(message(), store.pending(identity))
    }

    @Test fun missingKeyTamperingCorruptJsonAndOversizeFilesRequireReconnect() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        store.saveCredential(credential()); store.savePending(message())
        keys.key = null
        assertNull(store.readCredential()); assertNull(disk.bytes)
        store.saveCredential(credential())
        disk.bytes!![disk.bytes!!.lastIndex] = (disk.bytes!!.last() + 1).toByte()
        assertNull(store.readCredential()); assertNull(disk.bytes)
        disk.bytes = AesGcmSessionCipher(keys).encrypt("{invalid-json".toByteArray())
        assertNull(store.readCredential()); assertNull(disk.bytes)
        disk.bytes = ByteArray(EncryptedSessionStore.MAX_FILE_BYTES + 1)
        assertNull(store.readCredential()); assertNull(disk.bytes)
    }

    @Test fun ciphertextNonceChangesAndFormatCannotBeSilentlyReinterpreted() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        store.saveCredential(credential()); val first = checkNotNull(disk.bytes).copyOf()
        store.saveCredential(credential()); val second = checkNotNull(disk.bytes).copyOf()
        assertFalse(first.contentEquals(second))
        second[0] = (second[0] + 1).toByte(); disk.bytes = second
        assertNull(store.readCredential()); assertNull(disk.bytes)
    }

    @Test fun logoutDestroysJournalAndCredentialWithoutLoadingTheirKey() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        store.saveCredential(credential()); store.savePending(message())
        keys.key = null
        val keyReads = keys.reads
        store.clear()
        assertEquals(keyReads, keys.reads)
        assertNull(disk.bytes); assertNull(keys.key); assertNull(store.readCredential())
    }

    @Test fun failedFileDeletionStillDestroysKeyAndExposesOnlySanitizedFailure() = runTest {
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        store.saveCredential(credential()); store.savePending(message())
        disk.failDelete = true
        try { store.clear(); fail("Deletion failure must be visible") } catch (error: SessionStorageException) {
            assertNull(error.cause)
            assertEquals(SessionStoreFailure.Unavailable, error.failure)
        }
        assertNotNull(disk.bytes)
        assertNull(keys.key)
    }

    @Test fun boundsAndCanonicalServerValidationDoNotEchoPrivateInput() = runTest {
        assertThrows(IllegalArgumentException::class.java) { SessionIdentity("https://user:private@example/", identity.owner) }
        assertThrows(IllegalArgumentException::class.java) { SessionIdentity("https://ADA.EXAMPLE:443", identity.owner) }
        val disk = MemorySessionDisk(); val keys = MemorySessionKeys(); val store = store(disk, keys)
        store.saveCredential(credential())
        try { store.savePending(message(body = message().body.copy(content = "x".repeat(4001)))); fail("Oversize payload accepted") } catch (_: SessionStorageException) { }
        try { store.savePending(message(body = message().body.copy(content = "invalid\u0000text"))); fail("NUL accepted") } catch (_: SessionStorageException) { }
        try { store.savePending(message(body = message().body.copy(as_of = "2026-10-08T00:00:00.0001Z"))); fail("Sub-millisecond instant accepted") } catch (_: SessionStorageException) { }
        store.savePending(message(body = message().body.copy(content = "😀".repeat(4000))))
        assertEquals(4000, store.pending(identity)!!.body.content.codePointCount(0, store.pending(identity)!!.body.content.length))
    }
}
