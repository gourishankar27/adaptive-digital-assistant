package dev.ada.assistant

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import dev.ada.assistant.ui.AdaTheme
import dev.ada.assistant.ui.SafeChatText
import dev.ada.assistant.ui.ThemePalette
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class ChatTextSafetyTest {
    @get:Rule val compose = createComposeRule()

    @Test fun sourceMarkupAndCommandsStayLiteralAndOnlySafeExplicitLinksAppear() {
        val literal = "<script>synthetic</script> javascript:alert(1)\n```sh\nsynthetic-command\n```\n" +
            "https://example.com/source https://user:password@example.com/private"
        compose.setContent {
            AdaTheme(ThemePalette.OliveGreen, dark = true) {
                Surface(Modifier.fillMaxSize()) {
                    Column(Modifier.verticalScroll(rememberScrollState())) { SafeChatText(literal) }
                }
            }
        }
        compose.onNodeWithText(literal).assertIsDisplayed()
        assertEquals(1, compose.onAllNodesWithText("Open link to example.com").fetchSemanticsNodes().size)
        assertEquals(0, compose.onAllNodesWithText("Run", substring = false).fetchSemanticsNodes().size)
    }
}
