package house.anderson.amigos

import android.app.Notification
import android.content.Context
import android.os.Bundle
import android.service.notification.StatusBarNotification

data class NavigationSnapshot(
    val appPackage: String,
    val title: String?,
    val text: String?,
    val bigText: String?,
    val subText: String?,
    val infoText: String?,
    val whenMs: Long
) {
    fun bestInstruction(): String? =
        sequenceOf(text, bigText, title, subText, infoText)
            .mapNotNull { it?.trim()?.takeIf(String::isNotEmpty) }
            .firstOrNull()

    fun compact(): String {
        val pieces = linkedSetOf<String>()
        listOf(title, text, bigText, subText, infoText).forEach {
            val v = it?.trim()
            if (!v.isNullOrEmpty()) pieces += v
        }
        return pieces.joinToString(" | ").take(600)
    }
}

object NavigationStateStore {
    private const val PREFS = "navigation_state"

    private val navigationPackages = setOf(
        "com.google.android.apps.maps",
        "com.waze"
    )

    fun isNavigationPackage(packageName: String): Boolean =
        packageName in navigationPackages

    fun fromNotification(sbn: StatusBarNotification): NavigationSnapshot {
        val e: Bundle = sbn.notification.extras
        return NavigationSnapshot(
            appPackage = sbn.packageName,
            title = e.getCharSequence(Notification.EXTRA_TITLE)?.toString(),
            text = e.getCharSequence(Notification.EXTRA_TEXT)?.toString(),
            bigText = e.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString(),
            subText = e.getCharSequence(Notification.EXTRA_SUB_TEXT)?.toString(),
            infoText = e.getCharSequence(Notification.EXTRA_INFO_TEXT)?.toString(),
            whenMs = System.currentTimeMillis()
        )
    }

    fun record(context: Context, snap: NavigationSnapshot) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putString("package", snap.appPackage)
            .putString("instruction", snap.bestInstruction())
            .putString("compact", snap.compact())
            .putLong("when_ms", snap.whenMs)
            .putLong("count",
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                    .getLong("count", 0L) + 1L
            )
            .apply()
    }

    fun snapshot(context: Context): String {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val count = p.getLong("count", 0L)
        val pkg = p.getString("package", "none") ?: "none"
        val instruction = p.getString("instruction", "none") ?: "none"
        return "NAVIGATION PROOF\n" +
            "Navigation updates: $count\n" +
            "Navigation app: $pkg\n" +
            "Latest instruction: $instruction\n" +
            "Companion: " + LocationTracker.privateSummary(context)
    }
}
