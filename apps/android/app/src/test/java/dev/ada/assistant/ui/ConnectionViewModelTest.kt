package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/** Test-only injected mock; unconfigured API calls fail instead of reaching a server. */
private class MockAdaApi : AdaApi by unsupportedApi() {
    var meResponse: suspend () -> ApiResult<MeDto> = { ApiResult.Success(MeDto(UUID.fromString("00000000-0000-4000-8000-000000000001"), "Test")) }
    var capabilitiesResponse: suspend () -> ApiResult<CapabilitiesDto> = { ApiResult.Success(adaJson.decodeFromString(fixture("capabilities-current.json"))) }
    override suspend fun me(connection: ConnectionCredential) = meResponse()
    override suspend fun capabilities(connection: ConnectionCredential) = capabilitiesResponse()
}
private fun unsupportedApi(): AdaApi = java.lang.reflect.Proxy.newProxyInstance(
    AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java),
) { _, method, _ -> error("Unexpected test API call: ${method.name}") } as AdaApi

@OptIn(ExperimentalCoroutinesApi::class)
class ConnectionViewModelTest {
    @Before fun setup() { Dispatchers.setMain(StandardTestDispatcher()) }
    @After fun cleanup() { Dispatchers.resetMain() }

    @Test fun successfulConnectionChecksOwnerAndCapabilities() = runTest {
        val vm = ConnectionViewModel(MockAdaApi(), true)
        vm.connect("http://localhost:8000", "test-only")
        assertEquals(ConnectionState.Validating, vm.state.value)
        advanceUntilIdle()
        assertEquals("Test", (vm.state.value as ConnectionState.Connected).account.name)
        vm.disconnect()
        assertEquals(ConnectionState.Empty, vm.state.value)
    }
    @Test fun revokedTokenClearsPrivatePrincipalAndNeverReturnsFakeSuccess() = runTest {
        val api = MockAdaApi()
        val vm = ConnectionViewModel(api, true)
        vm.connect("http://localhost:8000", "test-only"); advanceUntilIdle()
        api.meResponse = { ApiResult.Failure(ApiFailure.Unauthorized) }
        vm.connect("http://localhost:8000", "revoked-test")
        assertEquals(ConnectionState.Validating, vm.state.value)
        advanceUntilIdle()
        assertEquals(ConnectionState.Error(ApiFailure.Unauthorized), vm.state.value)
    }
    @Test fun changingServerCancelsOldConnectionAndRejectsMalformedInput() = runTest {
        val gate = CompletableDeferred<ApiResult<MeDto>>()
        val api = MockAdaApi()
        api.meResponse = { gate.await() }
        val vm = ConnectionViewModel(api, true)
        vm.connect("http://localhost:8000", "test-only"); runCurrent()
        vm.connect("http://external.example", "test-only")
        gate.complete(ApiResult.Success(MeDto(UUID.randomUUID(), "Old account")))
        advanceUntilIdle()
        assertEquals(ConnectionState.InvalidInput, vm.state.value)
    }
    @Test fun incompatibleApiNeverEnablesLaterFeatures() = runTest {
        val api = MockAdaApi()
        api.capabilitiesResponse = { ApiResult.Success(adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(api_version = "v99")) }
        val vm = ConnectionViewModel(api, true)
        vm.connect("http://localhost:8000", "test-only"); advanceUntilIdle()
        assertEquals(ConnectionState.Error(ApiFailure.IncompatibleContract), vm.state.value)
    }
}
