package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class EntityRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun resumesExactEntityAfterProcessStopWithoutDuplicate() {
        val args = InstrumentationRegistry.getArguments(); assumeTrue("Run explicit entity recovery stages", args.getString("adaEntityRecovery") == "true")
        val expected = UUID.fromString(args.getString("expectedEntityOperation")); vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null && vm.entities.state.value.pending?.operationId == expected && !vm.entities.state.value.busy }
        val store = AndroidSessionStore(compose.activity.applicationContext); val saved = runBlocking { store.readCredential() }!!; val pending = runBlocking { store.entityPending(saved.identity) }!!
        assertEquals(expected, pending.operationId); assertTrue(pending.body.contains("Synthetic recovery"))
        val conn = ConnectionCredential.parse(saved.identity.server, saved.token, true)!!; val api = HttpAdaApi()
        val before = runBlocking { success(api.entityOperation(conn, expected)) }; assertEquals(1, runBlocking { success(api.entities(conn, pending.scopeId)) }.size)
        compose.runOnIdle { vm.navigate(ChatDestination.Entities) }
        compose.onNodeWithTag("entities-list").performScrollToNode(hasTestTag("entity-resume")); compose.onNodeWithTag("entity-resume").performClick()
        compose.waitUntil(20_000) { vm.entities.state.value.pending == null && !vm.entities.state.value.busy }
        assertNull(runBlocking { store.entityPending(saved.identity) }); assertEquals(before, runBlocking { success(api.entityOperation(conn, expected)) })
        assertEquals(1, runBlocking { success(api.entities(conn, pending.scopeId)) }.size)
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
