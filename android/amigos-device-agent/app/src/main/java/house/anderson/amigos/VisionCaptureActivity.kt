package house.anderson.amigos

import android.Manifest
import android.app.Activity
import android.content.ClipData
import android.content.ContentValues
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.Gravity
import android.widget.FrameLayout
import android.widget.TextView
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.FocusMeteringAction
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.core.SurfaceOrientedMeteringPointFactory
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.LifecycleRegistry
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

class VisionCaptureActivity : Activity(), LifecycleOwner {
    companion object {
        private const val REQ_CAMERA = 401
        private const val REQ_SYSTEM_CAMERA = 402
        const val EXTRA_SEND_TO_CHATGPT = "vision_send_to_chatgpt"
        const val EXTRA_PROMPT = "vision_prompt"
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
    }

    private val lifecycleRegistry = LifecycleRegistry(this)
    override val lifecycle: Lifecycle
        get() = lifecycleRegistry

    private lateinit var previewView: PreviewView
    private lateinit var status: TextView
    private var imageCapture: ImageCapture? = null
    private var provider: ProcessCameraProvider? = null
    private var fallbackUri: Uri? = null
    private val captureStarted = AtomicBoolean(false)
    private var cameraStarted = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleRegistry.currentState = Lifecycle.State.CREATED

        previewView = PreviewView(this).apply {
            scaleType = PreviewView.ScaleType.FILL_CENTER
            implementationMode = PreviewView.ImplementationMode.COMPATIBLE
            setBackgroundColor(Color.BLACK)
        }

