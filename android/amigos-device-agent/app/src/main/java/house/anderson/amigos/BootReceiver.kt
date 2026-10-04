package house.anderson.amigos

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.provider.Settings

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        val action = intent?.action ?: return
        if (action != Intent.ACTION_BOOT_COMPLETED &&
            action != Intent.ACTION_LOCKED_BOOT_COMPLETED) return

        BootProof.recordBootSeen(context, action)

        if (!WakeService.isArmed(context)) return
        if (context.checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) return
        if (!Settings.canDrawOverlays(context)) return

        try {
            context.startActivity(
                Intent(context, BootShimActivity::class.java)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            )
            BootProof.recordShimStart(context)
        } catch (_: Throwable) {
            BootProof.recordShimError(context)
        }
    }
}

object BootProof {
    private const val PREFS = "open_sesame_boot"

    private fun p(context: Context) =
        context.createDeviceProtectedStorageContext()
            .getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun recordBootSeen(context: Context, action: String) {
        val p = p(context)
        p.edit()
            .putLong("boot_seen_count", p.getLong("boot_seen_count", 0L) + 1L)
            .putString("last_boot_action", action)
            .apply()
    }

    fun recordShimStart(context: Context) {
        val p = p(context)
        p.edit().putLong("shim_start_count", p.getLong("shim_start_count", 0L) + 1L).apply()
    }

    fun recordShimError(context: Context) {
        val p = p(context)
        p.edit().putLong("shim_error_count", p.getLong("shim_error_count", 0L) + 1L).apply()
    }

    fun snapshot(context: Context): String {
        val p = p(context)
        return "Start at boot armed: " + WakeService.isArmed(context) + "\n" +
            "Boot broadcasts seen: " + p.getLong("boot_seen_count", 0L) + "\n" +
            "Boot shim starts: " + p.getLong("shim_start_count", 0L) + "\n" +
            "Boot shim errors: " + p.getLong("shim_error_count", 0L)
    }
}
