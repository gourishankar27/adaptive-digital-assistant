package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import java.time.Instant
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.UUID
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Only the separate emulator app and explicit disposable server can use this clock driver. */
class ScheduleUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private fun <T> success(result: ApiResult<T>): T { assertTrue(result is ApiResult.Success); return (result as ApiResult.Success).value }
    private fun origin() = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
    private fun connection(api: HttpAdaApi): ConnectionCredential = runBlocking {
        val login = success(api.passwordLogin(origin(), "synthetic-admin", "Public synthetic Android passphrase 123", true))
        ConnectionCredential.parse(origin(), login.access_token, true)!!
    }
    private fun click(tag: String) {
        compose.onNodeWithTag("schedule-screen").performScrollToNode(hasTestTag(tag))
        compose.onNodeWithTag(tag).performClick()
    }
    private fun field(tag: String, value: String) {
        compose.onNodeWithTag("schedule-screen").performScrollToNode(hasTestTag(tag))
        compose.onNodeWithTag(tag).performTextClearance()
        compose.onNodeWithTag(tag).performTextInput(value)
        closeSoftKeyboard()
    }
    @Test fun schedulePrepareBeforeProcessStop() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.phase27.debug")
        val api = HttpAdaApi(); val conn = connection(api)
        val conversation = runBlocking {
            val profile = success(api.createPersonality(conn, PersonalityInputDto(name = "Scheduling validation")))
            success(api.createConversation(conn, ConversationInputDto(profile.id, "Public schedule validation")))
        }
        val store = AndroidSessionStore(compose.activity.applicationContext)
        runBlocking { store.clear() }
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.passwordLogin(origin(), "synthetic-admin", "Public synthetic Android passphrase 123") }
        compose.waitUntil(30000) { vm.state.value.account != null && vm.scheduling.state.value.policy != null && vm.state.value.profiles.items.isNotEmpty() }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(10000) { vm.state.value.conversation?.id == conversation.id }
        compose.onNodeWithTag("chat-menu").performClick()
        compose.onNodeWithTag("open-schedules").performScrollTo().performClick()
        click("schedule-consent")
        compose.waitUntil(10000) { vm.scheduling.state.value.policy?.enabled == true && !vm.scheduling.state.value.busy }
        click("schedule-new")
        field("schedule-text", "Review the public sample notebook.")
        field("schedule-timezone", "Etc/UTC")
        val local = Instant.now().plusSeconds(300).atOffset(ZoneOffset.UTC).format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm"))
        field("schedule-local", local)
        click("schedule-calendar-options")
        field("schedule-hours-start", "00:00")
        field("schedule-hours-end", "24:00")
        click("schedule-preview")
        compose.waitUntil(15000) { vm.scheduling.state.value.preview != null && !vm.scheduling.state.value.busy }
        assertEquals(1, vm.scheduling.state.value.preview!!.occurrences!!.size)
        click("schedule-confirm")
        compose.waitUntil(15000) { vm.scheduling.state.value.schedules.size == 1 && !vm.scheduling.state.value.busy }
        val http = OkHttpClient.Builder().followRedirects(false).build()
        http.newCall(Request.Builder().url(origin().trimEnd('/') + "/v1/fixture/scheduling/run")
            .header("Authorization", "Bearer ${conn.token}").post("{}".toRequestBody("application/json".toMediaType())).build()).execute().use { assertEquals(200, it.code) }
        compose.runOnIdle { vm.scheduling.refresh() }
        compose.waitUntil(15000) { vm.scheduling.state.value.inbox.size == 1 && !vm.scheduling.state.value.busy }
        click("schedule-open")
        compose.waitUntil(15000) { vm.scheduling.state.value.inbox.single().opened_conversation_id != null && !vm.scheduling.state.value.busy }
        val item = vm.scheduling.state.value.inbox.single()
        assertEquals("Review the public sample notebook.", item.text)
        assertFalse(vm.scheduling.state.value.policy!!.background_push)
        runBlocking {
            assertTrue(success(api.events(conn, item.opened_conversation_id!!, 100, 0)).isEmpty())
            val opId = UUID.randomUUID()
            val operation = SchedulePending(opId, "inbox_action", adaJson.encodeToString(ScheduleInboxActionDto(opId, "acknowledge")), scopeId = item.scope_id, itemId = item.id)
            val identity = SessionIdentity(origin().trimEnd('/') + "/", vm.state.value.account!!.owner)
            store.saveScheduleOperation(identity, operation)
            assertEquals("completed", success(api.scheduleWrite(conn, operation)).state)
            assertTrue(store.scheduleJournal(identity)!!.operations.contains(operation))
        }
    }
    @Test fun scheduleRestoreAfterProcessStop() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.phase27.debug")
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(30000) { vm.state.value.account != null && vm.scheduling.state.value.pending.isEmpty() && vm.scheduling.state.value.receipts.values.any { it.action == "inbox_action" } && vm.scheduling.state.value.inbox.size == 1 }
        val receipt = vm.scheduling.state.value.receipts.values.single { it.action == "inbox_action" }
        val api = HttpAdaApi(); val conn = connection(api)
        val items = runBlocking { success(api.scheduleInbox(conn)) }
        assertEquals(1, items.size); assertEquals(receipt.item_id, items.single().id)
        assertNotNull(items.single().acknowledged_at)
        runBlocking { assertTrue(success(api.events(conn, items.single().opened_conversation_id!!, 100, 0)).isEmpty()) }
        compose.runOnIdle { vm.navigate(ChatDestination.Schedules) }
        compose.waitUntil(10000) { vm.scheduling.state.value.policy != null }
        click("schedule-consent")
        compose.waitUntil(10000) { vm.scheduling.state.value.policy?.enabled == false && !vm.scheduling.state.value.busy }
        assertFalse(vm.scheduling.state.value.policy!!.background_push)
    }
}
