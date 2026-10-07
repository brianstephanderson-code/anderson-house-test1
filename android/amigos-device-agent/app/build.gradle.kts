plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "house.anderson.amigos"
    compileSdk = 35

    defaultConfig {
        applicationId = "house.anderson.amigos"
        minSdk = 30
        targetSdk = 35
        ndk { abiFilters += "arm64-v8a" }
        versionCode = (System.getenv("AMIGOS_VERSION_CODE") ?: "1007").toInt()
        versionName = System.getenv("AMIGOS_VERSION_NAME") ?: "replay-speakback-cleanreset-1"
    }

    signingConfigs {
        create("amigosRelease") {
            val ks = System.getenv("AMIGOS_KEYSTORE_PATH")
            if (!ks.isNullOrBlank()) {
                storeFile = file(ks)
                storePassword = System.getenv("AMIGOS_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("AMIGOS_KEY_ALIAS")
                keyPassword = System.getenv("AMIGOS_KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("amigosRelease")
            isMinifyEnabled = false
        }
    }

    androidResources {
        noCompress += listOf("onnx", "txt")
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}


dependencies {
    implementation(files("libs/sherpa-onnx-1.13.4-classes.jar"))
}
