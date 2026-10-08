package house.anderson.amigos.updater

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.net.Uri
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

class MainActivity : Activity() {
    companion object {
        const val ACTION_INSTALL_READY = "house.anderson.amigos.updater.INSTALL_READY"
        private const val PERIODIC_WORK = "amigos-device-agent-update-check"
    }

    private lateinit var status: TextView
    private lateinit var autoButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        UpdaterNotifier.ensureChannel(this)
        scheduleBackgroundChecks()

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "Amigos Updater — Brianless v4\n\nChecks GitHub automatically. One-tap install is the reliable lane; LAB AUTO tries zero-touch when Android permits it."
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
            text = "CHECK GITHUB NOW"
            setOnClickListener { checkNow() }
        })

        autoButton = Button(this).apply {
            setOnClickListener {
                val next = !UpdaterState.labAutoInstall(this@MainActivity)
                UpdaterState.setLabAutoInstall(this@MainActivity, next)
                refresh()
            }
        }
        layout.addView(autoButton)

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

        handleInstallIntent(intent)
        verifyCompletedInstall()
        refresh()
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleInstallIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        verifyCompletedInstall()
        refresh()
    }

    private fun scheduleBackgroundChecks() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val periodic = PeriodicWorkRequestBuilder<UpdateWorker>(15, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            PERIODIC_WORK,
            ExistingPeriodicWorkPolicy.UPDATE,
            periodic
        )
    }

    private fun checkNow() {
        UpdaterState.note(this, "CHECKING GITHUB…")
        refresh()

        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val request = OneTimeWorkRequestBuilder<UpdateWorker>()
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(this).enqueue(request)
    }

    private fun handleInstallIntent(intent: Intent?) {
        if (intent?.action != ACTION_INSTALL_READY) return
        try {
            UpdateEngine.launchReadyInstaller(this)
            UpdaterNotifier.status(this, "INSTALLING…")
        } catch (t: Throwable) {
            UpdaterState.note(this, "INSTALL FAILED ❌\n${t.message ?: t.javaClass.simpleName}")
        }
    }

    private fun verifyCompletedInstall() {
        if (!UpdaterState.isArmed(this)) return
        if (UpdaterState.phase(this) != "installing") return

        try {
            val installed = packageManager.getPackageInfo(UpdateEngine.TARGET_PACKAGE, 0)
            val baseline = UpdaterState.baselineUpdateTime(this)
            val targetVersion = UpdaterState.targetVersion(this)
            val installedVersion = UpdateEngine.versionCode(installed)

            if (installed.lastUpdateTime > baseline && installedVersion >= targetVersion) {
                UpdaterState.clear(
                    this,
                    "INSTALLED — GREEN ✅\nDevice Agent version $installedVersion is active."
                )
                UpdaterNotifier.status(this, "INSTALLED — GREEN ✅")
            }
        } catch (_: Throwable) {
        }
    }

    private fun refresh() {
        if (!::status.isInitialized) return
        autoButton.text =
            if (UpdaterState.labAutoInstall(this)) "LAB AUTO-INSTALL: ON"
            else "LAB AUTO-INSTALL: OFF"

        status.text =
            "STATUS\n" +
            "Armed: ${UpdaterState.isArmed(this)}\n" +
            "Phase: ${UpdaterState.phase(this)}\n" +
            "Installed Device Agent: ${runCatching { UpdateEngine.installedVersion(this) }.getOrDefault(-1L)}\n" +
            UpdaterState.status(this)
    }
}
