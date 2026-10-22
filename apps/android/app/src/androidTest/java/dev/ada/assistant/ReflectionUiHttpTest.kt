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
import kotlinx.serialization.encodeToString
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Real owner API and Keystore journal, separate APK and disposable synthetic server only. */
class ReflectionUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private fun <T> success(r: ApiResult<T>): T { assertTrue(r is ApiResult.Success); return (r as ApiResult.Success).value }
    private fun origin() = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
    private fun connection(api: HttpAdaApi) = runBlocking {
        val login = success(api.passwordLogin(origin(), "synthetic-admin", "Public synthetic Android passphrase 123", true))
        ConnectionCredential.parse(origin(), login.access_token, true)!!
    }
    private fun click(tag: String) {
        compose.onNodeWithTag("reflection-screen").performScrollToNode(hasTestTag(tag))
        compose.onNodeWithTag(tag).performClick()
    }
    @Test fun reflectionPrepareBeforeProcessStop() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.phase28.debug")
        val api = HttpAdaApi(); val conn = connection(api)
        val conversation = runBlocking {
            val p = success(api.createPersonality(conn, PersonalityInputDto(name = "Public reflection validation")))
            success(api.createConversation(conn, ConversationInputDto(p.id, "Public reflection example")))
        }
        runBlocking {
            success(api.createNote(conn, conversation.scope_id, NoteInputDto(UUID.randomUUID(), "TODO: Review the public sample notebook.")))
            val p = success(api.schedulePolicy(conn)); val key = UUID.randomUUID()
            success(api.scheduleWrite(conn, SchedulePending(key, "policy", adaJson.encodeToString(SchedulePolicyWriteDto(key, p.revision, true)))))
        }
        val store = AndroidSessionStore(compose.activity.applicationContext)
        runBlocking { store.clear() }
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.passwordLogin(origin(), "synthetic-admin", "Public synthetic Android passphrase 123") }
        compose.waitUntil(30000) { vm.state.value.account != null && vm.reflection.state.value.policy != null }
        compose.runOnIdle { vm.navigate(ChatDestination.Reflection) }
        compose.onNodeWithTag("reflection-screen").assertIsDisplayed()
        compose.waitUntil(10000) { !vm.reflection.state.value.busy }
        // Save exact source consent through the same production controller used by the editor.
        compose.runOnIdle { vm.reflection.save(ReflectionSettingsDto(enabled = true, scope_ids = listOf(conversation.scope_id), allowed_end = 1440, job_kinds = listOf("report"))) }
        compose.waitUntil(15000) { vm.reflection.state.value.policy?.settings?.enabled == true && !vm.reflection.state.value.busy }
        val http = OkHttpClient.Builder().followRedirects(false).build()
        http.newCall(Request.Builder().url(origin().trimEnd('/') + "/v1/fixture/reflection/run")
            .header("Authorization", "Bearer ${conn.token}").post("{}".toRequestBody("application/json".toMediaType())).build()).execute().use { assertEquals(200, it.code) }
        click("reflection-refresh")
        compose.waitUntil(15000) { vm.reflection.state.value.artifacts.size == 1 && !vm.reflection.state.value.busy }
        assertEquals(1, vm.reflection.state.value.artifacts.single().content!!.findings!!.size)
        click("reflection-keep")
        compose.waitUntil(15000) { vm.reflection.state.value.artifacts.single().state == "kept" && !vm.reflection.state.value.busy }
        runBlocking {
            val p = success(api.reflectionPolicy(conn)); val id = UUID.randomUUID()
            val op = ReflectionPending(id, "policy", adaJson.encodeToString(ReflectionPolicyWriteDto(id, p.revision, p.settings.copy(enabled = false))))
            val owner = SessionIdentity(origin().trimEnd('/') + "/", vm.state.value.account!!.owner)
            store.saveReflectionOperation(owner, op)
            success(api.reflectionWrite(conn, op))
            assertEquals(op, store.reflectionJournal(owner)!!.operations.single())
        }
    }
    @Test fun reflectionRestoreAfterProcessStop() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.phase28.debug")
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(30000) { vm.state.value.account != null && vm.reflection.state.value.policy != null && vm.reflection.state.value.pending.isEmpty() && vm.reflection.state.value.artifacts.size == 1 }
        assertFalse(vm.reflection.state.value.policy!!.settings.enabled)
        assertEquals("kept", vm.reflection.state.value.artifacts.single().state)
        val api = HttpAdaApi(); val conn = connection(api)
        OkHttpClient().newCall(Request.Builder().url(origin().trimEnd('/') + "/v1/fixture/reflection/counts")
            .header("Authorization", "Bearer ${conn.token}").build()).execute().use { response ->
            assertEquals(200, response.code)
            assertEquals("{\"reflection_posts\":3}", response.body!!.string())
        }
        compose.runOnIdle { vm.navigate(ChatDestination.Reflection) }
        compose.onNodeWithTag("reflection-screen").assertIsDisplayed()
    }
}
