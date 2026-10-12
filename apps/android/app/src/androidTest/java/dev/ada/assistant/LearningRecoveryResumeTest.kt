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

class LearningRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun exactReviewReceiptRestoresAfterActualForceStop() {
        val args = InstrumentationRegistry.getArguments(); assumeTrue(args.getString("adaLearningRecovery") == "true")
        val key = UUID.fromString(args.getString("expectedLearningKey")); vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null && !vm.learning.state.value.busy && vm.learning.state.value.data?.learned?.any { it.receipt_id == key } == true }
        assertNull(vm.learning.state.value.journal)
        val store = AndroidSessionStore(compose.activity.applicationContext); val credential = runBlocking { store.readCredential() }!!
        assertNull(runBlocking { store.learningJournal(credential.identity) })
        val c = ConnectionCredential.parse(credential.identity.server, credential.token, true)!!; val api = HttpAdaApi()
        val receipt = runBlocking { success(api.learningReceipt(c, key)) }; assertEquals("approve", receipt.decision)
        val current = runBlocking { success(api.learning(c, receipt.scope_id)) }
        assertEquals(1, current.learned.size); assertEquals(key, current.learned.single().receipt_id)
    }
    @After fun cleanup() { if(::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
