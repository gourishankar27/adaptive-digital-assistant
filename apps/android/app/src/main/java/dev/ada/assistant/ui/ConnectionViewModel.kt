package dev.ada.assistant.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.ada.assistant.data.AdaApi
import dev.ada.assistant.data.ApiFailure
import dev.ada.assistant.data.ApiResult
import dev.ada.assistant.data.ConnectionCredential
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ConnectionViewModel(private val api: AdaApi, private val allowDebugHttp: Boolean) : ViewModel() {
    private val mutableState = MutableStateFlow<ConnectionState>(ConnectionState.Empty)
    val state = mutableState.asStateFlow()
    private var connectJob: Job? = null
    private var generation = 0L

    fun disconnect() {
        generation++
        connectJob?.cancel()
        mutableState.value = ConnectionState.Empty
    }

    fun connect(server: String, token: String) {
        disconnect() // Clear the previous principal immediately, including on malformed switch input.
        val credential = ConnectionCredential.parse(server, token, allowDebugHttp)
        if (credential == null) { mutableState.value = ConnectionState.InvalidInput; return }
        val currentGeneration = generation
        mutableState.value = ConnectionState.Validating
        connectJob = viewModelScope.launch {
            val me = api.me(credential)
            if (currentGeneration != generation) return@launch
            if (me is ApiResult.Failure) { mutableState.value = ConnectionState.Error(me.reason); return@launch }
            val capabilities = api.capabilities(credential)
            if (currentGeneration != generation) return@launch
            if (capabilities is ApiResult.Failure) {
                mutableState.value = ConnectionState.Error(capabilities.reason); return@launch
            }
            val account = (me as ApiResult.Success).value
            val features = (capabilities as ApiResult.Success).value
            mutableState.value = if (features.api_version != "v1" || features.authority != "server") {
                ConnectionState.Error(ApiFailure.IncompatibleContract)
            } else {
                ConnectionState.Connected(AccountSummary(credential.server.toString(), account.id, account.name, features.provider, features.model))
            }
        }
    }
}
