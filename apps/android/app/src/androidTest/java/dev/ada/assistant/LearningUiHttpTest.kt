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
import kotlinx.serialization.encodeToString
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class LearningUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun exactContinuityCardIsShownFromTheOriginalRequest() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val c = ConnectionCredential.parse(fixtureOrigin(18764), token, true)!!; val api = HttpAdaApi()
        val profile = runBlocking { success(api.personalities(c)).first() }
        val conversation = runBlocking { success(api.createConversation(c, ConversationInputDto(profile.id, "Synthetic continuity UI"))) }
        val source = runBlocking { success(api.createNote(c, conversation.scope_id, NoteInputDto(UUID.randomUUID(), "Synthetic continuity tea planning."))) }
        val owner = runBlocking { SessionIdentity(c.server.toString(), success(api.me(c)).id) }
        val key = UUID.randomUUID(); val job = ConsolidationJournal(owner, conversation.scope_id, key,
            adaJson.encodeToString(ConsolidationInputDto(key, "episode", listOf(SourcePinDto(source.id, source.version, source.content_hash, 0, source.content.codePointCount(0, source.content.length))))))
        runBlocking { success(api.createConsolidationJob(c, job)) }
        compose.waitUntil(20_000) { runBlocking { success(api.consolidationJob(c, key)).status == "completed" } }
        val config = runBlocking { success(api.learning(c, conversation.scope_id)).config }; val operation = UUID.randomUUID()
        val journal = LearningJournal(owner, conversation.scope_id, operation, "config", adaJson.encodeToString(LearningConfigWriteDto(operation, config.revision, "enrolled", true)))
        val store = AndroidSessionStore(compose.activity.applicationContext)
        runBlocking { store.saveCredential(StoredCredential(owner, token)); store.saveLearningJournal(journal); success(api.learningOperation(c, journal)); store.removeLearningJournal(owner, operation) }
        val reply = runBlocking { success(api.send(c, conversation.id, ChatInputDto(UUID.randomUUID(), "Tea planning continuity?"))) }
        assertEquals(source.content, reply.continuity_citations.single().evidence.quote)
        assertEquals("C1", reply.continuity_citations.single().label)
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(c.server.toString(), token) }; compose.waitUntil(20_000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }; compose.waitUntil(20_000) { !vm.state.value.events.loading && vm.state.value.conversation?.id == conversation.id }
        compose.onNodeWithTag("source-chip-C1").performScrollTo().performClick()
        compose.waitUntil(20_000) { !vm.state.value.sourceLoading && vm.state.value.sources[reply.request_id]?.continuity_citations?.size == 1 }
        compose.onNodeWithTag("sources-list").performScrollToNode(hasText(source.content))
        compose.onNodeWithText(source.content).performScrollTo().assertIsDisplayed()
        assertEquals(reply, runBlocking { success(api.request(c, reply.request_id)) })
    }
    @Test fun enrollSelectEvidenceReviewEditRejectPauseAndResetOverRealHttp() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val c = ConnectionCredential.parse(fixtureOrigin(18764), token, true)!!; val api = HttpAdaApi()
        val profile = runBlocking { success(api.personalities(c)).first() }
        val conversation = runBlocking { success(api.createConversation(c, ConversationInputDto(profile.id, "Synthetic learning UI"))) }
        runBlocking { for(text in listOf("Concise planning helps.", "Brief coding explanations please.", "Short reviews are useful.", "Keep this next reply compact.")) success(api.send(c, conversation.id, ChatInputDto(UUID.randomUUID(), text))) }
        val events = runBlocking { success(api.events(c, conversation.id)) }.filter { it.role == "user" }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(c.server.toString(), token) }; compose.waitUntil(20_000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }; compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id && !vm.state.value.events.loading }
        val settings = compose.onNodeWithTag("nav-settings")
        if (compose.onAllNodesWithTag("expanded-navigation").fetchSemanticsNodes().isNotEmpty()) settings.performScrollTo()
        settings.assertIsDisplayed().performClick()
        compose.onNodeWithTag("settings-learning").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.data != null && !vm.learning.state.value.busy }
        compose.onNodeWithTag("learning-consent").performScrollTo().performClick()
        compose.onNodeWithTag("learning-enroll").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.data?.config?.status == "enrolled" && !vm.learning.state.value.busy }
        for(event in events.take(3)) {
            compose.onNodeWithTag("learning-source-${event.source_version_id}").performScrollTo().performClick()
            compose.waitUntil(20_000) { vm.learning.state.value.source?.id == event.source_version_id && !vm.learning.state.value.busy }
            compose.onNodeWithTag("learning-observe").performScrollTo().performClick()
            compose.waitUntil(20_000) { vm.learning.state.value.source == null && !vm.learning.state.value.busy }
        }
        val proposal = vm.learning.state.value.data!!.proposals.single(); assertTrue(proposal.eligible)
        compose.onNodeWithText("Reviewed value: Concise").performScrollTo().performClick()
        compose.onNodeWithText("Balanced", substring = false).performClick()
        compose.onNodeWithTag("learning-approve-${proposal.id}").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.data?.learned?.size == 1 && !vm.learning.state.value.busy }
        assertEquals("balanced", runBlocking { success(api.learning(c, conversation.scope_id)) }.learned.single().values.verbosity)
        val fourth = events[3]
        compose.onNodeWithTag("learning-source-${fourth.source_version_id}").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.source?.id == fourth.source_version_id && !vm.learning.state.value.busy }
        compose.onNodeWithTag("learning-observe").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.source == null && !vm.learning.state.value.busy }
        compose.onNodeWithTag("learning-reject-${proposal.id}").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.data?.proposals?.single()?.status == "rejected" && !vm.learning.state.value.busy }
        compose.onNodeWithTag("learning-pause").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.data?.config?.status == "paused" && !vm.learning.state.value.busy }
        compose.onNodeWithTag("learning-reset").performScrollTo().performClick()
        compose.onNodeWithTag("learning-reset-confirm").performClick()
        compose.waitUntil(20_000) { vm.learning.state.value.data?.config?.status == "off" && !vm.learning.state.value.busy }
        val cleared = runBlocking { success(api.learning(c, conversation.scope_id)) }
        assertTrue(cleared.learned.isEmpty() && cleared.observations.isEmpty() && cleared.proposals.isEmpty())
        assertNull(vm.learning.state.value.journal)
        assertEquals(conversation.personality, runBlocking { success(api.conversation(c, conversation.id)) }.personality)
    }
    @After fun cleanup() { if(::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
