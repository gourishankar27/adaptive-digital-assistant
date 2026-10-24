package dev.ada.assistant.data

import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.async
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

private class RefreshStore : SessionStore {
    var saved:StoredCredential?=null; var fail=false
    override suspend fun readCredential()=saved
    override suspend fun saveCredential(credential:StoredCredential) { if(fail) throw SessionStorageException(); saved=credential }
    override suspend fun replaceCredential(expected:StoredCredential,replacement:StoredCredential):Boolean {
        if(fail) throw SessionStorageException()
        if(saved?.sameRefreshCredential(expected)!=true) return false
        saved=replacement; return true
    }
    override suspend fun clear() { saved=null }
    override suspend fun pending(identity:SessionIdentity):PendingMessage?=null
    override suspend fun savePending(message:PendingMessage)=Unit
    override suspend fun removePending(identity:SessionIdentity,requestId:UUID)=Unit
}
private fun unexpectedRefreshApi()=java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader,arrayOf(AdaApi::class.java)) { _,method,_ -> error("Unexpected ${method.name}") } as AdaApi
private class RefreshApi(private val owner:UUID) : AdaApi by unexpectedRefreshApi() {
    var calls=0; var gate:CompletableDeferred<Unit>?=null; var unknown=false; var beforeReturn:(()->Unit)?=null
    val result=PasswordSessionDto("public-access-new","public-refresh-new",UUID.randomUUID(),1000000,2000000)
    override suspend fun refreshLogin(server:String,refresh:String,allowDebugHttp:Boolean):ApiResult<PasswordSessionDto> {
        calls++; gate?.await(); beforeReturn?.invoke()
        return if(unknown) ApiResult.Failure(ApiFailure.Unreachable) else ApiResult.Success(result)
    }
    override suspend fun me(connection:ConnectionCredential)=ApiResult.Success(MeDto(owner,"Public fixture",0))
    var logoutAccess:String?=null
    override suspend fun logoutSession(connection:ConnectionCredential,all:Boolean):ApiResult<AuthAcknowledgementDto> {logoutAccess=connection.token; return ApiResult.Success(AuthAcknowledgementDto("signed_out"))}
}

