import org.jetbrains.kotlin.gradle.dsl.JvmTarget
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}
android {
    namespace = "dev.ada.validation.focus"
    compileSdk = 36
    buildToolsVersion = "35.0.0"
    defaultConfig { applicationId = "dev.ada.validation.focus"; minSdk = 26; targetSdk = 36; versionCode = 1; versionName = "1" }
    buildTypes { debug { applicationIdSuffix = ".debug" }; release { isMinifyEnabled = false } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
}
kotlin { jvmToolchain(21); compilerOptions { jvmTarget.set(JvmTarget.JVM_17) } }
dependencyLocking { lockAllConfigurations() }
