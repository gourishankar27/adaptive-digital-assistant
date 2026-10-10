package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.MemoryController
import dev.ada.assistant.ui.MemoryDraft
import dev.ada.assistant.ui.MemoryScreen
import java.io.File
import java.util.UUID
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

internal val MEMORY_RECOVERY_NOTE = "The synthetic recovery project uses Oxford Blue. 😀 e\u0301\r\n日本語 العربية 中文.\r\n" +
    "Long accessible evidence stays exact across process interruption. ".repeat(18)

/** Stage one: real note commits; the explicit test adapter fails before any claim POST. */
class MemoryRecoveryPrepareTest {
    @Test fun prepareNoteSuccessAndClaimFailure() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue("Run the explicit memory force-stop recovery stages", InstrumentationRegistry.getArguments().getString("adaMemoryRecovery") == "true")
        val context = instrumentation.targetContext
        val tokenFile = File(context.filesDir, "foundation-test-token")
        assumeTrue("Provision the disposable Android fixture server", tokenFile.isFile)
        val store = AndroidSessionStore(context)
        store.clear()
        val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
        var controller: MemoryController? = null
        var prepared = false
        try {
            val token = tokenFile.readText().trim()
            val connection = checkNotNull(ConnectionCredential.parse("http://10.0.2.2:18764", token, true))
            val actual = HttpAdaApi()
            val me = success(actual.me(connection))
            val features = success(actual.capabilities(connection))
            assertEquals("Foundation Test", me.name)
            assertEquals("v1", features.api_version)
            assertEquals("server", features.authority)
            assertTrue(features.structured_memory && features.memory_writes == "explicit_user_assertions")
            val identity = SessionIdentity(connection.server.toString(), me.id)
            val ownedScope = success(actual.createScope(connection, ScopeInputDto("Memory process recovery verification")))
            store.saveCredential(StoredCredential(identity, token))
            val failing = BeforeClaimPostApi(actual)
            val memory = MemoryController(failing, store, scope) { error("Synthetic authenticated identity was unexpectedly revoked") }
            controller = memory
            withContext(Dispatchers.Main) { memory.setVerifiedSession(connection, identity, features); memory.activate() }
            await { memory.state.value.scopes.items.any { it.id == ownedScope.id } && !memory.state.value.scopes.loading }
            withContext(Dispatchers.Main) {
                memory.selectScope(ownedScope.id)
                memory.beginRemember()
                memory.updateDraft(MemoryDraft(note = MEMORY_RECOVERY_NOTE, subject = "Recovery project",
                    predicate = "color", value = "Oxford Blue", kind = "decision", validFrom = "2026-01-01T00:00:00.123Z"))
                memory.preview()
            }
            assertEquals(MemoryScreen.Preview, memory.state.value.screen)
            val reservation = checkNotNull(memory.state.value.preview).reservation
            assertTrue(reservation.note?.content == MEMORY_RECOVERY_NOTE)
            withContext(Dispatchers.Main) { memory.savePreview() }
            await { !memory.state.value.saving && memory.state.value.pending?.source != null }
            assertEquals(ApiFailure.Timeout, memory.state.value.fault)
            assertEquals(1, failing.notes.get())
            assertEquals(1, failing.claimAttempts.get())
            val pending = checkNotNull(store.memoryPending(identity))
            assertTrue(pending.reservation == reservation)
            assertTrue(pending.source?.content == MEMORY_RECOVERY_NOTE)
            assertTrue(pending.claimInput() == failing.attemptedClaim)
            assertEquals(reservation.note?.source_id, pending.source?.source_id)
            assertEquals(1, success(actual.sources(connection, ownedScope.id)).size)
            assertTrue(success(actual.claims(connection, ownedScope.id, history = true)).isEmpty())
            assertEquals(ApiFailure.NotFound, (actual.claim(connection, reservation.claimId) as ApiResult.Failure).reason)
            prepared = true
            // Only source/claim identifiers are emitted; no credential, note, hash or annotation.
            instrumentation.sendStatus(0, Bundle().apply {
                putString("recoveryMemorySource", checkNotNull(pending.source).source_id.toString())
                putString("recoveryMemoryClaim", reservation.claimId.toString())
            })
        } finally {
            withContext(Dispatchers.Main) { controller?.reset() }
            scope.cancel()
            if (!prepared) store.clear()
        }
        // verify-emulator.ps1 now force-stops the target process before the resume class.
    }

    private suspend fun await(ready: () -> Boolean) = withTimeout(20_000) { while (!ready()) delay(50) }
    private fun <T> success(result: ApiResult<T>): T {
        check(result is ApiResult.Success) { "The synthetic authenticated HTTP prerequisite failed" }
        return result.value
    }
    private class BeforeClaimPostApi(private val actual: AdaApi) : AdaApi by actual {
        val notes = AtomicInteger()
        val claimAttempts = AtomicInteger()
        @Volatile var attemptedClaim: ClaimInputDto? = null
        override suspend fun createNote(connection: ConnectionCredential, scope: UUID, body: NoteInputDto): ApiResult<SourceVersionDto> {
            notes.incrementAndGet()
            return actual.createNote(connection, scope, body)
        }
        override suspend fun createClaim(connection: ConnectionCredential, scope: UUID, body: ClaimInputDto): ApiResult<ClaimDto> {
            claimAttempts.incrementAndGet(); attemptedClaim = body
            return ApiResult.Failure(ApiFailure.Timeout) // Explicit simulation: this call never reaches HTTP.
        }
    }
}
