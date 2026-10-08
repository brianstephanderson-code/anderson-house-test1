package house.anderson.amigos.updater

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class PackageReplacedReceiver : BroadcastReceiver() {
    companion object {
        private const val TARGET_PACKAGE = "house.anderson.amigos"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_PACKAGE_REPLACED) return
        if (intent.data?.schemeSpecificPart != TARGET_PACKAGE) return
        if (!UpdaterState.isArmed(context)) return

        UpdaterState.markInstalled(context)

        try {
            context.packageManager.getLaunchIntentForPackage(TARGET_PACKAGE)?.let {
                it.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(it)
                UpdaterState.clear(context, "GREEN: Device Agent updated and relaunched")
            }
        } catch (t: Throwable) {
            UpdaterState.note(context, "Installed. Waiting for installer Open button.")
        }
    }
}
