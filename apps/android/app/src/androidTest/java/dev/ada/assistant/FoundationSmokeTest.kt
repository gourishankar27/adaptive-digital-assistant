package dev.ada.assistant

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.assertIsSelected
import androidx.compose.ui.test.assertIsOn
import androidx.compose.ui.test.assertIsOff
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.lifecycle.ViewModelProvider
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.ui.ChatViewModel
import kotlinx.coroutines.runBlocking
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.Before
import dev.ada.assistant.ui.AppearancePreferences
import dev.ada.assistant.ui.AppearanceSettings
import dev.ada.assistant.ui.ThemePalette

class FoundationSmokeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    @Before fun resetAppearanceAndSession() {
        compose.runOnIdle { ViewModelProvider(compose.activity)[ChatViewModel::class.java].logout() }
        runBlocking { AndroidSessionStore(InstrumentationRegistry.getInstrumentation().targetContext).clear() }
        AppearancePreferences(InstrumentationRegistry.getInstrumentation().targetContext).save(AppearanceSettings())
        compose.activityRule.scenario.recreate()
    }
    @Test fun launchesLabelsInputsAndThemePreview() {
        compose.runOnIdle {
            org.junit.Assert.assertTrue(compose.activity.window.attributes.flags and android.view.WindowManager.LayoutParams.FLAG_SECURE != 0)
            org.junit.Assert.assertFalse(androidx.core.view.WindowInsetsControllerCompat(compose.activity.window, compose.activity.window.decorView).isAppearanceLightStatusBars)
            org.junit.Assert.assertFalse(androidx.core.view.WindowInsetsControllerCompat(compose.activity.window, compose.activity.window.decorView).isAppearanceLightNavigationBars)
        }
        compose.onNodeWithText("Welcome back.").assertIsDisplayed()
        compose.onNodeWithText("Connect").assertIsNotEnabled()
        compose.onNodeWithText("ADA server URL").performScrollTo().performTextInput("http://external.example")
        compose.onNodeWithTag("connect-legacy").performScrollTo().performClick()
        compose.onNodeWithText("Bearer token").performScrollTo().performTextInput("invalid-test-only")
        compose.onNodeWithText("Connect").performScrollTo().performClick()
        compose.onNodeWithText("Check the entered values and try again.").performScrollTo().assertIsDisplayed()
        closeSoftKeyboard()
        compose.waitUntil(10_000) {
            compose.onAllNodes(androidx.compose.ui.test.hasTestTag("top-settings")).fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithTag("top-settings").performClick()
        compose.onNodeWithText("ADA Ambient").assertIsSelected()
        compose.onNodeWithText("Dark Red").performScrollTo().performClick().assertIsSelected()
        compose.onNodeWithText("Olive Green").performScrollTo().performClick().assertIsSelected()
        compose.onNodeWithContentDescription("Dark mode").performScrollTo().assertIsOn()
        compose.onNodeWithContentDescription("Dark mode").performScrollTo().performClick().assertIsOff()
        compose.runOnIdle {
            org.junit.Assert.assertTrue(androidx.core.view.WindowInsetsControllerCompat(compose.activity.window, compose.activity.window.decorView).isAppearanceLightStatusBars)
            org.junit.Assert.assertTrue(androidx.core.view.WindowInsetsControllerCompat(compose.activity.window, compose.activity.window.decorView).isAppearanceLightNavigationBars)
        }
        compose.activityRule.scenario.recreate()
        compose.onNodeWithText("Olive Green").performScrollTo().assertIsSelected()
        compose.onNodeWithContentDescription("Dark mode").performScrollTo().assertIsOff()
        val saved = AppearancePreferences(InstrumentationRegistry.getInstrumentation().targetContext).load()
        org.junit.Assert.assertEquals(ThemePalette.OliveGreen, saved.palette)
        org.junit.Assert.assertFalse(saved.dark)
        compose.onNodeWithText("Dark Red").performScrollTo().performClick().assertIsSelected()
        compose.onNodeWithText("Oxford Blue").performScrollTo().performClick().assertIsSelected()
        compose.onNodeWithContentDescription("Dark mode").performScrollTo().performClick()
        compose.onNodeWithText("Done").performScrollTo().performClick()
        compose.onNodeWithText("Welcome back.").performScrollTo().assertIsDisplayed()
    }
    @Test fun rejectedCredentialDisplaysSanitizedErrorWithRealHttp() {
        assumeTrue("Disposable HTTP helper must be explicitly provisioned", InstrumentationRegistry.getArguments().getString("adaHttpIntegration") == "true")
        compose.onNodeWithText("ADA server URL").performScrollTo().performTextInput("http://10.0.2.2:18764")
        compose.onNodeWithTag("connect-legacy").performScrollTo().performClick()
        compose.onNodeWithText("Bearer token").performScrollTo().performTextInput("invalid-test-only")
        compose.onNodeWithText("Connect").performScrollTo().performClick()
        compose.waitUntil(timeoutMillis = 15_000) {
            compose.onAllNodes(androidx.compose.ui.test.hasText("The token was rejected. Enter a current token and connect again.")).fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("The token was rejected. Enter a current token and connect again.").performScrollTo().assertIsDisplayed()
    }
}
