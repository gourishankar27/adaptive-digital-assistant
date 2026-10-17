package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Real owned disposable HTTP and Android Keystore, no production account or inference. */
class SecurityUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun deviceInstallRotationRevocationAndExplicitErasureClearPrivateRecovery() {
        assumeTrue(compose.activity.packageName.startsWith("dev.ada.validation."))
        val file = File(compose.activity.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val c = ConnectionCredential.parse(fixtureOrigin(), token, true)!!
        val api = HttpAdaApi(); val store = AndroidSessionStore(compose.activity.applicationContext)
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(c.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null && vm.security.state.value.status != null && !vm.security.state.value.busy }
        assumeTrue(vm.security.state.value.status!!.enrollment_enabled)
        compose.runOnIdle { vm.navigate(ChatDestination.Settings) }
        compose.onNodeWithTag("security-label").performScrollTo().performTextInput("Synthetic validation device")
        androidx.test.espresso.Espresso.closeSoftKeyboard()
        compose.onNodeWithText("Enroll device (30 days)").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.security.state.value.issued?.token != null && !vm.security.state.value.busy }
        val first = vm.security.state.value.issued!!.credential.id
        compose.runOnIdle { vm.security.useIssued() }
        compose.waitUntil(20_000) { vm.security.state.value.status?.current_credential_id == first && !vm.security.state.value.busy }
        val saved = runBlocking { store.readCredential() }!!
        assertEquals(vm.state.value.account!!.owner, saved.identity.owner)
        compose.runOnIdle { vm.security.enroll("Synthetic replacement", first) }
        compose.waitUntil(20_000) { vm.security.state.value.status?.current_credential_id?.let { it != first } == true && !vm.security.state.value.busy }
        val rotated = vm.security.state.value.status!!.current_credential_id!!
        val old = ConnectionCredential.parse(saved.identity.server, saved.token, true)!!
        assertEquals(ApiFailure.Unauthorized, (runBlocking { api.me(old) } as ApiResult.Failure).reason)
        compose.runOnIdle { vm.security.revoke(rotated) }
        compose.waitUntil(20_000) { vm.state.value.account == null }
        compose.waitUntil(10_000) { runBlocking { store.readCredential() } == null }
        compose.runOnIdle { vm.connect(c.server.toString(), token) }
        compose.waitUntil(20_000) { vm.security.state.value.status?.legacy_credential == true && !vm.security.state.value.busy }
        val profile = runBlocking { (api.personalities(c) as ApiResult.Success).value.first() }
        val conversation = runBlocking { (api.createConversation(c, ConversationInputDto(profile.id, "Synthetic deletion validation")) as ApiResult.Success).value }
        val request = UUID.randomUUID()
        assertTrue(runBlocking { api.send(c, conversation.id, ChatInputDto(request, "Synthetic saved content validation")) } is ApiResult.Success)
        compose.runOnIdle { vm.navigate(ChatDestination.Settings) }
        compose.onNodeWithTag("delete-preview").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.security.state.value.preview != null && !vm.security.state.value.busy }
        compose.onNodeWithTag("delete-confirm").performScrollTo().assertIsNotEnabled()
        compose.onNodeWithTag("delete-ack").performScrollTo().performClick()
        compose.onNodeWithTag("delete-confirm").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.security.state.value.pending?.kind == "delete" || vm.state.value.account == null }
        if (vm.state.value.account != null) {
            // Confirmation queues durable work; a single immediate refresh may still read queued.
            // Finish confirmation first: overlapping receipt polling can trip owner admission.
            // Then wait on the owned GET receipt before exercising explicit client refresh.
            compose.waitUntil(20_000) { !vm.security.state.value.busy }
            assertNotNull("No deletion acknowledgement; fixed client feedback: ${vm.security.state.value.notice}", vm.security.state.value.deletion)
            val deletionId = vm.security.state.value.pending!!.operation
            var observed: ApiResult<DeletionDto>? = null
            try {
                compose.waitUntil(20_000) {
                    observed = runBlocking { api.deletion(c, deletionId) }
                    (observed as? ApiResult.Success)?.value?.status == "completed"
                }
            } catch (failure: Throwable) {
                val safe = when (val result = observed) {
                    is ApiResult.Success -> "state=${result.value.status}, code=${result.value.error_code}"
                    is ApiResult.Failure -> "failure=${result.reason.javaClass.simpleName}, code=${result.code}"
                    null -> "no receipt"
                }
                throw AssertionError("Synthetic deletion did not complete: $safe", failure)
            }
            compose.waitUntil(20_000) { !vm.security.state.value.busy }
            compose.runOnIdle { vm.security.refresh() }
        }
        compose.waitUntil(20_000) { vm.state.value.account == null }
        compose.waitUntil(10_000) { runBlocking { store.readCredential() } == null }
        assertNull(vm.voice.state.value.draft); assertTrue(vm.state.value.sources.isEmpty())
        assertEquals(ApiFailure.Http(410), (runBlocking { api.request(c, request) } as ApiResult.Failure).reason)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() } }
}
