package dev.ada.assistant

import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.ApiFailure
import dev.ada.assistant.data.ApiResult
import dev.ada.assistant.data.ConnectionCredential
import dev.ada.assistant.data.HttpAdaApi
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assume.assumeTrue
import org.junit.Test

class RealHttpIntegrationTest {
    @Test fun emulatorUsesAuthenticatedRealAdaHttpAndRejectsInvalidToken() = runBlocking {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val tokenFile = File(context.filesDir, "foundation-test-token")
        // Optional integration prerequisite is provisioned by scripts/verify-emulator.ps1.
        assumeTrue("Run scripts/verify-emulator.ps1 to provision the disposable HTTP test server", tokenFile.isFile)
        // The helper removes this shared prerequisite after the entire instrumentation run.
        val credential = checkNotNull(ConnectionCredential.parse("http://10.0.2.2:18764", tokenFile.readText().trim(), true))
        val api = HttpAdaApi()
        val me = api.me(credential)
        check(me is ApiResult.Success) { "Authenticated /me did not succeed" }
        assertEquals("Foundation Test", me.value.name)
        val capabilities = api.capabilities(credential)
        check(capabilities is ApiResult.Success) { "Authenticated /capabilities did not succeed" }
        assertEquals("v1", capabilities.value.api_version)
        assertEquals("server", capabilities.value.authority)
        val rejected = checkNotNull(ConnectionCredential.parse("http://10.0.2.2:18764", "invalid-test-only", true))
        assertEquals(ApiFailure.Unauthorized, (api.me(rejected) as ApiResult.Failure).reason)
    }
}
