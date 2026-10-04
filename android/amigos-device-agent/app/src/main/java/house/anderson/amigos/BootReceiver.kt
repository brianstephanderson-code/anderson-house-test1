package house.anderson.amigos

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        val prefs = context.getSharedPreferences("open_sesame_boot", Context.MODE_PRIVATE)
        prefs.edit()
            .putLong("last_boot_seen_ms", System.currentTimeMillis())
            .putLong("boot_seen_count", prefs.getLong("boot_seen_count", 0L) + 1L)
            .apply()

        if (!WakeService.isArmed(context)) return
        if (context.checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) return

        try {
            val service = Intent(context, WakeService::class.java).setAction(WakeService.ACTION_START)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) context.startForegroundService(service)
            else context.startService(service)

            prefs.edit()
                .putLong("last_boot_start_ms", System.currentTimeMillis())
                .putLong("boot_start_count", prefs.getLong("boot_start_count", 0L) + 1L)
                .apply()
        } catch (_: Throwable) {
            prefs.edit()
                .putLong("boot_start_error_count", prefs.getLong("boot_start_error_count", 0L) + 1L)
                .apply()
        }
    }
}

object BootProof {
    fun snapshot(context: Context): String {
        val p = context.getSharedPreferences("open_sesame_boot", Context.MODE_PRIVATE)
        return "Start at boot armed: " + WakeService.isArmed(context) + "\n" +
            "Boot broadcasts seen: " + p.getLong("boot_seen_count", 0L) + "\n" +
            "Boot listener starts: " + p.getLong("boot_start_count", 0L) + "\n" +
            "Boot start errors: " + p.getLong("boot_start_error_count", 0L)
    }
}
