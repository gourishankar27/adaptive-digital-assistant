package dev.ada.assistant

import android.content.Intent
import android.os.SystemClock
import androidx.core.content.ContextCompat
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.audio.*
import dev.ada.assistant.data.*
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

/** Actual FGS + shared Keystore + HTTP renewal past the original one-minute access expiry. */
class SharedWakeSessionHttpTest {
    @Test fun backgroundWakeRenewsThenRemoteRevocationStopsIt()=runBlocking {
        val context=InstrumentationRegistry.getInstrumentation().targetContext
        assumeTrue(context.packageName.startsWith("dev.ada.validation."))
        val runtime=LocalSpeechFactory.create(context); assumeTrue(runtime.available); runtime.install()
        val origin=InstrumentationRegistry.getArguments().getString("passwordOrigin")!!
        val api=HttpAdaApi(); val store=AndroidSessionStore(context); store.clear()
        val login=(api.passwordLogin(origin,"synthetic-admin","Public synthetic Android passphrase 123",true) as ApiResult.Success).value
        assertTrue("Fixture must use a one-minute access lifetime",login.access_expires_at-System.currentTimeMillis() in 1000..60000)
        val c=ConnectionCredential.parse(origin,login.access_token,true)!!
        val me=(api.me(c) as ApiResult.Success).value; c.dataEpoch=me.data_epoch
        val profile=(api.createPersonality(c,PersonalityInputDto()) as ApiResult.Success).value
        val conversation=(api.createConversation(c,ConversationInputDto(profile.id,"Public shared wake session")) as ApiResult.Success).value
        val identity=SessionIdentity(c.server.toString(),me.id)
        val credential=StoredCredential(identity,login.refresh_token,me.data_epoch,true,false,login.session_id)
        store.saveCredential(credential)
        val shared=PasswordRefreshCoordinator.forStore(store); shared.remember(store,credential,login)
        ActivityScenario.launch(PrivateVoiceReviewActivity::class.java).use {scenario ->
            try {
                scenario.onActivity {
                    WakeAuthority.arm(WakeAuthority.Grant(identity,conversation.id,conversation.scope_id,me.data_epoch,login.access_expires_at,true,login.session_id))
                    ContextCompat.startForegroundService(it,Intent(it,HelloAdaService::class.java))
                }
                val ready=SystemClock.elapsedRealtime()+10000
                while(!HelloAdaService.status.value.startsWith("Armed") && SystemClock.elapsedRealtime()<ready) SystemClock.sleep(100)
                assertTrue(HelloAdaService.status.value.startsWith("Armed"))
                scenario.onActivity {it.startActivity(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME))}
                while(System.currentTimeMillis()<login.access_expires_at+5000) {assertNotNull(WakeAuthority.current()); SystemClock.sleep(500)}
                assertTrue(WakeAuthority.current()!!.expiresAt>login.access_expires_at)
                assertNotEquals(login.refresh_token,store.readCredential()!!.token)
                assertEquals(login.session_id,store.readCredential()!!.loginSessionId)
                val latest=(shared.refresh(api,store,store.readCredential()!!,true) as ApiResult.Success).value
                val access=ConnectionCredential.parse(origin,latest.access_token,true)!!.also {it.dataEpoch=me.data_epoch}
                assertTrue(api.logoutSession(access,false) is ApiResult.Success)
                val until=SystemClock.elapsedRealtime()+40000
                while(WakeAuthority.current()!=null && SystemClock.elapsedRealtime()<until) SystemClock.sleep(200)
                assertNull("Remote family revocation must stop background listening",WakeAuthority.current())
                assertFalse(VoiceAudioCoordinator.busy())
                assertTrue(store.readCredential()!!.refreshPending)
            } finally {
                WakeAuthority.revoke(); context.stopService(Intent(context,HelloAdaService::class.java)); store.clear()
            }
        }
    }
}
