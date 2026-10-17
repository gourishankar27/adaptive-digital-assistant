package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatViewModel
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import java.io.File
import java.security.MessageDigest
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Separate validation app, actual ADA HTTP, Android Keystore and Activity recreation. */
class PasswordLoginUiHttpTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    @Test fun passwordLoginAndRenewBeforeProcessStop() {
        assumeTrue(compose.activity.packageName.startsWith("dev.ada.validation."))
        val origin = InstrumentationRegistry.getArguments().getString("passwordOrigin")
        assumeTrue(origin != null)
        val store = AndroidSessionStore(compose.activity.applicationContext)
        runBlocking { store.clear() }
        var vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.disconnect() }
        compose.waitUntil(10000) { runBlocking { store.readCredential() } == null }
        compose.onNodeWithTag("connect-server").performTextInput(origin!!)
        compose.onNodeWithTag("connect-username").performScrollTo().performTextInput("synthetic-admin")
        compose.onNodeWithTag("connect-password").performScrollTo().performTextInput("Public synthetic Android passphrase 123")
        closeSoftKeyboard()
        compose.onNodeWithTag("connect-action").performScrollTo().performClick()
        compose.waitUntil(30000) { vm.state.value.account != null }
        val first = runBlocking { store.readCredential() }!!
        assertTrue(first.passwordSession)
        compose.activityRule.scenario.recreate()
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(30000) { vm.state.value.account != null }
        assertEquals(first.identity, runBlocking { store.readCredential() }!!.identity)
        compose.runOnIdle { vm.renewSession() }
        compose.waitUntil(30000) { vm.state.value.account != null && runBlocking { store.readCredential() }?.token != first.token }
        val renewed = runBlocking { store.readCredential() }!!
        File(compose.activity.filesDir, "password-refresh-before.sha256").writeText(digest(renewed.token))
    }
    @Test fun passwordRestoreAfterActualProcessStopThenRevoke() {
        assumeTrue(compose.activity.packageName.startsWith("dev.ada.validation."))
        val origin = InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
        val marker = File(compose.activity.filesDir, "password-refresh-before.sha256")
        assertTrue("Run the login stage first", marker.isFile)
        val store = AndroidSessionStore(compose.activity.applicationContext)
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(30000) { vm.state.value.account != null }
        val renewed = runBlocking { store.readCredential() }!!
        assertTrue(renewed.passwordSession)
        assertNotEquals(marker.readText(), digest(renewed.token))
        assertTrue(marker.delete())
        compose.runOnIdle { vm.logout(all = true) }
        compose.waitUntil(10000) { vm.state.value.account == null && runBlocking { store.readCredential() } == null }
        // Logout runs asynchronously without replay. Poll metadata-free refresh rejection once it settles.
        var denied = false
        compose.waitUntil(15000) {
            if (!denied) denied = runBlocking { HttpAdaApi().refreshLogin(origin, renewed.token, true) } is ApiResult.Failure
            denied
        }
        compose.onNodeWithTag("connect-password").assert(SemanticsMatcher.expectValue(androidx.compose.ui.semantics.SemanticsProperties.EditableText, androidx.compose.ui.text.AnnotatedString("")))
    }
    private fun digest(value: String) = MessageDigest.getInstance("SHA-256").digest(value.toByteArray()).joinToString("") { "%02x".format(it) }
}
