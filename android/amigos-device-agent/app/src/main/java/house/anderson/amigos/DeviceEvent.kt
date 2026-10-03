package house.anderson.amigos

import android.content.Context

data class DeviceEvent(
    val source: String,
    val packageName: String,
    val title: String? = null,
    val text: String? = null,
    val whenMs: Long = System.currentTimeMillis()
)

object DeviceEventBus {
    private val listeners = mutableSetOf<(DeviceEvent) -> Unit>()

    @Synchronized fun subscribe(listener: (DeviceEvent) -> Unit) { listeners += listener }
    @Synchronized fun unsubscribe(listener: (DeviceEvent) -> Unit) { listeners -= listener }

    @Synchronized fun publish(event: DeviceEvent) {
        listeners.toList().forEach { it(event) }
    }
}

object EventStore {
    private const val PREFS = "amigos_event_store"

    fun record(context: Context, event: DeviceEvent) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val countKey = if (event.source == "notification") "notification_count" else "accessibility_count"
        val next = prefs.getLong(countKey, 0L) + 1L
        prefs.edit()
            .putLong(countKey, next)
            .putString("last_source", event.source)
            .putString("last_package", event.packageName)
            .putLong("last_when", event.whenMs)
            .apply()
    }

    fun snapshot(context: Context): String {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val accessibility = prefs.getLong("accessibility_count", 0L)
        val notifications = prefs.getLong("notification_count", 0L)
        val source = prefs.getString("last_source", "none") ?: "none"
        val pkg = prefs.getString("last_package", "none") ?: "none"

        return "Accessibility events: $accessibility\n" +
            "Notification events: $notifications\n" +
            "Last event: $source\n" +
            "Last app: $pkg"
    }
}
