package house.anderson.amigos.updater

import android.content.Context

object UpdaterState {
    private const val PREFS = "amigos_updater"
    private const val KEY_ARMED = "armed"
    private const val KEY_PHASE = "phase"
    private const val KEY_STATUS = "status"

    fun arm(context: Context, status: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putBoolean(KEY_ARMED, true)
            .putString(KEY_PHASE, "installing")
            .putString(KEY_STATUS, status)
            .apply()
    }

    fun isArmed(context: Context): Boolean =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_ARMED, false)

    fun phase(context: Context): String =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY_PHASE, "idle") ?: "idle"

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
