@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.system.Os
import android.system.OsConstants
import android.util.AtomicFile
import dev.ada.assistant.BuildConfig
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.security.KeyStore
import java.security.MessageDigest
import java.time.OffsetDateTime
import java.util.UUID
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

/** Construct this identity from the normalized connection and authenticated /me response. */
@Serializable
data class SessionIdentity(val server: String, val owner: UUID) {
    init {
        val parsed = ConnectionCredential.parse(server, "identity-validation", true)
        require(parsed != null && parsed.server.toString() == server && server.length <= 2048) {
            "Invalid session identity"
        }
    }
}

@Serializable
class StoredCredential(val identity: SessionIdentity, val token: String) {
    init {
        require(ConnectionCredential.parse(identity.server, token, true) != null) { "Invalid stored credential" }
    }
    override fun toString() = "StoredCredential(redacted)"
}

/** Immutable exact reservation; changing an option/content requires a consciously new request. */
@Serializable
data class PendingMessage(val identity: SessionIdentity, val conversationId: UUID, val body: ChatInputDto,
    val voiceTranscript: TranscriptInputDto? = null, val voiceScopeId: UUID? = null) {
    override fun toString() = "PendingMessage(redacted)"
}

interface SessionStore {
    suspend fun voiceDraft(identity: SessionIdentity): VoiceDraft? = null
    suspend fun saveVoiceDraft(draft: VoiceDraft) { throw SessionStorageException() }
    suspend fun removeVoiceDraft(identity: SessionIdentity, transcript: UUID) { throw SessionStorageException() }
    suspend fun expressionJournal(identity: SessionIdentity): ExpressionJournal? = null
    suspend fun learningJournal(identity: SessionIdentity): LearningJournal? = null
    suspend fun saveLearningJournal(journal: LearningJournal) { throw SessionStorageException() }
    suspend fun removeLearningJournal(identity: SessionIdentity, operationId: UUID) { throw SessionStorageException() }
    suspend fun saveExpressionJournal(journal: ExpressionJournal) { throw SessionStorageException() }
    suspend fun removeExpressionJournal(identity: SessionIdentity, operationId: UUID) { throw SessionStorageException() }
    suspend fun consolidationJournal(identity: SessionIdentity): ConsolidationJournal? = null
    suspend fun saveConsolidationJournal(journal: ConsolidationJournal) { throw SessionStorageException() }
    suspend fun removeConsolidationJournal(identity: SessionIdentity, jobId: UUID) { throw SessionStorageException() }
    suspend fun agentJournal(identity: SessionIdentity): AgentJournal? = null
    suspend fun saveAgentJournal(journal: AgentJournal) { throw SessionStorageException() }
    suspend fun removeAgentJournal(identity: SessionIdentity, runId: UUID) { throw SessionStorageException() }
    /** Stored identity is a recovery binding, never proof that the token is still authorized. */
    suspend fun readCredential(): StoredCredential?
    /** Call only after /me and capabilities verify the owner and server. */
    suspend fun saveCredential(credential: StoredCredential)
    suspend fun clear()
    suspend fun pending(identity: SessionIdentity): PendingMessage?
    /** Must succeed before POST; a different pending reservation is never overwritten. */
    suspend fun savePending(message: PendingMessage)
    suspend fun removePending(identity: SessionIdentity, requestId: UUID)
    suspend fun memoryPending(identity: SessionIdentity): PendingMemory? = null
    /** Must commit the exact identity/scope-bound reservation before either memory POST. */
    suspend fun saveMemoryPending(pending: PendingMemory) { throw SessionStorageException() }
    suspend fun removeMemoryPending(identity: SessionIdentity, claimId: UUID) { throw SessionStorageException() }
    suspend fun documentPending(identity: SessionIdentity): PendingDocument? = null
    suspend fun saveDocumentPending(pending: PendingDocument) { throw SessionStorageException() }
    suspend fun removeDocumentPending(identity: SessionIdentity, uploadId: UUID) { throw SessionStorageException() }
    suspend fun entityPending(identity: SessionIdentity): PendingEntity? = null
    suspend fun saveEntityPending(pending: PendingEntity) { throw SessionStorageException() }
    suspend fun removeEntityPending(identity: SessionIdentity, operationId: UUID) { throw SessionStorageException() }
    suspend fun proposalPending(identity: SessionIdentity): PendingProposal? = null
    suspend fun saveProposalPending(pending: PendingProposal) { throw SessionStorageException() }
    suspend fun removeProposalPending(identity: SessionIdentity, operationId: UUID) { throw SessionStorageException() }
    suspend fun proposalDraft(identity: SessionIdentity): ProposalDraft? = null
    suspend fun saveProposalDraft(draft: ProposalDraft) { throw SessionStorageException() }
    suspend fun removeProposalDraft(identity: SessionIdentity) { throw SessionStorageException() }
}

