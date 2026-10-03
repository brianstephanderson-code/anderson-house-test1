package house.anderson.amigos

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
