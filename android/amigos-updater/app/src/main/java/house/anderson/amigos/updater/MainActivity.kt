package house.anderson.amigos.updater

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.FileProvider
import java.io.File
import java.security.MessageDigest

class MainActivity : Activity() {
    companion object {
        private const val PICK_APK = 401
        private const val TARGET_PACKAGE = "house.anderson.amigos"
    }

    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "Amigos Updater — installer proof v1\n\nThis helper will only arm itself for a verified Three Amigos Device Agent APK."
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
            text = "3. Pick Device Agent APK"
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
        refresh()
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

            if (!packageManager.canRequestPackageInstalls()) {
                UpdaterState.note(this, "Allow installs from this source, then pick the APK again")
                startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
                refresh()
                return
            }

            UpdaterState.arm(this, "Verified Device Agent APK. Installer launched.")
            val uri = FileProvider.getUriForFile(this, "$packageName.files", apk)
            val install = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(install)
            refresh()
        } catch (t: Throwable) {
            UpdaterState.clear(this, "REJECTED: ${t.message ?: t.javaClass.simpleName}")
            refresh()
        }
    }

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    private fun refresh() {
        if (!::status.isInitialized) return
        status.text =
            "STATUS\n" +
            "Armed: ${UpdaterState.isArmed(this)}\n" +
            "Phase: ${UpdaterState.phase(this)}\n" +
            UpdaterState.status(this)
    }
}
