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
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Separate emulator APK and disposable real ADA/PG; no normal app data or phone. */
class QualityUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private fun <T> value(result: ApiResult<T>): T {
        assertTrue("Synthetic HTTP operation must succeed", result is ApiResult.Success)
        return (result as ApiResult.Success).value
    }
    @Test fun calendarWindowAndQualityUpgrade() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.phase23.debug")
        val origin = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
        val api = HttpAdaApi()
        val password = "Public synthetic Android passphrase 123"
        val login = runBlocking { value(api.passwordLogin(origin, "synthetic-admin", password, true)) }
        val connection = ConnectionCredential.parse(origin, login.access_token, true)!!
        val scope = runBlocking { value(api.createScope(connection, ScopeInputDto("Public window validation"))) }
        val quotes = listOf("😀 Mira prefers tea.", "Mira prefers coffee.")
        runBlocking {
            quotes.forEachIndexed { index, text ->
                val note = value(api.createNote(connection, scope.id, NoteInputDto(UUID.randomUUID(), text)))
                value(api.createClaim(connection, scope.id, ClaimInputDto(UUID.randomUUID(), note.id, 0,
                    text.codePointCount(0, text.length), "Mira", "beverage", if (index == 0) "tea" else "coffee",
                    valid_from = "2025-01-01T00:00:00Z")))
            }
        }
        val store = AndroidSessionStore(compose.activity.applicationContext)
        runBlocking { store.clear() }
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.passwordLogin(origin, "synthetic-admin", password) }
        compose.waitUntil(30000) { vm.state.value.account != null }
        compose.runOnIdle { vm.navigate(ChatDestination.Memory) }
        compose.waitUntil(10000) { vm.memory.state.value.scopes.items.any { it.id == scope.id } }
        compose.runOnIdle { vm.memory.selectScope(scope.id) }
        compose.onNodeWithTag("memory-window-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("window-query").performScrollTo().performTextInput("Mira beverage")
        compose.onNodeWithTag("window-timezone").performScrollTo().performTextClearance()
        compose.onNodeWithTag("window-timezone").performTextInput("America/Phoenix")
        compose.onNodeWithTag("window-reference").performScrollTo().performTextClearance()
        compose.onNodeWithTag("window-reference").performTextInput("2025-06-02T12:00:00-07:00")
        closeSoftKeyboard()
        compose.onNodeWithTag("window-search").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.memory.state.value.window?.selected?.size == 2 }
        val window = vm.memory.state.value.window!!
        assertEquals("2025-06-01T00:00:00-07:00", window.resolution.local_start)
        assertEquals(24 * 3600000L, window.resolution.end!! - window.resolution.start!!)
        assertTrue(window.selected.all { it.conflict && it.scope_id == scope.id })
        assertEquals(quotes.toSet(), window.selected.map { it.evidence.quote }.toSet())
        compose.onNodeWithTag("window-resolved").performScrollTo().assertIsDisplayed()
        compose.runOnIdle { vm.memory.openClaim(window.selected.first().claim_id) }
        compose.waitUntil(10000) { vm.memory.state.value.evidenceVerified }
        val conversation = runBlocking {
            val profile = value(api.createPersonality(connection, PersonalityInputDto()))
            value(api.createConversation(connection, ConversationInputDto(profile.id, "Public quality validation", scope.id)))
        }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(10000) { vm.state.value.conversation?.id == conversation.id }
        compose.onNodeWithTag("quality-prompt-upgrade").performScrollTo().performClick()
        compose.onNodeWithText("Enable for future replies").performClick()
        compose.waitUntil(10000) { vm.state.value.conversation?.prompt_version == "ada-baseline-v5" && !vm.state.value.upgrading }
        assertEquals("ada-baseline-v5", runBlocking { value(api.conversation(connection, conversation.id)) }.prompt_version)
        compose.runOnIdle { vm.updateMemory(true); vm.updateDocuments(true) }
        assertTrue(vm.state.value.useDocuments)
    }
}
