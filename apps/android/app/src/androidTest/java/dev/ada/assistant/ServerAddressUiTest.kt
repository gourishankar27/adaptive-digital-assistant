package dev.ada.assistant

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Separate validation package; no normal app data, system trust or real network enrollment. */
class ServerAddressUiTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    @Test fun unresolvableReservedNameHasDnsFeedbackWithoutSendingALogin() = runBlocking {
        val credential = ConnectionCredential.parse("https://ada-phase21.invalid", "synthetic-never-sent", false)!!
        assertEquals(ApiFailure.Dns, (HttpAdaApi().me(credential) as ApiResult.Failure).reason)
    }
    @Test fun savedMetadataSurvivesReopenAndImportRequiresSelection() {
        assumeTrue(compose.activity.packageName.startsWith("dev.ada.validation."))
        val preferences = ServerProfilePreferences(compose.activity)
        assertTrue(preferences.save(emptyList()))
        compose.waitUntil(20_000) { compose.onAllNodesWithTag("connect-server").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithTag("connect-server").performTextInput("https://ada.example")
        compose.onNodeWithText("Saved servers and connection checks").performScrollTo().performClick()
        compose.onNodeWithText("Server name").performScrollTo().performTextInput("Laptop")
        compose.onNodeWithText("Save server address").performScrollTo().performClick()
        compose.runOnIdle { assertEquals(listOf(ServerProfile("Laptop", "https://ada.example/")), preferences.load()) }
        compose.activityRule.scenario.recreate()
        compose.waitUntil(20_000) { compose.onAllNodesWithTag("connect-server").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("Saved servers and connection checks").performScrollTo().performClick()
        compose.onNodeWithText("Use Laptop: https://ada.example/").assertExists()
        compose.onNodeWithText("Clear selected address").performScrollTo().performClick()
        assertEquals("", compose.onNodeWithTag("connect-server").fetchSemanticsNode().config[SemanticsProperties.EditableText].text)
        compose.onNodeWithText("Use Laptop: https://ada.example/").performScrollTo().performClick()
        compose.onNodeWithTag("connect-server").assertTextContains("https://ada.example/")
        compose.onNodeWithText("Server address import (JSON)").performScrollTo().performTextInput("""{"version":1,"label":"Other","origin":"https://other.example"}""")
        compose.onNodeWithText("Preview address import").performScrollTo().performClick()
        compose.onNodeWithTag("connect-server").assertTextContains("https://ada.example/")
        compose.onNodeWithText("Use reviewed address").performScrollTo().performClick()
        compose.onNodeWithTag("connect-server").assertTextContains("https://other.example/")
        compose.onNodeWithText("Remove Laptop").performScrollTo().performClick()
        compose.runOnIdle { assertTrue(preferences.load().isEmpty()) }
    }

    @Test fun platformTlsRejectsTheLaboratoryCaWithoutSendingTheSyntheticCredential() = runBlocking {
        val origin = InstrumentationRegistry.getArguments().getString("tlsProbeOrigin")
        assumeTrue("Run while the isolated TLS fixture is available", origin != null)
        val credential = ConnectionCredential.parse(origin!!, "synthetic-never-sent", false)!!
        val result = HttpAdaApi().me(credential)
        assertEquals(ApiFailure.Tls, (result as ApiResult.Failure).reason)
    }
}
