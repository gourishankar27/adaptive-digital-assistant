package dev.ada.assistant

import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.*
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

/** Two native Keystore clients, one real rotation; unknown outcome survives actual force-stop. */
class SharedPasswordSessionHttpTest {
    private val context get()=InstrumentationRegistry.getInstrumentation().targetContext
    private val origin get()=InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
    @Test fun sharedRotationThenUnknownOutcomeIsDurable()=runBlocking {
        assumeTrue(context.packageName.startsWith("dev.ada.validation."))
        val ui=AndroidSessionStore(context); val service=AndroidSessionStore(context)
        ui.clear()
        val http=HttpAdaApi()
        val login=(http.passwordLogin(origin,"synthetic-admin","Public synthetic Android passphrase 123",true) as ApiResult.Success).value
        val access=ConnectionCredential.parse(origin,login.access_token,true)!!
        val user=(http.me(access) as ApiResult.Success).value
        val saved=StoredCredential(SessionIdentity(access.server.toString(),user.id),login.refresh_token,user.data_epoch,true,false,login.session_id)
        ui.saveCredential(saved)
        val first=PasswordRefreshCoordinator.forStore(ui); val second=PasswordRefreshCoordinator.forStore(service)
        assertSame(first,second)
        val count=AtomicInteger()
        val api=object:AdaApi by http {
            override suspend fun refreshLogin(server:String,refresh:String,allowDebugHttp:Boolean):ApiResult<PasswordSessionDto> {
                assertTrue(ui.readCredential()!!.refreshPending)
                count.incrementAndGet(); delay(100)
                return http.refreshLogin(server,refresh,allowDebugHttp)
            }
        }
        val pair=awaitAll(async {first.refresh(api,ui,saved,true)},async {second.refresh(api,service,saved,true)})
        assertTrue(pair.all {it is ApiResult.Success}); assertEquals(1,count.get())
        val next=ui.readCredential()!!
        assertFalse(next.refreshPending); assertNotEquals(saved.token,next.token)
        assertEquals(login.session_id,next.loginSessionId)
        val unknown=object:AdaApi by http {
            override suspend fun refreshLogin(server:String,refresh:String,allowDebugHttp:Boolean):ApiResult<PasswordSessionDto> {
                assertTrue(ui.readCredential()!!.refreshPending)
                assertTrue(http.refreshLogin(server,refresh,allowDebugHttp) is ApiResult.Success)
                return ApiResult.Failure(ApiFailure.Unreachable)
            }
        }
        assertTrue(first.refresh(unknown,ui,next,true,force=true) is ApiResult.Failure)
        assertTrue(service.readCredential()!!.refreshPending)
    }
    @Test fun consumedSecretAfterProcessDeathNeverReturnsToHttp()=runBlocking {
        assumeTrue(context.packageName.startsWith("dev.ada.validation."))
        val store=AndroidSessionStore(context); val saved=store.readCredential()!!
        assertTrue(saved.refreshPending)
        val api=object:AdaApi by HttpAdaApi() {
            override suspend fun refreshLogin(server:String,refresh:String,allowDebugHttp:Boolean):ApiResult<PasswordSessionDto> = error("Consumed refresh reached HTTP")
        }
        assertTrue(PasswordRefreshCoordinator.forStore(store).refresh(api,store,saved,true) is ApiResult.Failure)
        assertTrue(store.readCredential()!!.refreshPending)
        store.clear()
    }
}
