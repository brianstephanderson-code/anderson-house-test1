package house.anderson.amigos

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var proofText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "Three Amigos Device Agent\n\nEnable both switches once. No Shizuku required."
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

        proofText = TextView(this).apply {
            textSize = 18f
            setPadding(0, 36, 0, 20)
        }
        layout.addView(proofText)

        layout.addView(Button(this).apply {
            text = "Refresh Proof"
            setOnClickListener { refreshProof() }
        })

        setContentView(layout)
        refreshProof()
    }

    override fun onResume() {
        super.onResume()
        if (::proofText.isInitialized) refreshProof()
    }

    private fun refreshProof() {
        proofText.text = "LIVE PROOF\n\n" + EventStore.snapshot(this)
    }
}
