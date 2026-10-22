package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
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

class ProposalUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun selectedSourceEditAcceptAndRejectUseRealHttpAndHonestEvidence() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val conn = ConnectionCredential.parse(fixtureOrigin(18764), token, true)!!; val api = HttpAdaApi()
        val me = runBlocking { success(api.me(conn)) }; val identity = SessionIdentity(conn.server.toString(), me.id)
        val scope = runBlocking { success(api.createScope(conn, ScopeInputDto("Synthetic proposal UI"))) }
        val text = "Android verification project uses Oxford Blue. 😀 e\u0301"
        val source = runBlocking { success(api.createNote(conn, scope.id, NoteInputDto(UUID.randomUUID(), text))) }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]; compose.runOnIdle { vm.connect(conn.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null && !vm.proposals.state.value.busy }
        compose.runOnIdle { vm.navigate(ChatDestination.Proposals) }; compose.waitUntil(20_000) { vm.proposals.state.value.scopes.items.any { it.id == scope.id } }
        compose.runOnIdle { vm.proposals.selectScope(scope.id) }; compose.waitUntil(20_000) { vm.proposals.state.value.sources.any { it.id == source.id } }
        compose.runOnIdle { vm.proposals.selectSource(source) }; compose.onNodeWithTag("proposal-selected-excerpt").performScrollTo(); compose.onNodeWithText(text).assertTextEquals(text)
        compose.onNodeWithTag("proposal-extract").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.proposals.state.value.inbox.items.size == 1 && vm.proposals.state.value.pending == null }
        assertTrue(runBlocking { success(api.claims(conn, scope.id)) }.isEmpty())
        val p = vm.proposals.state.value.inbox.items.single(); compose.onNodeWithTag("proposal-open-${p.id}").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.proposals.state.value.draft != null && !vm.proposals.state.value.busy }
        compose.onNodeWithTag("proposal-excerpt-0").performScrollTo(); compose.onNodeWithText(text).assertTextEquals(text)
        compose.onNodeWithTag("proposal-value").performScrollTo().performTextReplacement("Cobalt")
        closeSoftKeyboard(); compose.onNodeWithTag("proposal-preview").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.proposals.state.value.draft?.proposal?.revision == 2 && !vm.proposals.state.value.busy }
        compose.onNodeWithTag("proposal-annotation").performScrollTo().performTextInput("I explicitly choose cobalt in this synthetic review.")
        closeSoftKeyboard(); compose.onNodeWithTag("proposal-accept").performScrollTo().performClick(); compose.onNodeWithTag("proposal-confirm").performClick()
        compose.waitUntil(20_000) { vm.proposals.state.value.draft == null && vm.proposals.state.value.pending == null && !vm.proposals.state.value.busy }
        val saved = runBlocking { success(api.claims(conn, scope.id)) }.single(); assertEquals("Cobalt", saved.value); assertEquals("user_reviewed", saved.provenance?.origin)
        assertEquals(text, saved.provenance?.support?.single()?.evidence?.quote); assertNotEquals(source.id, saved.evidence.source_version_id)
        // A second proposal is explicitly rejected, retaining the first reviewed claim.
        val key = UUID.randomUUID(); val pending = PendingProposal(identity, scope.id, key, kind = "extract", body = adaJson.encodeToString(ExtractionInputDto(key, listOf(SourcePinDto(source.id, source.version, source.content_hash, 0, text.codePointCount(0, text.length))))))
        runBlocking { success(api.extractProposals(conn, pending)) }; compose.runOnIdle { vm.proposals.refresh() }
        compose.waitUntil(20_000) { vm.proposals.state.value.inbox.items.size == 1 }
        compose.runOnIdle { vm.proposals.open(vm.proposals.state.value.inbox.items.single()) }; compose.waitUntil(20_000) { vm.proposals.state.value.draft != null }
        compose.onNodeWithTag("proposal-annotation").performScrollTo().performTextInput("Reject the stale synthetic suggestion."); closeSoftKeyboard()
        compose.onNodeWithTag("proposal-reject").performScrollTo().performClick(); compose.onNodeWithTag("proposal-confirm").performClick()
        compose.waitUntil(20_000) { vm.proposals.state.value.draft == null && !vm.proposals.state.value.busy }
        assertEquals(1, runBlocking { success(api.claims(conn, scope.id)) }.size)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success) { "Synthetic proposal verification: ${(result as? ApiResult.Failure)?.reason}" }; return result.value }
}
