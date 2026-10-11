package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.EpisodeController
import java.io.File
import java.util.UUID
import kotlinx.coroutines.*
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

class EpisodeRecoveryPrepareTest {
    @Test fun prepareCommittedQueueWithoutDelivery() = runBlocking {
        assumeTrue(InstrumentationRegistry.getArguments().getString("adaEpisodeRecovery") == "true")
        val instrumentation = InstrumentationRegistry.getInstrumentation(); val context = instrumentation.targetContext
        val file = File(context.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val store = AndroidSessionStore(context); store.clear(); val work = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
        var prepared = false; var controller: EpisodeController? = null
        try {
            val token = file.readText().trim(); val conn = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val api = HttpAdaApi()
            val identity = SessionIdentity(conn.server.toString(), success(api.me(conn)).id); val caps = success(api.capabilities(conn))
            val profile = success(api.personalities(conn)).first(); val conversation = success(api.createConversation(conn, ConversationInputDto(profile.id, "Synthetic episode recovery")))
            success(api.send(conn, conversation.id, ChatInputDto(UUID.randomUUID(), "Synthetic restart continuity 😀.", use_memory = false)))
            store.saveCredential(StoredCredential(identity, token))
            val lost = object : AdaApi by api { override suspend fun createConsolidationJob(connection: ConnectionCredential, journal: ConsolidationJournal): ApiResult<ConsolidationJobDto> {
                assertNotNull(store.consolidationJournal(identity)); check(api.createConsolidationJob(connection, journal) is ApiResult.Success)
                return ApiResult.Failure(ApiFailure.Timeout)
            } }
            val c = EpisodeController(lost, store, work, { error("Synthetic identity revoked") }); controller = c
            withContext(Dispatchers.Main) { c.setVerifiedSession(conn, identity, caps) }
            await { !c.state.value.busy }
            withContext(Dispatchers.Main) { c.activate(conversation) }
            await { c.state.value.events.size == 2 && !c.state.value.busy }
            withContext(Dispatchers.Main) { c.toggle(c.state.value.events.first { it.role == "user" }.id); c.preview("episode") }
            await { c.state.value.preview != null && !c.state.value.busy }
            withContext(Dispatchers.Main) { c.queue() }; await { !c.state.value.busy && c.state.value.fault == ApiFailure.Timeout }
            val saved = checkNotNull(store.consolidationJournal(identity)); assertEquals(saved.jobId, success(api.consolidationJob(conn, saved.jobId)).id)
            prepared = true; instrumentation.sendStatus(0, Bundle().apply { putString("recoveryEpisodeJob", saved.jobId.toString()) })
        } finally { withContext(Dispatchers.Main) { controller?.reset() }; work.cancel(); if (!prepared) store.clear() }
    }
    private suspend fun await(check: () -> Boolean) = withTimeout(20_000) { while (!check()) delay(50) }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
