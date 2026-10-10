import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.gradle.api.artifacts.result.UnresolvedDependencyResult

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
}

android {
    namespace = "dev.ada.assistant"
    compileSdk = 36
    buildToolsVersion = "35.0.0"
    defaultConfig {
        applicationId = "dev.ada.assistant"
        minSdk = 26
        targetSdk = 36
        versionCode = 5
        versionName = "0.9.0-entities"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    buildTypes {
        debug { applicationIdSuffix = ".debug" }
        release { isMinifyEnabled = false }
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    testOptions { unitTests.isReturnDefaultValues = true }
    sourceSets["test"].resources.srcDir("../../../contracts/fixtures")
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}

kotlin {
    jvmToolchain(21)
    compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
}

dependencyLocking { lockAllConfigurations() }

tasks.register("resolveAndLockAll") {
    doFirst {
        require(gradle.startParameter.isWriteDependencyLocks) { "Use --write-locks" }
        // Resolve dependency graphs, not ambiguous AGP artifact variants of the app itself.
        val variants = setOf(
            "debugCompileClasspath", "debugRuntimeClasspath", "debugUnitTestCompileClasspath",
            "debugUnitTestRuntimeClasspath", "debugAndroidTestCompileClasspath", "debugAndroidTestRuntimeClasspath",
            "releaseCompileClasspath", "releaseRuntimeClasspath", "releaseUnitTestCompileClasspath", "releaseUnitTestRuntimeClasspath",
        )
        configurations.filter { it.isCanBeResolved && it.name in variants }.forEach { configuration ->
            val graph = configuration.incoming.resolutionResult
            graph.allComponents
            graph.allDependencies.filterIsInstance<UnresolvedDependencyResult>().firstOrNull()?.let {
                throw it.failure
            }
        }
    }
}

dependencies {
    implementation(libs.androidx.core)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.lifecycle.viewmodel)
    implementation(libs.androidx.lifecycle.compose)
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.ui.tooling.preview)
    implementation(libs.compose.material3)
    implementation(libs.coroutines)
    implementation(libs.serialization)
    implementation(libs.okhttp)
    debugImplementation(libs.compose.ui.tooling)
    debugImplementation(libs.compose.ui.test.manifest)
    testImplementation(libs.junit)
    testImplementation(libs.mockwebserver)
    testImplementation(libs.coroutines.test)
    androidTestImplementation(platform(libs.compose.bom))
    androidTestImplementation(libs.compose.ui.test)
    androidTestImplementation(libs.androidx.test.junit)
    androidTestImplementation(libs.androidx.test.runner)
    // 3.7 uses public InputManager APIs; Compose's transitive 3.5 fails on modern Android.
    androidTestImplementation(libs.androidx.test.espresso)
}