enum class SessionStoreFailure { Unavailable, IdentityMismatch, PendingConflict, InvalidPayload }
class SessionStorageException(val failure: SessionStoreFailure = SessionStoreFailure.Unavailable) :
    IOException(when (failure) {
        SessionStoreFailure.Unavailable -> "Secure session storage is unavailable. Reconnect before sending."
        SessionStoreFailure.IdentityMismatch -> "The request belongs to a different connection. Reconnect before sending."
        SessionStoreFailure.PendingConflict -> "Resolve the existing pending request before sending another."
        SessionStoreFailure.InvalidPayload -> "The pending request cannot be stored. Check the message and time options."
    }) // No nested exception, input, credential, private text or filesystem path is exposed.

/** Only the Keystore-backed implementation is wired by production clients. */
class AndroidSessionStore(context: Context) : SessionStore by EncryptedSessionStore(
    AtomicSessionDisk(File(context.applicationContext.noBackupFilesDir, FILE_NAME)),
    AesGcmSessionCipher(AndroidSessionKeys(KEY_ALIAS)),
    BuildConfig.DEBUG,
) {
    companion object {
        internal const val FILE_NAME = "ada-secure-session-v1.bin"
        internal const val KEY_ALIAS = "ada.secure-session.aes-gcm.v1"
    }
}

/** Preserves the Phase 03 token interface without introducing another persistence format. */
class SessionTokenStorageAdapter(private val sessions: SessionStore) : SecureTokenStorage {
    override suspend fun save(server: String, owner: UUID, token: String) =
        sessions.saveCredential(StoredCredential(SessionIdentity(server, owner), token))
    override suspend fun load(server: String, owner: UUID): String? =
        sessions.readCredential()?.takeIf { it.identity == SessionIdentity(server, owner) }?.token
    override suspend fun clear() = sessions.clear()
}

@Serializable
private data class PersistedSession(
    val version: Int = 10,
    val credential: StoredCredential,
    val pending: PendingMessage? = null,
    val memoryPending: PendingMemory? = null,
    val documentPending: PendingDocument? = null,
    val entityPending: PendingEntity? = null,
    val proposalPending: PendingProposal? = null,
    val proposalDraft: ProposalDraft? = null,
    val agentJournal: AgentJournal? = null,
    val consolidationJournal: ConsolidationJournal? = null,
    val expressionJournal: ExpressionJournal? = null,
    val learningJournal: LearningJournal? = null,
    val voiceDraft: VoiceDraft? = null,
)

internal interface SessionDisk {
    fun read(maxBytes: Int): ByteArray?
    /** Atomic commit: an interrupted write preserves the previously committed bytes. */
    fun write(bytes: ByteArray)
    fun delete()
}
internal interface SessionKeys {
    fun existing(): SecretKey?
    fun create(): SecretKey
    fun delete()
}
internal interface SessionCipher {
    fun encrypt(plaintext: ByteArray): ByteArray
    fun decrypt(ciphertext: ByteArray): ByteArray
    fun deleteKey()
}

