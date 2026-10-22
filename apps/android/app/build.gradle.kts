import java.security.MessageDigest
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
        val validationId = providers.gradleProperty("adaValidationApplicationId").orNull
        require(validationId == null || validationId.matches(Regex("dev\\.ada\\.validation\\.[a-z][a-z0-9_]{0,30}"))) {
            "Validation builds must use a separate dev.ada.validation.* application ID"
        }
        applicationId = validationId ?: "dev.ada.assistant"
        manifestPlaceholders["adaAppLabel"] = if (validationId == null) "ADA" else "ADA validation"
        minSdk = 26
        targetSdk = 36
        versionCode = 25
        versionName = "0.31.0-documents-drafts"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    val edgeNativeDir = providers.gradleProperty("adaEdgeNativeDir").orNull
    defaultConfig.buildConfigField("boolean", "EDGE_RUNTIME", if(edgeNativeDir == null) "false" else "true")
    if(edgeNativeDir != null) {
        val nativeRoot = file(edgeNativeDir)
        val library = nativeRoot.resolve("arm64-v8a/libada_edge.so")
        require(library.isFile && nativeRoot.resolve("runtime-manifest.json").isFile) { "Build the verified optional native runtime first" }
        val manifest = groovy.json.JsonSlurper().parse(nativeRoot.resolve("runtime-manifest.json")) as Map<*, *>
        val digest = MessageDigest.getInstance("SHA-256").digest(library.readBytes()).joinToString("") { "%02x".format(it) }
        require(manifest["runtime"] == "llama.cpp-620d2225cc436ab0b001e3200e590e3b286ef9ab" && manifest["library_sha256"] == digest && manifest["abi"] == "arm64-v8a") { "Optional native library or runtime manifest changed" }
        require(manifest["version"] == "ada-edge-native-v1" && manifest["source_archive_sha256"] == "1d4a987d9bd048f6e93107e838026438df70fbde237fc0c69c63d600512b4bd9" && manifest["ndk"] == "30.0.16248370" && (manifest["minimum_load_alignment"] as? Number)?.toLong()?.let { it >= 16384 } == true) { "Optional native build provenance is incomplete" }
        val inputs = manifest["files"] as Map<*, *>
        for(name in listOf("ops/edge-runtime/native.cpp", "ops/edge-runtime/CMakeLists.txt")) {
            val source = rootProject.file("../../$name").readText().replace("\r\n", "\n").toByteArray()
            require(inputs[name] == MessageDigest.getInstance("SHA-256").digest(source).joinToString("") { "%02x".format(it) }) { "Rebuild the optional native runtime after source edits" }
        }
        sourceSets["main"].jniLibs.srcDir(nativeRoot)
        require(nativeRoot.resolve("notices/ada-edge-third-party.txt").isFile) { "Native source license notices are required" }
        sourceSets["main"].assets.srcDir(nativeRoot.resolve("notices"))
        defaultConfig.ndk.abiFilters.add("arm64-v8a")
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
