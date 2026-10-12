package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

class ExpressionRecoveryPrepareTest {
    @Test fun prepareCommittedPreferenceWithoutDelivery() = runBlocking {
        assumeTrue(InstrumentationRegistry.getArguments().getString("adaExpressionRecovery") == "true")
        val i = InstrumentationRegistry.getInstrumentation(); val ctx = i.targetContext
        val file = File(ctx.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val store = AndroidSessionStore(ctx); store.clear()
        val token = file.readText().trim(); val c = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val api = HttpAdaApi()
        val identity = SessionIdentity(c.server.toString(), success(api.me(c)).id)
        store.saveCredential(StoredCredential(identity, token))
        val prior = success(api.preference(c, "account", identity.owner)); val key = UUID.randomUUID()
        val journal = ExpressionJournal(identity, key, "preferences", "account", identity.owner,
            adaJson.encodeToString(PreferenceWriteDto(key, prior.revision, PreferenceValuesDto(verbosity = "detailed", cadence = "stepwise"))))
        store.saveExpressionJournal(journal)
        val receipt = success(api.expressionOperation(c, journal))
        assertEquals(key, receipt.operation_id); assertEquals(journal, store.expressionJournal(identity))
        i.sendStatus(0, Bundle().apply { putString("recoveryExpressionKey", key.toString()) })
    }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
