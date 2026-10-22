package dev.ada.assistant.data

import java.util.UUID
import javax.crypto.KeyGenerator
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test

private class EdgeDisk:SessionDisk { var bytes:ByteArray?=null;var fail=false
    override fun read(maxBytes:Int)=bytes?.copyOf()
    override fun write(bytes:ByteArray){if(fail)error("Synthetic disk failure");this.bytes=bytes.copyOf()}
    override fun delete(){bytes=null}
}
private class EdgeKeys:SessionKeys {var value:javax.crypto.SecretKey?=null
    override fun existing()=value
    override fun create()=KeyGenerator.getInstance("AES").apply{init(256)}.generateKey().also{value=it}
    override fun delete(){value=null}
}
class EdgeJournalTest {
    @Test fun exactOperationDraftAndAcknowledgementSurviveEncryptedRecovery()=runTest {
        val disk=EdgeDisk();val keys=EdgeKeys();fun store()=EncryptedSessionStore(disk,AesGcmSessionCipher(keys),false)
        val who=SessionIdentity("https://ada.example/",UUID.randomUUID());val s=store()
        s.saveCredential(StoredCredential(who,"public-synthetic-token"))
        val draft=EdgeLocalDraft(UUID.randomUUID(),"Public request","Public generated draft",false,UUID.randomUUID(),1000)
        s.saveEdgeDraft(who,draft)
        val body=EdgeEnrollDto(UUID.randomUUID(),"Public installation","A".repeat(100))
        val op=EdgePending(body.operation_id,"enroll",UUID.randomUUID(),adaJson.encodeToString(body))
        s.saveEdgeOperation(who,op)
        assertEquals(draft,store().edgeJournal(who)!!.draft);assertEquals(listOf(op),store().edgeJournal(who)!!.operations)
        assertFalse(disk.bytes!!.toString(Charsets.UTF_8).contains("Public generated"))
        try{s.saveEdgeOperation(who,op.copy(body=adaJson.encodeToString(body.copy(label="Changed"))));fail()}catch(_:SessionStorageException){}
        disk.fail=true
        try{s.saveEdgeDraft(who,draft.copy(output="Changed"));fail()}catch(_:Exception){}
        disk.fail=false;assertEquals(draft,store().edgeJournal(who)!!.draft)
        s.removeEdgeOperation(who,op.operationId);assertEquals(draft,store().edgeJournal(who)!!.draft)
        s.acknowledgeEdgeProposal(who,draft.proposalId);assertNull(store().edgeJournal(who)!!.draft)
        assertEquals(draft.proposalId,store().edgeJournal(who)!!.lastProposal)
        val other=who.copy(owner=UUID.randomUUID());assertNull(s.edgeJournal(other))
        s.saveCredential(StoredCredential(other,"public-other-token"));assertNull(s.edgeJournal(other))
    }
    @Test fun unapprovedModelsAndBinaryPdfKeepDistinctLineage() {
        val who=SessionIdentity("https://ada.example/",UUID.randomUUID())
        val draft=EdgeLocalDraft(UUID.randomUUID(),"Public","Public draft",false,UUID.randomUUID(),1000,modelDigest="0".repeat(64))
        assertTrue(runCatching{validateEdgeJournal(EdgeJournal(who,draft=draft))}.isFailure)
        val raw="%PDF-1.4\n".toByteArray()+byteArrayOf(0xff.toByte(),0x80.toByte())
        val pending=PendingDocument(who,UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),"public.pdf","application/pdf",java.util.Base64.getEncoder().encodeToString(raw))
        validateDocument(pending);assertArrayEquals(raw,pending.rawBytes())
        assertTrue(runCatching{documentText(raw)}.isFailure)
    }
}
