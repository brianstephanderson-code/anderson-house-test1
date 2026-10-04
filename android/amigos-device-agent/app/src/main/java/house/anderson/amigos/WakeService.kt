package house.anderson.amigos

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager\nimport android.content.pm.ServiceInfo\nimport android.os.Build
import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.IBinder
import android.os.Process
import java.util.concurrent.atomic.AtomicBoolean

object WakeRuntime {
    @Volatile var captureActive: Boolean = false
    @Volatile var framesRead: Long = 0L
    @Volatile var lastRms: Int = 0
    @Volatile var peakRms: Int = 0
    @Volatile var engineReady: Boolean = false

    fun reset() {
        captureActive = false
        framesRead = 0L
        lastRms = 0
        peakRms = 0
        engineReady = false
    }
}

class WakeService : Service() {
    companion object {
        const val ACTION_START = "house.anderson.amigos.WAKE_START"
        const val ACTION_STOP = "house.anderson.amigos.WAKE_STOP"
        private const val CHANNEL_ID = "hey_tomo_listener"
        private const val NOTIFICATION_ID = 7311
        private const val PREFS = "hey_tomo"
        private const val KEY_ARMED = "armed"

        private fun prefs(context: android.content.Context) =
            context.createDeviceProtectedStorageContext()
                .getSharedPreferences(PREFS, MODE_PRIVATE)

        fun isArmed(context: android.content.Context): Boolean =
            prefs(context).getBoolean(KEY_ARMED, false)
    }

    private val serviceAlive = AtomicBoolean(false)
    private val captureRunning = AtomicBoolean(false)
    private val handoffRunning = AtomicBoolean(false)
    private var captureThread: Thread? = null
    private var recorder: AudioRecord? = null
    private var engine: WakeEngine? = null

