package dev.ada.assistant

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import android.os.Bundle

class StreamingRecoveryPrepareTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    @Test fun reserveAndSubmitBeforeActualForceStop() {
        assumeTrue(InstrumentationRegistry.getArguments().getString("adaStreamingRecovery") == "true")
        val token = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token").readText().trim()
        val c = ConnectionCredential.parse("http://10.0.2.2:18765", token, true)!!; val api = HttpAdaApi()
        val key = UUID.randomUUID()
        runBlocking {
            val owner = (api.me(c) as ApiResult.Success).value.id
            val profile = (api.personalities(c) as ApiResult.Success).value.first()
            val conversation = (api.createConversation(c, ConversationInputDto(profile.id, "Synthetic stream restart")) as ApiResult.Success).value
            val identity = SessionIdentity(c.server.toString(), owner)
            val body = ChatInputDto(key, "Synthetic streaming actual restart")
            val store = AndroidSessionStore(compose.activity.applicationContext)
            store.saveCredential(StoredCredential(identity, token)); store.savePending(PendingMessage(identity, conversation.id, body))
            check(api.submitStream(c, conversation.id, body) is ApiResult.Success)
        }
        InstrumentationRegistry.getInstrumentation().sendStatus(2, Bundle().apply { putString("streamRecoveryKey", key.toString()) })
    }
}
