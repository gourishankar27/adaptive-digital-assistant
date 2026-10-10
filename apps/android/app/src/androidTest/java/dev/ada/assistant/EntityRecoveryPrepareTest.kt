package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.EntityController
import java.io.File
import kotlinx.coroutines.*
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

class EntityRecoveryPrepareTest {
    @Test fun prepareCommittedEntityWithoutDelivery() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue("Run explicit entity recovery stages", InstrumentationRegistry.getArguments().getString("adaEntityRecovery") == "true")
        val context = instrumentation.targetContext; val file = File(context.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val store = AndroidSessionStore(context); store.clear(); val work = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
        var prepared = false; var controller: EntityController? = null
        try {
            val token = file.readText().trim(); val conn = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val actual = HttpAdaApi()
            val identity = SessionIdentity(conn.server.toString(), success(actual.me(conn)).id); val caps = success(actual.capabilities(conn)); val scope = success(actual.createScope(conn, ScopeInputDto("Synthetic entity recovery")))
            store.saveCredential(StoredCredential(identity, token))
            val lost = object : AdaApi by actual { override suspend fun writeEntity(connection: ConnectionCredential, pending: PendingEntity): ApiResult<EntityOperationDto> { check(actual.writeEntity(connection, pending) is ApiResult.Success); return ApiResult.Failure(ApiFailure.Timeout) } }
            val c = EntityController(lost, store, work, { error("Synthetic identity revoked") }); controller = c
            withContext(Dispatchers.Main) { c.setVerifiedSession(conn, identity, caps) }; await { !c.state.value.busy }
            withContext(Dispatchers.Main) { c.activate() }; await { c.state.value.scopes.items.any { it.id == scope.id } }
            withContext(Dispatchers.Main) { c.selectScope(scope.id); c.label("Synthetic recovery 😀 e\u0301"); c.resolve() }; await { !c.state.value.busy && c.state.value.resolution != null }
            withContext(Dispatchers.Main) { c.reviewCreate(); c.confirm() }; await { !c.state.value.busy && c.state.value.fault == ApiFailure.Timeout }
            val pending = checkNotNull(store.entityPending(identity)); assertTrue(success(actual.entityOperation(conn, pending.operationId)).entity != null)
            assertEquals(1, success(actual.entities(conn, scope.id)).size); prepared = true
            instrumentation.sendStatus(0, Bundle().apply { putString("recoveryEntityOperation", pending.operationId.toString()) })
        } finally { withContext(Dispatchers.Main) { controller?.reset() }; work.cancel(); if (!prepared) store.clear() }
    }
    private suspend fun await(check: () -> Boolean) = withTimeout(20_000) { while (!check()) delay(50) }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
