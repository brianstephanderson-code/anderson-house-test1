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
        private const val REQ_LOCATION = 302
        private const val REQ_VISION_CAMERA = 303
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
            text = "6. Test Vision Eye"
            setOnClickListener {
                startActivity(Intent(this@MainActivity, VisionCaptureActivity::class.java))
            }
        })

        layout.addView(Button(this).apply {
            text = "7. Start Vision Endpoint"
            setOnClickListener { ensureVisionEndpointStarted() }
        })

        layout.addView(Button(this).apply {
            text = "8. Stop Vision Endpoint"
            setOnClickListener {
                startService(
                    Intent(this@MainActivity, VisionEndpointService::class.java)
                        .setAction(VisionEndpointService.ACTION_STOP)
                )
            }
        })

        layout.addView(Button(this).apply {
            text = "9. Barge-In REPLAY"
            setOnClickListener {
                startActivity(Intent(this@MainActivity, BargeInReplayActivity::class.java))
            }
        })

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

    private fun ensureVisionEndpointStarted() {
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.CAMERA), REQ_VISION_CAMERA)
            return
        }
        val i = Intent(this, VisionEndpointService::class.java)
            .setAction(VisionEndpointService.ACTION_START)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(i) else startService(i)
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
        if (requestCode == REQ_VISION_CAMERA && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            ensureVisionEndpointStarted()
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
            "\n\n" + LocationTracker.snapshot(this)
    }
}
