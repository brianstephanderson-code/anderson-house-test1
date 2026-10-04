package house.anderson.amigos

import android.app.Activity
import android.content.Intent
import android.os.Build
import android.os.Bundle

class BootShimActivity : Activity() {
    private var dispatched = false

    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        setShowWhenLocked(true)
        setTurnScreenOn(false)
        window.setBackgroundDrawableResource(android.R.color.transparent)
    }

    override fun onResume() {
        super.onResume()
        if (dispatched) return
        dispatched = true

        window.decorView.postDelayed({
            try {
                val service = Intent(this, WakeService::class.java)
                    .setAction(WakeService.ACTION_START)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(service)
                else startService(service)
            } catch (_: Throwable) {
                BootProof.recordShimError(this)
            } finally {
                window.decorView.postDelayed({ finish() }, 800L)
            }
        }, 300L)
    }
}
