package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import dev.ada.assistant.edge.*
import java.util.UUID
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

private val edgeOwner=SessionIdentity("https://ada.example/",UUID.randomUUID())
private val edgeConnection=ConnectionCredential.parse(edgeOwner.server,"public-synthetic-token",false)!!
private val edgeScope=UUID.randomUUID()
private class EdgeTestStore:SessionStore {
    var journal=EdgeJournal(edgeOwner);var fail=false
    override suspend fun edgeJournal(identity:SessionIdentity)=journal.takeIf{it.identity==identity}
    override suspend fun saveEdgeOperation(identity:SessionIdentity,operation:EdgePending){if(fail)throw SessionStorageException();require(identity==journal.identity);journal=journal.copy(operations=journal.operations+operation)}
    override suspend fun removeEdgeOperation(identity:SessionIdentity,operationId:UUID){journal=journal.copy(operations=journal.operations.filter{it.operationId!=operationId})}
    override suspend fun readCredential():StoredCredential?=null
    override suspend fun saveCredential(credential:StoredCredential)=Unit
    override suspend fun clear()=Unit
    override suspend fun pending(identity:SessionIdentity):PendingMessage?=null
    override suspend fun savePending(message:PendingMessage)=error("Must never create chat")
    override suspend fun removePending(identity:SessionIdentity,requestId:UUID)=Unit
}
private fun noEdgeApi()=java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader,arrayOf(AdaApi::class.java)){_,method,_->error("Unexpected ${method.name}")} as AdaApi
private class EdgeTestApi(val disk:EdgeTestStore):AdaApi by noEdgeApi() {
    var writes=0;var reads=0;var respond=false;var changed=false;var rows=emptyList<EdgeDeviceDto>()
    override suspend fun scopes(connection:ConnectionCredential,limit:Int,offset:Int)=ApiResult.Success(listOf(ScopeDto(edgeScope,"Public scope","project",1000)))
    override suspend fun edgeDevices(connection:ConnectionCredential):ApiResult<List<EdgeDeviceDto>>{reads++;return ApiResult.Success(rows)}
    override suspend fun edgeDeviceWrite(connection:ConnectionCredential,op:EdgePending):ApiResult<EdgeDeviceDto>{
        val operation=op
        require(operation in disk.journal.operations);writes++
        if(!respond)return ApiResult.Failure(ApiFailure.Timeout)
        val b=adaJson.decodeFromString<EdgeEnrollDto>(operation.body)
        return ApiResult.Success(EdgeDeviceDto(id=operation.deviceId,revision=1,last_sequence=0,label=if(changed) "Wrong" else b.label,public_key=b.public_key,created_at=1000,enrollment_id=b.operation_id))
    }
}
private class EdgeTestPlatform:DraftPlatform {
    var calls=0
    var brokenKey=false
    override val supported=true
    override fun modelPresent()=true
    override suspend fun generate(text:String):NativeDraft {calls++;return NativeDraft("Public draft",false,100,100)}
    override fun publicKey(who:SessionIdentity,create:Boolean):String {if(brokenKey)error("Public key fixture failure");return "A".repeat(100)}
    override fun sign(who:SessionIdentity,message:ByteArray)="A".repeat(100)
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class EdgeControllerTest {
    private fun caps()=adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(device_draft_sync=EDGE_PROTOCOL)
    @Test fun unavailableSigningKeyCreatesNoPostOrRecoveryReservation()=runTest {
        val store=EdgeTestStore();val api=EdgeTestApi(store);val platform=EdgeTestPlatform();platform.brokenKey=true
        val c=EdgeController(api,store,this,platform){}
        c.setVerifiedSession(edgeConnection,edgeOwner,caps());c.observeVisible(true);runCurrent();c.enroll();runCurrent()
        assertEquals(0,api.writes);assertTrue(store.journal.operations.isEmpty());assertFalse(c.isRegistered());assertTrue(c.state.value.notice!!.contains("key is unavailable"));c.reset()
    }
    @Test fun failedEncryptionPreventsPostAndRestartReadsOnlyBeforeExactRetry()=runTest {
        val store=EdgeTestStore();val api=EdgeTestApi(store);val p=EdgeTestPlatform();val c=EdgeController(api,store,this,p){}
        c.setVerifiedSession(edgeConnection,edgeOwner,caps());c.observeVisible(true);runCurrent()
        store.fail=true;c.enroll();runCurrent();assertEquals(0,api.writes);assertTrue(store.journal.operations.isEmpty())
        store.fail=false;c.enroll();runCurrent();assertEquals(1,api.writes);val original=store.journal.operations.single()
        c.setVerifiedSession(edgeConnection,edgeOwner,caps());runCurrent();assertEquals(1,api.writes);assertEquals(original,c.state.value.pending.single())
        api.respond=true;api.changed=true;c.retry(original);runCurrent();assertEquals(original,store.journal.operations.single())
        api.changed=false;c.retry(original);runCurrent();assertTrue(store.journal.operations.isEmpty());assertEquals(3,api.writes)
        c.reset()
    }
    @Test fun failedQualityGateCannotBeEnabledEvenOnSupportedHardware()=runTest {
        val store=EdgeTestStore();val api=EdgeTestApi(store);val p=EdgeTestPlatform()
        api.rows=listOf(EdgeDeviceDto(id=UUID.randomUUID(),revision=1,last_sequence=0,label="Public installation",public_key=p.publicKey(edgeOwner),created_at=1000))
        val c=EdgeController(api,store,this,p){}
        c.setVerifiedSession(edgeConnection,edgeOwner,caps());c.observeVisible(true);runCurrent();c.selectScope(edgeScope)
        c.prompt("Public reply request");c.enableLocal(true);c.generate();runCurrent()
        assertFalse(c.state.value.localEnabled);assertEquals(0,p.calls);assertNull(c.state.value.draft);assertEquals(0,api.writes)
        c.reset();assertTrue(c.state.value.devices.isEmpty());assertEquals("",c.state.value.prompt)
    }
}
