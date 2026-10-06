package house.anderson.amigos

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.speech.RecognizerIntent
import java.util.Locale

class TextRadioCaptureActivity : Activity() {
    companion object {
        private const val REQ_SPEECH = 4401
        private const val FUTO_PACKAGE = "org.futo.voiceinput"
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
    }

    private var launched = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        launched = savedInstanceState?.getBoolean("launched", false) ?: false
        if (!launched) {
            launched = true
            TextRadioStore.beginCapture(this)
            launchRecognizer()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putBoolean("launched", launched)
        super.onSaveInstanceState(outState)
    }

    private fun launchRecognizer() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag())
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
        }
        if (isInstalled(FUTO_PACKAGE)) intent.setPackage(FUTO_PACKAGE)

        try {
            startActivityForResult(intent, REQ_SPEECH)
        } catch (t: Throwable) {
            failAndRearm("Speech recognizer could not start")
        }
    }

    @Deprecated("Legacy result callback retained for Android 11 compatibility")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != REQ_SPEECH) return

        if (resultCode != RESULT_OK) {
            failAndRearm("Speech capture cancelled")
            return
        }

        val transcript = data
            ?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            ?.firstOrNull()
            ?.trim()
            .orEmpty()

        if (transcript.isBlank()) {
            failAndRearm("Speech capture returned no text")
            return
        }

        if (VisionVoiceCommand.isVisionRequest(transcript)) {
            TextRadioStore.transcriptReady(this, transcript)
            try {
                startActivity(
                    Intent(this, VisionCaptureActivity::class.java).apply {
                        putExtra(VisionCaptureActivity.EXTRA_SEND_TO_CHATGPT, true)
                        putExtra(VisionCaptureActivity.EXTRA_PROMPT, transcript)
                    }
                )
                finish()
                return
            } catch (_: Throwable) {
                failAndRearm("Vision capture could not open")
                return
            }
        }

        TextRadioStore.transcriptReady(this, transcript)

        val launch = packageManager.getLaunchIntentForPackage(CHATGPT_PACKAGE)
        if (launch == null) {
            failAndRearm("ChatGPT app not found")
            return
        }

        try {
            launch.addFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK or
                    Intent.FLAG_ACTIVITY_CLEAR_TOP or
                    Intent.FLAG_ACTIVITY_SINGLE_TOP
            )
            startActivity(launch)
            finish()
        } catch (_: Throwable) {
            failAndRearm("ChatGPT could not open")
        }
    }

    private fun isInstalled(packageName: String): Boolean =
        try {
            packageManager.getPackageInfo(packageName, 0)
            true
        } catch (_: Throwable) {
            false
        }

    private fun failAndRearm(message: String) {
        TextRadioStore.fail(this, message)
        try {
            startService(
                Intent(this, WakeService::class.java)
                    .setAction(WakeService.ACTION_REARM)
            )
        } catch (_: Throwable) {}
        finish()
    }
}