internal class EncryptedSessionStore(
    private val disk: SessionDisk,
    private val cipher: SessionCipher,
    private val allowDebugHttp: Boolean,
) : SessionStore {
    companion object {
        internal const val MAX_PLAINTEXT_BYTES = 256 * 1024
        internal const val MAX_FILE_BYTES = MAX_PLAINTEXT_BYTES + 128
        // AtomicFile itself does not serialize callers. All instances in this app process share this lock.
        private val transactions = Mutex()
    }
    private val json = Json { encodeDefaults = true; explicitNulls = true; ignoreUnknownKeys = false }
    private suspend fun <T> transaction(block: () -> T): T = withContext(Dispatchers.IO) {
        transactions.withLock { block() }
    }

    override suspend fun readCredential(): StoredCredential? = transaction { read()?.credential }
    override suspend fun voiceDraft(identity: SessionIdentity): VoiceDraft? = transaction { read()?.takeIf { it.credential.identity == identity }?.voiceDraft }
    override suspend fun saveVoiceDraft(draft: VoiceDraft) = transaction {
        try { validateVoiceDraft(draft) } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
        val previous = read()
        if (previous == null || previous.credential.identity != draft.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        previous.voiceDraft?.let {
            if (it.conversationId != draft.conversationId || it.scopeId != draft.scopeId || it.transcript != draft.transcript) {
                throw SessionStorageException(SessionStoreFailure.PendingConflict)
            }
        }
        if (previous.pending?.voiceTranscript?.transcript_id == draft.transcript.transcript_id) throw SessionStorageException(SessionStoreFailure.PendingConflict)
        write(previous.copy(voiceDraft = draft))
    }
    override suspend fun removeVoiceDraft(identity: SessionIdentity, transcript: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.voiceDraft?.transcript?.transcript_id == transcript) write(previous.copy(voiceDraft = null))
    }
    override suspend fun learningJournal(identity: SessionIdentity): LearningJournal? = transaction { read()?.takeIf { it.credential.identity == identity }?.learningJournal }
    override suspend fun saveLearningJournal(journal: LearningJournal) = transaction {
        try { validateLearningJournal(journal) } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
        val previous = read()
        if (previous == null || previous.credential.identity != journal.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        if (previous.learningJournal != null && previous.learningJournal != journal) throw SessionStorageException(SessionStoreFailure.PendingConflict)
        write(previous.copy(learningJournal = journal))
    }
    override suspend fun removeLearningJournal(identity: SessionIdentity, operationId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.learningJournal?.operationId == operationId) write(previous.copy(learningJournal = null))
    }
    override suspend fun expressionJournal(identity: SessionIdentity): ExpressionJournal? = transaction { read()?.takeIf { it.credential.identity == identity }?.expressionJournal }
    override suspend fun saveExpressionJournal(journal: ExpressionJournal) = transaction {
        try { validateExpressionJournal(journal) } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
        val previous = read()
        if (previous == null || previous.credential.identity != journal.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        if (previous.expressionJournal != null && previous.expressionJournal != journal) throw SessionStorageException(SessionStoreFailure.PendingConflict)
        write(previous.copy(expressionJournal = journal))
    }
    override suspend fun removeExpressionJournal(identity: SessionIdentity, operationId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.expressionJournal?.operationId == operationId) write(previous.copy(expressionJournal = null))
    }
    override suspend fun consolidationJournal(identity: SessionIdentity): ConsolidationJournal? = transaction { read()?.takeIf { it.credential.identity == identity }?.consolidationJournal }
    override suspend fun saveConsolidationJournal(journal: ConsolidationJournal) = transaction {
        try { validateConsolidationJournal(journal) } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
        val previous = read()
        if (previous == null || previous.credential.identity != journal.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        if (previous.consolidationJournal != null && previous.consolidationJournal != journal) throw SessionStorageException(SessionStoreFailure.PendingConflict)
        write(previous.copy(consolidationJournal = journal))
    }
    override suspend fun removeConsolidationJournal(identity: SessionIdentity, jobId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.consolidationJournal?.jobId == jobId) write(previous.copy(consolidationJournal = null))
    }
    override suspend fun agentJournal(identity: SessionIdentity): AgentJournal? = transaction {
        read()?.takeIf { it.credential.identity == identity }?.agentJournal
    }
    override suspend fun saveAgentJournal(journal: AgentJournal) = transaction {
        try { validateAgentJournal(journal) } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
        val previous = read()
        if (previous == null || previous.credential.identity != journal.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        previous.agentJournal?.let { old ->
            if (old.copy(operation = null) != journal.copy(operation = null) ||
                (old.operation != null && journal.operation != null && old.operation != journal.operation)) throw SessionStorageException(SessionStoreFailure.PendingConflict)
        }
        write(previous.copy(agentJournal = journal))
    }
    override suspend fun removeAgentJournal(identity: SessionIdentity, runId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.agentJournal?.runId == runId) write(previous.copy(agentJournal = null))
    }
    override suspend fun pending(identity: SessionIdentity): PendingMessage? = transaction {
        read()?.takeIf { it.credential.identity == identity }?.pending?.takeIf { it.identity == identity }
    }
    override suspend fun memoryPending(identity: SessionIdentity): PendingMemory? = transaction {
        read()?.takeIf { it.credential.identity == identity }?.memoryPending?.takeIf { it.reservation.identity == identity }
    }
    override suspend fun documentPending(identity: SessionIdentity): PendingDocument? = transaction {
        read()?.takeIf { it.credential.identity == identity }?.documentPending?.takeIf { it.identity == identity }
    }
    override suspend fun entityPending(identity: SessionIdentity): PendingEntity? = transaction {
        read()?.takeIf { it.credential.identity == identity }?.entityPending?.takeIf { it.identity == identity }
    }
    override suspend fun proposalPending(identity: SessionIdentity): PendingProposal? = transaction {
        read()?.takeIf { it.credential.identity == identity }?.proposalPending?.takeIf { it.identity == identity }
    }
    override suspend fun proposalDraft(identity: SessionIdentity): ProposalDraft? = transaction {
        read()?.takeIf { it.credential.identity == identity }?.proposalDraft?.takeIf { it.identity == identity }
    }
    override suspend fun saveCredential(credential: StoredCredential) = transaction {
        validateCredential(credential)
        val previous = read()
        val sameIdentity = previous?.credential?.identity == credential.identity
        write(PersistedSession(credential = credential,
            pending = previous?.pending?.takeIf { sameIdentity && it.identity == credential.identity },
            memoryPending = previous?.memoryPending?.takeIf { sameIdentity && it.reservation.identity == credential.identity },
            documentPending = previous?.documentPending?.takeIf { sameIdentity && it.identity == credential.identity },
            entityPending = previous?.entityPending?.takeIf { sameIdentity && it.identity == credential.identity },
            proposalPending = previous?.proposalPending?.takeIf { sameIdentity && it.identity == credential.identity },
            proposalDraft = previous?.proposalDraft?.takeIf { sameIdentity && it.identity == credential.identity },
            agentJournal = previous?.agentJournal?.takeIf { sameIdentity && it.identity == credential.identity },
            consolidationJournal = previous?.consolidationJournal?.takeIf { sameIdentity && it.identity == credential.identity },
            expressionJournal = previous?.expressionJournal?.takeIf { sameIdentity && it.identity == credential.identity },
            learningJournal = previous?.learningJournal?.takeIf { sameIdentity && it.identity == credential.identity },
            voiceDraft = previous?.voiceDraft?.takeIf { sameIdentity && it.identity == credential.identity },
        ))
    }
    override suspend fun savePending(message: PendingMessage) = transaction {
        validatePending(message)
        val previous = read()
        if (previous == null || previous.credential.identity != message.identity) {
            throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        }
        if (previous.pending != null && previous.pending != message) {
            throw SessionStorageException(SessionStoreFailure.PendingConflict)
        }
        val voice = message.voiceTranscript
        if (voice != null && previous.pending == null) {
            val draft = previous.voiceDraft
            if (draft == null || !draft.approved || draft.identity != message.identity ||
                draft.conversationId != message.conversationId || draft.scopeId != message.voiceScopeId ||
                draft.transcript != voice || draft.reviewedText != message.body.content) {
                throw SessionStorageException(SessionStoreFailure.InvalidPayload)
            }
        }
        write(previous.copy(pending = message, voiceDraft = if (voice != null) null else previous.voiceDraft))
    }
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.pending?.identity == identity &&
            previous.pending.body.request_id == requestId) {
            write(previous.copy(pending = null))
        }
    }
    override suspend fun saveMemoryPending(pending: PendingMemory) = transaction {
        validateMemoryPending(pending)
        val previous = read()
        if (previous == null || previous.credential.identity != pending.reservation.identity) {
            throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        }
        previous.memoryPending?.let { committed ->
            if (committed.reservation != pending.reservation ||
                (committed.source != null && committed.source != pending.source)) {
                throw SessionStorageException(SessionStoreFailure.PendingConflict)
            }
        }
        write(previous.copy(memoryPending = pending))
    }
    override suspend fun removeMemoryPending(identity: SessionIdentity, claimId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.memoryPending?.reservation?.identity == identity &&
            previous.memoryPending.reservation.claimId == claimId) {
            write(previous.copy(memoryPending = null))
        }
    }
    override suspend fun saveDocumentPending(pending: PendingDocument) = transaction {
        validateDocument(pending)
        val previous = read()
        if (previous == null || previous.credential.identity != pending.identity) {
            throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        }
        if (previous.documentPending != null && previous.documentPending != pending) {
            throw SessionStorageException(SessionStoreFailure.PendingConflict)
        }
        write(previous.copy(documentPending = pending))
    }
    override suspend fun removeDocumentPending(identity: SessionIdentity, uploadId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.documentPending?.identity == identity &&
            previous.documentPending.uploadId == uploadId) write(previous.copy(documentPending = null))
    }
    override suspend fun saveEntityPending(pending: PendingEntity) = transaction {
        validateEntityPending(pending)
        val previous = read()
        if (previous == null || previous.credential.identity != pending.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        if (previous.entityPending != null && previous.entityPending != pending) throw SessionStorageException(SessionStoreFailure.PendingConflict)
        write(previous.copy(entityPending = pending))
    }
    override suspend fun removeEntityPending(identity: SessionIdentity, operationId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.entityPending?.identity == identity && previous.entityPending.operationId == operationId) write(previous.copy(entityPending = null))
    }
    override suspend fun clear() = transaction { destroy() }
    override suspend fun saveProposalPending(pending: PendingProposal) = transaction {
        validateProposalPending(pending)
        val previous = read()
        if (previous == null || previous.credential.identity != pending.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        if (previous.proposalPending != null && previous.proposalPending != pending) throw SessionStorageException(SessionStoreFailure.PendingConflict)
        write(previous.copy(proposalPending = pending))
    }
    override suspend fun removeProposalPending(identity: SessionIdentity, operationId: UUID) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity && previous.proposalPending?.operationId == operationId) write(previous.copy(proposalPending = null))
    }
    override suspend fun saveProposalDraft(draft: ProposalDraft) = transaction {
        validateProposalDraft(draft)
        val previous = read()
        if (previous == null || previous.credential.identity != draft.identity) throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        write(previous.copy(proposalDraft = draft))
    }
    override suspend fun removeProposalDraft(identity: SessionIdentity) = transaction {
        val previous = read() ?: return@transaction
        if (previous.credential.identity == identity) write(previous.copy(proposalDraft = null))
    }

    private fun validateCredential(credential: StoredCredential) {
        if (ConnectionCredential.parse(credential.identity.server, credential.token, allowDebugHttp) == null) {
            throw SessionStorageException(SessionStoreFailure.IdentityMismatch)
        }
    }
    private fun validatePending(message: PendingMessage) {
        if ((message.voiceTranscript == null) != (message.voiceScopeId == null)) throw SessionStorageException(SessionStoreFailure.InvalidPayload)
        message.voiceTranscript?.let {
            try { validateTranscript(it) } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
        }
        val body = message.body
        val content = body.content
        var index = 0
        while (index < content.length) {
            val char = content[index]
            if (char.isHighSurrogate()) {
                if (index + 1 >= content.length || !content[index + 1].isLowSurrogate()) {
                    throw SessionStorageException(SessionStoreFailure.InvalidPayload)
                }
                index += 2
            } else {
                if (char.isLowSurrogate() || char == '\u0000') throw SessionStorageException(SessionStoreFailure.InvalidPayload)
                index++
            }
        }
        if (content.isBlank() || content.codePointCount(0, content.length) !in 1..4000) {
            throw SessionStorageException(SessionStoreFailure.InvalidPayload)
        }
        body.as_of?.let {
            try {
                if (it.length > 64 || OffsetDateTime.parse(it).nano % 1_000_000 != 0) {
                    throw SessionStorageException(SessionStoreFailure.InvalidPayload)
                }
            } catch (_: Exception) { throw SessionStorageException(SessionStoreFailure.InvalidPayload) }
        }
    }

    private fun read(): PersistedSession? {
        var plaintext: ByteArray? = null
        try {
            val bytes = disk.read(MAX_FILE_BYTES) ?: return null
            plaintext = cipher.decrypt(bytes)
            if (plaintext.size > MAX_PLAINTEXT_BYTES) throw IOException("Invalid session record")
            val snapshot = json.decodeFromString<PersistedSession>(plaintext.toString(Charsets.UTF_8))
            if (snapshot.version < 10 && (snapshot.voiceDraft != null || snapshot.pending?.voiceTranscript != null || snapshot.pending?.voiceScopeId != null)) throw IOException("Unsupported session record")
            if (snapshot.version !in 1..10 || (snapshot.version == 1 && snapshot.memoryPending != null) ||
                (snapshot.version < 3 && snapshot.documentPending != null) || (snapshot.version < 4 && snapshot.entityPending != null) ||
                (snapshot.version < 5 && (snapshot.proposalPending != null || snapshot.proposalDraft != null)) || (snapshot.version < 6 && snapshot.agentJournal != null) || (snapshot.version < 7 && snapshot.consolidationJournal != null) || (snapshot.version < 8 && snapshot.expressionJournal != null) || (snapshot.version < 9 && snapshot.learningJournal != null)) {
                throw IOException("Unsupported session record")
            }
            validateCredential(snapshot.credential)
            snapshot.voiceDraft?.let {
                if (it.identity != snapshot.credential.identity || snapshot.pending?.voiceTranscript?.transcript_id == it.transcript.transcript_id) throw IOException("Invalid session binding")
                validateVoiceDraft(it)
            }
            snapshot.pending?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validatePending(it)
            }
            snapshot.memoryPending?.let {
                if (it.reservation.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateMemoryPending(it)
            }
            snapshot.documentPending?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateDocument(it)
            }
            snapshot.entityPending?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateEntityPending(it)
            }
            snapshot.proposalPending?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateProposalPending(it)
            }
            snapshot.proposalDraft?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateProposalDraft(it)
            }
            snapshot.agentJournal?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateAgentJournal(it)
            }
            snapshot.consolidationJournal?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateConsolidationJournal(it)
            }
            snapshot.expressionJournal?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateExpressionJournal(it)
            }
            snapshot.learningJournal?.let {
                if (it.identity != snapshot.credential.identity) throw IOException("Invalid session binding")
                validateLearningJournal(it)
            }
            return snapshot
        } catch (error: Exception) {
            if (error is CancellationException) throw error
            // Key loss, tampering and unknown local formats fail closed: reconnect, never replay.
            destroy()
            return null
        } finally { plaintext?.fill(0) }
    }
    private fun write(snapshot: PersistedSession) {
        var plaintext: ByteArray? = null
        try {
            plaintext = json.encodeToString(snapshot.copy(version = 10)).toByteArray(Charsets.UTF_8)
            if (plaintext.size > MAX_PLAINTEXT_BYTES) throw SessionStorageException(SessionStoreFailure.InvalidPayload)
            val ciphertext = cipher.encrypt(plaintext)
            if (ciphertext.size > MAX_FILE_BYTES) throw SessionStorageException(SessionStoreFailure.InvalidPayload)
            disk.write(ciphertext)
        } catch (error: Exception) {
            if (error is CancellationException || error is SessionStorageException) throw error
            throw SessionStorageException()
        } finally { plaintext?.fill(0) }
    }
    private fun destroy() {
        var failed = false
        try { disk.delete() } catch (_: Exception) { failed = true }
        // Crypto-shredding also protects an undeletable damaged record. No key read is required.
        try { cipher.deleteKey() } catch (_: Exception) { failed = true }
        if (failed) throw SessionStorageException()
    }
}

