package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import dev.ada.assistant.edge.*
import java.io.InputStream
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

data class EdgeState(val supported:Boolean=false,val busy:Boolean=false,val localEnabled:Boolean=false,
    val scopes:List<ScopeDto> = emptyList(),val scope:UUID?=null,val devices:List<EdgeDeviceDto> = emptyList(),
    val prompt:String="",val draft:EdgeLocalDraft?=null,val pending:List<EdgePending> = emptyList(),
    val receipt:EdgeProposalDto?=null,val notice:String?=null,val nativeSupported:Boolean=false,val modelPresent:Boolean=false) { override fun toString()="EdgeState(redacted)" }

/** Local drafts never become messages, facts, tools or server answers. Recovery performs GET only. */
class EdgeController(private val api:AdaApi,private val store:SessionStore,private val scope:CoroutineScope,
    val platform:DraftPlatform?,private val unauthorized:()->Unit) {
    private val mutable=MutableStateFlow(EdgeState());val state=mutable.asStateFlow()
    private var credential:ConnectionCredential?=null;private var owner:SessionIdentity?=null
    private var epoch=0L;private var selection=0L;private var visible=false;private var foreground=true
    private var cooldown=0L;private val jobs=mutableSetOf<Job>();private var nativeJob:Job?=null
    private fun update(f:(EdgeState)->EdgeState){mutable.value=f(state.value)}
    private fun current(e:Long)=e==epoch && owner!=null
    private fun live(e:Long,q:Long)=current(e) && selection==q && visible && foreground
    fun reset(){epoch++;selection++;jobs.toList().forEach{it.cancel()};jobs.clear();credential=null;owner=null;nativeJob=null;cooldown=0;mutable.value=EdgeState()}
    fun observeVisible(active:Boolean){if(visible==active)return;visible=active;selection++;if(!active){nativeJob?.cancel();update{it.copy(busy=false,localEnabled=false)}}else refresh()}
    fun observeForeground(active:Boolean){foreground=active;selection++;if(!active){nativeJob?.cancel();update{it.copy(busy=false,localEnabled=false)}}else if(visible)refresh()}
    private fun launch(block:suspend(ConnectionCredential,SessionIdentity,Long)->Unit):Job? {
        val c=credential?:return null;val who=owner?:return null;val e=epoch
        return scope.launch(start=CoroutineStart.UNDISPATCHED) {
            try{if(current(e))block(c,who,e)}
            catch(cancel:CancellationException){throw cancel}
            catch(_:Exception){if(current(e))update{it.copy(busy=false,notice="Result unconfirmed. Keep the original recovery record and check before retrying.")}}
        }.also{job->jobs+=job;job.invokeOnCompletion{jobs-=job}}
    }
    private fun <T> accept(r:ApiResult<T>,e:Long):T? {
        if(!current(e))return null
        if(r is ApiResult.Success)return r.value
        val failure=(r as ApiResult.Failure).reason
        if(failure==ApiFailure.Unauthorized){reset();unauthorized();return null}
        if(failure is ApiFailure.Busy)cooldown=System.currentTimeMillis()+(failure.retryAfterSeconds?:3).coerceIn(1,300)*1000L
        if(failure is ApiFailure.Http && failure.status==429)cooldown=System.currentTimeMillis()+60000
        update{it.copy(busy=false,notice=when(failure){ApiFailure.Conflict->"The device sequence, source or original input changed. Check the saved result; do not replace a pending operation."
            ApiFailure.Http(410)->"The device, privacy epoch or input is no longer valid. A stale draft cannot authorize anything."
            else->"Device drafts are unavailable or this result is unconfirmed. Your local draft remains separate from chat."})};return null
    }
    fun setVerifiedSession(c:ConnectionCredential,who:SessionIdentity,caps:CapabilitiesDto){
        reset();credential=c;owner=who;update{it.copy(supported=caps.device_draft_sync==EDGE_PROTOCOL,nativeSupported=platform?.supported==true,modelPresent=platform?.modelPresent()==true)}
        launch{conn,identity,e->
            val journal=store.edgeJournal(identity);if(!current(e))return@launch
            update{it.copy(draft=journal?.draft,prompt=journal?.draft?.prompt.orEmpty(),scope=journal?.draft?.scopeId,pending=journal?.operations.orEmpty())}
            journal?.operations?.forEach{check(conn,identity,it,e)}
            journal?.lastProposal?.let { id -> val result=api.edgeProposal(conn,id);if(result is ApiResult.Success && current(e) && visible && foreground && result.value.scope_id==state.value.scope){validate(result.value);update{it.copy(receipt=result.value)}} }
        }
    }
    fun refresh(){if(!visible || !foreground || !state.value.supported)return
        val q=selection
        launch{c,_,e->
            val scopes=accept(api.scopes(c,100,0),e)?:return@launch;if(!live(e,q))return@launch
            val devices=accept(api.edgeDevices(c),e)?:return@launch;if(!live(e,q))return@launch
            require(scopes.size<=100 && devices.size<=5 && devices.all{it.version==EDGE_PROTOCOL && it.revision>0})
            update{it.copy(scopes=scopes,devices=devices,modelPresent=platform?.modelPresent()==true,busy=false)}
        }
    }
    fun selectScope(id:UUID){if(state.value.scopes.none{it.id==id})return;nativeJob?.cancel();selection++;update{it.copy(scope=id,receipt=null,busy=false)}}
    fun prompt(value:String){if(state.value.busy)return;selection++;update{it.copy(prompt=value,draft=null,receipt=null)}}
    fun enableLocal(enabled:Boolean){if(state.value.busy)return;update{it.copy(localEnabled=enabled && EDGE_QUALITY_APPROVED)}}
    private fun device():EdgeDeviceDto? = runCatching { val who=owner?:return null;val key=platform?.publicKey(who)?:return null;state.value.devices.singleOrNull{it.public_key==key && it.revoked_at==null} }.getOrNull()
    fun isRegistered()=device()!=null
    fun generate(){val selected=state.value.scope?:return;val prompt=state.value.prompt
        if(!EDGE_QUALITY_APPROVED || !visible || !foreground || state.value.busy || !state.value.localEnabled || device()==null || platform?.supported!=true || !platform.modelPresent())return
        require(prompt.toByteArray().size in 1..1500)
        val q=++selection;update{it.copy(busy=true,notice="Generating an on-device draft. Nothing is sent or acted on.")}
        nativeJob=launch{_,who,e->
            val result=platform.generate(prompt);if(!live(e,q)||state.value.scope!=selected)return@launch
            require(voiceTextValid(result.text) && result.text.codePointCount(0,result.text.length)<=4000)
            val draft=EdgeLocalDraft(selected,prompt,result.text,result.truncated,UUID.randomUUID(),System.currentTimeMillis())
            store.saveEdgeDraft(who,draft);if(!live(e,q))return@launch
            update{it.copy(draft=draft,busy=false,notice=if(result.truncated)"Local draft reached its length limit. Review before using or saving it." else "On-device generated draft saved locally for review. It is not a server reply or factual memory.")}
        }
    }
    fun stop(){nativeJob?.cancel();nativeJob=null;selection++;update{it.copy(busy=false,notice="Local generation stopped. No server request or action was created.")}}
    fun importModel(input:InputStream){if(state.value.busy || !visible || !foreground){input.close();return};val p=platform as? EdgePlatform?:run{input.close();return}
        update{it.copy(busy=true)};nativeJob=launch{_,_,e->p.importModel(input);if(current(e))update{it.copy(busy=false,modelPresent=p.modelPresent(),notice="Pinned model imported. Enable local drafts explicitly before generation.")}}
    }
    fun removeModel(){stop();(platform as? EdgePlatform)?.removeModel();update{it.copy(modelPresent=false,localEnabled=false)}}
    private suspend fun pending(who:SessionIdentity,e:Long){val journal=store.edgeJournal(who);if(current(e))update{it.copy(pending=journal?.operations.orEmpty())}}
    private fun queue(op:EdgePending){if(!visible || !foreground || state.value.busy || !state.value.supported || System.currentTimeMillis()<cooldown)return
        val who=owner?:return;validateEdgeJournal(EdgeJournal(who,listOf(op)));update{it.copy(busy=true)}
        launch{c,identity,e->store.saveEdgeOperation(identity,op);if(current(e)){pending(identity,e);submit(c,identity,op,e)}}
    }
    fun enroll(){if(device()!=null)return;val who=owner?:return;val key=runCatching{platform?.publicKey(who,true)}.getOrElse{update{it.copy(notice="The device signing key is unavailable. No registration was sent.")};return}?:return
        val body=EdgeEnrollDto(UUID.randomUUID(),"This Android installation",key);queue(EdgePending(body.operation_id,"enroll",UUID.randomUUID(),adaJson.encodeToString(body)))}
    fun revoke(row:EdgeDeviceDto){val body=EdgeRevokeDto(UUID.randomUUID(),row.revision);queue(EdgePending(body.operation_id,"revoke",row.id,adaJson.encodeToString(body)))}
    fun sync(){val who=owner?:return;val draft=state.value.draft?:return;val device=device()?:return
        if(draft.scopeId!=state.value.scope || state.value.pending.any{it.deviceId==device.id && it.kind=="sync"})return
        val body=EdgeSyncDto(draft.proposalId,device.id,device.revision,device.last_sequence+1,draft.prompt,voiceHash(draft.prompt),draft.output,"")
        val signed=runCatching{body.copy(signature=platform!!.sign(who,edgeSigningMessage(draft.scopeId,body)))}.getOrElse{update{it.copy(notice="The device signing key is unavailable. Keep the local draft; nothing was sent.")};return}
        queue(EdgePending(body.proposal_id,"sync",device.id,adaJson.encodeToString(signed),draft.scopeId))
    }
    private fun validate(row:EdgeProposalDto){require(row.version==EDGE_PROTOCOL && row.trust_class=="model_generated" && row.state=="draft" && row.task=="offline_reply" && row.model_id==EDGE_MODEL_ID && row.model_digest==EDGE_MODEL_DIGEST && row.runtime==EDGE_RUNTIME && voiceTextValid(row.output))}
    private suspend fun ack(who:SessionIdentity,p:EdgePending,row:EdgeProposalDto,e:Long){
        val body=adaJson.decodeFromString<EdgeSyncDto>(p.body);validate(row)
        require(row.id==p.operationId && row.scope_id==p.scopeId && row.device_id==p.deviceId && row.sequence==body.sequence && row.output==body.output && row.prompt_hash==body.prompt_hash && row.sources==body.sources)
        if(!current(e))return;store.acknowledgeEdgeProposal(who,p.operationId);if(!current(e))return
        pending(who,e);if(visible && foreground && state.value.scope==row.scope_id)update{it.copy(receipt=row,draft=null,busy=false,notice="Saved as generated device draft only. Chat, memory and tool permissions were not changed.")};refresh()
    }
    private suspend fun ackDevice(who:SessionIdentity,p:EdgePending,row:EdgeDeviceDto,e:Long){
        require(row.version==EDGE_PROTOCOL && row.id==p.deviceId)
        if(p.kind=="enroll"){val b=adaJson.decodeFromString<EdgeEnrollDto>(p.body);require(row.enrollment_id==p.operationId && row.public_key==b.public_key && row.label==b.label)}
        else {val b=adaJson.decodeFromString<EdgeRevokeDto>(p.body);require(row.revocation_id==p.operationId && row.revoked_at!=null && row.revision==b.expected_revision+1)}
        if(!current(e))return;store.removeEdgeOperation(who,p.operationId);if(current(e)){pending(who,e);update{it.copy(busy=false,notice="Device registration result confirmed.")};refresh()}
    }
    private suspend fun check(c:ConnectionCredential,who:SessionIdentity,p:EdgePending,e:Long){
        if(p.kind=="sync"){when(val r=api.edgeProposal(c,p.operationId)){is ApiResult.Success->ack(who,p,r.value,e);is ApiResult.Failure->if(r.reason!=ApiFailure.NotFound)accept(r,e)}}
        else {val rows=accept(api.edgeDevices(c),e)?:return;rows.firstOrNull{it.id==p.deviceId}?.let{row->if(p.kind=="enroll" || row.revocation_id==p.operationId)ackDevice(who,p,row,e)}}
        if(current(e))update{it.copy(busy=false)}
    }
    private suspend fun submit(c:ConnectionCredential,who:SessionIdentity,p:EdgePending,e:Long){
        if(p.kind=="sync"){val row=accept(api.edgeSync(c,p),e)?:return;ack(who,p,row,e)}
        else {val row=accept(api.edgeDeviceWrite(c,p),e)?:return;ackDevice(who,p,row,e)}
    }
    fun check(p:EdgePending){if(p in state.value.pending)launch{c,o,e->check(c,o,p,e)}}
    fun retry(p:EdgePending){if(p in state.value.pending && visible && foreground && !state.value.busy && System.currentTimeMillis()>=cooldown){update{it.copy(busy=true)};launch{c,o,e->submit(c,o,p,e)}}}
    fun discard(p:EdgePending){if(p in state.value.pending)launch{_,o,e->store.removeEdgeOperation(o,p.operationId);if(current(e)){pending(o,e);update{it.copy(notice="Only the local recovery record was discarded; a server draft or device may still exist.")}}}}
}
