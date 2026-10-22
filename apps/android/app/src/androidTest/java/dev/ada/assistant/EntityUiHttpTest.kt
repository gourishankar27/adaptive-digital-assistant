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
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Production UI and authenticated API; identities and assertions are synthetic. */
class EntityUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    private fun click(tag: String) { compose.onNodeWithTag("entities-list").performScrollToNode(hasTestTag(tag)); compose.onNodeWithTag(tag).performScrollTo().performClick() }
    @Test fun reviewedCreationAliasesAmbiguityLinksMergeAndUndoPreserveEvidence() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token")
        assumeTrue("Provision disposable HTTP fixtures", file.isFile)
        val token = file.readText().trim(); val conn = ConnectionCredential.parse(fixtureOrigin(18764), token, true)!!; val api = HttpAdaApi()
        val scope = runBlocking { success(api.createScope(conn, ScopeInputDto("Synthetic entity UI"))) }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(conn.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null && !vm.entities.state.value.busy }
        compose.runOnIdle { vm.navigate(ChatDestination.Entities) }
        compose.waitUntil(20_000) { vm.entities.state.value.scopes.items.any { it.id == scope.id } }
        compose.runOnIdle { vm.entities.selectScope(scope.id) }
        fun create(label: String): EntityDto {
            compose.onNodeWithTag("entities-list").performScrollToNode(hasTestTag("entity-label"))
            compose.onNodeWithTag("entity-label").performTextInput(label); closeSoftKeyboard(); click("entity-resolve")
            compose.waitUntil(20_000) { vm.entities.state.value.resolution != null && !vm.entities.state.value.busy }
            click("entity-create"); assertNotNull(vm.entities.state.value.preview)
            val count = runBlocking { success(api.entities(conn, scope.id)) }.size
            compose.onNodeWithTag("entity-confirm").performClick()
            compose.waitUntil(20_000) { vm.entities.state.value.pending == null && !vm.entities.state.value.busy && vm.entities.state.value.entities.items.size == count + 1 }
            return vm.entities.state.value.entities.items.single { it.label == label }
        }
        val first = create("Synthetic Alex One"); val second = create("Synthetic Alex Two")
        fun confirm() { compose.onNodeWithTag("entity-confirm").performClick(); compose.waitUntil(20_000) { !vm.entities.state.value.busy && vm.entities.state.value.pending == null }; assertNull(vm.entities.state.value.fault) }
        for (row in listOf(first, second)) {
            click("entity-select-${row.id}")
            compose.waitUntil(20_000) { vm.entities.state.value.aliases.isNotEmpty() }
            compose.runOnIdle { vm.entities.label("ＡＬＥＸ"); vm.entities.reviewAlias() }; confirm()
            compose.waitUntil(20_000) { !vm.entities.state.value.entities.loading }
        }
        compose.runOnIdle { vm.entities.label("alex"); vm.entities.resolve() }
        compose.waitUntil(20_000) { vm.entities.state.value.resolution?.state == "ambiguous" }
        compose.onNodeWithTag("entities-list").performScrollToNode(hasTestTag("entity-resolution"))
        compose.onNodeWithTag("entity-resolution").assertTextContains("Ambiguous", substring = true)
        compose.runOnIdle { vm.entities.resolve(first.id) }; compose.waitUntil(20_000) { vm.entities.state.value.resolution?.explicitly_selected == true }
        val exact = "Synthetic raw Alex prefers cobalt. 😀 e\u0301"
        val source = runBlocking { success(api.createNote(conn, scope.id, NoteInputDto(java.util.UUID.randomUUID(), exact))) }
        val claim = runBlocking { success(api.createClaim(conn, scope.id, ClaimInputDto(claim_id = java.util.UUID.randomUUID(), source_version_id = source.id, span_start = 0, span_end = exact.codePointCount(0, exact.length), subject = "Raw Alex", predicate = "material", value = "cobalt"))) }
        compose.runOnIdle { vm.entities.refresh() }; compose.waitUntil(20_000) { vm.entities.state.value.claims.items.any { it.id == claim.id } }
        click("entity-select-${first.id}")
        compose.runOnIdle { vm.entities.selectClaim(claim.id); vm.entities.reviewLink() }; confirm()
        assertEquals(first.id, runBlocking { success(api.claims(conn, scope.id)) }.single().subject_entity_id)
        compose.waitUntil(20_000) { !vm.entities.state.value.entities.loading }; click("entity-select-${first.id}")
        compose.runOnIdle { vm.entities.previewMerge(second.id) }; compose.waitUntil(20_000) { vm.entities.state.value.mergePreview != null && !vm.entities.state.value.busy }
        assertNull(runBlocking { success(api.entities(conn, scope.id)) }.single { it.id == first.id }.redirect_id)
        compose.runOnIdle { vm.entities.reviewMerge() }; confirm()
        compose.waitUntil(20_000) { vm.entities.state.value.entities.items.any { it.id == first.id && it.redirect_id == second.id } }; click("entity-select-${first.id}")
        compose.runOnIdle { vm.entities.reviewUndo() }; confirm()
        val original = runBlocking { success(api.claims(conn, scope.id)) }.single()
        assertEquals("Raw Alex", original.subject); assertEquals(exact, original.evidence.quote); assertEquals(first.id, original.subject_entity_id)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success) { "Synthetic entity verification failed" }; return result.value }
}
