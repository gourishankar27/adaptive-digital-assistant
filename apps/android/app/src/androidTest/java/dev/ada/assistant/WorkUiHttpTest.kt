package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import okhttp3.OkHttpClient
import okhttp3.Request
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

/** Synthetic owner content, real HTTP/Keystore and runner-controlled actual force-stop. */
class WorkUiHttpTest {
    @get:Rule val compose=createAndroidComposeRule<MainActivity>()
    private val context get()=InstrumentationRegistry.getInstrumentation().targetContext
    private val credentialFile get()=File(context.filesDir,"foundation-test-token")
    private val record get()=File(context.filesDir,"work-recovery-metadata")
    private fun credential()=ConnectionCredential.parse(fixtureOrigin(),credentialFile.readText().trim(),true)!!
    private fun count():Int {
        val origin=fixtureOrigin().trimEnd('/')
        val request=Request.Builder().url("$origin/v1/fixture/work/counts").header("Authorization","Bearer "+credentialFile.readText().trim()).build()
        return OkHttpClient().newCall(request).execute().use { response -> require(response.isSuccessful); kotlinx.serialization.json.Json.parseToJsonElement(response.body!!.string()).let { (it as kotlinx.serialization.json.JsonObject)["work_posts"].toString().toInt() } }
    }
    @Test fun workPrepareBeforeProcessStop() {
        require(context.packageName=="dev.ada.validation.phase30.debug")
        val c=credential(); val api=HttpAdaApi()
        val profile=runBlocking { (api.personalities(c) as ApiResult.Success).value.first() }
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { vm.connect(c.server.toString(),credentialFile.readText().trim()) }
        compose.waitUntil(20000) { vm.state.value.account!=null }
        compose.runOnIdle { vm.navigate(ChatDestination.Work) }
        compose.waitUntil(10000) { vm.work.state.value.scopes.isNotEmpty() && !vm.work.state.value.busy }
        compose.onNodeWithTag("work-scopes").performScrollTo().performClick()
        compose.onNodeWithTag("work-project-name").performScrollTo().performTextReplacement("Public UI development project")
        androidx.test.espresso.Espresso.closeSoftKeyboard()
        compose.onNodeWithTag("work-project-create").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.work.state.value.scopes.any { it.name=="Public UI development project" } && !vm.work.state.value.busy }
        val projectScope=vm.work.state.value.scopes.single { it.name=="Public UI development project" }.id
        val conversation=runBlocking { (api.createConversation(c,ConversationInputDto(profile.id,"Public work UI project",scope_id=projectScope)) as ApiResult.Success).value }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(10000) { vm.state.value.conversation?.id==conversation.id && !vm.state.value.events.loading }
        compose.runOnIdle { vm.updateDraft("Public synthetic project follow-through sample.");vm.send() }
        compose.waitUntil(20000) { vm.state.value.pending==null && vm.state.value.submittedMessages.isNotEmpty() }
        val event=runBlocking { (api.events(c,conversation.id) as ApiResult.Success).value.last { it.role=="assistant" } }
        val original=runBlocking { (api.request(c,event.request_id) as ApiResult.Success).value }
        compose.runOnIdle { vm.saveNextAction(event) }
        compose.waitUntil(10000) { vm.work.state.value.draft!=null && !vm.work.state.value.busy }
        compose.onNodeWithTag("work-description").performScrollTo().performTextReplacement("Review the public follow-through sample")
        androidx.test.espresso.Espresso.closeSoftKeyboard()
        compose.onNodeWithTag("work-preview").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.work.state.value.preview!=null && !vm.work.state.value.busy }
        compose.onNodeWithTag("work-exact-preview").performScrollTo().assertTextContains("not scheduled",substring=true)
        compose.onNodeWithTag("work-save").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.work.state.value.items.size==1 && vm.work.state.value.pending.isEmpty() && !vm.work.state.value.busy }
        val task=vm.work.state.value.items.single()
        assertEquals("owner_reviewed_suggestion",task.provenance);assertEquals(conversation.id,task.origin_conversation_id)
        compose.onNodeWithTag("work-select-${task.id}").performScrollTo().performClick()
        compose.onNodeWithTag("work-screen").performScrollToNode(hasTestTag("work-brief-editor"))
        compose.onNodeWithTag("work-brief-editor").performClick()
        compose.onNodeWithTag("work-create-brief").performScrollTo().performClick()
        compose.waitUntil(10000) { vm.work.state.value.brief!=null && !vm.work.state.value.busy }
        compose.onNodeWithTag("work-screen").performScrollToNode(hasTestTag("work-brief"))
        compose.onNodeWithTag("work-brief").assertExists()
        val after=runBlocking { (api.request(c,event.request_id) as ApiResult.Success).value }
        assertEquals(original,after)
        val op=WorkWriteDto(UUID.randomUUID(),task.revision,task.fields.copy(status="done"))
        val preview=runBlocking { (api.workPreview(c,task.scope_id,task.id,op) as ApiResult.Success).value }
        val pending=WorkPending(op.operation_id,"save",adaJson.encodeToString(op.copy(preview_hash=preview.preview_hash)),task.scope_id,task.id)
        val identity=SessionIdentity(c.server.toString(),vm.state.value.account!!.owner)
        val store=AndroidSessionStore(context)
        runBlocking { store.saveWorkOperation(identity,pending) }
        // A received POST whose acknowledgement is deliberately retained as unknown locally.
        val p=WorkProjectDto(UUID.randomUUID(),"Public acknowledged recovery project")
        val project=WorkPending(p.operation_id,"project",adaJson.encodeToString(p),UUID.randomUUID())
        runBlocking { store.saveWorkOperation(identity,project); assertTrue(api.workWrite(c,project) is ApiResult.Success) }
        record.writeText(listOf(task.id,task.scope_id,op.operation_id,count()).joinToString("\n"))
    }
    @Test fun workRestoreAfterProcessStop() {
        require(context.packageName=="dev.ada.validation.phase30.debug" && record.isFile)
        val data=record.readLines();val task=UUID.fromString(data[0]);val selected=UUID.fromString(data[1]);val op=UUID.fromString(data[2]);val before=data[3].toInt()
        val c=credential();val api=HttpAdaApi()
        val vm=ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20000) { vm.state.value.account!=null && vm.work.state.value.pending.size==1 }
        assertEquals(op,vm.work.state.value.pending.single().operationId)
        assertEquals(before,count())
        val rows=runBlocking { (api.workItems(c,selected) as ApiResult.Success).value }
        assertEquals("planned",rows.single { it.id==task }.fields.status)
        compose.runOnIdle { vm.navigate(ChatDestination.Work) }
        compose.waitUntil(10000) { vm.work.state.value.scopes.any { it.id==selected } }
        compose.runOnIdle { vm.work.selectScope(selected) }
        compose.waitUntil(10000) { !vm.work.state.value.busy && vm.work.state.value.items.any { it.id==task } }
        compose.runOnIdle { vm.work.retry(vm.work.state.value.pending.single()) }
        compose.waitUntil(10000) { vm.work.state.value.pending.isEmpty() && vm.work.state.value.items.any { it.id==task && it.fields.status=="done" } }
        assertEquals(before+1,count())
        val history=runBlocking { (api.workHistory(c,task) as ApiResult.Success).value }
        assertEquals(listOf("planned","done"),history.map { it.fields.status })
        val identity=SessionIdentity(c.server.toString(),vm.state.value.account!!.owner)
        assertNull(runBlocking { AndroidSessionStore(context).workJournal(identity) })
    }
}
