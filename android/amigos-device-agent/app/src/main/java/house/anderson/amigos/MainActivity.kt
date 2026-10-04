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
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.ScrollView
import android.os.Handler
import android.os.Looper

class MainActivity : Activity() {
    companion object {
        private const val REQ_MIC = 301
    }

    private lateinit var proofText: TextView
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
            text = "Three Amigos Device Agent\n\nEnable the Android switches once, allow wake launch, then arm Hey Tomo."
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
            text = "3. Allow Hey Tomo to open Voice"
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
            text = "4. Start Hey Tomo"
            setOnClickListener { ensureReadyAndStart() }
        })

        layout.addView(Button(this).apply {
            text = "Stop Hey Tomo"
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
    }

    private fun refreshProof() {
        proofText.text =
            "LIVE PROOF\n\n" +
            EventStore.snapshot(this) +
            "\n\n" +
            WakeWordStore.snapshot(this) +
            "\nWake launch allowed: " + Settings.canDrawOverlays(this)
    }
}
