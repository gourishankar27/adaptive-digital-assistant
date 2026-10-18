package dev.ada.assistant

import android.graphics.Bitmap
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/** Test-only host for public synthetic images; MainActivity keeps FLAG_SECURE intact. */
@OptIn(ExperimentalLayoutApi::class)
class AmbientUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private lateinit var vm: ChatViewModel
    private var dark by mutableStateOf(true)
    private var gallery by mutableStateOf(false)
    private var appearanceOpen by mutableStateOf(false)
    private var imeBottom = 0
    private var imeTarget = 0
    private val origin get() = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!

    @Before fun publicHost() {
        assumeTrue(compose.activity.packageName == "dev.ada.validation.redesign.debug")
        runBlocking { AndroidSessionStore(compose.activity).clear() }
        vm = ViewModelProvider(compose.activity, object : androidx.lifecycle.ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST") override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T =
                ChatViewModel(HttpAdaApi(), AndroidSessionStore(compose.activity), true) as T
        })[ChatViewModel::class.java]
        compose.runOnUiThread {
            compose.activity.window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
            compose.activity.enableEdgeToEdge(SystemBarStyle.dark(android.graphics.Color.TRANSPARENT), SystemBarStyle.dark(android.graphics.Color.TRANSPARENT))
        }
        compose.setContent {
            CompositionLocalProvider(LocalAdaMotionEnabled provides false) {
                AdaTheme(dark = dark) {
                    val density = LocalDensity.current
                    val bottom = WindowInsets.ime.getBottom(density)
                    val target = WindowInsets.imeAnimationTarget.getBottom(density)
                    SideEffect { imeBottom = bottom; imeTarget = target }
                    AdaAppFrame {
                        if (gallery) Column(Modifier.fillMaxSize().padding(AdaSpacing.medium)) {
                            Text("Public presence validation", style = MaterialTheme.typography.titleLarge)
                            AdaPresenceState.entries.forEach { state -> Row { AdaPresence(state, Modifier.size(AdaSpacing.touch)); Text(state.label) } }
                        } else ChatApp(vm) { appearanceOpen = true }
                    }
                    if (appearanceOpen) AppearanceSettingsDialog(AppearanceSettings(dark = dark), { dark = it.dark }, { appearanceOpen = false })
                }
            }
        }
    }
    @After fun releaseFixture() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() } }

    private fun capture(name: String) {
        compose.waitUntil(10000) { imeBottom == imeTarget }
        compose.waitForIdle()
        val bitmap = compose.onRoot().captureToImage().asAndroidBitmap()
        File(compose.activity.filesDir, "ada-public-$name.png").outputStream().use { assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG, 100, it)) }
        // Separate public test host only: include the OS keyboard to distinguish
        // a rotated Compose-layer capture from the actual visible app window.
        if (name == "typing") InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()?.let { window ->
            File(compose.activity.filesDir, "ada-public-typing-window.png").outputStream().use { assertTrue(window.compress(Bitmap.CompressFormat.PNG, 100, it)) }
        }
    }
    private fun login() {
        compose.onNodeWithTag("connect-server").performScrollTo().performTextInput(origin)
        compose.onNodeWithTag("connect-username").performScrollTo().performTextInput("synthetic-admin")
        compose.onNodeWithTag("connect-password").performScrollTo().performTextInput("Public synthetic Android passphrase 123")
        compose.onNodeWithTag("connect-action").performScrollTo().performClick()
        compose.waitUntil(30000) { vm.state.value.account != null && !vm.state.value.profiles.loading }
        compose.waitUntil(10000) { imeBottom == 0 }
    }
    private fun assertReadableHeading() {
        val layouts = mutableListOf<TextLayoutResult>()
        compose.onNodeWithText("Welcome back.").performSemanticsAction(SemanticsActions.GetTextLayoutResult) { it(layouts) }
        val ink = layouts.single().layoutInput.style.color.luminance()
        val canvas = ThemePalette.AmbientViolet.colorScheme(dark).background.luminance()
        assertTrue("Rendered heading must use readable theme ink", (maxOf(ink, canvas) + .05f) / (minOf(ink, canvas) + .05f) >= 4.5f)
    }
    private fun navigate(tag: String) {
        val node = compose.onNodeWithTag(tag)
        if (compose.onAllNodesWithTag("expanded-navigation").fetchSemanticsNodes().isNotEmpty()) node.performScrollTo()
        node.assertIsDisplayed().performClick()
    }
    private fun createConversation() {
        compose.onNodeWithTag("conversation-list").performScrollToNode(hasTestTag("new-conversation"))
        compose.onNodeWithTag("new-conversation").performClick()
        compose.onNodeWithTag("new-title").performScrollTo().performTextInput("Public ambient validation")
        closeSoftKeyboard()
        compose.waitUntil(10000) { imeBottom == 0 }
        if (vm.state.value.profiles.items.isEmpty()) {
            compose.onNodeWithTag("new-profile-name").performScrollTo().performTextReplacement("Public ambient style")
            compose.onNodeWithTag("create-profile").performScrollTo().performClick()
            compose.waitUntil(15000) { vm.state.value.createProfileId != null && !vm.state.value.creatingProfile }
        } else {
            val profile = vm.state.value.profiles.items.first().id
            compose.onNodeWithTag("profile-$profile").performScrollTo().performClick()
        }
        compose.waitUntil(10000) { imeBottom == 0 }
        compose.onNodeWithTag("create-conversation").performScrollTo().assertIsDisplayed().assertIsEnabled().performClick()
        try {
            compose.waitUntil(15000) { vm.state.value.destination == ChatDestination.Chat && vm.state.value.conversation != null }
        } catch (_: ComposeTimeoutException) {
            capture("chat")
            val s = vm.state.value
            throw AssertionError("Creation metadata: destination=${s.destination}, creating=${s.creating}, uncertain=${s.creationUncertain}, fault=${s.fault}, titleLength=${s.createTitle.length}, profile=${s.createProfileId != null}")
        }
    }
    private fun assertCompactChatControls() {
        compose.onNodeWithTag("open-curiosity").assertDoesNotExist()
        compose.onNodeWithTag("message-options").assertDoesNotExist()
        compose.onNodeWithTag("voice-controls-dialog").assertDoesNotExist()
        compose.onNodeWithTag("message-options-dialog").assertDoesNotExist()
        val density = compose.activity.resources.displayMetrics.density
        val controls = listOf("composer-menu", "voice-toggle", "send").map { tag ->
            val node = compose.onNodeWithTag(tag).assertIsDisplayed()
            node.assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.ContentDescription))
            val bounds = node.fetchSemanticsNode().boundsInRoot
            assertTrue("$tag needs a 48dp touch width", bounds.width >= 47.5f * density)
            assertTrue("$tag needs a 48dp touch height", bounds.height >= 47.5f * density)
            bounds
        }
        assertTrue("Attach, microphone and Send belong on one compact line", controls.maxOf { it.center.y } - controls.minOf { it.center.y } <= 8f * density)
        val root = compose.onRoot().fetchSemanticsNode().boundsInRoot
        val history = compose.onNodeWithTag("chat-history").assertIsDisplayed().fetchSemanticsNode().boundsInRoot
        val composer = compose.onNodeWithTag("chat-composer-surface").fetchSemanticsNode().boundsInRoot
        // Space is judged on the primary portrait phone, without imposing a fixed height
        // on large-font or short landscape windows where controls need to scroll.
        if (root.height > root.width * 1.2f && compose.activity.resources.configuration.fontScale <= 1.1f) {
            assertTrue("The conversation should retain most of the portrait viewport", history.height >= root.height * .45f)
            assertTrue("Idle controls must not consume a large composer panel", composer.height <= 148f * density)
        }
    }
    private fun inspectExpandableActionsAndOptions() {
        val conversation = vm.state.value.conversation!!
        compose.onNodeWithTag("chat-menu").assertIsDisplayed().performClick()
        val capabilities = vm.state.value.capabilities
        listOf(
            "open-research" to (capabilities?.web_research == "ada-web-research-v1"),
            "open-curiosity" to (capabilities?.curiosity_protocol == "ada-curiosity-v1"),
            "open-tools" to (capabilities?.hasAgentTools() == true),
            "open-episodes" to (capabilities?.hasEpisodes() == true),
        ).forEach { (tag, supported) ->
            if (supported) compose.onNodeWithTag(tag).performScrollTo().assertIsDisplayed()
            else compose.onNodeWithTag(tag).assertDoesNotExist()
        }
        compose.onNodeWithTag("conversation-details").performScrollTo().performClick()
        compose.onNodeWithTag("conversation-details-dialog").assertIsDisplayed()
        compose.onNodeWithTag("conversation-details-done").assertIsDisplayed().performClick()
        compose.onNodeWithTag("open-curiosity").assertDoesNotExist()

        val memory = vm.state.value.useMemory
        compose.onNodeWithTag("composer-menu").performClick()
        compose.onNodeWithTag("message-options").performClick()
        compose.onNodeWithTag("message-options-dialog").assertIsDisplayed()
        compose.onNodeWithContentDescription("Use saved memory in this message").performScrollTo().performClick()
        assertEquals(!memory, vm.state.value.useMemory)
        compose.onNodeWithContentDescription("Use saved memory in this message").performClick()
        val instant = "2026-10-08T12:00:00.000Z"
        compose.onNodeWithTag("historical-instant").performScrollTo().performTextInput(instant)
        closeSoftKeyboard()
        compose.waitUntil(10000) { imeBottom == 0 }
        compose.onNodeWithTag("message-options-done").assertIsDisplayed().performClick()
        compose.onNodeWithTag("message-options-dialog").assertDoesNotExist()
        compose.onNodeWithTag("composer-menu").performClick()
        compose.onNodeWithTag("message-options").performClick()
        compose.onNodeWithTag("historical-instant").performScrollTo().assertTextContains(instant).performTextReplacement("")
        closeSoftKeyboard()
        compose.waitUntil(10000) { imeBottom == 0 }
        compose.onNodeWithTag("message-options-done").assertIsDisplayed().performClick()
        assertEquals(memory, vm.state.value.useMemory)
        assertTrue(vm.state.value.asOf.isEmpty())
        assertNull(vm.state.value.pending)
        assertTrue(vm.state.value.events.items.isEmpty())

        compose.onNodeWithTag("voice-toggle").performClick()
        compose.onNodeWithTag("voice-controls-dialog").assertIsDisplayed()
        compose.onNodeWithTag("voice-controls-close").assertIsDisplayed().performClick()
        compose.onNodeWithTag("voice-controls-dialog").assertDoesNotExist()
        assertNull(vm.voice.state.value.draft)
        assertFalse(vm.voice.captureActive)

        // This is the existing scoped import screen, not a fabricated message attachment.
        compose.onNodeWithTag("composer-menu").performClick()
        compose.onNodeWithTag("attach-document").performClick()
        compose.waitUntil(10000) { vm.state.value.destination == ChatDestination.Documents }
        compose.onNodeWithTag("documents-list").assertIsDisplayed()
        assertNull(vm.state.value.pending)
        navigate("nav-chat")
        compose.waitUntil(15000) {
            vm.state.value.destination == ChatDestination.Conversations && !vm.state.value.conversations.loading
        }
        compose.onNodeWithTag("conversation-list").performScrollToNode(hasTestTag("conversation-${conversation.id}"))
        compose.waitForIdle()
        compose.onNodeWithTag("conversation-${conversation.id}").assertIsDisplayed().performTouchInput { click() }
        try {
            compose.waitUntil(15000) {
                vm.state.value.destination == ChatDestination.Chat &&
                    vm.state.value.conversation?.id == conversation.id && !vm.state.value.events.loading
            }
        } catch (error: ComposeTimeoutException) {
            runCatching { capture("chat") }
            val current = vm.state.value
            throw AssertionError(
                "Public document-return metadata: destination=${current.destination}, " +
                    "sameConversation=${current.conversation?.id == conversation.id}, " +
                    "eventsLoading=${current.events.loading}, listLoading=${current.conversations.loading}, " +
                    "accountPresent=${current.account != null}, fault=${current.fault?.javaClass?.simpleName}, " +
                    "imeBottom=$imeBottom, imeTarget=$imeTarget, windowFocus=${compose.activity.hasWindowFocus()}",
                error,
            )
        }
        assertEquals(conversation.id, vm.state.value.conversation?.id)
        assertTrue(vm.state.value.draft.isEmpty())
        assertTrue(vm.state.value.events.items.isEmpty())
    }
    @Test fun publicChatAndKeyboard() {
        assertReadableHeading()
        capture("connect")
        login(); capture("home"); createConversation(); capture("chat")
        assertCompactChatControls(); inspectExpandableActionsAndOptions(); capture("chat")
        compose.onNodeWithTag("composer").performScrollTo().performTextInput("Public sample: astronomy and maps.\nSecond public line 🌌")
        compose.onNodeWithTag("composer").assertIsFocused()
        compose.waitUntil(10000) { imeBottom > 0 && imeBottom == imeTarget }
        val root = compose.onRoot().fetchSemanticsNode().boundsInRoot
        val composer = compose.onNodeWithTag("chat-composer-surface").fetchSemanticsNode().boundsInRoot
        assertTrue("Composer must sit above the IME", kotlin.math.abs(composer.bottom - (root.bottom - imeBottom)) < 80f)
        val density = compose.activity.resources.displayMetrics.density
        listOf("composer-menu", "voice-toggle", "send").forEach { tag ->
            val bounds = compose.onNodeWithTag(tag).assertIsDisplayed().fetchSemanticsNode().boundsInRoot
            assertTrue("$tag must keep its full touch height while typing", bounds.height >= 47.5f * density)
            assertTrue("$tag must remain inside the visible app above the keyboard", bounds.top >= root.top && bounds.bottom <= composer.bottom + 1f)
        }
        capture("typing")
        compose.onNodeWithTag("send").performScrollTo().assertIsDisplayed().performClick()
        compose.waitUntil(30000) { vm.state.value.pending == null && vm.state.value.events.items.any { it.role == "assistant" } }
        val request = vm.state.value.events.items.last { it.role == "assistant" }.request_id
        val conn = vm.state.value.conversation!!
        val sourcesAction = hasText("Sources for this reply") or hasContentDescription("Sources for this reply")
        compose.onNodeWithTag("chat-history").performScrollToNode(sourcesAction)
        capture("chat")
        compose.onNode(sourcesAction).performClick()
        compose.waitUntil(10000) { !vm.state.value.sourceLoading && vm.state.value.sourceRequestId == request }
        capture("sources")
        assertEquals(conn.id, vm.state.value.sources[request]!!.conversation_id)
        navigate("nav-settings"); capture("settings")
        compose.onNodeWithTag("appearance").performScrollTo().performClick()
        compose.onNodeWithText("ADA Ambient").assertIsSelected()
    }
    @Test fun presenceSemanticsAndLightMode() {
        compose.runOnIdle { dark = false }; assertReadableHeading(); capture("light")
        compose.runOnIdle { dark = true; gallery = true }
        AdaPresenceState.entries.forEach { state ->
            compose.onNodeWithTag("ada-presence-${state.name}").assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription, state.label))
        }
        capture("presence")
    }
    @Test fun expandedNavigationAndFontScaling() {
        login()
        compose.onNodeWithTag("expanded-navigation").assertIsDisplayed()
        navigate("nav-memory")
        navigate("nav-documents")
        navigate("nav-settings")
        capture("settings")
        navigate("nav-chat"); createConversation()
        compose.onNodeWithTag("composer").performScrollTo().performTextInput("Public large-window typing check.")
        compose.onNodeWithTag("composer").assertIsFocused()
        compose.waitUntil(10000) { imeBottom > 0 && imeBottom == imeTarget }
        compose.onNodeWithTag("send").performScrollTo().assertIsDisplayed()
        capture("typing")
    }
}
