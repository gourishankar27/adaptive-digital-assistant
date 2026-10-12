package dev.ada.assistant

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatViewModel
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class ExpressionRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun exactPreferenceReceiptRestoresAfterActualForceStop() {
        val args = InstrumentationRegistry.getArguments(); assumeTrue(args.getString("adaExpressionRecovery") == "true")
        val key = UUID.fromString(args.getString("expectedExpressionKey")); vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null && !vm.expression.state.value.busy && vm.expression.state.value.preference?.receipt_id == key }
        assertNull(vm.expression.state.value.journal)
        assertEquals("detailed", vm.expression.state.value.preference!!.values.verbosity)
        assertEquals("stepwise", vm.expression.state.value.preference!!.values.cadence)
        val store = AndroidSessionStore(compose.activity.applicationContext); val saved = runBlocking { store.readCredential() }!!
        assertNull(runBlocking { store.expressionJournal(saved.identity) })
        val c = ConnectionCredential.parse(saved.identity.server, saved.token, true)!!; val api = HttpAdaApi()
        val receipt = runBlocking { success(api.expressionReceipt(c, key)) }
        assertEquals(vm.expression.state.value.preference!!.revision, receipt.preference!!.revision)
        assertEquals(key, runBlocking { success(api.preference(c, "account", saved.identity.owner)) }.receipt_id)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
