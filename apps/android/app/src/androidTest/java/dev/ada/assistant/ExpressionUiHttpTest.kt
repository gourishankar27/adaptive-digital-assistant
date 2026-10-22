package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatViewModel
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class ExpressionUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun explicitScopedPreferencesToneDisableAndResetOverRealHttp() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val c = ConnectionCredential.parse(fixtureOrigin(18764), token, true)!!; val api = HttpAdaApi()
        val profile = runBlocking { success(api.personalities(c)).first() }
        val conversation = runBlocking { success(api.createConversation(c, ConversationInputDto(profile.id, "Synthetic expression UI"))) }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(c.server.toString(), token) }; compose.waitUntil(20_000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }; compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id }
        val settings = compose.onNodeWithTag("nav-settings")
        if (compose.onAllNodesWithTag("expanded-navigation").fetchSemanticsNodes().isNotEmpty()) settings.performScrollTo()
        settings.assertIsDisplayed().performClick()
        compose.onNodeWithTag("settings-preferences").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.expression.state.value.preference?.target_id == conversation.id && !vm.expression.state.value.busy }
        compose.onNodeWithTag("expression-field-verbosity").performScrollTo().performClick()
        compose.onNodeWithTag("expression-choice-verbosity-concise").performClick()
        compose.onNodeWithTag("expression-dynamic").performScrollTo().performClick()
        compose.onNodeWithTag("expression-save").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.expression.state.value.preference?.revision == 1 && !vm.expression.state.value.busy }
        assertNull(vm.expression.state.value.journal)
        val original = runBlocking { success(api.expression(c, conversation.id)) }
        assertEquals("concise", original.preferences.verbosity); assertTrue(original.dynamic_enabled)
        assertEquals(conversation.personality, runBlocking { success(api.conversation(c, conversation.id)) }.personality)
        runBlocking { success(api.send(c, conversation.id, ChatInputDto(UUID.randomUUID(), "Synthetic tone request", use_memory = false))) }
        compose.runOnIdle { vm.expression.refresh() }; compose.waitUntil(20_000) { !vm.expression.state.value.busy && vm.expression.state.value.expression?.turn == 1 }
        compose.onNodeWithTag("expression-warmth").performScrollTo().performClick()
        compose.waitUntil(20_000) { !vm.expression.state.value.busy && vm.expression.state.value.expression?.vector?.warmth == 70 }
        val adjusted = vm.expression.state.value.expression!!
        compose.onNodeWithTag("expression-reset-session").performScrollTo().performClick()
        compose.waitUntil(20_000) { !vm.expression.state.value.busy && vm.expression.state.value.expression?.session_id != adjusted.session_id }
        assertEquals(60, vm.expression.state.value.expression!!.vector.warmth)
        compose.onNodeWithTag("expression-dynamic").performScrollTo().performClick()
        compose.onNodeWithTag("expression-save").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.expression.state.value.preference?.revision == 2 && !vm.expression.state.value.busy }
        assertFalse(runBlocking { success(api.expression(c, conversation.id)) }.dynamic_enabled)
        assertEquals("concise", runBlocking { success(api.preference(c, "conversation", conversation.id)) }.values.verbosity)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
