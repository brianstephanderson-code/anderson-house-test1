package house.anderson.amigos

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

object LocalBridgeSender {
    private const val ENDPOINT = "http://127.0.0.1:8765/event"
    private val executor = Executors.newSingleThreadExecutor()
    private val lastAccessibilitySentMs = AtomicLong(0L)

    fun send(event: DeviceEvent) {
        if (event.source == "accessibility") {
            val now = System.currentTimeMillis()
            val previous = lastAccessibilitySentMs.get()
            if (now - previous < 300L) return
            if (!lastAccessibilitySentMs.compareAndSet(previous, now)) return
        }

        executor.execute {
            try {
                val payload = JSONObject().apply {
                    put("source", event.source)
                    put("packageName", event.packageName)
                    put("whenMs", event.whenMs)
                    if (event.source == "notification" || event.source == "navigation") {
                        if (event.title != null) put("title", event.title)
                        if (event.text != null) put("text", event.text)
                    }
                }.toString()

                val connection = (URL(ENDPOINT).openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = 1000
                    readTimeout = 1000
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=utf-8")
                    setFixedLengthStreamingMode(payload.toByteArray(Charsets.UTF_8).size)
                }

                connection.outputStream.use { out ->
                    out.write(payload.toByteArray(Charsets.UTF_8))
                }
                connection.inputStream.use { it.readBytes() }
                connection.disconnect()
            } catch (_: Exception) {
                // Local bridge may be restarting. EventStore remains the on-device proof.
            }
        }
    }
}