    override fun onCreate() {
        super.onCreate()
        serviceAlive.set(true)
    }

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
        WakeRuntime.reset()
        ensureChannel()
        startForegroundForCapabilities()
        AppContextHolder.context = applicationContext
        startListening()
        return START_STICKY
    }

    private fun setArmed(value: Boolean) {
        createDeviceProtectedStorageContext()
            .getSharedPreferences(PREFS, MODE_PRIVATE)
            .edit().putBoolean(KEY_ARMED, value).apply()
    }

    private fun startForegroundForCapabilities() {
        val notification = buildNotification()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            var types = ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
            if (LocationTracker.hasPermission(this)) {
                types = types or ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
            }
            startForeground(NOTIFICATION_ID, notification, types)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun ensureChannel() {
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ID,
                "Open Sesame listener",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Local wake-word listener for Open Sesame"
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
            .setContentTitle("Open Sesame is listening")
            .setContentText("Wake phrase: Open Sesame")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .setContentIntent(open)
            .addAction(Notification.Action.Builder(null, "Stop", stop).build())
            .setCategory(Notification.CATEGORY_SERVICE)
            .setVisibility(Notification.VISIBILITY_PRIVATE)
            .build()
    }

    @Synchronized
    private fun startListening() {
        if (!serviceAlive.get() || !WakeService.isArmed(this)) return
        if (captureRunning.get() || handoffRunning.get()) return

        captureRunning.set(true)
        captureThread = Thread({
            Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO)
            var detected = false
            try {
                val localEngine = WakeEngine(assets)
                localEngine.start()
                engine = localEngine
                WakeRuntime.engineReady = true

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
                WakeRuntime.captureActive = true

                val shorts = ShortArray(1600)
                while (serviceAlive.get() && captureRunning.get()) {
                    val n = localRecorder.read(shorts, 0, shorts.size)
                    if (n <= 0) continue
                    WakeRuntime.framesRead += 1L
                    var sum = 0.0
                    val floats = FloatArray(n)
                    for (i in 0 until n) {
                        val v = shorts[i].toDouble()
                        sum += v * v
                        floats[i] = shorts[i] / 32768.0f
                    }
                    WakeRuntime.lastRms = kotlin.math.sqrt(sum / n).toInt()
                    if (WakeRuntime.lastRms > WakeRuntime.peakRms) WakeRuntime.peakRms = WakeRuntime.lastRms
                    if (localEngine.accept(floats, sampleRate)) {
                        detected = true
                        captureRunning.set(false)
                        break
                    }
                }
            } catch (_: Throwable) {
                val event = DeviceEvent(source = "wake_error", packageName = packageName)
                LocalBridgeSender.send(event)
                WakeWordStore.record(this, detected = false, error = true)
            } finally {
                releaseCapture()
            }

            if (detected && serviceAlive.get()) handleWakeHandoff()
            else if (serviceAlive.get() && WakeService.isArmed(this) && !handoffRunning.get()) {
                Thread.sleep(500L)
                startListening()
            }
        }, "hey-tomo-kws").apply { start() }
    }

    @Synchronized
    private fun releaseCapture() {
        try { recorder?.stop() } catch (_: Throwable) {}
        try { recorder?.release() } catch (_: Throwable) {}
        recorder = null
        WakeRuntime.captureActive = false
        engine?.close()
        engine = null
        WakeRuntime.engineReady = false
        captureRunning.set(false)
    }

    private fun handleWakeHandoff() {
        if (!handoffRunning.compareAndSet(false, true)) return

        WakeWordStore.record(this, detected = true, error = false)
        val event = DeviceEvent(source = "wake_word", packageName = packageName)
        LocalBridgeSender.send(event)
        DeviceEventBus.publish(event)

        // Important: our microphone is fully released before ChatGPT Voice starts.
        try { Thread.sleep(300L) } catch (_: InterruptedException) {}
        GptVoiceLauncher.launch(this)

        Thread({
            try {
                val audio = getSystemService(AudioManager::class.java)
                val start = System.currentTimeMillis()
                var voiceSeen = false
                var quietSince = 0L

                // Wait for ChatGPT voice to become active, then wait until it really ends.
                while (serviceAlive.get() && WakeService.isArmed(this)) {
                    val now = System.currentTimeMillis()
                    val active = isCommunicationCaptureActive(audio)

                    if (active) {
                        voiceSeen = true
                        quietSince = 0L
                    } else if (voiceSeen) {
                        if (quietSince == 0L) quietSince = now
                        if (now - quietSince >= 1500L) break
                    } else if (now - start >= 12000L) {
                        // Launch failed or voice never took the mic: restore Hey Tomo.
                        break
                    }

                    try { Thread.sleep(250L) } catch (_: InterruptedException) { break }
                }
            } finally {
                handoffRunning.set(false)
                if (serviceAlive.get() && WakeService.isArmed(this)) startListening()
            }
        }, "hey-tomo-reacquire").start()
    }

    private fun isCommunicationCaptureActive(audio: AudioManager): Boolean {
        val mode = audio.mode
        val commMode = mode == AudioManager.MODE_IN_COMMUNICATION || mode == AudioManager.MODE_IN_CALL
        if (!commMode) return false

        return try {
            audio.activeRecordingConfigurations.any { cfg ->
                val src = cfg.clientAudioSource
                val commSource =
                    src == MediaRecorder.AudioSource.VOICE_COMMUNICATION ||
                    src == MediaRecorder.AudioSource.VOICE_CALL
                commSource && !cfg.isClientSilenced
            }
        } catch (_: Throwable) {
            commMode
        }
    }

    override fun onDestroy() {
        serviceAlive.set(false)
        handoffRunning.set(false)
        captureRunning.set(false)
        releaseCapture()
        captureThread?.interrupt()
        captureThread = null
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
        return "Open Sesame armed: " + WakeService.isArmed(context) + "\n" +
            "Wake detections: " + p.getLong("wake_count", 0L) + "\n" +
            "Wake errors: " + p.getLong("error_count", 0L) + "\n" +
            "Engine ready: " + WakeRuntime.engineReady + "\n" +
            "Mic capture active: " + WakeRuntime.captureActive + "\n" +
            "Audio frames: " + WakeRuntime.framesRead + "\n" +
            "Mic level now: " + WakeRuntime.lastRms + "\n" +
            "Mic peak since start: " + WakeRuntime.peakRms
    }
}
