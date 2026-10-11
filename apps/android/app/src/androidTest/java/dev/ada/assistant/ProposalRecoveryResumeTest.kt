package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class ProposalRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun exactReviewReceiptSurvivesActualForceStop() {
        val args = InstrumentationRegistry.getArguments(); assumeTrue(args.getString("adaProposalRecovery") == "true")
        val expected = UUID.fromString(args.getString("expectedProposalReview")); vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null && vm.proposals.state.value.pending?.operationId == expected && !vm.proposals.state.value.busy }
        val store = AndroidSessionStore(compose.activity.applicationContext); val saved = runBlocking { store.readCredential() }!!; val pending = runBlocking { store.proposalPending(saved.identity) }!!
        assertEquals(expected, pending.operationId); assertNotNull(runBlocking { store.proposalDraft(saved.identity) })
        val conn = ConnectionCredential.parse(saved.identity.server, saved.token, true)!!; val api = HttpAdaApi(); val before = runBlocking { success(api.reviewReceipt(conn, expected)) }
        assertEquals(1, runBlocking { success(api.claims(conn, pending.scopeId)) }.size)
        compose.runOnIdle { vm.navigate(ChatDestination.Proposals) }
        compose.onNodeWithTag("proposal-retry").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.proposals.state.value.pending == null && !vm.proposals.state.value.busy }
        assertNull(runBlocking { store.proposalPending(saved.identity) }); assertEquals(before, runBlocking { success(api.reviewReceipt(conn, expected)) })
        assertEquals(1, runBlocking { success(api.claims(conn, pending.scopeId)) }.size)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
