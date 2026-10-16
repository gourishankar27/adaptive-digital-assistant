package dev.ada.assistant

import android.Manifest
import android.content.pm.PackageManager
import android.view.accessibility.AccessibilityNodeInfo
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Actual OS dialog + verified permission state; capture is synthetic and never starts a mic. */
class VoicePermissionDialogTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    private val capture = InstrumentedVoiceCapture()
    private fun shell(command: String) {
        InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand(command).use {
            android.os.ParcelFileDescriptor.AutoCloseInputStream(it).use { stream -> stream.readBytes() }
        }
    }
    private fun prepare() {
        val context = compose.activity
        assumeTrue(context.packageName.startsWith("dev.ada.validation."))
        assertEquals(PackageManager.PERMISSION_DENIED, ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO))
        assertFalse(context.shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO))
        val file = File(context.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val token = file.readText().trim(); val c = ConnectionCredential.parse(fixtureOrigin(), token, true)!!
        val api = HttpAdaApi()
        val profile = runBlocking { (api.personalities(c) as ApiResult.Success).value.first() }
        val conversation = runBlocking { (api.createConversation(c, ConversationInputDto(profile.id, "Synthetic OS permission test")) as ApiResult.Success).value }
        vm = ViewModelProvider(context)[ChatViewModel::class.java]
        compose.runOnIdle { vm.voice.attachAudio(capture, InstrumentedVoicePlayback()); vm.connect(c.server.toString(), token) }
        compose.waitUntil(20_000) { vm.state.value.account != null }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id && !vm.state.value.events.loading }
        compose.onNodeWithTag("voice-toggle").performScrollTo().performClick()
    }
    private fun clickPermission(vararg endings: String) {
        val automation = InstrumentationRegistry.getInstrumentation().uiAutomation
        val deadline = System.currentTimeMillis() + 10_000
        fun find(node: AccessibilityNodeInfo?): AccessibilityNodeInfo? {
            if (node == null) return null
            if (endings.any { node.viewIdResourceName?.endsWith(it) == true } && node.isClickable) return node
            for (index in 0 until node.childCount) find(node.getChild(index))?.let { return it }
            return null
        }
        while (System.currentTimeMillis() < deadline) {
            val button = find(automation.rootInActiveWindow)
            if (button != null && button.performAction(AccessibilityNodeInfo.ACTION_CLICK)) return
            Thread.sleep(100)
        }
        fail("Expected OS permission button was not found; this is not a denial/grant pass")
    }
    @Test fun firstGrantPreservesOwnDialogIntent() {
        prepare()
        compose.onNodeWithTag("voice-record").performScrollTo().performClick()
        clickPermission("permission_allow_foreground_only_button", "permission_allow_one_time_button", "permission_allow_button")
        compose.waitUntil(10_000) { capture.callback != null }
        assertEquals(PackageManager.PERMISSION_GRANTED, ContextCompat.checkSelfPermission(compose.activity, Manifest.permission.RECORD_AUDIO))
        assertTrue(vm.voice.state.value.phase in setOf(VoicePhase.Checking, VoicePhase.Recording))
    }
    @Test fun verifiedDenialAndRepeatedDenialRemainActionable() {
        prepare()
        repeat(2) {
            compose.onNodeWithTag("voice-record").performScrollTo().performClick()
            clickPermission("permission_deny_button", "permission_deny_and_dont_ask_again_button")
            compose.waitUntil(10_000) { vm.voice.state.value.phase == VoicePhase.Denied }
            assertEquals(PackageManager.PERMISSION_DENIED, ContextCompat.checkSelfPermission(compose.activity, Manifest.permission.RECORD_AUDIO))
            assertNull(capture.callback)
            if (it == 0) assertTrue(compose.activity.shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO))
        }
        assertTrue(vm.voice.state.value.permissionPermanent)
        assertFalse(compose.activity.shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO))
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() } }
}
