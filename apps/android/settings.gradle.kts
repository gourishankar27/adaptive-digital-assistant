pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "AdaAndroid"
check(JavaVersion.current() == JavaVersion.VERSION_21) {
    "Use the pinned JDK 21 runtime (.java-version); Android Studio's default JBR may differ."
}
include(":app")
include(":focus-fixture")
