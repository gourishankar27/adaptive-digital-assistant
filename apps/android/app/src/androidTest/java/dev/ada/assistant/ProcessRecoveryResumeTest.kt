package dev.ada.assistant

import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.data.ApiResult
import dev.ada.assistant.data.ConnectionCredential
import dev.ada.assistant.data.HttpAdaApi
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Stage two: root has performed adb force-stop between the two distinct instrumentations. */
class ProcessRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel

    @Test fun recoversCommittedReplyAfterProcessStop() {
        val arguments = InstrumentationRegistry.getArguments()
        assumeTrue("Run the explicit force-stop recovery stages", arguments.getString("adaProcessRecovery") == "true")
        val expectedRequest = UUID.fromString(checkNotNull(arguments.getString("expectedRequest")))
        val expectedConversation = UUID.fromString(checkNotNull(arguments.getString("expectedConversation")))
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        // MainActivity's production factory restores the encrypted credential, reauthenticates,
        // checks the exact request via GET, then restores history. The test never calls Send.
        compose.waitUntil(20_000) {
            val state = vm.state.value
            state.account != null && !state.connecting && state.pending == null &&
                state.destination == ChatDestination.Chat && state.conversation?.id == expectedConversation &&
                !state.events.loading && state.events.items.size == 2
        }
        val restored = vm.state.value
        assertEquals("Foundation Test", restored.account?.name)
        assertEquals(expectedConversation, restored.conversation?.id)
        assertEquals(1, restored.events.items.count { it.role == "user" && it.request_id == expectedRequest })
        assertEquals(1, restored.events.items.count { it.role == "assistant" && it.request_id == expectedRequest })
        assertEquals(2, restored.events.items.map { it.id }.distinct().size)
        assertTrue(restored.events.items.all { it.request_status == "completed" })
        assertTrue(restored.draft.isEmpty())
        val store = AndroidSessionStore(compose.activity.applicationContext)
        val saved = runBlocking { store.readCredential() }
        assertNotNull(saved)
        assertEquals(restored.account?.owner, saved!!.identity.owner)
        assertNull(runBlocking { store.pending(saved.identity) })
        val credential = checkNotNull(ConnectionCredential.parse(saved.identity.server, saved.token, true))
        val api = HttpAdaApi()
        val serverEvents = runBlocking { success(api.events(credential, expectedConversation)) }
        assertEquals(restored.events.items.map { it.id }, serverEvents.map { it.id })
        val original = runBlocking { success(api.request(credential, expectedRequest)) }
        assertEquals(expectedRequest, original.request_id)
        assertEquals(expectedConversation, original.conversation_id)
        assertEquals("completed", original.status)
        assertEquals(1, original.attempt)
        val card = original.citations.single { it.label == "M1" }
        assertTrue(card.evidence.quote.contains("Oxford Blue") && card.evidence.quote.contains("😀"))
        compose.onNodeWithTag("chat-history").performScrollToNode(hasTestTag("source-chip-M1"))
        compose.onNodeWithTag("source-chip-M1").performScrollTo().performClick()
        compose.waitUntil(15_000) { !vm.state.value.sourceLoading && vm.state.value.sourceRequestId == expectedRequest }
        assertEquals(card, vm.state.value.sources[expectedRequest]?.citations?.single { it.label == "M1" })
        compose.onNodeWithTag("sources-list").performScrollToNode(hasText("Exact source quote"))
        compose.onNodeWithTag("source-quote-M1").assertTextContains(card.evidence.quote)
    }

    @After fun clearPrivateRecoveryState() {
        if (::vm.isInitialized) {
            compose.runOnIdle { vm.logout() }
            runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() }
        }
    }

    private fun <T> success(result: ApiResult<T>): T {
        check(result is ApiResult.Success) { "The synthetic authenticated HTTP verification failed" }
        return result.value
    }
}
