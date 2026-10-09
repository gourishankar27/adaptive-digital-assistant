package dev.ada.assistant

import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.compose.ui.test.performTextInput
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.espresso.Espresso.closeSoftKeyboard
import dev.ada.assistant.data.AdaApi
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.data.ApiFailure
import dev.ada.assistant.data.ApiResult
import dev.ada.assistant.data.ChatInputDto
import dev.ada.assistant.data.ConnectionCredential
import dev.ada.assistant.data.ConversationInputDto
import dev.ada.assistant.data.HttpAdaApi
import dev.ada.assistant.data.RequestDto
import dev.ada.assistant.ui.AdaTheme
import dev.ada.assistant.ui.ChatApp
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import dev.ada.assistant.ui.PendingPhase
import dev.ada.assistant.ui.ThemePalette
import java.io.File
import java.util.UUID
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Actual HTTP commits the reply; only response delivery and the GET wait are simulated. */
class DeliveryLossRecoveryTest {
    @get:Rule val compose = createComposeRule()
    private val viewModels = ViewModelStore()
    private lateinit var vm: ChatViewModel
    private lateinit var adapter: LostDeliveryApi
    private lateinit var store: AndroidSessionStore

    @Test fun unknownOutcomeKeepsOriginalIdAcrossNavigationAndDoesNotSendAgain() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val tokenFile = File(context.filesDir, "foundation-test-token")
        assumeTrue("Provision the disposable Android chat fixture server", tokenFile.isFile)
        store = AndroidSessionStore(context)
        runBlocking { store.clear() }
        val token = tokenFile.readText().trim()
        val credential = checkNotNull(ConnectionCredential.parse("http://10.0.2.2:18764", token, true))
        val actual = HttpAdaApi()
        val profile = runBlocking { success(actual.personalities(credential)) }.single { it.name == "ADA Test" }
        val scope = runBlocking { success(actual.scopes(credential)) }.single { it.name == "Android verification" }
        val conversation = runBlocking { success(actual.createConversation(credential, ConversationInputDto(profile.id, "Simulated delivery recovery", scope.id))) }
        adapter = LostDeliveryApi(actual)
        compose.runOnIdle {
            vm = ViewModelProvider(viewModels, object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T =
                    ChatViewModel(adapter, store, allowDebugHttp = true, pollDelaysMs = listOf(0)) as T
            })[ChatViewModel::class.java]
        }
        compose.setContent { AdaTheme(ThemePalette.DarkRed, dark = false) { ChatApp(vm, openSettings = {}) } }
        compose.runOnIdle { vm.connect(credential.server.toString(), token) }
        compose.waitUntil(15_000) { vm.state.value.account != null && !vm.state.value.connecting }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(15_000) { vm.state.value.conversation?.id == conversation.id && !vm.state.value.events.loading }
        compose.onNodeWithTag("composer").performScrollTo().performTextInput("Which color does the Android verification project use?")
        compose.onNodeWithTag("send").performScrollTo().performClick()
        compose.waitUntil(15_000) { vm.state.value.pending?.phase == PendingPhase.Unknown && adapter.gets.get() == 1 }
        val reservation = vm.state.value.pending!!.message
        assertEquals(adapter.requestId, reservation.body.request_id)
        compose.waitUntil(10_000) { compose.onAllNodesWithTag("chat-history").fetchSemanticsNodes().isNotEmpty() }
        scrollPendingIntoComposition("pending-status")
        compose.onNodeWithTag("pending-status").performScrollTo().assertTextContains("The reply’s outcome is not known yet")
        compose.onNodeWithTag("composer").performScrollTo().performTextInput("Keep this separate draft 😀")
        compose.onNodeWithTag("send").performScrollTo().assertIsNotEnabled()
        compose.runOnIdle { vm.send() }
        assertEquals(1, adapter.posts.get())
        // Navigation chrome is intentionally hidden during typing on a short viewport.
        closeSoftKeyboard()
        compose.waitUntil(10_000) { compose.onAllNodesWithTag("nav-chat").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithTag("nav-chat").performClick()
        compose.onNodeWithTag("conversation-list").performScrollToNode(hasText("Return to pending message", substring = false))
        compose.onNodeWithText("Return to pending message", substring = false).performClick()
        compose.waitUntil(15_000) { vm.state.value.destination == ChatDestination.Chat && !vm.state.value.events.loading }
        assertEquals(reservation.body.request_id, vm.state.value.pending?.message?.body?.request_id)
        assertEquals("Keep this separate draft 😀", vm.state.value.draft)
        val pendingOnDisk = runBlocking { store.pending(reservation.identity) }
        assertNotNull(pendingOnDisk)
        assertEquals(reservation.body.request_id, pendingOnDisk!!.body.request_id)
        // Check while an existing GET is in flight is safe: it cannot submit another POST.
        scrollPendingIntoComposition("check-request")
        compose.onNodeWithTag("check-request").performScrollTo().performClick()
        assertEquals(1, adapter.posts.get())
        adapter.releaseGet.complete(Unit)
        compose.waitUntil(15_000) { vm.state.value.pending == null && !vm.state.value.events.loading && vm.state.value.events.items.size == 2 }
        assertEquals(1, adapter.posts.get())
        assertEquals(1, adapter.gets.get())
        assertEquals("Keep this separate draft 😀", vm.state.value.draft)
        assertEquals(1, vm.state.value.events.items.count { it.role == "user" && it.request_id == reservation.body.request_id })
        assertEquals(1, vm.state.value.events.items.count { it.role == "assistant" && it.request_id == reservation.body.request_id })
        assertEquals(reservation.body.request_id, vm.state.value.sources[reservation.body.request_id]?.request_id)
        assertNull(runBlocking { store.pending(reservation.identity) })
    }

    @After fun clearSyntheticPrivateState() {
        if (::adapter.isInitialized) adapter.releaseGet.complete(Unit)
        if (::vm.isInitialized) compose.runOnIdle { vm.logout(); viewModels.clear() }
        if (::store.isInitialized) runBlocking { store.clear() }
    }

    private fun <T> success(result: ApiResult<T>): T {
        check(result is ApiResult.Success) { "The synthetic authenticated HTTP prerequisite failed" }
        return result.value
    }

    private fun scrollPendingIntoComposition(tag: String) {
        if (compose.onAllNodesWithTag(tag).fetchSemanticsNodes().isEmpty()) {
            compose.onNodeWithTag("chat-history").performScrollToNode(hasTestTag(tag))
        }
    }

    private class LostDeliveryApi(private val actual: AdaApi) : AdaApi by actual {
        val posts = AtomicInteger()
        val gets = AtomicInteger()
        val releaseGet = CompletableDeferred<Unit>()
        @Volatile var requestId: UUID? = null
        override suspend fun send(connection: ConnectionCredential, conversation: UUID, body: ChatInputDto): ApiResult<RequestDto> {
            posts.incrementAndGet()
            requestId = body.request_id
            val committed = actual.send(connection, conversation, body)
            check(committed is ApiResult.Success && committed.value.status == "completed") { "The synthetic HTTP reply did not commit" }
            return ApiResult.Failure(ApiFailure.Timeout)
        }
        override suspend fun request(connection: ConnectionCredential, id: UUID): ApiResult<RequestDto> {
            gets.incrementAndGet()
            releaseGet.await()
            return actual.request(connection, id)
        }
    }
}
