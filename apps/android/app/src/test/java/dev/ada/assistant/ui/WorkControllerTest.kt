package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.test.*
import kotlinx.coroutines.withContext
import org.junit.Assert.*
import org.junit.Test

private val workOwner = SessionIdentity("https://work.example/",UUID.randomUUID())
private val workCredential = ConnectionCredential.parse(workOwner.server,"synthetic-work-fixture",false)!!
private val workScopeId = UUID.randomUUID()
private class WorkTestStore : SessionStore {
    val rows=mutableListOf<WorkPending>(); var fail=false
    override suspend fun workJournal(identity: SessionIdentity)=WorkJournal(identity,rows.toList())
    override suspend fun saveWorkOperation(identity: SessionIdentity, operation: WorkPending) { if(fail) throw SessionStorageException(); rows+=operation }
    override suspend fun removeWorkOperation(identity: SessionIdentity, operationId: UUID) { rows.removeAll { it.operationId==operationId } }
    override suspend fun readCredential(): StoredCredential?=null
    override suspend fun saveCredential(credential: StoredCredential) = Unit
    override suspend fun clear()=Unit
    override suspend fun pending(identity: SessionIdentity): PendingMessage?=null
    override suspend fun savePending(message: PendingMessage)=error("Must not send chat")
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID)=Unit
}
private fun noWorkApi() = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader,arrayOf(AdaApi::class.java)) { _,method,_ -> error("Unexpected ${method.name}") } as AdaApi
private class WorkTestApi(private val store: WorkTestStore) : AdaApi by noWorkApi() {
    var writes=0; var reads=0; var unknown=true; var returnedRevision=1
    var receiptResult: WorkReceiptDto?=null
    var gate: CompletableDeferred<ApiResult<WorkPreviewDto>>?=null
    var briefGate: CompletableDeferred<ApiResult<WorkBriefDto>>?=null
    override suspend fun scopes(connection: ConnectionCredential,limit:Int,offset:Int)=ApiResult.Success(listOf(ScopeDto(workScopeId,"Public work scope","project",1000)))
    override suspend fun workItems(connection: ConnectionCredential,scope:UUID,offset:Int)=ApiResult.Success(emptyList<WorkItemDto>())
    override suspend fun curiosityPolicy(connection: ConnectionCredential):ApiResult<CuriosityPolicyDto> = ApiResult.Failure(ApiFailure.IncompatibleContract)
    override suspend fun schedulePolicy(connection: ConnectionCredential):ApiResult<SchedulePolicyDto> = ApiResult.Failure(ApiFailure.IncompatibleContract)
    override suspend fun workPreview(connection: ConnectionCredential,scope:UUID,item:UUID,body:WorkWriteDto):ApiResult<WorkPreviewDto> = gate?.let { withContext(NonCancellable) { it.await() } } ?: ApiResult.Success(WorkPreviewDto(WORK_PROTOCOL,"a".repeat(64),sources=emptyList(),provenance="owner_created",reminder="not_scheduled"))
    override suspend fun workReceipt(connection: ConnectionCredential,operation:UUID):ApiResult<WorkReceiptDto> { reads++; return receiptResult?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound) }
    override suspend fun workWrite(connection: ConnectionCredential,operation:WorkPending):ApiResult<WorkReceiptDto> {
        require(operation in store.rows); writes++
        if(unknown) return ApiResult.Failure(ApiFailure.Timeout)
        return ApiResult.Success(WorkReceiptDto(WORK_PROTOCOL,operation.operationId,"save","completed",item_id=operation.itemId,revision=returnedRevision,created_at=1000))
    }
    override suspend fun workCreateBrief(connection: ConnectionCredential,operation:WorkPending):ApiResult<WorkBriefDto> {
        require(operation in store.rows);writes++
        return withContext(NonCancellable) { briefGate!!.await() }
    }
}
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class WorkControllerTest {
    @Test fun reminderRecoveryChecksExactDefinitionButAcceptsEquivalentExpiryInstants()=runTest {
        val(c,api,store)=ready();val key=UUID.randomUUID();val operation=UUID.randomUUID()
        val definition=ScheduleDefinitionDto(text="Public reminder",timezone="UTC",start_local="2026-11-01T10:00",expires_at="2026-11-02T10:00:00Z")
        val op=WorkPending(operation,"reminder_preview",adaJson.encodeToString(WorkReminderPreviewDto(operation,1,definition)),workScopeId,key)
        store.rows+=op
        val preview=ScheduleReceiptDto("ada-scheduling-v1",operation,"preview","completed",definition=definition.copy(expires_at="2026-11-02T10:00:00+00:00"),occurrences=listOf(SchedulePlanDto(1000,"2026-11-01T10:00")),timezone_data="synthetic",preview_expires_at=2000,created_at=1000)
        api.receiptResult=WorkReceiptDto(WORK_PROTOCOL,operation,"reminder_preview","completed",item_id=key,revision=1,schedule_preview=preview.copy(definition=definition.copy(text="Changed public text")),created_at=1000)
        val caps=adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(work_protocol=WORK_PROTOCOL)
        c.setVerifiedSession(workCredential,workOwner,caps);c.observeVisible(true);c.refresh();runCurrent();c.selectScope(workScopeId);runCurrent();c.check(op);runCurrent()
        assertNull(c.state.value.reminder);assertEquals(op,store.rows.single())
        api.receiptResult=api.receiptResult!!.copy(schedule_preview=preview);c.check(op);runCurrent()
        assertEquals(operation,c.state.value.reminder!!.operation_id);assertEquals(0,api.writes);assertEquals(op,store.rows.single());c.reset()
    }
    @Test fun mismatchedReceiptCannotClearTheExactRecoveryRecord()=runTest {
        val(c,api,store)=ready();api.unknown=false;api.returnedRevision=8
        c.begin();c.fields(c.state.value.draft!!.body.fields.copy(description="Public receipt mismatch"));c.prepare();runCurrent();c.save();runCurrent()
        assertEquals(1,api.writes);assertEquals(1,store.rows.size);assertNotNull(c.state.value.draft)
        assertTrue(c.state.value.notice!!.contains("unconfirmed"));c.reset()
    }
    private data class Rig(val controller:WorkController,val api:WorkTestApi,val store:WorkTestStore)
    private fun TestScope.ready():Rig {
        val store=WorkTestStore();val api=WorkTestApi(store);val c=WorkController(api,store,this,{})
        val caps=adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(work_protocol=WORK_PROTOCOL)
        c.setVerifiedSession(workCredential,workOwner,caps);c.observeVisible(true);runCurrent();c.selectScope(workScopeId);runCurrent();return Rig(c,api,store)
    }
    @Test fun saveIsEncryptedFirstAndUnknownRecoveryOnlyReadsUntilExplicitRetry()=runTest {
        val(c,api,store)=ready();c.begin();c.fields(c.state.value.draft!!.body.fields.copy(description="Public selected action"));c.prepare();runCurrent();c.save();runCurrent()
        assertEquals(1,api.writes);assertEquals(1,store.rows.size)
        val original=store.rows.single();val caps=adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")).copy(work_protocol=WORK_PROTOCOL)
        c.setVerifiedSession(workCredential,workOwner,caps);runCurrent();assertEquals(1,api.writes);assertEquals(original,store.rows.single());assertTrue(api.reads>0)
        c.observeVisible(true);runCurrent();api.unknown=false;c.retry(original);runCurrent();assertEquals(2,api.writes);assertTrue(store.rows.isEmpty());c.reset()
    }
    @Test fun failedStorageNeverPostsAndLatePreviewCannotCrossOwnerOrSelection()=runTest {
        val(c,api,store)=ready();c.begin();c.fields(c.state.value.draft!!.body.fields.copy(description="Public selected action"));c.prepare();runCurrent();store.fail=true;c.save();runCurrent();assertEquals(0,api.writes)
        store.fail=false;api.gate=CompletableDeferred();c.prepare();runCurrent();c.reset();api.gate!!.complete(ApiResult.Success(WorkPreviewDto(WORK_PROTOCOL,"a".repeat(64),sources=emptyList(),provenance="owner_created",reminder="not_scheduled")));runCurrent();assertNull(c.state.value.preview);assertNull(c.state.value.draft)
    }
    @Test fun editingInvalidatesPreviewAndBackgroundDoesNotSubmitOrDisplayLateResult()=runTest {
        val(c,api,_)=ready();c.begin();c.fields(c.state.value.draft!!.body.fields.copy(description="First public action"));c.prepare();runCurrent();assertNotNull(c.state.value.preview)
        c.fields(c.state.value.draft!!.body.fields.copy(description="Changed public action"));assertNull(c.state.value.preview);c.save();runCurrent();assertEquals(0,api.writes)
        api.gate=CompletableDeferred();c.prepare();runCurrent();c.observeForeground(false);api.gate!!.complete(ApiResult.Success(WorkPreviewDto(WORK_PROTOCOL,"a".repeat(64),sources=emptyList(),provenance="owner_created",reminder="not_scheduled")));runCurrent();assertNull(c.state.value.preview);c.reset()
    }
    @Test fun lateBriefIsNotDisplayedAndKeepsRecoveryWhenHiddenOrSelectionChanges()=runTest {
        for (hidden in listOf(true,false)) {
            val(c,api,store)=ready()
            val row=WorkItemDto(WORK_PROTOCOL,UUID.randomUUID(),workScopeId,1,WorkFieldsDto("task","Public late brief task"),overdue=false,provenance="owner_created",sources=emptyList(),created_at=1000,updated_at=1000)
            c.selectForBrief(row,true);api.briefGate=CompletableDeferred();c.brief("2026-10-22","UTC");runCurrent()
            val op=store.rows.single()
            if(hidden) c.observeForeground(false) else c.selectForBrief(row,false)
            val result=WorkBriefDto(WORK_PROTOCOL,op.operationId,listOf(workScopeId),"2026-10-22","UTC",listOf(WorkBriefItemDto("T1",row,false,false,listOf("created"))),0,"deterministic_task_projection",false,1000)
            api.briefGate!!.complete(ApiResult.Success(result));runCurrent()
            assertNull(c.state.value.brief);assertEquals(op,store.rows.single());c.reset()
        }
    }
}