internal class AndroidSessionKeys(private val alias: String) : SessionKeys {
    private fun store() = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    override fun existing(): SecretKey? = store().getKey(alias, null) as? SecretKey
    override fun create(): SecretKey = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").apply {
        init(KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setRandomizedEncryptionRequired(true)
            .setUserAuthenticationRequired(false)
            .build())
    }.generateKey()
    override fun delete() { store().deleteEntry(alias) }
}

internal class AesGcmSessionCipher(private val keys: SessionKeys) : SessionCipher {
    private val header = byteArrayOf(0x41, 0x44, 0x41, 0x53, 0x01)
    override fun encrypt(plaintext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, keys.existing() ?: keys.create())
        cipher.updateAAD(header)
        val iv = cipher.iv
        require(iv.size == 12) { "Invalid session IV" }
        return header + iv + cipher.doFinal(plaintext)
    }
    override fun decrypt(ciphertext: ByteArray): ByteArray {
        require(ciphertext.size >= header.size + 12 + 16 && ciphertext.copyOfRange(0, header.size).contentEquals(header)) {
            "Invalid encrypted session"
        }
        val key = keys.existing() ?: throw IOException("Session key is unavailable")
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, ciphertext.copyOfRange(header.size, header.size + 12)))
        cipher.updateAAD(header)
        return cipher.doFinal(ciphertext, header.size + 12, ciphertext.size - header.size - 12)
    }
    override fun deleteKey() = keys.delete()
}

