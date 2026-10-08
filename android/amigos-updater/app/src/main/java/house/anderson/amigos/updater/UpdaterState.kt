package house.anderson.amigos.updater

import android.content.Context

object UpdaterState {
    private const val PREFS = "amigos_updater"
    private const val KEY_ARMED = "armed"
    private const val KEY_PHASE = "phase"
    private const val KEY_STATUS = "status"
    private const val KEY_BASELINE_UPDATE_TIME = "baseline_update_time"
    private const val KEY_TARGET_VERSION = "target_version"

    fun arm(
        context: Context,
        status: String,
        baselineUpdateTime: Long,
        targetVersion: Long
    ) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putBoolean(KEY_ARMED, true)
            .putString(KEY_PHASE, "installing")
            .putString(KEY_STATUS, status)
            .putLong(KEY_BASELINE_UPDATE_TIME, baselineUpdateTime)
            .putLong(KEY_TARGET_VERSION, targetVersion)
            .apply()
    }

    fun isArmed(context: Context): Boolean =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_ARMED, false)

    fun phase(context: Context): String =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY_PHASE, "idle") ?: "idle"

    fun baselineUpdateTime(context: Context): Long =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getLong(KEY_BASELINE_UPDATE_TIME, 0L)

    fun targetVersion(context: Context): Long =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getLong(KEY_TARGET_VERSION, -1L)

    fun markInstalled(context: Context) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putString(KEY_PHASE, "installed")
            .putString(KEY_STATUS, "Device Agent replaced successfully")
            .apply()
    }

    fun clear(context: Context, status: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putBoolean(KEY_ARMED, false)
            .putString(KEY_PHASE, "idle")
            .putString(KEY_STATUS, status)
            .remove(KEY_BASELINE_UPDATE_TIME)
            .remove(KEY_TARGET_VERSION)
            .apply()
    }

    fun status(context: Context): String =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY_STATUS, "Ready") ?: "Ready"

    fun note(context: Context, status: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putString(KEY_STATUS, status)
            .apply()
    }
}
