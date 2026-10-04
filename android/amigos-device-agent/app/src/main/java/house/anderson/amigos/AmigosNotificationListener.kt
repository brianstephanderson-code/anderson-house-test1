package house.anderson.amigos

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

class AmigosNotificationListener : NotificationListenerService() {
    private val activeNavigationKeys = mutableSetOf<String>()

    override fun onListenerConnected() {
        super.onListenerConnected()
        AppContextHolder.context = applicationContext
    }

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
        LocalBridgeSender.send(deviceEvent)
        DeviceEventBus.publish(deviceEvent)

        if (NavigationStateStore.isNavigationPackage(sbn.packageName)) {
            activeNavigationKeys += sbn.key
            AppContextHolder.context = applicationContext
            LocationTracker.start(this)
            val nav = NavigationStateStore.fromNotification(sbn)
            NavigationStateStore.record(this, nav)
            val navEvent = DeviceEvent(
                source = "navigation",
                packageName = sbn.packageName,
                title = "navigation_state",
                text = nav.compact()
            )
            LocalBridgeSender.send(navEvent)
            DeviceEventBus.publish(navEvent)
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification) {
        if (!NavigationStateStore.isNavigationPackage(sbn.packageName)) return
        activeNavigationKeys -= sbn.key
        if (activeNavigationKeys.isEmpty()) {
            LocationTracker.stop()
        }
    }
}
