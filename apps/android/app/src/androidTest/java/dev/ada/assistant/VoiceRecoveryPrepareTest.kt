package dev.ada.assistant

import android.os.Bundle
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

class VoiceRecoveryPrepareTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private fun prepare(submit: Boolean) {
        assumeTrue(InstrumentationRegistry.getArguments().getString("adaVoiceRecovery") == "true")
        val token = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token").readText().trim()
        val c = ConnectionCredential.parse(dev.ada.assistant.fixtureOrigin(), token, true)!!; val api = HttpAdaApi()
        val transcript = TranscriptInputDto(UUID.randomUUID(), "android_on_device", "Explicit recovery test adapter", "en-US", 2000, "Original generated recovery cattle")
        val key = UUID.randomUUID()
        runBlocking {
            val owner = (api.me(c) as ApiResult.Success).value.id
            val profile = (api.personalities(c) as ApiResult.Success).value.first()
            val conversation = (api.createConversation(c, ConversationInputDto(profile.id, "Synthetic voice recovery")) as ApiResult.Success).value
            val identity = SessionIdentity(c.server.toString(), owner)
            val draft = VoiceDraft(identity, conversation.id, conversation.scope_id, transcript, if (submit) "Synthetic streaming reviewed recovery kettle" else "Reviewed recovery kettle", approved = submit)
            val store = AndroidSessionStore(compose.activity.applicationContext)
            store.saveCredential(StoredCredential(identity, token)); store.saveVoiceDraft(draft)
            if (submit) {
                val pending = PendingMessage(identity, conversation.id, ChatInputDto(key, draft.reviewedText), transcript, conversation.scope_id)
                store.savePending(pending)
                check(api.submitVoice(c, conversation.id, ReviewedVoiceInputDto.from(pending)) is ApiResult.Success)
            }
        }
        InstrumentationRegistry.getInstrumentation().sendStatus(2, Bundle().apply { putString(if (submit) "voiceRequestKey" else "voiceDraftKey", (if (submit) key else transcript.transcript_id).toString()) })
    }
    @Test fun saveEditedDraftBeforeActualForceStop() = prepare(false)
    @Test fun reserveAndSubmitReviewedVoiceBeforeActualForceStop() = prepare(true)
}
