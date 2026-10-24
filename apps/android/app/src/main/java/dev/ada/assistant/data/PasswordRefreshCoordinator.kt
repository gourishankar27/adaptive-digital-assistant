package dev.ada.assistant.data

import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext

fun StoredCredential.sameRefreshCredential(other:StoredCredential) = identity==other.identity && dataEpoch==other.dataEpoch &&
    passwordSession==other.passwordSession && token==other.token && refreshPending==other.refreshPending && loginSessionId==other.loginSessionId

/** One bounded rotation for UI/service. Persist the unknown-outcome marker BEFORE HTTP. */
class PasswordRefreshCoordinator(private val now:()->Long=System::currentTimeMillis) {
    private val rotation=Mutex()
    private var cached:PasswordSessionDto?=null
    private var identity:SessionIdentity?=null
    private var epoch:Long?=null
    private var consumed:String?=null
    private val visibleClients=mutableSetOf<Any>()
    @Synchronized fun foreground(client:Any,visible:Boolean) { if(visible) visibleClients.add(client) else visibleClients.remove(client) }
    @Synchronized private fun uiVisible()=visibleClients.isNotEmpty()
    suspend fun remember(store:SessionStore,expected:StoredCredential,result:PasswordSessionDto) = rotation.withLock {
        if(store.readCredential()?.sameRefreshCredential(expected)==true && expected.token==result.refresh_token && expected.loginSessionId==result.session_id && !expected.refreshPending) {
            if(cached?.refresh_token!=result.refresh_token || identity!=expected.identity || epoch!=expected.dataEpoch) consumed=null
            cached=result; identity=expected.identity; epoch=expected.dataEpoch
        }
    }
    suspend fun logout(api:AdaApi,store:SessionStore,owner:SessionIdentity,family:java.util.UUID?,fallback:ConnectionCredential,all:Boolean,debug:Boolean):ApiResult<AuthAcknowledgementDto> = rotation.withLock {
        withContext(NonCancellable) {
            try {
                val saved=store.readCredential()
                if(saved==null || saved.identity!=owner || saved.dataEpoch!=fallback.dataEpoch || !saved.passwordSession || saved.refreshPending || saved.loginSessionId!=family) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                val known=cached?.takeIf {identity==owner && epoch==saved.dataEpoch && it.session_id==family && it.refresh_token==saved.token && it.access_expires_at>now()}
                val access=known?.let {ConnectionCredential.parse(owner.server,it.access_token,debug)?.also {c -> c.dataEpoch=saved.dataEpoch}} ?: fallback
                // Also fence queued consumers/process death if durable cleanup fails.
                if(!store.replaceCredential(saved,StoredCredential(saved.identity,saved.token,saved.dataEpoch,true,true,saved.loginSessionId))) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                val result=api.logoutSession(access,all)
                cached=null; consumed=null
                result
            } catch (_:Exception) {ApiResult.Failure(ApiFailure.IncompatibleContract)}
        }
    }
    companion object {
        private val processes=mutableMapOf<String,PasswordRefreshCoordinator>()
        @Synchronized fun forStore(store:SessionStore):PasswordRefreshCoordinator = store.coordinationKey?.let { processes.getOrPut(it) { PasswordRefreshCoordinator() } } ?: PasswordRefreshCoordinator()
    }
    suspend fun refresh(api:AdaApi,store:SessionStore,expected:StoredCredential,debug:Boolean,background:Boolean=false,force:Boolean=false):ApiResult<PasswordSessionDto> = rotation.withLock {
        withContext(NonCancellable) {
            try {
                val current=store.readCredential()
                if(current==null || current.identity!=expected.identity || current.dataEpoch!=expected.dataEpoch || !current.passwordSession || !expected.passwordSession) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                if(current.refreshPending) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                val known=cached?.takeIf { identity==current.identity && epoch==current.dataEpoch && current.token==it.refresh_token &&
                    !current.refreshPending && current.loginSessionId==it.session_id &&
                    (expected.loginSessionId==null || expected.loginSessionId==it.session_id) &&
                    it.access_expires_at-now()>(if(background && uiVisible()) 0 else 60000) && (expected.token==it.refresh_token || expected.token==consumed) }
                if(known!=null && (!force || expected.token==consumed)) return@withContext ApiResult.Success(known)
                // The visible UI cancels private work before rotating. A background service
                // must never invalidate the token used by its active controllers/stream.
                if(background && uiVisible()) return@withContext ApiResult.Failure(ApiFailure.Busy(1))
                if(!current.sameRefreshCredential(expected)) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                val pending=StoredCredential(current.identity,current.token,current.dataEpoch,true,true,current.loginSessionId)
                if(!store.replaceCredential(current,pending)) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                val response=api.refreshLogin(current.identity.server,current.token,debug)
                if(response !is ApiResult.Success) { cached=null; return@withContext response }
                val result=response.value
                if(result.refresh_token==current.token || result.access_expires_at<=now() || result.expires_at<result.access_expires_at ||
                    (current.loginSessionId!=null && current.loginSessionId!=result.session_id)) return@withContext ApiResult.Failure(ApiFailure.IncompatibleContract)
                val access=ConnectionCredential.parse(current.identity.server,result.access_token,debug) ?: return@withContext ApiResult.Failure(ApiFailure.IncompatibleContract)
                access.dataEpoch=current.dataEpoch
                val verified=api.me(access)
                if(verified !is ApiResult.Success) return@withContext when(verified) { is ApiResult.Failure -> verified; else -> ApiResult.Failure(ApiFailure.Unauthorized) }
                if(verified.value.id!=current.identity.owner || verified.value.data_epoch!=current.dataEpoch) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                val replacement=StoredCredential(current.identity,result.refresh_token,current.dataEpoch,true,false,result.session_id)
                if(!store.replaceCredential(pending,replacement)) return@withContext ApiResult.Failure(ApiFailure.Unauthorized)
                cached=result; identity=current.identity; epoch=current.dataEpoch; consumed=current.token
                ApiResult.Success(result)
            } catch (_: Exception) { cached=null; ApiResult.Failure(ApiFailure.IncompatibleContract) }
        }
    }
}
