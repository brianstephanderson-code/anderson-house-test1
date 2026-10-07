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
        private const val END_WORD = "over"
    }

    private var launched = false
    private var accumulatedTranscript = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        launched = savedInstanceState?.getBoolean("launched", false) ?: false
        accumulatedTranscript = savedInstanceState?.getString("accumulatedTranscript").orEmpty()

        if (!launched) {
            launched = true
            TextRadioStore.beginCapture(this)
            launchRecognizer()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putBoolean("launched", launched)
        outState.putString("accumulatedTranscript", accumulatedTranscript)
        super.onSaveInstanceState(outState)
    }

    private fun launchRecognizer() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag())
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                if (accumulatedTranscript.isBlank()) "Speak, then say OVER when finished"
                else "Continue, then say OVER when finished"
            )
        }
        if (isInstalled(FUTO_PACKAGE)) intent.setPackage(FUTO_PACKAGE)

        try {
            startActivityForResult(intent, REQ_SPEECH)
        } catch (_: Throwable) {
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

        val chunk = data
            ?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            ?.firstOrNull()
            ?.trim()
            .orEmpty()

        if (chunk.isBlank()) {
            failAndRearm("Speech capture returned no text")
            return
        }

        val (cleanChunk, ended) = stripTerminalOver(chunk)
        accumulatedTranscript = listOf(accumulatedTranscript, cleanChunk)
            .filter { it.isNotBlank() }
            .joinToString(" ")
            .trim()

        // Radio-style turn boundary:
        // recognizer pauses may end a single capture, but we do not send to ChatGPT
        // until the user explicitly finishes with the word "OVER".
        if (!ended) {
            launchRecognizer()
            return
        }

        val transcript = accumulatedTranscript.trim()
        accumulatedTranscript = ""

        if (transcript.isBlank()) {
            failAndRearm("Nothing was spoken before OVER")
            return
        }

        if (VisionVoiceCommand.isVisionRequest(transcript)) {
            TextRadioStore.visionTranscriptReady(this, transcript)
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

    private fun stripTerminalOver(text: String): Pair<String, Boolean> {
        val match = Regex("""(?i)(?:^|\\s)over[.!?,;:]*\\s*$""").find(text)
            ?: return text.trim() to false
        return text.substring(0, match.range.first).trim() to true
    }

    private fun isInstalled(packageName: String): Boolean =
        try {
            packageManager.getPackageInfo(packageName, 0)
            true
        } catch (_: Throwable) {
            false
        }

    private fun failAndRearm(message: String) {
        accumulatedTranscript = ""
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
