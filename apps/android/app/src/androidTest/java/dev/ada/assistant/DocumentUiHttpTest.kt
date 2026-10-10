package dev.ada.assistant

import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.performTextInput
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import dev.ada.assistant.ui.DocumentScreen
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** The production Compose preview/upload/details path with real HTTP, synthetic text and no provider call. */
class DocumentUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun reviewedExactPastedTextUploadsOnlyAfterExplicitButton() {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token")
        assumeTrue("Provision the disposable Android HTTP fixture server", file.isFile)
        val token = file.readText().trim(); val connection = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!
        val api = HttpAdaApi(); val scope = runBlocking { success(api.createScope(connection, ScopeInputDto("Document reviewed UI verification"))) }
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(connection.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null && !vm.state.value.connecting }
        compose.onNodeWithTag("nav-documents").performClick()
        compose.waitUntil(20_000) { vm.documents.state.value.scopes.items.any { it.id == scope.id } && !vm.documents.state.value.scopes.loading }
        compose.runOnIdle { vm.documents.selectScope(scope.id) }
        compose.onNodeWithTag("documents-list").performScrollToNode(hasTestTag("document-new"))
        compose.onNodeWithTag("document-new").performScrollTo().performClick()
        val exact = "Synthetic Document Falcon UI uses Oxford Blue. 😀 e\u0301\n日本語 <script>literal</script>"
        compose.onNodeWithTag("document-text").performScrollTo().performTextInput(exact)
        closeSoftKeyboard()
        compose.onNodeWithTag("document-preview").performScrollTo().performClick()
        compose.waitUntil(5_000) { vm.documents.state.value.screen == DocumentScreen.Preview }
        compose.onNodeWithTag("document-preview-text").performScrollTo().assertTextContains(exact)
        assertTrue(runBlocking { success(api.documentUploads(connection, scope.id)) }.isEmpty())
        assertNull(runBlocking { AndroidSessionStore(compose.activity.applicationContext).documentPending(SessionIdentity(connection.server.toString(), vm.state.value.account!!.owner)) })
        compose.onNodeWithTag("document-upload").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.documents.state.value.pending == null && !vm.documents.state.value.saving && vm.documents.state.value.version?.content == exact }
        compose.onNodeWithTag("document-version-text").performScrollTo().assertTextContains(exact)
        val receipt = vm.documents.state.value.detail!!
        assertEquals("imported_untrusted", receipt.trust_class); assertEquals("imported_document", receipt.origin)
        assertEquals(1, runBlocking { success(api.documentUploads(connection, scope.id)) }.size)
        assertTrue(runBlocking { success(api.claims(connection, scope.id)) }.isEmpty())
        compose.runOnIdle { vm.navigate(ChatDestination.Conversations) }
    }
    @After fun cleanup() {
        if (::vm.isInitialized) compose.runOnIdle { vm.logout() }
        runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() }
    }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success) { "Synthetic authenticated document UI verification failed" }; return result.value }
}
