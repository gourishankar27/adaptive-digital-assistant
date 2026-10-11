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

class EpisodeUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun explicitSummaryShowsGeneratedLabelAndExactOriginalOverHttp() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val conn = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val api = HttpAdaApi()
        val profile = runBlocking { success(api.personalities(conn)) }.first()
        val conversation = runBlocking { success(api.createConversation(conn, ConversationInputDto(profile.id, "Synthetic episode UI"))) }
        val text = "Synthetic episode continuity: a tentative choice 😀 café é."
        runBlocking { success(api.send(conn, conversation.id, ChatInputDto(UUID.randomUUID(), text, use_memory = false))) }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]; compose.runOnIdle { vm.connect(conn.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }; compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id }
        compose.onNodeWithTag("open-episodes").performClick()
        compose.waitUntil(20_000) { vm.episodes.state.value.events.size == 2 && !vm.episodes.state.value.busy }
        compose.onNodeWithTag("episode-list").performScrollToNode(hasTestTag("episode-event-user"))
        compose.onNodeWithTag("episode-event-user").performClick()
        compose.onNodeWithTag("episode-list").performScrollToNode(hasTestTag("episode-preview"))
        compose.onNodeWithTag("episode-preview").performClick()
        compose.waitUntil(20_000) { vm.episodes.state.value.preview != null }
        assertEquals(text, vm.episodes.state.value.preview!!.single().content)
        compose.onNodeWithText("${vm.episodes.state.value.preview!!.single().trust_class}: $text").assertExists()
        compose.onNodeWithText("Queue episode").assertIsDisplayed()
        compose.onNodeWithTag("episode-queue").performClick()
        compose.waitUntil(20_000) { vm.episodes.state.value.job != null && !vm.episodes.state.value.busy }
        repeat(30) {
            if (vm.episodes.state.value.job?.status != "completed") {
                Thread.sleep(250); compose.runOnIdle { vm.episodes.refresh() }
                compose.waitUntil(20_000) { !vm.episodes.state.value.busy }
            }
        }
        val state = vm.episodes.state.value; assertEquals("completed", state.job!!.status); assertEquals(1, state.job.attempt)
        assertEquals(state.job.id, runBlocking { success(api.createConsolidationJob(conn, state.journal!!)) }.id)
        assertEquals(1, state.episodes.size)
        compose.onNodeWithTag("episode-list").performScrollToNode(hasTestTag("episode-open"))
        compose.onNodeWithTag("episode-open").performClick()
        compose.waitUntil(20_000) { vm.episodes.state.value.episode != null && !vm.episodes.state.value.busy }
        val episode = vm.episodes.state.value.episode!!; assertEquals("model_generated", episode.trust_class)
        assertEquals(text, episode.sources.single().evidence.quote); assertEquals(conversation.id, episode.sources.single().conversation_id)
        assertEquals(text.codePointCount(0, text.length), episode.sources.single().evidence.span_end)
        compose.onNodeWithTag("episode-list").performScrollToNode(hasText("Generated interpretation"))
        compose.onNodeWithText("Generated interpretation").performScrollTo().assertIsDisplayed()
        compose.onNodeWithTag("episode-list").performScrollToNode(hasText("Open exact original version"))
        compose.onNodeWithText("Open exact original version").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.episodes.state.value.original != null }
        assertEquals(text, vm.episodes.state.value.original!!.content)
        assertTrue(runBlocking { success(api.claims(conn, conversation.scope_id)) }.isEmpty())
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
