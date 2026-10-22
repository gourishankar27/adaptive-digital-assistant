package dev.ada.assistant

import android.graphics.Bitmap
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.platform.UriHandler
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/** Public synthetic HTTP/Keystore/UI only; never targets the ordinary ADA app or account. */
@OptIn(ExperimentalLayoutApi::class, ExperimentalTestApi::class)
class DesignGapsUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private lateinit var vm: ChatViewModel
    private var dark by mutableStateOf(true)
    private var gallery by mutableStateOf(false)
    private var confirmed = 0
    private var selected by mutableStateOf(false)
    private var dialog by mutableStateOf(false)
    private var openedUri: String? = null
    private val publicLinkText = "Public https://example.test/guide and unsafe javascript:alert(1) https://user:pass@example.test"
    private var imeBottom = 0
    private var imeTarget = 0
    private val origin get() = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
    private val variant get() = InstrumentationRegistry.getArguments().getString("designVariant") ?: "phone"

    @Before fun publicHost() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.designgaps.debug")
        if (variant == "landscape" || variant == "expanded") {
            compose.runOnUiThread {
                compose.activity.requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
            }
            compose.waitUntil(10000) {
                val current = compose.activity.resources.configuration
                current.screenWidthDp > current.screenHeightDp
            }
        }
        val configuration = compose.activity.resources.configuration
        if (variant == "landscape") assertTrue("Require actual landscape configuration", configuration.screenWidthDp > configuration.screenHeightDp)
        if (variant == "expanded") assertTrue("Require expanded window", configuration.screenWidthDp >= 840)
        if (variant == "large-font") assertTrue("Require enlarged system font", configuration.fontScale >= 1.3f)
        runBlocking { AndroidSessionStore(compose.activity).clear() }
        vm = ViewModelProvider(compose.activity, object : androidx.lifecycle.ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST") override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T =
                ChatViewModel(HttpAdaApi(), AndroidSessionStore(compose.activity), true) as T
        })[ChatViewModel::class.java]
        compose.runOnUiThread {
            compose.activity.window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
            compose.activity.enableEdgeToEdge(SystemBarStyle.dark(android.graphics.Color.TRANSPARENT), SystemBarStyle.dark(android.graphics.Color.TRANSPARENT))
        }
        compose.runOnIdle { vm.voice.attachAudio(InstrumentedVoiceCapture(), InstrumentedVoicePlayback()) }
        compose.setContent {
            CompositionLocalProvider(LocalAdaMotionEnabled provides false) {
                AdaTheme(dark = dark) {
                    val density = LocalDensity.current
                    val bottom = WindowInsets.ime.getBottom(density)
                    val target = WindowInsets.imeAnimationTarget.getBottom(density)
                    SideEffect { imeBottom = bottom; imeTarget = target }
                    AdaAppFrame {
                        if (gallery) Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                            AdaFailureNotice(ApiFailure.Tls, Modifier.testTag("public-error"))
                            AdaLoading("Checking public validation state", Modifier.testTag("public-loading"))
                            AdaTextButton({}, Modifier.testTag("native-button")) { Text("Native target") }
                            AdaChoiceChip(selected, "Public selection", { selected = !selected }, Modifier.testTag("public-choice"))
                            AdaToggle(selected, "Public checkbox label", { selected = it }, Modifier.testTag("public-toggle"))
                            CompositionLocalProvider(LocalUriHandler provides object : UriHandler {
                                override fun openUri(uri: String) { openedUri = uri }
                            }) { SafeChatText(publicLinkText) }
                            Button({ dialog = true }, Modifier.testTag("open-confirm")) { Text("Review confirmation") }
                            if (dialog) AdaConfirmation("Public confirmation", "Only a synthetic callback is under test.", "Confirm", { dialog = false }, { confirmed++; dialog = false }, "public-confirm")
                        } else ChatApp(vm) {}
                    }
                }
            }
        }
    }

    @After fun clearValidationOnly() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() } }

    private fun capture(name: String, tag: String? = null) {
        closeSoftKeyboard()
        compose.waitUntil(10000) { imeBottom == 0 }
        compose.waitForIdle()
        val bitmap = (if (tag == null) compose.onRoot() else compose.onNodeWithTag(tag)).captureToImage().asAndroidBitmap()
        File(compose.activity.filesDir, "ada-design-$name.png").outputStream().use { assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG, 100, it)) }
    }
    private fun login() {
        compose.onNodeWithTag("connect-server").performScrollTo().performTextInput(origin)
        compose.onNodeWithTag("connect-username").performScrollTo().performTextInput("synthetic-owner")
        compose.onNodeWithTag("connect-password").performScrollTo().performTextInput("Public synthetic Android passphrase 123")
        compose.onNodeWithTag("connect-action").performScrollTo().performClick()
        compose.waitUntil(30000) { vm.state.value.account != null && !vm.state.value.profiles.loading }
        compose.waitUntil(10000) { imeBottom == 0 }
    }
    private fun navigate(tag: String) {
        val node = compose.onNodeWithTag(tag)
        if (compose.onAllNodesWithTag("expanded-navigation").fetchSemanticsNodes().isNotEmpty()) node.performScrollTo()
        node.assertIsDisplayed().performClick()
    }
    private fun createConversation() {
        compose.onNodeWithTag("new-conversation").performScrollTo().performClick()
        compose.onNodeWithTag("new-title").performScrollTo().performTextInput("Public design validation")
        closeSoftKeyboard(); compose.waitUntil(10000) { imeBottom == 0 }
        compose.waitUntil(15000) { !vm.state.value.profiles.loading && !vm.state.value.scopes.loading && vm.state.value.createProfileId != null }
        val scope = vm.state.value.scopes.items.firstOrNull { it.name == "Android verification" }
        if (scope != null) compose.onNodeWithTag("scope-${scope.id}").performScrollTo().performClick()
        compose.onNodeWithTag("create-conversation").performScrollTo().performClick()
        compose.waitUntil(15000) { vm.state.value.conversation != null && !vm.state.value.events.loading }
    }
    private fun openFeature(tag: String) {
        if (vm.state.value.destination != ChatDestination.Chat) compose.runOnIdle { vm.navigate(ChatDestination.Chat) }
        compose.onNodeWithTag("chat-menu").performClick()
        compose.onNodeWithTag(tag).performScrollTo().performClick()
    }
    private fun schemeWalk(isDark: Boolean) {
        compose.runOnIdle { dark = isDark }
        val mode = if (isDark) "dark" else "light"
        capture("$mode-connect")
        login(); capture("$mode-conversations"); createConversation()
        compose.onNodeWithTag("composer").performTextInput("Which color does the Android verification project use?")
        closeSoftKeyboard(); compose.waitUntil(10000) { imeBottom == 0 }
        compose.onNodeWithTag("send").performClick()
        compose.waitUntil(30000) { vm.state.value.pending == null && vm.state.value.events.items.any { it.role == "assistant" } }
        capture("$mode-chat")
        compose.onNodeWithTag("chat-history").performScrollToNode(hasTestTag("source-chip-M1"))
        compose.onNodeWithTag("source-chip-M1").performClick()
        compose.waitUntil(10000) { !vm.state.value.sourceLoading }
        capture("$mode-sources")
        compose.onNodeWithTag("sources-list").performScrollToNode(hasTestTag("screen-back"))
        compose.onNodeWithTag("screen-back").performClick()

        compose.onNodeWithTag("composer-menu").performClick(); compose.onNodeWithTag("message-options").performClick()
        val options = compose.onNodeWithTag("message-options-dialog").assertIsDisplayed()
        assertTrue(options.fetchSemanticsNode().boundsInRoot.height <= compose.activity.resources.displayMetrics.heightPixels)
        compose.onNodeWithTag("message-options-done").assertIsDisplayed().performClick()
        compose.onNodeWithTag("voice-toggle").performClick()
        capture("$mode-voice", "voice-controls-dialog")
        compose.onNodeWithTag("voice-controls-close").performClick()

        navigate("nav-settings"); capture("$mode-settings")
        compose.onNodeWithTag("settings-password").performScrollTo().performClick()
        compose.onNodeWithText("Review signed-in devices").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.passwordSessions.value.any { it.revoked_at == null } }
        compose.onAllNodesWithText("Revoke").onFirst().performScrollTo().performClick()
        compose.onNodeWithTag("password-revoke-dialog").assertIsDisplayed()
        compose.onNodeWithTag("password-revoke-cancel").assertIsFocused().performClick()
        assertNotNull(vm.state.value.account)
        compose.onNodeWithTag("logout").performScrollTo().performClick()
        compose.onNodeWithTag("logout-cancel").assertIsFocused().performKeyInput { pressKey(Key.Enter) }
        assertNotNull(vm.state.value.account)
        compose.onNodeWithTag("logout-dialog").assertDoesNotExist()
        navigate("nav-memory")
        compose.waitUntil(15000) { !vm.memory.state.value.claims.loading && !vm.memory.state.value.scopes.loading }
        vm.memory.state.value.claims.items.firstOrNull()?.let { claim ->
            compose.onNodeWithTag("memory-list").performScrollToNode(hasTestTag("memory-claim-${claim.id}"))
            compose.onNodeWithTag("memory-claim-${claim.id}").assert(SemanticsMatcher.expectValue(SemanticsProperties.Role, Role.Button))
        }
        capture("$mode-memory")
        compose.onNodeWithTag("open-entities").performClick()
        compose.waitUntil(15000) { !vm.entities.state.value.busy && !vm.entities.state.value.scopes.loading }
        capture("$mode-entities")
        compose.runOnIdle { vm.navigate(ChatDestination.Memory) }
        compose.onNodeWithTag("open-proposals").performClick()
        compose.waitUntil(15000) { !vm.proposals.state.value.busy }
        capture("$mode-proposals")
        navigate("nav-documents")
        compose.waitUntil(15000) { !vm.documents.state.value.uploads.loading && !vm.documents.state.value.scopes.loading }
        capture("$mode-documents")
        openFeature("open-episodes")
        compose.waitUntil(15000) { !vm.episodes.state.value.busy }
        capture("$mode-episodes")
        openFeature("open-tools"); capture("$mode-tools")
        openFeature("open-research"); capture("$mode-research")
        openFeature("open-curiosity")
        compose.waitUntil(15000) { vm.curiosity.state.value.policy != null && !vm.curiosity.state.value.busy }
        compose.onNodeWithTag("curiosity-enabled").assertIsOff()
        capture("$mode-curiosity")
    }
    @Test fun darkPrimaryScreensAndSafeConfirmations() = schemeWalk(true)
    @Test fun lightPrimaryScreensAndSafeConfirmations() = schemeWalk(false)

    @Test fun feedbackSelectionNativeTargetsAndModalKeyboardFocus() {
        compose.runOnIdle { gallery = true }
        compose.onNodeWithTag("public-error").assert(SemanticsMatcher.expectValue(SemanticsProperties.LiveRegion, LiveRegionMode.Polite))
        compose.onNodeWithTag("public-error").assertTextContains("secure server identity could not be verified", substring = true)
        compose.onNodeWithContentDescription("Checking public validation state").assertExists()
        val density = compose.activity.resources.displayMetrics.density
        val bounds = compose.onNodeWithTag("native-button").performScrollTo().fetchSemanticsNode().boundsInRoot
        assertTrue("Shared native button must reserve at least48dp", bounds.height >= density * 47.5f)
        compose.onNodeWithTag("public-choice").performScrollTo().assertIsNotSelected().performClick().assertIsSelected()
        compose.onNodeWithTag("public-toggle").performScrollTo().assertIsOn().performClick().assertIsOff()
        val link = compose.onNodeWithText(publicLinkText).performScrollTo()
        val layouts = mutableListOf<androidx.compose.ui.text.TextLayoutResult>()
        link.performSemanticsAction(SemanticsActions.GetTextLayoutResult) { assertTrue(it(layouts)) }
        val annotated = layouts.single().layoutInput.text
        assertEquals(publicLinkText, annotated.text)
        assertEquals(1, annotated.getLinkAnnotations(0, annotated.length).size)
        assertNull(openedUri)
        val box = layouts.single().getBoundingBox(publicLinkText.indexOf("https://"))
        link.performTouchInput { click(box.center) }
        compose.runOnIdle { assertEquals("https://example.test/guide", openedUri) }
        compose.onNodeWithTag("open-confirm").performScrollTo().performClick()
        compose.onNodeWithTag("public-confirm-cancel").also {
            compose.waitUntil(5000) { it.fetchSemanticsNode().config.getOrElse(SemanticsProperties.Focused) { false } }
        }.assertIsFocused().performKeyInput { pressKey(Key.Enter) }
        assertEquals(0, confirmed)
        compose.onNodeWithTag("open-confirm").performScrollTo().performClick()
        compose.onNodeWithTag("public-confirm-confirm").performClick()
        assertEquals(1, confirmed)
        capture("feedback-selection")
    }

    @Test fun keyboardBackPreservesConversationAndTypedDraft() {
        login(); createConversation()
        val id = vm.state.value.conversation!!.id
        compose.onNodeWithTag("composer").performTextInput("Public multiline draft\nSecond line 😀")
        compose.waitUntil(10000) { imeBottom > 0 && imeBottom == imeTarget }
        compose.onNodeWithTag("send").assertIsDisplayed()
        androidx.test.espresso.Espresso.pressBack()
        compose.waitUntil(10000) { imeBottom == 0 }
        assertEquals(ChatDestination.Chat, vm.state.value.destination)
        assertEquals(id, vm.state.value.conversation!!.id)
        assertEquals("Public multiline draft\nSecond line 😀", vm.state.value.draft)
        assertNull(vm.state.value.pending)
        compose.onNodeWithTag("chat-menu").assertIsDisplayed()
    }

    @Test fun shortWindowContextAndOptionsStayInsideWindow() {
        login(); createConversation()
        compose.onNodeWithTag("chat-menu").performClick(); compose.onNodeWithTag("conversation-details").performClick()
        val context = compose.onNodeWithTag("conversation-details-dialog").assertIsDisplayed().fetchSemanticsNode().boundsInRoot
        assertTrue(context.height <= compose.activity.resources.displayMetrics.heightPixels)
        compose.onNodeWithTag("conversation-details-done").assertIsDisplayed()
        capture("context-dialog", "conversation-details-dialog")
        compose.onNodeWithTag("conversation-details-done").performClick()
        compose.onNodeWithTag("composer-menu").performClick(); compose.onNodeWithTag("message-options").performClick()
        compose.onNodeWithTag("historical-instant").performScrollTo().performTextInput("2026-10-18T12:00:00Z")
        closeSoftKeyboard()
        compose.onNodeWithTag("message-options-done").assertIsDisplayed()
        capture("options-dialog", "message-options-dialog")
        compose.onNodeWithTag("message-options-done").performClick()
        assertNull(vm.state.value.pending)
        assertTrue(vm.state.value.events.items.isEmpty())
    }
}
