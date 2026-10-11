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

class EpisodeRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun exactJobIsRestoredByGetAfterActualForceStop() {
        val args = InstrumentationRegistry.getArguments(); assumeTrue(args.getString("adaEpisodeRecovery") == "true")
        val jobId = UUID.fromString(args.getString("expectedEpisodeJob")); vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null && vm.episodes.state.value.job?.id == jobId && !vm.episodes.state.value.busy }
        val store = AndroidSessionStore(compose.activity.applicationContext); val credential = runBlocking { store.readCredential() }!!
        val conn = ConnectionCredential.parse(credential.identity.server, credential.token, true)!!; val api = HttpAdaApi()
        repeat(30) { if (vm.episodes.state.value.job?.status != "completed") {
            Thread.sleep(250); compose.runOnIdle { vm.episodes.refresh() }; compose.waitUntil(20_000) { !vm.episodes.state.value.busy }
        } }
        val state = vm.episodes.state.value; assertEquals("completed", state.job!!.status); assertEquals(1, state.job.attempt)
        assertEquals(jobId, state.job.receipt!!.job_id); assertEquals(jobId, state.journal!!.jobId)
        assertEquals(state.journal.body, runBlocking { store.consolidationJournal(credential.identity) }!!.body)
        val rows = runBlocking { success(api.episodes(conn, state.job.scope_id)) }; assertEquals(1, rows.size); assertEquals(jobId, rows.single().job_id)
        assertEquals(1, runBlocking { success(api.consolidationJobs(conn, state.job.scope_id)) }.size)
        assertTrue(runBlocking { success(api.claims(conn, state.job.scope_id)) }.isEmpty())
    }
    @After fun cleanup() { if (::vm.isInitialized) compose.runOnIdle { vm.logout() }; runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() } }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