internal class AtomicSessionDisk(private val file: File) : SessionDisk {
    private val atomic = AtomicFile(file)
    override fun read(maxBytes: Int): ByteArray? {
        if (!file.exists() && !File(file.path + ".bak").exists()) return null
        atomic.openRead().use { stream ->
            val output = ByteArrayOutputStream()
            val buffer = ByteArray(4096)
            while (true) {
                val count = stream.read(buffer)
                if (count < 0) break
                if (output.size() + count > maxBytes) throw IOException("Session file bound exceeded")
                output.write(buffer, 0, count)
            }
            return output.toByteArray()
        }
    }
    override fun write(bytes: ByteArray) {
        var stream: FileOutputStream? = null
        try {
            stream = atomic.startWrite()
            stream.write(bytes)
            stream.fd.sync() // A failed fsync prevents network submission by throwing to the caller.
            atomic.finishWrite(stream)
            stream = null // finishWrite owns/closed it; post-commit failures must not remove the committed record.
            val directory = Os.open(checkNotNull(file.parentFile).path, OsConstants.O_RDONLY, 0)
            try { Os.fsync(directory) } finally { Os.close(directory) }
            // AtomicFile may log a rename error instead of throwing. Verify the committed ciphertext.
            if (!MessageDigest.isEqual(read(EncryptedSessionStore.MAX_FILE_BYTES), bytes)) {
                throw IOException("Session commit failed")
            }
        } catch (error: Exception) {
            stream?.let { atomic.failWrite(it) }
            throw error
        }
    }
    override fun delete() {
        atomic.delete()
        if (listOf(file, File(file.path + ".bak"), File(file.path + ".new")).any { it.exists() }) {
            throw IOException("Session file removal failed")
        }
    }
}
