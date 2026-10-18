package dev.ada.assistant

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertIsFocused
import androidx.compose.ui.test.assertIsEnabled
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.compose.ui.test.performTextInput
import androidx.compose.ui.test.performTextReplacement
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.text.AnnotatedString
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/** Real HTTP/Keystore/Compose flow. All data is explicitly synthetic test-server data. */
class ChatFlowSmokeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel

    @Before fun startWithNoPrivateSession() {
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.logout() }
        runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() }
        compose.waitForIdle()
        compose.onNodeWithTag("connect-password").assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Password))
    }

    @After fun clearPrivateTestState() {
        if (::vm.isInitialized) compose.runOnIdle { vm.logout() }
        runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() }
        // The helper owns foundation-test-token cleanup after the complete instrumented run.
    }

    private fun connectRealServer() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val tokenFile = File(context.filesDir, "foundation-test-token")
        assumeTrue("Run verify-emulator.ps1 with the disposable Android chat fixture server", tokenFile.isFile)
        // Avoid passing a bearer through a text-injection action that could echo it on failure.
        // The production ViewModel authenticates and encrypts it through the real adapter/store.
        val token = tokenFile.readText().trim()
        compose.runOnIdle { vm.connect("http://10.0.2.2:18764", token) }
        compose.waitUntil(15_000) { vm.state.value.account != null && !vm.state.value.profiles.loading && !vm.state.value.scopes.loading }
        assertEquals("Foundation Test", vm.state.value.account?.name)
    }

    private fun createConversation(title: String, projectScope: Boolean) {
        compose.onNodeWithTag("conversation-list").performScrollToNode(hasTestTag("new-conversation"))
        compose.onNodeWithTag("new-conversation").performScrollTo().performClick()
        compose.waitUntil(15_000) { vm.state.value.profiles.items.any { it.name == "ADA Test" } && !vm.state.value.profiles.loading }
        compose.onNodeWithTag("new-title").performScrollTo().performTextInput(title)
        compose.onNodeWithText("ADA Test").performScrollTo().performClick()
        if (projectScope) {
            compose.onNodeWithText("Android verification", substring = false).performScrollTo().performClick()
        } else {
            compose.onNodeWithTag("scope-personal").performScrollTo().performClick()
        }
        compose.onNodeWithTag("create-conversation").performScrollTo().performClick()
        compose.waitUntil(15_000) { vm.state.value.destination == ChatDestination.Chat && vm.state.value.conversation != null && !vm.state.value.events.loading }
        assertEquals(title, vm.state.value.conversation?.title)
        if (!projectScope) assertEquals("personal", vm.state.value.conversation?.scope_kind)
    }

    @Test fun realOwnedConversationReplyOriginalSourcesAndLogout() {
        connectRealServer()
        createConversation("Compose source verification", projectScope = true)
        val question = "Which color does the Android verification project use?"
        compose.onNodeWithTag("composer").performScrollTo().performTextInput(question)
        compose.onNodeWithTag("send").performScrollTo().performClick()
        // A second Send action while reserved cannot allocate a duplicate request.
        compose.runOnIdle { vm.send() }
        compose.waitUntil(15_000) { vm.state.value.pending == null && vm.state.value.events.items.any { it.role == "assistant" } }
        val state = vm.state.value
        val users = state.events.items.filter { it.role == "user" }
        val replies = state.events.items.filter { it.role == "assistant" }
        assertEquals(1, users.size)
        assertEquals(1, replies.size)
        assertEquals(users.single().request_id, replies.single().request_id)
        assertEquals(state.events.items.size, state.events.items.map { it.id }.distinct().size)
        val originalEventIds = state.events.items.map { it.id }
        val conversationId = state.conversation!!.id
        // Resume through the real conversation list, rather than keeping only a transient reply.
        closeSoftKeyboard()
        compose.waitUntil(10_000) {
            compose.onAllNodes(hasTestTag("nav-chat")).fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithTag("nav-chat").performClick()
        compose.waitUntil(15_000) { !vm.state.value.conversations.loading }
        compose.onNodeWithTag("conversation-list").performScrollToNode(hasText("Compose source verification", substring = false))
        compose.onNodeWithText("Compose source verification", substring = false).performClick()
        compose.waitUntil(15_000) { vm.state.value.destination == ChatDestination.Chat && !vm.state.value.events.loading }
        assertEquals(conversationId, vm.state.value.conversation?.id)
        assertEquals(originalEventIds, vm.state.value.events.items.map { it.id })
        assertEquals(1, vm.state.value.events.items.count { it.role == "user" })
        assertEquals(1, vm.state.value.events.items.count { it.role == "assistant" })
        compose.onNodeWithTag("chat-history").performScrollToNode(hasTestTag("source-chip-M1"))
        compose.onNodeWithTag("source-chip-M1").performScrollTo().performClick()
        compose.waitUntil(15_000) { !vm.state.value.sourceLoading && vm.state.value.sources[replies.single().request_id]?.citations?.isNotEmpty() == true }
        assertEquals(replies.single().request_id, vm.state.value.sourceRequestId)
        val card = vm.state.value.sources[replies.single().request_id]?.citations?.single()
        assertNotNull(card)
        assertTrue(card!!.evidence.quote.contains("Oxford Blue"))
        assertTrue(card.evidence.quote.contains("😀"))
        compose.onNodeWithTag("sources-list").performScrollToNode(hasText("Exact source quote"))
        compose.onNodeWithTag("source-quote-M1").assertTextContains(card.evidence.quote)
        // An unknown label is explicit and cannot borrow a card from this or another request.
        compose.runOnIdle { vm.openSources(replies.single().request_id, "M99") }
        compose.waitUntil(15_000) { !vm.state.value.sourceLoading && vm.state.value.sourceLabel == "M99" }
        compose.onNodeWithTag("sources-list").performScrollToNode(hasText("Source unavailable", substring = false))
        compose.onNodeWithText("Source unavailable", substring = false).assertIsDisplayed()
        compose.onNodeWithTag("source-card-M99").assertDoesNotExist()
        compose.onNodeWithTag("source-card-M1").assertDoesNotExist()
        compose.runOnIdle { vm.openSources(replies.single().request_id, "M1") }
        compose.waitUntil(15_000) { !vm.state.value.sourceLoading && vm.state.value.sourceLabel == "M1" }
        compose.onNodeWithTag("sources-list").performScrollToNode(hasText("Source details", substring = false))
        compose.onNodeWithText("Source details", substring = false).performScrollTo().performClick()
        compose.onNodeWithTag("sources-list").performScrollToNode(hasTestTag("retrieval-details"))
        compose.onNodeWithTag("retrieval-details").performScrollTo().performClick()
        compose.waitUntil(15_000) { !vm.state.value.traceLoading && vm.state.value.trace != null }
        assertEquals(replies.single().request_id, vm.state.value.trace?.request_id)
        compose.onNodeWithText("Retrieval details", substring = false).assertIsDisplayed()
        compose.onNodeWithTag("nav-settings").performClick()
        compose.onNodeWithTag("logout").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.state.value.account == null }
        assertTrue(vm.state.value.events.items.isEmpty())
        assertTrue(vm.state.value.sources.isEmpty())
        assertTrue(vm.state.value.draft.isEmpty())
        compose.onNodeWithTag("connect-password").assert(SemanticsMatcher.expectValue(SemanticsProperties.EditableText, AnnotatedString("")))
    }

    @Test fun personalScopeEmojiDraftRotationAndHistoricalValidation() {
        connectRealServer()
        createConversation("Compose draft verification", projectScope = false)
        // The compact composer hides ordinary counts. Exercise the actual Unicode limit
        // through enabled/error behavior rather than expecting a permanent counter row.
        compose.onNodeWithTag("composer").performScrollTo().performTextReplacement("😀".repeat(4000))
        compose.onNodeWithTag("send").performScrollTo().assertIsEnabled()
        compose.onNodeWithTag("composer").performScrollTo().performTextInput("😀")
        compose.onNodeWithTag("send").performScrollTo().assertIsNotEnabled()
        compose.onNodeWithTag("composer").performScrollTo().performTextReplacement("Hello 😀")
        // Dismiss the small landscape IME before rotating and opening a separate dialog.
        closeSoftKeyboard()
        compose.waitForIdle()
        compose.onNodeWithTag("composer").assertTextContains("Hello 😀")
        compose.activityRule.scenario.recreate()
        compose.waitForIdle()
        compose.onNodeWithTag("composer").performScrollTo().assertTextContains("Hello 😀")
        compose.onNodeWithTag("composer-menu").performScrollTo().performClick()
        compose.onNodeWithTag("message-options").performClick()
        compose.onNodeWithTag("historical-instant").performScrollTo().performTextInput("2026-10-08T12:00:00.0001Z")
        closeSoftKeyboard()
        compose.onNodeWithTag("message-options-done").assertIsDisplayed().performClick()
        compose.onNodeWithTag("send").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.state.value.fault != null }
        // Validation closes the IME; short screens then restore their lazy context panel.
        compose.waitUntil(10_000) {
            compose.onAllNodes(hasTestTag("chat-history")).fetchSemanticsNodes().isNotEmpty()
        }
        if (compose.onAllNodes(hasTestTag("failure-notice")).fetchSemanticsNodes().isEmpty()) {
            compose.onNodeWithTag("chat-history").performScrollToNode(hasTestTag("failure-notice"))
        }
        compose.onNodeWithTag("failure-notice").performScrollTo().assertIsFocused().assertIsDisplayed()
        assertEquals("Hello 😀", vm.state.value.draft)
        assertTrue(vm.state.value.pending == null)
        assertTrue(vm.state.value.events.items.isEmpty())
        compose.onNodeWithTag("composer").performScrollTo().assertTextContains("Hello 😀")
    }
}
