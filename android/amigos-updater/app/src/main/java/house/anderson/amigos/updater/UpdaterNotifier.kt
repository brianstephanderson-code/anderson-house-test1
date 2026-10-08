package house.anderson.amigos.updater

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat

object UpdaterNotifier {
    private const val CHANNEL_ID = "amigos_updater_status"
    private const val NOTIFY_ID = 7001

    fun ensureChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = context.getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "Amigos Updater", NotificationManager.IMPORTANCE_DEFAULT)
            )
        }
    }

    fun status(context: Context, message: String) {
        ensureChannel(context)
        val manager = context.getSystemService(NotificationManager::class.java)
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_download_done)
            .setContentTitle("Amigos Updater")
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setAutoCancel(false)
            .build()
        manager.notify(NOTIFY_ID, notification)
    }

    fun updateReady(context: Context, version: Long) {
        ensureChannel(context)
        val intent = Intent(context, MainActivity::class.java).apply {
            action = MainActivity.ACTION_INSTALL_READY
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        val pending = PendingIntent.getActivity(
            context,
            41,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val message = "UPDATE READY ✅ — Device Agent $version"
        val manager = context.getSystemService(NotificationManager::class.java)
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_download_done)
            .setContentTitle("Amigos Updater")
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText("$message\nTap once to install."))
            .setContentIntent(pending)
            .setAutoCancel(false)
            .build()
        manager.notify(NOTIFY_ID, notification)
    }
}
