package dev.ada.assistant

import android.content.*
import android.os.*
import androidx.activity.compose.setContent
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.edge.*
import dev.ada.assistant.ui.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.*
import okhttp3.OkHttpClient
import okhttp3.Request
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

/** Public data only. This never activates a candidate in the production UI. */
class PdfEdgeDeviceTest {
    @get:Rule val compose=createAndroidComposeRule<MainActivity>()
    private val context get()=InstrumentationRegistry.getInstrumentation().targetContext
    private val token get()=File(context.filesDir,"foundation-test-token").readText().trim()
    private val record get()=File(context.filesDir,"pdf-edge-metadata")
    private fun connection()=ConnectionCredential.parse(fixtureOrigin(),token,true)!!
    private fun guard(){require(context.packageName=="dev.ada.validation.phase19.debug")}
    private fun <T> success(value:ApiResult<T>):T {require(value is ApiResult.Success){"Synthetic device operation failed"};return value.value}
    private fun count():Int {
        val request=Request.Builder().url(fixtureOrigin().trimEnd('/')+"/v1/fixture/pdf-edge/counts").header("Authorization","Bearer $token").build()
        return OkHttpClient().newCall(request).execute().use { response -> require(response.isSuccessful);(kotlinx.serialization.json.Json.parseToJsonElement(response.body!!.string()) as kotlinx.serialization.json.JsonObject)["edge_posts"].toString().toInt() }
    }
    @Test fun preparePdfAndPrivateModelDirectory() {
        require(context.packageName=="dev.ada.validation.phase19.debug");val api=HttpAdaApi();val c=connection()
        val selected=runBlocking{success(api.createScope(c,ScopeInputDto("Public PDF device study")))}
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle{vm.connect(c.server.toString(),token)}
        compose.waitUntil(20000){vm.state.value.account!=null}
        compose.runOnIdle{vm.navigate(ChatDestination.Documents)}
        compose.waitUntil(15000){vm.documents.state.value.pdfEnabled && vm.documents.state.value.scopes.items.any{it.id==selected.id}}
        val raw=File(context.filesDir,"public-study.pdf").readBytes()
        compose.runOnIdle{vm.documents.selectScope(selected.id);vm.documents.beginUpload();vm.documents.chooseFile(vm.documents.beginFileSelection()!!,"public-study.pdf",raw);vm.documents.preview()}
        compose.waitUntil(5000){vm.documents.state.value.preview!=null}
        compose.onNodeWithTag("document-preview-text").performScrollTo().assertTextContains("Exact binary PDF",substring=true)
        assertTrue(runBlocking{success(api.documentUploads(c,selected.id))}.isEmpty())
        compose.onNodeWithTag("document-upload").performScrollTo().performClick()
        compose.waitUntil(20000){vm.documents.state.value.version?.extraction?.pages?.size==2 && vm.documents.state.value.chunks.items.size==2}
        val version=vm.documents.state.value.version!!
        assertTrue(verifyDocumentVersion(version,vm.documents.state.value.detail!!))
        assertEquals(listOf(1,2),vm.documents.state.value.chunks.items.map{it.pdf!!.page})
        assertEquals("imported_untrusted",version.trust_class)
        assertTrue(runBlocking{success(api.claims(c,selected.id))}.isEmpty())
        val cards=runBlocking{success(api.retrieve(c,selected.id,RetrieveInputDto("orbit launch",use_documents=true)))}.document_selected
        assertEquals(1,cards.first().pdf!!.page)
        val scan=File(context.filesDir,"public-scan.pdf").readBytes()
        compose.runOnIdle{vm.documents.beginUpload();vm.documents.chooseFile(vm.documents.beginFileSelection()!!,"public-scan.pdf",scan);vm.documents.preview();vm.documents.savePreview()}
        compose.waitUntil(20000){vm.documents.state.value.pendingReceipt?.state=="failed" && !vm.documents.state.value.saving}
        compose.onNodeWithText("This PDF has a scanned or blank page.",substring=true).performScrollTo().assertIsDisplayed()
        assertEquals("pdf_ocr_required",vm.documents.state.value.pendingReceipt!!.error_code)
        compose.runOnIdle{vm.documents.discardPending()}
        compose.waitUntil(5000){vm.documents.state.value.pending==null}
        compose.runOnIdle{compose.activity.setContent{AdaTheme{DocumentSourceCard(cards.first(),UUID.randomUUID())}}}
        compose.onNodeWithTag("source-quote-D1").assertTextContains("Public orbit launch is Monday.",substring=true)
        val identity=SessionIdentity(c.server.toString(),vm.state.value.account!!.owner)
        val pending=PendingDocument(identity,selected.id,UUID.randomUUID(),UUID.randomUUID(),"public-study.pdf","application/pdf",java.util.Base64.getEncoder().encodeToString(raw))
        runBlocking{AndroidSessionStore(context).saveDocumentPending(pending)}
        File(context.filesDir,"edge").mkdirs()
        record.writeText(selected.id.toString()+"\n"+pending.uploadId)
    }
    @Test fun nativeIsolatedReplyAndSignedUnknownReceipt() {
        guard();require(BuildConfig.EDGE_RUNTIME);val c=connection();val api=HttpAdaApi();val scope=UUID.fromString(record.readLines()[0])
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20000){vm.state.value.account!=null && vm.documents.state.value.pending!=null}
        compose.runOnIdle{vm.navigate(ChatDestination.Documents);vm.documents.checkPending()}
        compose.waitUntil(10000){!vm.documents.state.value.saving}
        assertEquals(UUID.fromString(record.readLines()[1]),vm.documents.state.value.pending!!.uploadId)
        val identity=SessionIdentity(c.server.toString(),vm.state.value.account!!.owner)
        val platform=EdgePlatform(context)
        val measured=runBlocking{withContext(Dispatchers.Main){platform.generate("Write a brief reply saying I have not received tracking details yet. Ask them to send the tracking number. Do not claim to have checked it.")}}
        assertFalse(measured.internetAllowed);assertNotEquals(android.os.Process.myUid(),measured.isolatedUid)
        assertTrue(measured.pssKiB in 1..768*1024);assertTrue(measured.elapsed in 1..20000)
        println("NATIVE_PUBLIC_PROBE elapsed_ms=${measured.elapsed} pss_kib=${measured.pssKiB} isolated_uid=${measured.isolatedUid} internet=${measured.internetAllowed}")
        val device=UUID.randomUUID();val enrollment=EdgeEnrollDto(UUID.randomUUID(),"Public S24 FE validation",platform.publicKey(identity,true)!!)
        val enrolled=runBlocking{success(api.edgeDeviceWrite(c,EdgePending(enrollment.operation_id,"enroll",device,adaJson.encodeToString(enrollment))))}
        assertEquals(enrollment.operation_id,enrolled.enrollment_id)
        val store=AndroidSessionStore(context)
        fun operation(sequence:Int):EdgePending {
            val body=EdgeSyncDto(UUID.randomUUID(),device,enrolled.revision,sequence,"Public native probe",voiceHash("Public native probe"),measured.text,"")
            val signed=body.copy(signature=platform.sign(identity,edgeSigningMessage(scope,body)))
            return EdgePending(body.proposal_id,"sync",device,adaJson.encodeToString(signed),scope)
        }
        val first=operation(1);val second=operation(2)
        runBlocking{store.saveEdgeOperation(identity,first);assertEquals("model_generated",success(api.edgeSync(c,first)).trust_class);store.saveEdgeOperation(identity,second)}
        assertFalse(runBlocking{success(api.capabilities(c))}.edge_inference)
        assertFalse(EDGE_QUALITY_APPROVED)
        record.appendText("\n${second.operationId}\n${count()}\n$device\n${first.operationId}")
    }
    @Test fun restorePdfOnlyAfterProcessStop() {
        require(context.packageName=="dev.ada.validation.phase19.debug")
        val c=connection();val api=HttpAdaApi();val lines=record.readLines();val selected=UUID.fromString(lines[0])
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20000){vm.state.value.account!=null && vm.documents.state.value.pending?.uploadId==UUID.fromString(lines[1])}
        assertEquals(2,runBlocking{success(api.documentUploads(c,selected))}.size)
        compose.runOnIdle{vm.navigate(ChatDestination.Documents);vm.documents.checkPending()}
        compose.waitUntil(10000){!vm.documents.state.value.saving}
        assertNotNull(vm.documents.state.value.pending)
        assertEquals(2,runBlocking{success(api.documentUploads(c,selected))}.size)
        compose.runOnIdle{vm.documents.resumePending()}
        compose.waitUntil(20000){vm.documents.state.value.pending==null && vm.documents.state.value.version?.extraction?.pages?.size==2}
        assertEquals(3,runBlocking{success(api.documentUploads(c,selected))}.size)
        assertTrue(runBlocking{success(api.claims(c,selected))}.isEmpty())
    }
    @Test fun restoreGetOnlyRetryOriginalAndRevoke() {
        guard();val lines=record.readLines();val c=connection();val api=HttpAdaApi();val scope=UUID.fromString(lines[0]);val id=UUID.fromString(lines[2]);val posts=lines[3].toInt()
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20000){vm.state.value.account!=null && vm.edge.state.value.pending.size==1}
        assertEquals(id,vm.edge.state.value.pending.single().operationId);assertEquals(posts,count())
        compose.runOnIdle{vm.navigate(ChatDestination.Edge)}
        compose.waitUntil(10000){vm.edge.state.value.scopes.any{it.id==scope} && vm.edge.state.value.devices.isNotEmpty()}
        compose.runOnIdle{vm.edge.selectScope(scope);vm.edge.retry(vm.edge.state.value.pending.single())}
        compose.waitUntil(10000){vm.edge.state.value.pending.isEmpty() && vm.edge.state.value.receipt?.id==id}
        assertEquals(posts+1,count());compose.onNodeWithTag("edge-receipt").performScrollTo().performClick()
        assertTrue(runBlocking{success(api.claims(c,scope))}.isEmpty())
        val row=vm.edge.state.value.devices.single{it.id==UUID.fromString(lines[4])}
        compose.runOnIdle{vm.edge.revoke(row)}
        compose.waitUntil(10000){vm.edge.state.value.devices.any{it.id==row.id && it.revoked_at!=null}}
        assertTrue(runBlocking{api.edgeProposal(c,UUID.fromString(lines[5]))} is ApiResult.Failure)
    }
    @Test fun prepareSignedReceiptFixtureWithoutInference() {
        guard();val c=connection();val api=HttpAdaApi();val scope=UUID.fromString(record.readLines()[0])
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20000){vm.state.value.account!=null}
        val who=SessionIdentity(c.server.toString(),vm.state.value.account!!.owner)
        val platform=EdgePlatform(context);val device=UUID.randomUUID()
        val body=EdgeEnrollDto(UUID.randomUUID(),"Public emulator signing fixture",platform.publicKey(who,true)!!)
        val enrolled=runBlocking{success(api.edgeDeviceWrite(c,EdgePending(body.operation_id,"enroll",device,adaJson.encodeToString(body))))}
        assertEquals(body.operation_id,enrolled.enrollment_id)
        val store=AndroidSessionStore(context)
        fun operation(sequence:Int):EdgePending {
            // Synthetic test output: a model tag is a declaration, not inference attestation.
            val input=EdgeSyncDto(UUID.randomUUID(),device,enrolled.revision,sequence,"Public receipt protocol fixture",voiceHash("Public receipt protocol fixture"),"Public synthetic generated draft, no native inference.","")
            val signed=input.copy(signature=platform.sign(who,edgeSigningMessage(scope,input)))
            return EdgePending(input.proposal_id,"sync",device,adaJson.encodeToString(signed),scope)
        }
        val first=operation(1);val second=operation(2)
        runBlocking{store.saveEdgeOperation(who,first);assertEquals("model_generated",success(api.edgeSync(c,first)).trust_class);store.saveEdgeOperation(who,second)}
        record.appendText("\n${second.operationId}\n${count()}\n$device\n${first.operationId}")
        assertFalse(EDGE_QUALITY_APPROVED)
    }
    @Test fun isolatedNativeCancellationTerminatesBinder()=runBlocking {
        guard();require(BuildConfig.EDGE_RUNTIME);val model=File(context.filesDir,"edge/qwen3-0.6b-q8.gguf")
        val binder=CompletableDeferred<IBinder>()
        val connection=object:ServiceConnection {
            override fun onServiceConnected(name:ComponentName,service:IBinder){binder.complete(service)}
            override fun onServiceDisconnected(name:ComponentName){}
        }
        val bound=context.bindService(Intent(context,NativeDraftService::class.java),connection,Context.BIND_AUTO_CREATE)
        require(bound)
        val fd=ParcelFileDescriptor.open(model,ParcelFileDescriptor.MODE_READ_ONLY)
        val service=withTimeout(10000){binder.await()}
        try {
            val reply=Messenger(Handler(Looper.getMainLooper()){true})
            Messenger(service).send(Message.obtain(null,1).apply{replyTo=reply;data=Bundle().apply{putString("request",UUID.randomUUID().toString());putByteArray("prompt","<|im_start|>user\nWrite a long public story.<|im_end|>\n<|im_start|>assistant\n".toByteArray());putParcelable("model",fd)}})
            delay(500)
        } finally {context.unbindService(connection);fd.close()}
        withTimeout(5000){while(service.isBinderAlive)delay(50)}
        assertFalse(service.isBinderAlive)
    }
}
