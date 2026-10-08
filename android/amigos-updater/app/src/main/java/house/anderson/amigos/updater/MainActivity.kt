package house.anderson.amigos.updater

import android.app.Activity
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.content.pm.PackageInfo
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.app.NotificationCompat
import androidx.core.content.FileProvider
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

class MainActivity : Activity() {
    companion object {
        private const val PICK_APK = 401
        private const val TARGET_PACKAGE = "house.anderson.amigos"
        private const val APK_URL = "https://github.com/brianstephanderson-code/anderson-house-test1/releases/download/three-amigos-device-agent-latest/three-amigos-device-agent.apk"
        private const val SHA_URL = "$APK_URL.sha256"
        private const val CHANNEL_ID = "amigos_updater_status"
        private const val NOTIFY_ID = 7001
    }

    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createNotificationChannel()

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "Amigos Updater — installer proof v3\n\nDownloads and verifies the latest signed Three Amigos Device Agent directly from GitHub."
            textSize = 20f
        })

        layout.addView(Button(this).apply {
            text = "1. Enable Updater Accessibility"
            setOnClickListener { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }
        })

        layout.addView(Button(this).apply {
            text = "2. Allow Install Unknown Apps"
            setOnClickListener {
                startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
            }
        })

        layout.addView(Button(this).apply {
            text = "3. DOWNLOAD LATEST DEVICE AGENT"
            setOnClickListener { downloadLatestAndInstall() }
        })

        layout.addView(Button(this).apply {
            text = "Manual fallback: Pick Device Agent APK"
            setOnClickListener {
                val i = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "application/vnd.android.package-archive"
                }
                startActivityForResult(i, PICK_APK)
            }
        })

        layout.addView(Button(this).apply {
            text = "DISARM"
            setOnClickListener {
                UpdaterState.clear(this@MainActivity, "Disarmed")
                refresh()
            }
        })

        status = TextView(this).apply {
            textSize = 18f
            setPadding(0, 40, 0, 20)
        }
        layout.addView(status)
        setContentView(layout)
        refresh()
    }

    override fun onResume() {
        super.onResume()
        verifyCompletedInstall()
        refresh()
    }

    private fun downloadLatestAndInstall() {
        if (!packageManager.canRequestPackageInstalls()) {
            UpdaterState.note(this, "Allow installs from this source first.")
            startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
            refresh()
            return
        }

        UpdaterState.note(this, "DOWNLOADING…")
        notifyStatus("DOWNLOADING…")
        refresh()

        Thread {
            try {
                val dir = File(cacheDir, "updates").apply { mkdirs() }
                val apk = File(dir, "device-agent-update.apk")
                val shaFile = File(dir, "device-agent-update.apk.sha256")

                downloadTo(APK_URL, apk)
                downloadTo(SHA_URL, shaFile)

                runOnUiThread {
                    UpdaterState.note(this, "DOWNLOADED — COMPLETE ✅")
                    notifyStatus("DOWNLOADED — COMPLETE ✅")
                    refresh()
                }

                val expected = shaFile.readText().trim().substringBefore(" ").lowercase()
                val actual = sha256(apk.readBytes())
                require(expected == actual) { "SHA-256 mismatch" }

                runOnUiThread {
                    UpdaterState.note(this, "VERIFIED ✅")
                    notifyStatus("VERIFIED ✅")
                    refresh()
                }

                verifyAndLaunch(apk)
            } catch (t: Throwable) {
                runOnUiThread {
                    UpdaterState.clear(this, "FAILED ❌\n${t.message ?: t.javaClass.simpleName}")
                    notifyStatus("FAILED ❌")
                    refresh()
                }
            }
        }.start()
    }

    @Deprecated("legacy result API is sufficient for Android 11 proof app")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != PICK_APK || resultCode != RESULT_OK) return
        val source = data?.data ?: return

        try {
            val dir = File(cacheDir, "updates").apply { mkdirs() }
            val apk = File(dir, "device-agent-update.apk")
            contentResolver.openInputStream(source).use { input ->
                requireNotNull(input) { "Could not open selected APK" }
                apk.outputStream().use { output -> input.copyTo(output) }
            }
            verifyAndLaunch(apk)
        } catch (t: Throwable) {
            UpdaterState.clear(this, "REJECTED: ${t.message ?: t.javaClass.simpleName}")
            refresh()
        }
    }

    private fun verifyAndLaunch(apk: File) {
        val archive = packageManager.getPackageArchiveInfo(
            apk.absolutePath,
            PackageManager.GET_SIGNING_CERTIFICATES
        ) ?: error("Selected file is not a readable APK")

        require(archive.packageName == TARGET_PACKAGE) {
            "Wrong APK package: ${archive.packageName}"
        }

        val installed = packageManager.getPackageInfo(
            TARGET_PACKAGE,
            PackageManager.GET_SIGNING_CERTIFICATES
        )

        val archiveCerts = archive.signingInfo?.apkContentsSigners.orEmpty().map { sha256(it.toByteArray()) }.toSet()
        val installedCerts = installed.signingInfo?.apkContentsSigners.orEmpty().map { sha256(it.toByteArray()) }.toSet()

        require(archiveCerts.isNotEmpty() && archiveCerts == installedCerts) {
            "APK signing certificate does not match the installed Device Agent"
        }

        UpdaterState.arm(
            this,
            "INSTALLING…",
            installed.lastUpdateTime,
            versionCode(archive)
        )

        notifyStatus("INSTALLING…")

        val uri = FileProvider.getUriForFile(this, "$packageName.files", apk)
        val install = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        startActivity(install)
        runOnUiThread { refresh() }
    }

    private fun verifyCompletedInstall() {
        if (!UpdaterState.isArmed(this)) return
        if (UpdaterState.phase(this) != "installing") return

        try {
            val installed = packageManager.getPackageInfo(TARGET_PACKAGE, 0)
            val baseline = UpdaterState.baselineUpdateTime(this)
            val targetVersion = UpdaterState.targetVersion(this)
            val installedVersion = versionCode(installed)

            val replaced = installed.lastUpdateTime > baseline
            val versionOkay = targetVersion < 0 || installedVersion >= targetVersion

            if (replaced && versionOkay) {
                UpdaterState.clear(
                    this,
                    "INSTALLED — GREEN ✅\nDevice Agent version $installedVersion is active."
                )
                notifyStatus("INSTALLED — GREEN ✅")
            }
        } catch (_: Throwable) {
        }
    }

    private fun downloadTo(url: String, file: File) {
        val connection = URL(url).openConnection() as HttpURLConnection
        connection.instanceFollowRedirects = true
        connection.connectTimeout = 15000
        connection.readTimeout = 30000
        connection.setRequestProperty("User-Agent", "AmigosUpdater/3")
        connection.connect()
        require(connection.responseCode in 200..299) { "HTTP ${connection.responseCode}" }
        connection.inputStream.use { input ->
            file.outputStream().use { output -> input.copyTo(output) }
        }
        connection.disconnect()
    }

    private fun versionCode(info: PackageInfo): Long =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) info.longVersionCode
        else @Suppress("DEPRECATION") info.versionCode.toLong()

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "Amigos Updater", NotificationManager.IMPORTANCE_DEFAULT)
            )
        }
    }

    private fun notifyStatus(message: String) {
        val manager = getSystemService(NotificationManager::class.java)
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_download_done)
            .setContentTitle("Amigos Updater")
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setAutoCancel(false)
            .build()
        manager.notify(NOTIFY_ID, notification)
    }

    private fun refresh() {
        if (!::status.isInitialized) return
        status.text =
            "STATUS\n" +
            "Armed: ${UpdaterState.isArmed(this)}\n" +
            "Phase: ${UpdaterState.phase(this)}\n" +
            UpdaterState.status(this)
    }
}
