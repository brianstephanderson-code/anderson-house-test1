package house.anderson.amigos

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.graphics.ImageFormat
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CaptureRequest
import android.graphics.SurfaceTexture
import android.view.Surface
import android.media.ImageReader
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import org.json.JSONObject
import java.io.BufferedReader
import java.io.File
import java.io.InputStreamReader
import java.net.InetAddress
import java.net.ServerSocket
import java.net.Socket
import java.nio.charset.StandardCharsets
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

class VisionEndpointService : Service() {
    companion object {
        const val ACTION_START = "house.anderson.amigos.VISION_ENDPOINT_START"
        const val ACTION_STOP = "house.anderson.amigos.VISION_ENDPOINT_STOP"
        private const val CHANNEL_ID = "vision_endpoint"
        private const val NOTIFICATION_ID = 7341
        private const val PORT = 8787
    }

    @Volatile private var mode = "parked"
    @Volatile private var lastCaptureMs: Long? = null
    @Volatile private var captureActive = false
    private val alive = AtomicBoolean(false)
    private var server: ServerSocket? = null
    private var serverThread: Thread? = null

    override fun onCreate() {
        super.onCreate()
        ensureChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            stopEndpoint()
            stopSelf()
            return START_NOT_STICKY
        }

        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            stopSelf()
            return START_NOT_STICKY
        }

        startForegroundForCamera()
        if (alive.compareAndSet(false, true)) startServer()
        return START_STICKY
    }

    private fun startForegroundForCamera() {
        val notification = buildNotification("Vision endpoint PARKED", "Local camera endpoint ready")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun ensureChannel() {
        getSystemService(NotificationManager::class.java).createNotificationChannel(
            NotificationChannel(CHANNEL_ID, "Vision Eye", NotificationManager.IMPORTANCE_LOW).apply {
                description = "Visible local camera endpoint for Three Amigos"
                setShowBadge(false)
            }
        )
    }

    private fun buildNotification(title: String, text: String): Notification {
        val open = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val stop = PendingIntent.getService(
            this, 1,
            Intent(this, VisionEndpointService::class.java).setAction(ACTION_STOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        return Notification.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setOngoing(true)
            .setContentIntent(open)
            .addAction(Notification.Action.Builder(null, "Stop", stop).build())
            .setCategory(Notification.CATEGORY_SERVICE)
            .setVisibility(Notification.VISIBILITY_PUBLIC)
            .build()
    }

    private fun updateNotification(title: String, text: String) {
        getSystemService(NotificationManager::class.java)
            .notify(NOTIFICATION_ID, buildNotification(title, text))
    }

    private fun startServer() {
        serverThread = Thread({
            try {
                server = ServerSocket(PORT, 8, InetAddress.getByName("127.0.0.1"))
                while (alive.get()) {
                    val socket = server?.accept() ?: break
                    Thread({ handle(socket) }, "vision-http-client").start()
                }
            } catch (_: Throwable) {
                if (alive.get()) updateNotification("Vision endpoint DEGRADED", "Local endpoint failed")
            }
        }, "vision-http-server").apply { start() }
    }

    private fun handle(socket: Socket) {
        socket.use { s ->
            s.soTimeout = 15000
            val reader = BufferedReader(InputStreamReader(s.getInputStream(), StandardCharsets.UTF_8))
            val requestLine = reader.readLine() ?: return
            val parts = requestLine.split(" ")
            if (parts.size < 2) return
            val method = parts[0]
            val path = parts[1]

            var contentLength = 0
            while (true) {
                val line = reader.readLine() ?: break
                if (line.isEmpty()) break
                if (line.startsWith("Content-Length:", ignoreCase = true)) {
                    contentLength = line.substringAfter(":").trim().toIntOrNull() ?: 0
                }
            }

            val body = if (contentLength > 0) {
                val chars = CharArray(contentLength)
                var read = 0
                while (read < contentLength) {
                    val n = reader.read(chars, read, contentLength - read)
                    if (n <= 0) break
                    read += n
                }
                String(chars, 0, read)
            } else ""

            try {
                when {
                    method == "POST" && path == "/ping" ->
                        sendJson(s, 200, JSONObject().put("ok", true).put("device", "android-phone-vision-v1"))

                    method == "GET" && path == "/status" ->
                        sendJson(s, 200, statusJson())

                    method == "POST" && path == "/mode" -> {
                        val requested = JSONObject(body.ifBlank { "{}" }).optString("mode")
                        if (requested != "parked" && requested != "active") {
                            sendJson(s, 400, JSONObject().put("ok", false).put("error", "bad_mode"))
                        } else {
                            mode = requested
                            updateNotification(
                                if (mode == "active") "Vision endpoint ACTIVE" else "Vision endpoint PARKED",
                                if (mode == "active") "Still capture is armed" else "Camera capture disabled"
                            )
                            sendJson(s, 200, JSONObject().put("ok", true).put("mode", mode))
                        }
                    }

                    method == "POST" && path == "/capture" -> {
                        if (mode != "active") {
                            sendJson(s, 409, JSONObject().put("ok", false).put("error", "parked_mode"))
                        } else if (captureActive) {
                            sendJson(s, 409, JSONObject().put("ok", false).put("error", "camera_busy"))
                        } else {
                            val req = JSONObject(body.ifBlank { "{}" })
                            val result = captureOneJpeg()
                            val id = UUID.randomUUID().toString()
                            File(filesDir, "vision-captures/${id}.jpg").apply {
                                parentFile?.mkdirs()
                                writeBytes(result.bytes)
                            }
                            lastCaptureMs = System.currentTimeMillis()
                            sendJson(
                                s, 200,
                                JSONObject()
                                    .put("ok", true)
                                    .put("request_id", req.optString("request_id"))
                                    .put("capture_id", id)
                                    .put("mime", "image/jpeg")
                                    .put("image_path", "/captures/${id}.jpg")
                                    .put("timestamp", lastCaptureMs)
                                    .put("width", result.width)
                                    .put("height", result.height)
                            )
                        }
                    }

                    method == "GET" && path.startsWith("/captures/") -> {
                        val name = path.substringAfterLast("/")
                        if (!name.matches(Regex("[A-Za-z0-9._-]+\\.jpg"))) {
                            sendJson(s, 400, JSONObject().put("ok", false).put("error", "bad_capture_id"))
                        } else {
                            val file = File(filesDir, "vision-captures/${name}")
                            if (!file.exists()) {
                                sendJson(s, 404, JSONObject().put("ok", false).put("error", "not_found"))
                            } else {
                                sendBytes(s, 200, "image/jpeg", file.readBytes())
                            }
                        }
                    }

                    else -> sendJson(s, 404, JSONObject().put("ok", false).put("error", "not_found"))
                }
            } catch (t: Throwable) {
                sendJson(
                    s, 500,
                    JSONObject().put("ok", false).put("error", "camera_error")
                        .put("detail", t.javaClass.simpleName + ": " + (t.message ?: ""))
                )
            }
        }
    }

    private fun statusJson(): JSONObject =
        JSONObject()
            .put("device", "android-phone-vision-v1")
            .put("state", mode)
            .put("camera", if (captureActive) "busy" else "ready")
            .put("battery_percent", JSONObject.NULL)
            .put("rssi", JSONObject.NULL)
            .put("active_indicator", captureActive)
            .put("last_capture_ms", lastCaptureMs ?: JSONObject.NULL)

    private data class CaptureResult(val bytes: ByteArray, val width: Int, val height: Int)

    private fun captureOneJpeg(): CaptureResult {
        captureActive = true
        updateNotification("VISION ACTIVE — CAPTURING", "One still image is being captured")

        val cameraThread = HandlerThread("vision-camera").apply { start() }
        val handler = Handler(cameraThread.looper)
        var device: CameraDevice? = null
        var reader: ImageReader? = null
        var session: CameraCaptureSession? = null
        var previewTexture: SurfaceTexture? = null
        var previewSurface: Surface? = null

        try {
            val manager = getSystemService(CameraManager::class.java)

            // Pick the primary rear camera rather than whichever rear ID happens
            // to be listed first. Multi-camera phones can expose macro/depth
            // cameras before the main sensor.
            val rearIds = manager.cameraIdList.filter { id ->
                manager.getCameraCharacteristics(id)
                    .get(CameraCharacteristics.LENS_FACING) == CameraCharacteristics.LENS_FACING_BACK
            }
            val cameraId = rearIds.maxByOrNull { id ->
                val px = manager.getCameraCharacteristics(id)
                    .get(CameraCharacteristics.SENSOR_INFO_PIXEL_ARRAY_SIZE)
                (px?.width?.toLong() ?: 0L) * (px?.height?.toLong() ?: 0L)
            } ?: manager.cameraIdList.firstOrNull() ?: error("no camera")

            val characteristics = manager.getCameraCharacteristics(cameraId)
            val sizes = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
                ?.getOutputSizes(ImageFormat.JPEG)?.toList() ?: error("no JPEG sizes")

            val size = sizes
                .filter { it.width <= 1920 && it.height <= 1080 }
                .maxByOrNull { it.width.toLong() * it.height.toLong() }
                ?: sizes.minByOrNull { it.width.toLong() * it.height.toLong() }
                ?: error("no JPEG size")

            reader = ImageReader.newInstance(size.width, size.height, ImageFormat.JPEG, 2)

            // Camera2 needs a live repeating stream so autofocus, auto-exposure,
            // and auto-white-balance can converge before the JPEG is requested.
            // A tiny off-screen SurfaceTexture gives the 3A algorithms real
            // frames without needing a visible camera preview.
            previewTexture = SurfaceTexture(0).apply {
                setDefaultBufferSize(640, 480)
            }
            previewSurface = Surface(previewTexture)

            val openLatch = CountDownLatch(1)
            var openError: Throwable? = null
            manager.openCamera(cameraId, object : CameraDevice.StateCallback() {
                override fun onOpened(camera: CameraDevice) {
                    device = camera
                    openLatch.countDown()
                }
                override fun onDisconnected(camera: CameraDevice) {
                    openError = IllegalStateException("camera disconnected")
                    camera.close()
                    openLatch.countDown()
                }
                override fun onError(camera: CameraDevice, error: Int) {
                    openError = IllegalStateException("camera error $error")
                    camera.close()
                    openLatch.countDown()
                }
            }, handler)

            if (!openLatch.await(6, TimeUnit.SECONDS)) error("camera open timeout")
            openError?.let { throw it }
            val opened = device ?: error("camera did not open")

            val sessionLatch = CountDownLatch(1)
            var sessionError: Throwable? = null
            opened.createCaptureSession(
                listOf(previewSurface!!, reader!!.surface),
                object : CameraCaptureSession.StateCallback() {
                    override fun onConfigured(s: CameraCaptureSession) {
                        session = s
                        sessionLatch.countDown()
                    }
                    override fun onConfigureFailed(s: CameraCaptureSession) {
                        sessionError = IllegalStateException("capture session failed")
                        sessionLatch.countDown()
                    }
                },
                handler
            )

            if (!sessionLatch.await(6, TimeUnit.SECONDS)) error("session timeout")
            sessionError?.let { throw it }
            val configured = session ?: error("session unavailable")

            // Warm the camera for up to ~2.5 seconds before the still capture.
            // This fixes the dark/blurry "first frame" behavior seen through the
            // Tomo endpoint while the stock Camera app is sharp from the same spot.
            val settleLatch = CountDownLatch(1)
            var previewFrames = 0
            val previewRequest = opened.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW).apply {
                addTarget(previewSurface!!)
                set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
                set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
                set(CaptureRequest.CONTROL_AWB_MODE, CaptureRequest.CONTROL_AWB_MODE_AUTO)
            }.build()
            configured.setRepeatingRequest(
                previewRequest,
                object : CameraCaptureSession.CaptureCallback() {
                    override fun onCaptureCompleted(
                        session: CameraCaptureSession,
                        request: CaptureRequest,
                        result: android.hardware.camera2.TotalCaptureResult
                    ) {
                        previewFrames += 1
                        if (previewFrames >= 20) settleLatch.countDown()
                    }
                },
                handler
            )
            settleLatch.await(2500, TimeUnit.MILLISECONDS)
            try { configured.stopRepeating() } catch (_: Throwable) {}

            val imageLatch = CountDownLatch(1)
            var jpeg: ByteArray? = null
            reader!!.setOnImageAvailableListener({ r ->
                val image = r.acquireLatestImage() ?: return@setOnImageAvailableListener
                try {
                    val buffer = image.planes[0].buffer
                    val bytes = ByteArray(buffer.remaining())
                    buffer.get(bytes)
                    jpeg = bytes
                } finally {
                    image.close()
                    imageLatch.countDown()
                }
            }, handler)

            val request = opened.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE).apply {
                addTarget(reader!!.surface)
                set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
                set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
                set(CaptureRequest.CONTROL_AWB_MODE, CaptureRequest.CONTROL_AWB_MODE_AUTO)
                set(CaptureRequest.JPEG_QUALITY, 95.toByte())
            }.build()
            configured.capture(request, object : CameraCaptureSession.CaptureCallback() {}, handler)

            if (!imageLatch.await(10, TimeUnit.SECONDS)) error("image timeout")
            val bytes = jpeg ?: error("empty image")
            return CaptureResult(bytes, size.width, size.height)
        } finally {
            try { session?.close() } catch (_: Throwable) {}
            try { device?.close() } catch (_: Throwable) {}
            try { reader?.close() } catch (_: Throwable) {}
            try { previewSurface?.release() } catch (_: Throwable) {}
            try { previewTexture?.release() } catch (_: Throwable) {}
            cameraThread.quitSafely()
            captureActive = false
            updateNotification(
                if (mode == "active") "Vision endpoint ACTIVE" else "Vision endpoint PARKED",
                if (mode == "active") "Still capture is armed" else "Camera capture disabled"
            )
        }
    }

    private fun sendJson(socket: Socket, code: Int, obj: JSONObject) {
        sendBytes(socket, code, "application/json", obj.toString().toByteArray(StandardCharsets.UTF_8))
    }

    private fun sendBytes(socket: Socket, code: Int, contentType: String, bytes: ByteArray) {
        val reason = when (code) {
            200 -> "OK"
            400 -> "Bad Request"
            404 -> "Not Found"
            409 -> "Conflict"
            else -> "Internal Server Error"
        }
        val header = buildString {
            append("HTTP/1.1 $code $reason\r\n")
            append("Content-Type: $contentType\r\n")
            append("Content-Length: ${bytes.size}\r\n")
            append("Connection: close\r\n\r\n")
        }.toByteArray(StandardCharsets.UTF_8)
        val out = socket.getOutputStream()
        out.write(header)
        out.write(bytes)
        out.flush()
    }

    private fun stopEndpoint() {
        alive.set(false)
        try { server?.close() } catch (_: Throwable) {}
        server = null
        serverThread?.interrupt()
        serverThread = null
        mode = "parked"
    }

    override fun onDestroy() {
        stopEndpoint()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
