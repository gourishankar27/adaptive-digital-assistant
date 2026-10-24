package dev.ada.assistant.data

import java.util.UUID
import org.junit.Assert.*
import org.junit.Test

class LongVoiceContractTest {
    @Test fun contextUsesUnicodePositionsAndCannotReplaceTheFullReviewedNarrative() {
        val identity=SessionIdentity("https://ada.test/",UUID.randomUUID())
        val words="🫖"+"a".repeat(5000)
        val segment=TranscriptSegmentDto(UUID.randomUUID(),0,125000,words,voiceHash(words))
        val transcript=TranscriptInputDto(UUID.randomUUID(),LONG_VOICE_ENGINE,"sherpa-onnx-1.13.8","en-US",125000,words,"a".repeat(64),listOf(segment))
        val draft=VoiceDraft(identity,UUID.randomUUID(),UUID.randomUUID(),transcript,words)
        validateVoiceDraft(draft); assertNull(draft.contextText())
        val selected=draft.copy(contextStart=1,contextEnd=4,approved=true)
        assertEquals("aaa",selected.contextText())
        val message=PendingMessage(identity,draft.conversationId,ChatInputDto(UUID.randomUUID(),"aaa"),transcript,draft.scopeId,words,1,0)
        val body=longVoiceRequest(message)
        assertEquals(words,body.reviewed_text); assertEquals(words,body.transcript.segments.single().text)
        assertEquals(1,body.context_start); assertEquals(4,body.context_end)
        try { longVoiceRequest(message.copy(body=message.body.copy(content="forged"))); fail() } catch (_: IllegalArgumentException) { }
    }
    @Test fun legacyWireHasNoNewEngineMetadataAndLongSegmentsCannotLieAboutHashes() {
        val old=TranscriptInputDto(UUID.randomUUID(),"android_on_device","Android synthetic","en-US",1000,"public words")
        val wire=adaJson.encodeToString(TranscriptInputDto.serializer(),old)
        assertFalse(wire.contains("segments")); assertFalse(wire.contains("modelSha256"))
        val row=TranscriptSegmentDto(UUID.randomUUID(),0,1000,"public words","0".repeat(64))
        try { validateTranscript(old.copy(engine_id=LONG_VOICE_ENGINE,engine_version="sherpa-onnx-1.13.8",modelSha256="a".repeat(64),segments=listOf(row))); fail() } catch (_: IllegalArgumentException) { }
    }
}