        status = TextView(this).apply {
            text = "VISION ACTIVE\n\nStarting CameraX eye…"
            textSize = 22f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.argb(140, 0, 0, 0))
            gravity = Gravity.CENTER
            setPadding(28, 24, 28, 24)
        }

        val root = FrameLayout(this).apply {
            setBackgroundColor(Color.BLACK)
            addView(
                previewView,
                FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.MATCH_PARENT
                )
            )
            addView(
                status,
                FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.WRAP_CONTENT,
                    Gravity.TOP
                )
            )
        }
        setContentView(root)

        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            status.text = "VISION ACTIVE\n\nCamera permission is required once."
            requestPermissions(arrayOf(Manifest.permission.CAMERA), REQ_CAMERA)
        }
    }

    override fun onStart() {
        super.onStart()
        lifecycleRegistry.currentState = Lifecycle.State.STARTED
        if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            startCameraXOnce()
        }
    }

    override fun onResume() {
        super.onResume()
        lifecycleRegistry.currentState = Lifecycle.State.RESUMED
    }

    override fun onPause() {
        lifecycleRegistry.currentState = Lifecycle.State.STARTED
        super.onPause()
    }

    override fun onStop() {
        lifecycleRegistry.currentState = Lifecycle.State.CREATED
        super.onStop()
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQ_CAMERA && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            startCameraXOnce()
        } else if (requestCode == REQ_CAMERA) {
            failAndRearm("Camera permission was not granted")
        }
    }

    private fun startCameraXOnce() {
        if (cameraStarted || captureStarted.get()) return
        cameraStarted = true
        status.text = "VISION ACTIVE\n\nOpening rear camera…"

        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            try {
                val cameraProvider = future.get()
                provider = cameraProvider

                val preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }
                val still = ImageCapture.Builder()
                    .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                    .setJpegQuality(95)
                    .build()
                imageCapture = still

                cameraProvider.unbindAll()
                val camera = cameraProvider.bindToLifecycle(
                    this,
                    CameraSelector.DEFAULT_BACK_CAMERA,
                    preview,
                    still
                )

                status.text = "VISION ACTIVE\n\nFocusing and setting exposure…"
                previewView.postDelayed({ focusAndCapture(camera) }, 900L)
            } catch (t: Throwable) {
                cameraStarted = false
                launchSystemCameraFallback("CameraX unavailable: ${t.javaClass.simpleName}")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun focusAndCapture(camera: Camera) {
        if (captureStarted.get()) return
        try {
            val factory = SurfaceOrientedMeteringPointFactory(1f, 1f)
            val center = factory.createPoint(0.5f, 0.5f)
            val action = FocusMeteringAction.Builder(
                center,
                FocusMeteringAction.FLAG_AF or
                    FocusMeteringAction.FLAG_AE or
                    FocusMeteringAction.FLAG_AWB
            )
                .setAutoCancelDuration(3, TimeUnit.SECONDS)
                .build()

            val focus = camera.cameraControl.startFocusAndMetering(action)
            focus.addListener(
                { captureCameraXStill() },
                ContextCompat.getMainExecutor(this)
            )
            previewView.postDelayed({ captureCameraXStill() }, 1800L)
        } catch (_: Throwable) {
            previewView.postDelayed({ captureCameraXStill() }, 700L)
        }
    }

    private fun captureCameraXStill() {
        if (!captureStarted.compareAndSet(false, true)) return
        val still = imageCapture ?: run {
            captureStarted.set(false)
            launchSystemCameraFallback("CameraX still capture was not ready")
            return
        }

        status.text = "VISION ACTIVE\n\nTaking one sharp still…"
        val values = newImageValues("vision_camerax")
        val output = ImageCapture.OutputFileOptions.Builder(
            contentResolver,
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            values
        ).build()

        still.takePicture(
            output,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(result: ImageCapture.OutputFileResults) {
                    val uri = result.savedUri
                    if (uri == null) {
                        captureStarted.set(false)
                        launchSystemCameraFallback("CameraX returned no image")
                        return
                    }
                    status.setBackgroundColor(Color.argb(170, 0, 90, 0))
                    status.text = "VISION CAPTURE GREEN\n\nSharp still captured."
                    provider?.unbindAll()

                    if (intent.getBooleanExtra(EXTRA_SEND_TO_CHATGPT, false)) {
                        shareToChatGPT(uri, intent.getStringExtra(EXTRA_PROMPT).orEmpty())
                    } else {
                        finish()
                    }
                }

                override fun onError(exception: ImageCaptureException) {
                    captureStarted.set(false)
                    provider?.unbindAll()
                    launchSystemCameraFallback("CameraX capture failed")
                }
            }
        )
    }

    private fun launchSystemCameraFallback(reason: String) {
        if (isFinishing) return
        provider?.unbindAll()
        status.text = "VISION FALLBACK\n\n$reason\n\nOpening the phone camera…"

        val uri = createPendingFallbackUri()
        fallbackUri = uri
        val cameraIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
            putExtra(MediaStore.EXTRA_OUTPUT, uri)
            clipData = ClipData.newUri(contentResolver, "Vision fallback", uri)
            addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION or Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

        if (cameraIntent.resolveActivity(packageManager) == null) {
            abandonPendingFallback()
            failAndRearm("No system camera app is available")
            return
        }

        try {
            startActivityForResult(cameraIntent, REQ_SYSTEM_CAMERA)
        } catch (_: Throwable) {
            abandonPendingFallback()
            failAndRearm("System camera fallback could not open")
        }
    }

    @Deprecated("Legacy result callback retained for Android 11 compatibility")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != REQ_SYSTEM_CAMERA) return

        val uri = fallbackUri
        fallbackUri = null
        if (resultCode != RESULT_OK || uri == null) {
            uri?.let { contentResolver.delete(it, null, null) }
            failAndRearm("System camera fallback was cancelled")
            return
        }

        val complete = ContentValues().apply {
            put(MediaStore.Images.Media.IS_PENDING, 0)
        }
        contentResolver.update(uri, complete, null, null)

        status.setBackgroundColor(Color.argb(170, 0, 90, 0))
        status.text = "VISION FALLBACK GREEN\n\nPhone camera captured the image."
        if (intent.getBooleanExtra(EXTRA_SEND_TO_CHATGPT, false)) {
            shareToChatGPT(uri, intent.getStringExtra(EXTRA_PROMPT).orEmpty())
        } else {
            finish()
        }
    }

    private fun newImageValues(prefix: String): ContentValues {
        val stamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        return ContentValues().apply {
            put(MediaStore.Images.Media.DISPLAY_NAME, "${prefix}_$stamp.jpg")
            put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/ThreeAmigos")
        }
    }

    private fun createPendingFallbackUri(): Uri {
        val values = newImageValues("vision_system_camera").apply {
            put(MediaStore.Images.Media.IS_PENDING, 1)
        }
        return contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            ?: error("MediaStore insert failed")
    }

    private fun abandonPendingFallback() {
        fallbackUri?.let {
            try { contentResolver.delete(it, null, null) } catch (_: Throwable) {}
        }
        fallbackUri = null
    }

    private fun shareToChatGPT(uri: Uri, prompt: String) {
        val share = Intent(Intent.ACTION_SEND).apply {
            type = "image/jpeg"
            setPackage(CHATGPT_PACKAGE)
            putExtra(Intent.EXTRA_STREAM, uri)
            clipData = ClipData.newUri(contentResolver, "Vision capture", uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        try {
            status.text = "VISION CAPTURE GREEN\n\nOpening ChatGPT with this image…"
            startActivity(share)
            finish()
        } catch (_: Throwable) {
            TextRadioStore.fail(this, "Vision image handoff to ChatGPT failed")
            rearmWake()
            finish()
        }
    }

    private fun failAndRearm(message: String) {
        status.text = "VISION DEGRADED\n\n$message"
        TextRadioStore.fail(this, message)
        rearmWake()
        finish()
    }

    private fun rearmWake() {
        try {
            startService(
                Intent(this, WakeService::class.java)
                    .setAction(WakeService.ACTION_REARM)
            )
        } catch (_: Throwable) {}
    }

    override fun onDestroy() {
        provider?.unbindAll()
        abandonPendingFallback()
        lifecycleRegistry.currentState = Lifecycle.State.DESTROYED
        super.onDestroy()
    }
}