@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class PasswordRefreshCoordinatorTest {
    private fun credential()=StoredCredential(SessionIdentity("https://ada.test/",UUID.randomUUID()),"public-refresh-old",passwordSession=true)
    @Test fun simultaneousUiAndServiceUseOneRotationAndPersistBeforeReturning()=runTest {
        val old=credential(); val store=RefreshStore().apply { saved=old }; val api=RefreshApi(old.identity.owner)
        api.gate=CompletableDeferred(); val coordinator=PasswordRefreshCoordinator { 100L }
        val ui=async { coordinator.refresh(api,store,old,false) }; runCurrent()
        assertTrue(store.saved!!.refreshPending); assertEquals(1,api.calls)
        val background=async { coordinator.refresh(api,store,old,false) }; runCurrent()
        assertEquals(1,api.calls); api.gate!!.complete(Unit)
        assertTrue(ui.await() is ApiResult.Success); assertTrue(background.await() is ApiResult.Success)
        assertEquals(1,api.calls); assertFalse(store.saved!!.refreshPending)
        assertEquals(api.result.refresh_token,store.saved!!.token)
        assertEquals(api.result.session_id,store.saved!!.loginSessionId)
    }
    @Test fun unknownRotationAndProcessRestartNeverReuseTheConsumedSecret()=runTest {
        val old=credential(); val store=RefreshStore().apply { saved=old }; val api=RefreshApi(old.identity.owner).apply { unknown=true }
        assertTrue(PasswordRefreshCoordinator {100L}.refresh(api,store,old,false) is ApiResult.Failure)
        assertTrue(store.saved!!.refreshPending)
        assertTrue(PasswordRefreshCoordinator {100L}.refresh(api,store,store.saved!!,false) is ApiResult.Failure)
        assertEquals(1,api.calls)
    }
    @Test fun storageFailureBlocksHttpAndLateRotationCannotOverwriteAnotherOwner()=runTest {
        val old=credential(); val store=RefreshStore().apply { saved=old; fail=true }; val api=RefreshApi(old.identity.owner)
        assertTrue(PasswordRefreshCoordinator {100L}.refresh(api,store,old,false) is ApiResult.Failure)
        assertEquals(0,api.calls)
        store.fail=false; val other=credential()
        api.beforeReturn={store.saved=other}
        assertTrue(PasswordRefreshCoordinator {100L}.refresh(api,store,old,false) is ApiResult.Failure)
        assertSame(other,store.saved)
    }
    @Test fun visibleUiOwnsRotationAndBackgroundUsesOnlyItsVerifiedAccess()=runTest {
        val old=credential(); val store=RefreshStore().apply { saved=old }; val api=RefreshApi(old.identity.owner)
        var time=100L
        val coordinator=PasswordRefreshCoordinator {time}; val ui=Any()
        coordinator.foreground(ui,true)
        assertTrue(coordinator.refresh(api,store,old,false,background=true) is ApiResult.Failure)
        assertEquals(0,api.calls)
        assertTrue(coordinator.refresh(api,store,old,false) is ApiResult.Success)
        time=api.result.access_expires_at-30000
        val saved=store.saved!!
        assertTrue(coordinator.refresh(api,store,saved,false,background=true) is ApiResult.Success)
        assertEquals(1,api.calls)
        coordinator.foreground(ui,false)
        api.unknown=true
        assertTrue(coordinator.refresh(api,store,saved,false,background=true) is ApiResult.Failure)
        assertEquals(2,api.calls)
        assertTrue(store.saved!!.refreshPending)
        coordinator.foreground(ui,true)
        assertEquals(ApiFailure.Unauthorized,(coordinator.refresh(api,store,store.saved!!,false,background=true) as ApiResult.Failure).reason)
    }
    @Test fun revokedOrDifferentFamilyCannotReuseCachedAccess()=runTest {
        val old=credential(); val store=RefreshStore().apply { saved=old }; val api=RefreshApi(old.identity.owner)
        val coordinator=PasswordRefreshCoordinator {100L}
        assertTrue(coordinator.refresh(api,store,old,false) is ApiResult.Success)
        val changed=StoredCredential(old.identity,api.result.refresh_token,0,true,false,UUID.randomUUID())
        store.saved=changed
        assertTrue(coordinator.refresh(api,store,store.saved!!,false) is ApiResult.Failure)
        assertTrue(store.saved!!.refreshPending)
        store.saved=null
        assertTrue(coordinator.refresh(api,store,changed,false) is ApiResult.Failure)
    }
    @Test fun logoutJoinsRotationAndFencesQueuedConsumersBeforeCleanup()=runTest {
        val base=credential(); val api=RefreshApi(base.identity.owner).apply {gate=CompletableDeferred()}
        val old=StoredCredential(base.identity,base.token,0,true,false,api.result.session_id)
        val store=RefreshStore().apply {saved=old}; val coordinator=PasswordRefreshCoordinator {100L}
        val fallback=ConnectionCredential.parse(old.identity.server,"public-old-access",false)!!.also {it.dataEpoch=0}
        val rotation=async {coordinator.refresh(api,store,old,false)}; runCurrent()
        val logout=async {coordinator.logout(api,store,old.identity,old.loginSessionId,fallback,false,false)}; runCurrent()
        assertNull(api.logoutAccess); api.gate!!.complete(Unit)
        assertTrue(rotation.await() is ApiResult.Success); assertTrue(logout.await() is ApiResult.Success)
        assertEquals(api.result.access_token,api.logoutAccess); assertTrue(store.saved!!.refreshPending)
        assertTrue(coordinator.refresh(api,store,store.saved!!,false) is ApiResult.Failure)
        assertEquals(1,api.calls)
    }
}
