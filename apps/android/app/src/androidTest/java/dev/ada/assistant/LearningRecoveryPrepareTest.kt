package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

class LearningRecoveryPrepareTest {
    @Test fun prepareCommittedReviewWithoutDelivery() = runBlocking {
        assumeTrue(InstrumentationRegistry.getArguments().getString("adaLearningRecovery") == "true")
        val i = InstrumentationRegistry.getInstrumentation(); val ctx = i.targetContext; val file = File(ctx.filesDir, "foundation-test-token"); assumeTrue(file.isFile)
        val store = AndroidSessionStore(ctx); store.clear(); val token = file.readText().trim()
        val c = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!; val api = HttpAdaApi()
        val owner = SessionIdentity(c.server.toString(), success(api.me(c)).id); store.saveCredential(StoredCredential(owner, token))
        val profile = success(api.personalities(c)).first(); val conversation = success(api.createConversation(c, ConversationInputDto(profile.id, "Synthetic recovery review")))
        val prior = success(api.learning(c, conversation.scope_id)).config; val configKey = UUID.randomUUID()
        val config = LearningJournal(owner, conversation.scope_id, configKey, "config", adaJson.encodeToString(LearningConfigWriteDto(configKey, prior.revision, "enrolled")))
        store.saveLearningJournal(config); success(api.learningOperation(c, config)); store.removeLearningJournal(owner, configKey)
        for(text in listOf("Concise recovery planning.", "Brief recovery explanations.", "Compact recovery reviews.")) {
            val request = success(api.send(c, conversation.id, ChatInputDto(UUID.randomUUID(), text)))
            val event = success(api.events(c, conversation.id)).single { it.role == "user" && it.request_id == request.request_id }
            val source = success(api.source(c, event.source_version_id)); val key = UUID.randomUUID()
            val observation = LearningJournal(owner, conversation.scope_id, key, "observe", adaJson.encodeToString(LearningObservationWriteDto(key,
                SourcePinDto(source.id, source.version, source.content_hash, 0, source.content.codePointCount(0, source.content.length)), PreferenceValuesDto(verbosity = "concise"), "repeated_observation")))
            store.saveLearningJournal(observation); success(api.learningOperation(c, observation)); store.removeLearningJournal(owner, key)
        }
        val proposal = success(api.learning(c, conversation.scope_id)).proposals.single(); val key = UUID.randomUUID()
        val journal = LearningJournal(owner, conversation.scope_id, key, "review", adaJson.encodeToString(LearningReviewWriteDto(key, proposal.id, proposal.revision, "approve")))
        store.saveLearningJournal(journal); val receipt = success(api.learningOperation(c, journal))
        assertEquals(key, receipt.operation_id); assertEquals(journal, store.learningJournal(owner))
        i.sendStatus(0, Bundle().apply { putString("recoveryLearningKey", key.toString()) })
    }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success); return result.value }
}
