package house.anderson.amigos

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

class AmigosNotificationListener : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val extras = sbn.notification.extras
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString()
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString()

        val deviceEvent = DeviceEvent(
            source = "notification",
            packageName = sbn.packageName,
            title = title,
            text = text
        )
        EventStore.record(this, deviceEvent)
        DeviceEventBus.publish(deviceEvent)
    }
}
