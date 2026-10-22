package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import java.util.UUID
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Separate emulator app, real PG/HTTP/password/Keystore, explicit FakeProvider. */
class CuriosityUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private fun <T> success(result: ApiResult<T>): T { assertTrue(result is ApiResult.Success); return (result as ApiResult.Success).value }
    private fun origin() = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
    private fun connection(api: HttpAdaApi): ConnectionCredential = runBlocking {
        val login = success(api.passwordLogin(origin(), "synthetic-admin", "Public synthetic Android passphrase 123", true))
        ConnectionCredential.parse(origin(), login.access_token, true)!!
    }
    @Test fun curiosityPrepareBeforeProcessStop() {
        assumeTrue(compose.activity.packageName in setOf("dev.ada.validation.phase25.debug", "dev.ada.validation.redesign.debug", "dev.ada.validation.designgaps.debug"))
        val api = HttpAdaApi(); val conn = connection(api)
        val conversation = runBlocking {
            val p = success(api.createPersonality(conn, PersonalityInputDto(name = "Curiosity validation")))
            success(api.createConversation(conn, ConversationInputDto(p.id, "Public curiosity validation")))
        }
        val store = AndroidSessionStore(compose.activity.applicationContext)
        runBlocking { store.clear() }
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.passwordLogin(origin(), "synthetic-admin", "Public synthetic Android passphrase 123") }
        compose.waitUntil(30000) { vm.state.value.account != null && vm.curiosity.state.value.policy != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(10000) { vm.state.value.conversation?.id == conversation.id }
        compose.onNodeWithTag("chat-menu").performClick()
        compose.onNodeWithTag("open-curiosity").performScrollTo().performClick()
        compose.onNodeWithTag("curiosity-enabled").performScrollTo().performClick()
        compose.onNodeWithTag("curiosity-save").performScrollTo().performClick()
        compose.waitUntil(15000) { vm.curiosity.state.value.policy?.settings?.enabled == true && !vm.curiosity.state.value.busy }
        compose.onNodeWithTag("curiosity-create").performScrollTo().performClick()
        compose.waitUntil(15000) { vm.curiosity.state.value.questions.any { it.state == "pending" } && !vm.curiosity.state.value.busy }
        val original = vm.curiosity.state.value.questions.single()
        assertNull(original.source)
        compose.onNodeWithText("Open with Curiosity validation").performScrollTo().performClick()
        compose.waitUntil(15000) { vm.curiosity.state.value.questions.single().opened_conversation_id != null && !vm.curiosity.state.value.busy }
        val opened = vm.curiosity.state.value.questions.single()
        runBlocking { assertTrue(success(api.events(conn, opened.opened_conversation_id!!, 100, 0)).isEmpty()) }
        compose.onNodeWithTag("curiosity-answer-text").performScrollTo().performTextInput("I enjoy public astronomy talks.")
        closeSoftKeyboard()
        compose.onNodeWithTag("curiosity-answer").performScrollTo().performClick()
        try {
            compose.waitUntil(20000) { vm.curiosity.state.value.answer?.status == "completed" && vm.curiosity.state.value.questions.any { it.id == opened.id && it.state == "answered" } && !vm.curiosity.state.value.busy }
        } catch (_: androidx.compose.ui.test.ComposeTimeoutException) {
            val server = runBlocking { success(api.curiosityQuestion(conn, opened.id)) }
            throw AssertionError("Curiosity metadata: server=${server.state}, client=${vm.curiosity.state.value.questions.map { it.state }}, answer=${vm.curiosity.state.value.answer?.status}, pending=${vm.curiosity.state.value.pending.map { it.kind }}, notice=${vm.curiosity.state.value.notice}")
        }
        val answered = vm.curiosity.state.value.questions.single()
        assertEquals("answered", answered.state)
        runBlocking {
            val events = success(api.events(conn, answered.opened_conversation_id!!, 100, 0))
            assertEquals(listOf("I enjoy public astronomy talks."), events.filter { it.role == "user" }.map { it.content })
            // Simulate a lost action acknowledgement while retaining the exact encrypted key.
            val opId = UUID.randomUUID()
            val operation = CuriosityPending(opId, "action", answered.scope_id, answered.id,
                adaJson.encodeToString(CuriosityActionDto(opId, "helpful")))
            val identity = SessionIdentity(origin().trimEnd('/') + "/", vm.state.value.account!!.owner)
            store.saveCuriosityOperation(identity, operation)
            assertEquals("completed", success(api.curiosityWrite(conn, operation)).state)
            assertTrue(store.curiosityJournal(identity)!!.operations.contains(operation))
        }
    }
    @Test fun curiosityRestoreAfterProcessStop() {
        assumeTrue(compose.activity.packageName in setOf("dev.ada.validation.phase25.debug", "dev.ada.validation.redesign.debug", "dev.ada.validation.designgaps.debug"))
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(30000) { vm.state.value.account != null && vm.curiosity.state.value.pending.isEmpty() && vm.curiosity.state.value.receipts.values.any { it.action == "action" && it.state == "completed" } }
        val receipt = vm.curiosity.state.value.receipts.values.single { it.action == "action" }
        assertTrue(vm.curiosity.state.value.pending.isEmpty())
        val api = HttpAdaApi(); val conn = connection(api)
        val q = runBlocking { success(api.curiosityQuestion(conn, receipt.question_id!!)) }
        assertEquals("answered", q.state)
        runBlocking {
            val events = success(api.events(conn, q.opened_conversation_id!!, 100, 0))
            assertEquals(1, events.count { it.role == "user" })
            assertNotNull(success(api.request(conn, q.answer_request_id!!)).response)
        }
        compose.runOnIdle { vm.openConversation(q.opened_conversation_id!!) }
        compose.waitUntil(10000) { vm.state.value.conversation?.id == q.opened_conversation_id }
        compose.onNodeWithTag("chat-menu").performClick()
        compose.onNodeWithTag("open-curiosity").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.curiosity.state.value.questions.any { it.id == q.id } }
        compose.onNodeWithTag("curiosity-off").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.curiosity.state.value.policy?.settings?.enabled == false }
        assertTrue(vm.curiosity.state.value.questions.isEmpty())
    }
}
