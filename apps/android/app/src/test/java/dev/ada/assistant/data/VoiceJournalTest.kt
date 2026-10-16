package dev.ada.assistant.data

import java.io.IOException
import java.util.UUID
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test

private class VoiceDisk : SessionDisk {
    var bytes: ByteArray? = null; var failWrite = false
    override fun read(maxBytes: Int) = bytes?.copyOf()
    override fun write(bytes: ByteArray) { if (failWrite) throw IOException("Synthetic write failure"); this.bytes = bytes.copyOf() }
    override fun delete() { bytes = null }
}
private class VoiceKeys : SessionKeys {
    var key: SecretKey? = null
    override fun existing() = key
    override fun create() = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey().also { key = it }
    override fun delete() { key = null }
}
class VoiceJournalTest {
    private val identity = SessionIdentity("http://localhost:8000/", UUID.randomUUID())
    private val cid = UUID.randomUUID(); private val sid = UUID.randomUUID()
    private fun draft() = VoiceDraft(identity,cid,sid,
        TranscriptInputDto(UUID.randomUUID(),"android_on_device","Android 16 API36","en-US",2300,"Generated cattle 🫖"),
        "Reviewed kettle 🫖",true)
    @Test fun releasedV9WithoutVoiceFieldsReadsAndFutureVoiceDataFailsClosed() = runTest {
        val disk = VoiceDisk(); val cipher = AesGcmSessionCipher(VoiceKeys()); val store = EncryptedSessionStore(disk,cipher,true)
        store.saveCredential(StoredCredential(identity,"synthetic-voice-token"))
        val plain = PendingMessage(identity,cid,ChatInputDto(UUID.randomUUID(),"Original typed recovery"))
        store.savePending(plain)
        val old = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":11", "\"version\":9")
            .replace(",\"voiceTranscript\":null", "").replace(",\"voiceScopeId\":null", "").replace(",\"voiceDraft\":null", "")
        disk.bytes = cipher.encrypt(old.toByteArray(Charsets.UTF_8))
        assertEquals(plain, store.pending(identity))
        store.savePending(plain); assertTrue(cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).contains("\"version\":11"))
        store.removePending(identity,plain.body.request_id); store.saveVoiceDraft(draft())
        val forged = cipher.decrypt(disk.bytes!!).toString(Charsets.UTF_8).replace("\"version\":11", "\"version\":9")
        disk.bytes = cipher.encrypt(forged.toByteArray(Charsets.UTF_8))
        assertNull(store.readCredential()); assertNull(disk.bytes)
    }
    @Test fun encryptedApprovalAndPendingCommitAreAtomicAndIdentityIsolated() = runTest {
        val disk = VoiceDisk(); val cipher = AesGcmSessionCipher(VoiceKeys()); val store = EncryptedSessionStore(disk,cipher,true)
        store.saveCredential(StoredCredential(identity,"synthetic-voice-token"))
        val draft = draft(); store.saveVoiceDraft(draft)
        assertEquals(draft,store.voiceDraft(identity))
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains(draft.transcript.original_text))
        val pending = PendingMessage(identity,cid,ChatInputDto(UUID.randomUUID(),draft.reviewedText),draft.transcript,sid)
        disk.failWrite = true
        try { store.savePending(pending); fail("write should fail") } catch (_: SessionStorageException) { }
        disk.failWrite = false
        assertEquals(draft,store.voiceDraft(identity)); assertNull(store.pending(identity))
        store.savePending(pending)
        assertEquals(pending,store.pending(identity)); assertNull(store.voiceDraft(identity))
        assertEquals(pending,EncryptedSessionStore(disk,cipher,true).pending(identity))
        store.savePending(pending) // Exact retry works after the review draft has been consumed.
        store.saveCredential(StoredCredential(identity.copy(owner = UUID.randomUUID()),"synthetic-other-token"))
        assertNull(store.pending(identity)); assertNull(store.voiceDraft(identity))
    }
    @Test fun unapprovedChangedTextAndForeignScopeCannotBecomePendingVoice() = runTest {
        val store = EncryptedSessionStore(VoiceDisk(),AesGcmSessionCipher(VoiceKeys()),true)
        store.saveCredential(StoredCredential(identity,"synthetic-voice-token"))
        val draft = draft().copy(approved = false); store.saveVoiceDraft(draft)
        val pending = PendingMessage(identity,cid,ChatInputDto(UUID.randomUUID(),draft.reviewedText),draft.transcript,sid)
        try { store.savePending(pending); fail("approval required") } catch (_: SessionStorageException) { }
        store.saveVoiceDraft(draft.copy(approved = true))
        for (changed in listOf(pending.copy(body = pending.body.copy(content = "Different text")),pending.copy(voiceScopeId = UUID.randomUUID()))) {
            try { store.savePending(changed); fail("exact reviewed binding required") } catch (_: SessionStorageException) { }
        }
        assertNull(store.pending(identity)); assertNotNull(store.voiceDraft(identity))
    }
}
