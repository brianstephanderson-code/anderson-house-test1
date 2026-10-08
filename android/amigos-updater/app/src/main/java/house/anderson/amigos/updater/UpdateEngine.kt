package house.anderson.amigos.updater

import android.content.Context
import android.content.Intent
import android.content.pm.PackageInfo
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import androidx.core.content.FileProvider
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

object UpdateEngine {
    const val TARGET_PACKAGE = "house.anderson.amigos"
    const val APK_URL = "https://github.com/brianstephanderson-code/anderson-house-test1/releases/download/three-amigos-device-agent-latest/three-amigos-device-agent.apk"
    const val SHA_URL = "$APK_URL.sha256"

    sealed class CheckResult {
        data class Ready(val version: Long) : CheckResult()
        data class UpToDate(val version: Long) : CheckResult()
    }

    fun checkAndDownload(context: Context): CheckResult {
        val dir = File(context.cacheDir, "updates").apply { mkdirs() }
        val apk = File(dir, "device-agent-update.apk")
        val shaFile = File(dir, "device-agent-update.apk.sha256")

        downloadTo(SHA_URL, shaFile)
        downloadTo(APK_URL, apk)

        val expected = shaFile.readText().trim().substringBefore(" ").lowercase()
        val actual = sha256(apk.readBytes())
        require(expected == actual) { "SHA-256 mismatch" }

        val archive = context.packageManager.getPackageArchiveInfo(
            apk.absolutePath,
            PackageManager.GET_SIGNING_CERTIFICATES
        ) ?: error("Downloaded file is not a readable APK")

        require(archive.packageName == TARGET_PACKAGE) { "Wrong APK package: ${archive.packageName}" }

        val installed = context.packageManager.getPackageInfo(
            TARGET_PACKAGE,
            PackageManager.GET_SIGNING_CERTIFICATES
        )

        val archiveCerts = archive.signingInfo?.apkContentsSigners.orEmpty()
            .map { sha256(it.toByteArray()) }.toSet()
        val installedCerts = installed.signingInfo?.apkContentsSigners.orEmpty()
            .map { sha256(it.toByteArray()) }.toSet()

        require(archiveCerts.isNotEmpty() && archiveCerts == installedCerts) {
            "APK signing certificate does not match installed Device Agent"
        }

        val remoteVersion = versionCode(archive)
        val installedVersion = versionCode(installed)

        return if (remoteVersion > installedVersion) {
            UpdaterState.markReady(context, remoteVersion)
            CheckResult.Ready(remoteVersion)
        } else {
            CheckResult.UpToDate(installedVersion)
        }
    }

    fun launchReadyInstaller(context: Context) {
        require(context.packageManager.canRequestPackageInstalls()) {
            "Install unknown apps permission is not enabled"
        }

        val apk = File(File(context.cacheDir, "updates"), "device-agent-update.apk")
        require(apk.isFile && apk.length() > 0L) { "No verified update is cached" }

        val archive = context.packageManager.getPackageArchiveInfo(
            apk.absolutePath,
            PackageManager.GET_SIGNING_CERTIFICATES
        ) ?: error("Cached update is not a readable APK")

        val installed = context.packageManager.getPackageInfo(
            TARGET_PACKAGE,
            PackageManager.GET_SIGNING_CERTIFICATES
        )

        val archiveCerts = archive.signingInfo?.apkContentsSigners.orEmpty()
            .map { sha256(it.toByteArray()) }.toSet()
        val installedCerts = installed.signingInfo?.apkContentsSigners.orEmpty()
            .map { sha256(it.toByteArray()) }.toSet()
        require(archive.packageName == TARGET_PACKAGE && archiveCerts == installedCerts) {
            "Cached APK verification failed"
        }

        UpdaterState.arm(
            context,
            "INSTALLING…",
            installed.lastUpdateTime,
            versionCode(archive)
        )

        val uri = FileProvider.getUriForFile(context, "${context.packageName}.files", apk)
        val install = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(install)
    }

    fun installedVersion(context: Context): Long =
        versionCode(context.packageManager.getPackageInfo(TARGET_PACKAGE, 0))

    fun versionCode(info: PackageInfo): Long =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) info.longVersionCode
        else @Suppress("DEPRECATION") info.versionCode.toLong()

    private fun downloadTo(url: String, file: File) {
        val connection = URL(url).openConnection() as HttpURLConnection
        connection.instanceFollowRedirects = true
        connection.connectTimeout = 15000
        connection.readTimeout = 60000
        connection.setRequestProperty("User-Agent", "AmigosUpdater/4")
        connection.connect()
        require(connection.responseCode in 200..299) { "HTTP ${connection.responseCode}" }
        connection.inputStream.use { input ->
            file.outputStream().use { output -> input.copyTo(output) }
        }
        connection.disconnect()
    }

    fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
