package house.anderson.amigos

import android.Manifest
import android.app.Activity
import android.content.ClipData
import android.content.ContentValues
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.media.ImageReader
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Visible, one-shot camera substitute for Vision Band replay.
 *
 * Privacy rule: this Activity is intentionally visible while the camera is active.
 * It takes exactly one still image and then closes the camera.
 */
class VisionCaptureActivity : Activity() {
    companion object {
        private const val REQ_CAMERA = 401
        const val EXTRA_SEND_TO_CHATGPT = "vision_send_to_chatgpt"
        const val EXTRA_PROMPT = "vision_prompt"
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
    }

    private lateinit var status: TextView
    private var imageReader: ImageReader? = null
    private var camera: CameraDevice? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        status = TextView(this).apply {
            text = "VISION ACTIVE\n\nPreparing one test image…"
            textSize = 26f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.rgb(150, 0, 0))
            gravity = Gravity.CENTER
            setPadding(40, 40, 40, 40)
        }

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.BLACK)
            addView(
                status,
                LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.MATCH_PARENT
                )
            )
        }
        setContentView(root)

        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            status.text = "VISION ACTIVE\n\nCamera permission is required once."
            requestPermissions(arrayOf(Manifest.permission.CAMERA), REQ_CAMERA)
        } else {
            captureOneVisibleFrame()
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQ_CAMERA && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            captureOneVisibleFrame()
        } else {
            status.text = "VISION PARKED\n\nCamera permission was not granted."
        }
    }

    private fun captureOneVisibleFrame() {
        val manager = getSystemService(CameraManager::class.java)
        val cameraId = manager.cameraIdList.firstOrNull { id ->
            manager.getCameraCharacteristics(id)
                .get(CameraCharacteristics.LENS_FACING) == CameraCharacteristics.LENS_FACING_BACK
        } ?: manager.cameraIdList.firstOrNull()

        if (cameraId == null) {
            status.text = "VISION DEGRADED\n\nNo camera found."
            return
        }

        imageReader = ImageReader.newInstance(1280, 720, android.graphics.ImageFormat.JPEG, 2).apply {
            setOnImageAvailableListener({ reader ->
                val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
                try {
                    val buffer = image.planes[0].buffer
                    val bytes = ByteArray(buffer.remaining())
                    buffer.get(bytes)
                    val uri = saveToPictures(bytes)
                    runOnUiThread {
                        status.setBackgroundColor(Color.rgb(0, 100, 0))
                        status.text = "VISION CAPTURE GREEN\n\nSaved one real image:\n$uri"
                        if (intent.getBooleanExtra(EXTRA_SEND_TO_CHATGPT, false)) {
                            shareToChatGPT(uri, intent.getStringExtra(EXTRA_PROMPT).orEmpty())
                        }
                    }
                } catch (t: Throwable) {
                    runOnUiThread {
                        status.text = "VISION DEGRADED\n\nSave failed: ${t.javaClass.simpleName}"
                    }
                } finally {
                    image.close()
                    camera?.close()
                    camera = null
                    imageReader?.close()
                    imageReader = null
                }
            }, null)
        }

        try {
            manager.openCamera(cameraId, object : CameraDevice.StateCallback() {
                override fun onOpened(device: CameraDevice) {
                    camera = device
                    val target = imageReader?.surface ?: run {
                        device.close()
                        return
                    }
                    device.createCaptureSession(
                        listOf(target),
                        object : CameraCaptureSession.StateCallback() {
                            override fun onConfigured(session: CameraCaptureSession) {
                                try {
                                    val request = device.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE).apply {
                                        addTarget(target)
                                    }.build()
                                    session.capture(
                                        request,
                                        object : CameraCaptureSession.CaptureCallback() {},
                                        null
                                    )
                                } catch (t: Throwable) {
                                    status.text = "VISION DEGRADED\n\nCapture failed: ${t.javaClass.simpleName}"
                                    device.close()
                                }
                            }

                            override fun onConfigureFailed(session: CameraCaptureSession) {
                                status.text = "VISION DEGRADED\n\nCamera session failed."
                                device.close()
                            }
                        },
                        null
                    )
                }

                override fun onDisconnected(device: CameraDevice) {
                    status.text = "VISION DEGRADED\n\nCamera disconnected."
                    device.close()
                }

                override fun onError(device: CameraDevice, error: Int) {
                    status.text = "VISION DEGRADED\n\nCamera error: $error"
                    device.close()
                }
            }, null)
        } catch (t: Throwable) {
            status.text = "VISION DEGRADED\n\nOpen failed: ${t.javaClass.simpleName}"
        }
    }

    private fun saveToPictures(bytes: ByteArray): android.net.Uri {
        val stamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        val values = ContentValues().apply {
            put(MediaStore.Images.Media.DISPLAY_NAME, "vision_replay_$stamp.jpg")
            put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/ThreeAmigos")
            put(MediaStore.Images.Media.IS_PENDING, 1)
        }
        val uri = contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            ?: error("MediaStore insert failed")

        contentResolver.openOutputStream(uri)?.use { it.write(bytes) }
            ?: error("MediaStore output stream failed")

        values.clear()
        values.put(MediaStore.Images.Media.IS_PENDING, 0)
        contentResolver.update(uri, values, null, null)
        return uri
    }

    private fun shareToChatGPT(uri: android.net.Uri, prompt: String) {
        val safePrompt = prompt.trim().ifBlank { "Look at this." }
        val share = Intent(Intent.ACTION_SEND).apply {
            type = "image/jpeg"
            setPackage(CHATGPT_PACKAGE)
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_TEXT, safePrompt)
            clipData = ClipData.newUri(contentResolver, "Vision capture", uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        try {
            status.text = "VISION CAPTURE GREEN\n\nOpening ChatGPT with this image…"
            startActivity(share)
            TextRadioStore.complete(this)
            startService(
                Intent(this, WakeService::class.java)
                    .setAction(WakeService.ACTION_REARM)
            )
            finish()
        } catch (t: Throwable) {
            status.text = "VISION DEGRADED\n\nCould not hand image to ChatGPT: ${t.javaClass.simpleName}"
            TextRadioStore.fail(this, "Vision image handoff to ChatGPT failed")
            try {
                startService(
                    Intent(this, WakeService::class.java)
                        .setAction(WakeService.ACTION_REARM)
                )
            } catch (_: Throwable) {}
        }
    }

    override fun onDestroy() {
        camera?.close()
        imageReader?.close()
        super.onDestroy()
    }
}
