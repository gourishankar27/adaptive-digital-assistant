package dev.ada.assistant

import androidx.compose.ui.test.assertIsFocused
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import dev.ada.assistant.ui.MemoryScreen
import java.time.Instant
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Stage two uses production restoration/Keystore/controller after an actual adb force-stop. */
class MemoryRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel

    @Test fun resumesOriginalMemoryAfterProcessStopWithoutDuplicates() {
        val arguments = InstrumentationRegistry.getArguments()
        assumeTrue("Run the explicit memory force-stop recovery stages", arguments.getString("adaMemoryRecovery") == "true")
        val expectedSource = UUID.fromString(checkNotNull(arguments.getString("expectedMemorySource")))
        val expectedClaim = UUID.fromString(checkNotNull(arguments.getString("expectedMemoryClaim")))
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) {
            vm.state.value.account != null && !vm.state.value.connecting &&
                vm.memory.state.value.pending?.reservation?.claimId == expectedClaim
        }
        val store = AndroidSessionStore(compose.activity.applicationContext)
        val saved = checkNotNull(runBlocking { store.readCredential() })
        assertEquals(vm.state.value.account?.owner, saved.identity.owner)
        val pending = checkNotNull(runBlocking { store.memoryPending(saved.identity) })
        assertEquals(expectedClaim, pending.reservation.claimId)
        assertEquals(expectedSource, pending.reservation.note?.source_id)
        assertEquals(expectedSource, pending.source?.source_id)
        assertTrue(pending.reservation.note?.content == MEMORY_RECOVERY_NOTE)
        assertTrue(pending.source?.content == MEMORY_RECOVERY_NOTE)
        val originalInput = pending.claimInput()
        val connection = checkNotNull(ConnectionCredential.parse(saved.identity.server, saved.token, true))
        val api = HttpAdaApi()
        // Restore is verification only; no claim is submitted until the user presses Resume.
        assertEquals(ApiFailure.NotFound, (runBlocking { api.claim(connection, expectedClaim) } as ApiResult.Failure).reason)
        assertEquals(1, runBlocking { success(api.sources(connection, pending.reservation.scopeId)) }.size)
        compose.runOnIdle { vm.navigate(ChatDestination.Memory) }
        compose.waitUntil(15_000) { !vm.memory.state.value.scopes.loading && !vm.memory.state.value.claims.loading }
        compose.onNodeWithTag("memory-resume-pending").performScrollTo().performClick()
        compose.waitUntil(20_000) {
            val memory = vm.memory.state.value
            memory.pending == null && !memory.saving && memory.screen == MemoryScreen.Detail &&
                memory.detail?.id == expectedClaim && memory.evidenceVerified
        }
        val memory = vm.memory.state.value
        val restored = checkNotNull(memory.detail)
        val source = checkNotNull(memory.detailSource)
        assertEquals(originalInput.claim_id, restored.id)
        assertEquals(originalInput.source_version_id, restored.evidence.source_version_id)
        assertEquals(originalInput.span_start, restored.evidence.span_start)
        assertEquals(originalInput.span_end, restored.evidence.span_end)
        assertTrue(restored.subject == originalInput.subject && restored.predicate == originalInput.predicate &&
            restored.value == originalInput.value && restored.kind == originalInput.kind)
        assertEquals(Instant.parse(originalInput.valid_from).toEpochMilli(), restored.valid_from)
        assertTrue(restored.evidence.quote == MEMORY_RECOVERY_NOTE && verifyClaimEvidence(restored, source))
        assertTrue(source == pending.source)
        assertNull(runBlocking { store.memoryPending(saved.identity) })
        assertNull(runBlocking { store.pending(saved.identity) })
        val sources = runBlocking { success(api.sources(connection, pending.reservation.scopeId)) }
        val claims = runBlocking { success(api.claims(connection, pending.reservation.scopeId, history = true)) }
        assertEquals(listOf(expectedSource), sources.map { it.source_id })
        assertEquals(listOf(expectedClaim), claims.map { it.id })
        assertTrue(runBlocking { success(api.createClaim(connection, pending.reservation.scopeId, originalInput)) } == restored)
        assertEquals(1, runBlocking { success(api.claims(connection, pending.reservation.scopeId, history = true)) }.size)
        compose.onNodeWithTag("memory-detail-quote").performScrollTo().assertTextContains(MEMORY_RECOVERY_NOTE)
        compose.onNodeWithTag("memory-detail-source").performScrollTo().assertTextContains(MEMORY_RECOVERY_NOTE)
        // Exercise keyboard, validation focus and long evidence preview without submitting a new write.
        compose.onNodeWithTag("memory-correct").performScrollTo().performClick()
        compose.onNodeWithTag("memory-preview").performScrollTo().performClick()
        compose.onNodeWithTag("memory-error").performScrollTo().assertIsFocused()
        compose.onNodeWithTag("memory-value").performScrollTo().performTextInput("Olive Green")
        compose.onNodeWithTag("memory-valid-from").performScrollTo().performTextInput("2090-01-01T00:00:00.321Z")
        compose.onNodeWithTag("memory-note").performScrollTo().performTextInput(MEMORY_RECOVERY_NOTE)
        closeSoftKeyboard()
        compose.onNodeWithTag("memory-preview").performScrollTo().performClick()
        compose.waitUntil(5_000) { vm.memory.state.value.screen == MemoryScreen.Preview }
        assertEquals(expectedClaim, vm.memory.state.value.preview?.reservation?.corrects?.id)
        compose.onNodeWithTag("memory-preview-quote").performScrollTo().assertTextContains(MEMORY_RECOVERY_NOTE)
        assertTrue(runBlocking { success(api.claim(connection, expectedClaim)) } == restored)
        assertNull(runBlocking { store.memoryPending(saved.identity) })
    }

    @After fun clearSyntheticRecoveryState() {
        if (::vm.isInitialized) compose.runOnIdle { vm.logout() }
        runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() }
    }

    private fun <T> success(result: ApiResult<T>): T {
        check(result is ApiResult.Success) { "The synthetic authenticated memory HTTP verification failed" }
        return result.value
    }
}
