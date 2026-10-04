package house.anderson.amigos

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.IBinder
import android.os.Process
import java.util.concurrent.atomic.AtomicBoolean

class WakeService : Service() {
    companion object {
        const val ACTION_START = "house.anderson.amigos.WAKE_START"
        const val ACTION_STOP = "house.anderson.amigos.WAKE_STOP"
        private const val CHANNEL_ID = "hey_tomo_listener"
        private const val NOTIFICATION_ID = 7311
        private const val PREFS = "hey_tomo"
        private const val KEY_ARMED = "armed"

        fun isArmed(context: android.content.Context): Boolean =
            context.getSharedPreferences(PREFS, MODE_PRIVATE).getBoolean(KEY_ARMED, false)
    }

    private val running = AtomicBoolean(false)
    private var thread: Thread? = null
    private var recorder: AudioRecord? = null
    private var engine: WakeEngine? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            setArmed(false)
            stopSelf()
            return START_NOT_STICKY
        }

        if (checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            stopSelf()
            return START_NOT_STICKY
        }

        setArmed(true)
        ensureChannel()
        startForeground(NOTIFICATION_ID, buildNotification())
        if (!running.get()) startListening()
        return START_STICKY
    }

    private fun setArmed(value: Boolean) {
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().putBoolean(KEY_ARMED, value).apply()
    }

    private fun ensureChannel() {
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ID,
                "Hey Tomo listener",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Local wake-word listener for Hey Tomo"
                setShowBadge(false)
            }
        )
    }

    private fun buildNotification(): Notification {
        val open = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val stop = PendingIntent.getService(
            this, 1,
            Intent(this, WakeService::class.java).setAction(ACTION_STOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        return Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("Hey Tomo is listening")
            .setContentText("Wake phrase: Hey Tomo")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .setContentIntent(open)
            .addAction(Notification.Action.Builder(null, "Stop", stop).build())
            .setCategory(Notification.CATEGORY_SERVICE)
            .setVisibility(Notification.VISIBILITY_PRIVATE)
            .build()
    }

    private fun startListening() {
        running.set(true)
        thread = Thread({
            Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO)
            try {
                val localEngine = WakeEngine(assets)
                localEngine.start()
                engine = localEngine

                val sampleRate = 16000
                val min = AudioRecord.getMinBufferSize(
                    sampleRate,
                    AudioFormat.CHANNEL_IN_MONO,
                    AudioFormat.ENCODING_PCM_16BIT
                )
                val bufferSize = maxOf(min, 3200)
                val localRecorder = AudioRecord(
                    MediaRecorder.AudioSource.VOICE_RECOGNITION,
                    sampleRate,
                    AudioFormat.CHANNEL_IN_MONO,
                    AudioFormat.ENCODING_PCM_16BIT,
                    bufferSize
                )
                recorder = localRecorder
                localRecorder.startRecording()

                val shorts = ShortArray(1600)
                while (running.get()) {
                    val n = localRecorder.read(shorts, 0, shorts.size)
                    if (n <= 0) continue
                    val floats = FloatArray(n)
                    for (i in 0 until n) floats[i] = shorts[i] / 32768.0f
                    if (localEngine.accept(floats, sampleRate)) onWakeDetected()
                }
            } catch (_: Throwable) {
                val event = DeviceEvent(
                    source = "wake_error",
                    packageName = packageName
                )
                LocalBridgeSender.send(event)
                WakeWordStore.record(this, detected = false, error = true)
            } finally {
                try { recorder?.stop() } catch (_: Throwable) {}
                try { recorder?.release() } catch (_: Throwable) {}
                recorder = null
                engine?.close()
                engine = null
                running.set(false)
            }
        }, "hey-tomo-kws").apply { start() }
    }

    private fun onWakeDetected() {
        WakeWordStore.record(this, detected = true, error = false)
        val event = DeviceEvent(
            source = "wake_word",
            packageName = packageName
        )
        LocalBridgeSender.send(event)
        DeviceEventBus.publish(event)

        GptVoiceLauncher.launch(this)
        try { Thread.sleep(2500L) } catch (_: InterruptedException) {}
    }

    override fun onDestroy() {
        running.set(false)
        try { recorder?.stop() } catch (_: Throwable) {}
        thread?.interrupt()
        thread = null
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

object WakeWordStore {
    private const val PREFS = "hey_tomo_proof"

    fun record(context: android.content.Context, detected: Boolean, error: Boolean) {
        val p = context.getSharedPreferences(PREFS, android.content.Context.MODE_PRIVATE)
        val e = p.edit().putLong("last_ms", System.currentTimeMillis())
        if (detected) e.putLong("wake_count", p.getLong("wake_count", 0L) + 1L)
        if (error) e.putLong("error_count", p.getLong("error_count", 0L) + 1L)
        e.apply()
    }

    fun snapshot(context: android.content.Context): String {
        val p = context.getSharedPreferences(PREFS, android.content.Context.MODE_PRIVATE)
        return "Hey Tomo armed: " + WakeService.isArmed(context) + "\\n" +
            "Wake detections: " + p.getLong("wake_count", 0L) + "\\n" +
            "Wake errors: " + p.getLong("error_count", 0L)
    }
}
