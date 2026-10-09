package dev.ada.assistant.data

import android.util.AtomicFile
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import java.security.KeyStore
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test

class SecureSessionStoreInstrumentedTest {
    private fun exercise(block: suspend (File, String, SessionStore) -> Unit) = runBlocking {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val suffix = UUID.randomUUID().toString()
        val file = File(context.noBackupFilesDir, "session-storage-test-$suffix.bin")
        val alias = "ada.session.test.$suffix"
        val store = EncryptedSessionStore(AtomicSessionDisk(file), AesGcmSessionCipher(AndroidSessionKeys(alias)), true)
        try { block(file, alias, store) } finally { store.clear() }
    }
    private val identity = SessionIdentity("https://ada.example/", UUID.fromString("00000000-0000-4000-8000-000000000001"))
    private fun pending() = PendingMessage(identity, UUID.fromString("00000000-0000-4000-8000-000000000002"),
        ChatInputDto(UUID.fromString("00000000-0000-4000-8000-000000000003"), "Synthetic 😀 recovery\r\n", "2026-10-08T00:00:00.000Z", false))

    @Test fun actualKeystorePersistsEncryptedExactJournalAndExcludesBackupLocation() = exercise { file, alias, store ->
        store.saveCredential(StoredCredential(identity, "synthetic-instrumented-token"))
        store.savePending(pending())
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals(context.noBackupFilesDir.canonicalFile, checkNotNull(file.parentFile).canonicalFile)
        val bytes = file.readBytes()
        assertFalse(bytes.toString(Charsets.UTF_8).contains("synthetic-instrumented-token"))
        assertFalse(bytes.toString(Charsets.UTF_8).contains("Synthetic"))
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val key = keyStore.getKey(alias, null)
        assertNull(key.encoded) // Keystore key material cannot be exported.
        val recreated = EncryptedSessionStore(AtomicSessionDisk(file), AesGcmSessionCipher(AndroidSessionKeys(alias)), true)
        assertEquals("synthetic-instrumented-token", recreated.readCredential()?.token)
        assertEquals(pending(), recreated.pending(identity))
    }

    @Test fun actualKeyLossAndCiphertextCorruptionDeleteStateAndRequireReconnect() = exercise { file, alias, store ->
        store.saveCredential(StoredCredential(identity, "synthetic-instrumented-token")); store.savePending(pending())
        KeyStore.getInstance("AndroidKeyStore").apply { load(null); deleteEntry(alias) }
        assertNull(store.readCredential())
        assertFalse(file.exists())
        store.saveCredential(StoredCredential(identity, "new-synthetic-token"))
        val corrupt = file.readBytes().also { it[it.lastIndex] = (it.last() + 1).toByte() }
        file.writeBytes(corrupt)
        assertNull(store.readCredential()); assertFalse(file.exists())
    }

    @Test fun interruptedAtomicWriteRestoresTheOldCommittedReservation() = exercise { file, alias, store ->
        store.saveCredential(StoredCredential(identity, "synthetic-instrumented-token")); store.savePending(pending())
        val committed = file.readBytes()
        // Model process death before finishWrite. AtomicFile.openRead must discard/recover the interrupted write.
        AtomicFile(file).startWrite().use { stream -> stream.write(byteArrayOf(1, 2, 3)); stream.fd.sync() }
        val recreated = EncryptedSessionStore(AtomicSessionDisk(file), AesGcmSessionCipher(AndroidSessionKeys(alias)), true)
        assertEquals(pending(), recreated.pending(identity))
        assertArrayEquals(committed, file.readBytes())
    }

    @Test fun logoutRemovesPrivateStateEvenAfterTheKeystoreEntryDisappears() = exercise { file, alias, store ->
        store.saveCredential(StoredCredential(identity, "synthetic-instrumented-token")); store.savePending(pending())
        KeyStore.getInstance("AndroidKeyStore").apply { load(null); deleteEntry(alias) }
        store.clear()
        assertFalse(file.exists())
        assertNull(store.readCredential()); assertNull(store.pending(identity))
    }
}
