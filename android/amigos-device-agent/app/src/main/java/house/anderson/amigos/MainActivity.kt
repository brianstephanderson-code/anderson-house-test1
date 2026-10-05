package house.anderson.amigos

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.os.Handler
import android.os.Looper

class MainActivity : Activity() {
    companion object {
        private const val REQ_MIC = 301
        private const val REQ_LOCATION = 302
        private const val REQ_FILE_TREE = 303
    }

    private lateinit var proofText: TextView
    private lateinit var fileQuery: EditText
    private lateinit var fileResults: TextView
    private val ui = Handler(Looper.getMainLooper())
    private val ticker = object : Runnable {
        override fun run() {
            if (::proofText.isInitialized) refreshProof()
            ui.postDelayed(this, 1000L)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "Three Amigos Device Agent\n\nOpen Sesame now uses Text Radio: wake, dictate, send, hear reply, sleep."
            textSize = 20f
        })

        layout.addView(Button(this).apply {
            text = "1. Enable Accessibility Service"
            setOnClickListener { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }
        })

        layout.addView(Button(this).apply {
            text = "2. Enable Notification Access"
            setOnClickListener { startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)) }
        })

        layout.addView(Button(this).apply {
            text = "3. Allow hands-free wake launch"
            setOnClickListener {
                startActivity(
                    Intent(
                        Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:$packageName")
                    )
                )
            }
        })

        layout.addView(Button(this).apply {
            text = "4. Start Open Sesame"
            setOnClickListener { ensureReadyAndStart() }
        })

        layout.addView(Button(this).apply {
            text = "5. Enable GPS for navigation"
            setOnClickListener {
                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(
                        arrayOf(
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                        ),
                        REQ_LOCATION
                    )
                } else {
                    startWakeService()
                    refreshProof()
                }
            }
        })

        layout.addView(Button(this).apply {
            text = "6. Choose searchable phone folder"
            setOnClickListener { chooseFileTree() }
        })

        fileQuery = EditText(this).apply {
            hint = "Search chosen folder, e.g. nicotine"
            setSingleLine(true)
        }
        layout.addView(fileQuery)

        layout.addView(Button(this).apply {
            text = "Search chosen folder"
            setOnClickListener { runPhoneFileSearch() }
        })

        fileResults = TextView(this).apply {
            textSize = 16f
            setPadding(0, 20, 0, 20)
            text = "PHONE FILE SEARCH\nChoose a folder, then enter a word or phrase."
        }
        layout.addView(fileResults)

        layout.addView(Button(this).apply {
            text = "Stop Open Sesame"
            setOnClickListener {
                startService(Intent(this@MainActivity, WakeService::class.java).setAction(WakeService.ACTION_STOP))
                refreshProof()
            }
        })

        proofText = TextView(this).apply {
            textSize = 18f
            setPadding(0, 36, 0, 20)
        }
        layout.addView(proofText)

        layout.addView(Button(this).apply {
            text = "Refresh Proof"
            setOnClickListener { refreshProof() }
        })

        val scroll = ScrollView(this).apply { addView(layout) }
        setContentView(scroll)
        refreshProof()
    }

    override fun onResume() {
        super.onResume()
        if (::proofText.isInitialized) refreshProof()
        ui.removeCallbacks(ticker)
        ui.post(ticker)
    }

    override fun onPause() {
        ui.removeCallbacks(ticker)
        super.onPause()
    }

    private fun chooseFileTree() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE).apply {
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
            addFlags(Intent.FLAG_GRANT_PREFIX_URI_PERMISSION)
        }
        startActivityForResult(intent, REQ_FILE_TREE)
    }

    @Deprecated("Kept for Android 11 compatibility in this small standalone Activity")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQ_FILE_TREE && resultCode == RESULT_OK) {
            val uri = data?.data ?: return
            try {
                PhoneFileAccess.grant(this, uri, data.flags)
                fileResults.text = "Folder granted. You can search it now."
            } catch (t: Throwable) {
                fileResults.text = "Could not keep folder permission: ${t.message ?: "unknown error"}"
            }
            refreshProof()
        }
    }

    private fun runPhoneFileSearch() {
        val query = fileQuery.text?.toString().orEmpty().trim()
        if (query.isEmpty()) {
            fileResults.text = "Type a word or phrase first."
            return
        }

        fileResults.text = "Searching..."
        Thread {
            val result = PhoneFileSearch.search(this, query)
            runOnUiThread { fileResults.text = result }
        }.start()
    }

    private fun ensureReadyAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            startActivity(
                Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:$packageName")
                )
            )
            return
        }

        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), REQ_MIC)
            return
        }
        startWakeService()
    }

    private fun startWakeService() {
        val i = Intent(this, WakeService::class.java).setAction(WakeService.ACTION_START)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(i) else startService(i)
        proofText.postDelayed({ refreshProof() }, 1000L)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQ_MIC && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            startWakeService()
        }
        if (requestCode == REQ_LOCATION && grantResults.any { it == PackageManager.PERMISSION_GRANTED }) {
            startWakeService()
            refreshProof()
        }
    }

    private fun refreshProof() {
        proofText.text =
            "LIVE PROOF\n\n" +
            EventStore.snapshot(this) +
            "\n\n" +
            WakeWordStore.snapshot(this) +
            "\n\n" + TextRadioStore.snapshot(this) +
            "\nWake launch allowed: " + Settings.canDrawOverlays(this) +
            "\n\n" + BootProof.snapshot(this) +
            "\n\n" + NavigationStateStore.snapshot(this) +
            "\n\n" + LocationTracker.snapshot(this) +
            "\n\n" + PhoneFileAccess.snapshot(this)
    }
}
