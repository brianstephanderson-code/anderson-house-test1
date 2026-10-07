package house.anderson.amigos

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import java.util.Locale

class TextRadioCaptureActivity : Activity(), RecognitionListener {
    companion object {
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
        private const val END_WORD = "over"
        private const val RESTART_DELAY_MS = 250L
    }

    private val handler = Handler(Looper.getMainLooper())
    private var recognizer: SpeechRecognizer? = null
    private var accumulatedTranscript = ""
    private var finishingTurn = false
    private var recognitionStarted = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        accumulatedTranscript = savedInstanceState
            ?.getString("accumulatedTranscript")
            .orEmpty()

        TextRadioStore.beginCapture(this)

        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            failAndRearm("Speech recognition is not available on this device")
            return
        }

        recognizer = SpeechRecognizer.createSpeechRecognizer(this).also {
            it.setRecognitionListener(this)
        }
        startListening()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString("accumulatedTranscript", accumulatedTranscript)
        super.onSaveInstanceState(outState)
    }

    private fun startListening() {
        if (finishingTurn || isFinishing || isDestroyed) return

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE,
                Locale.getDefault().toLanguageTag()
            )
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
        }

        try {
            recognitionStarted = true
            recognizer?.startListening(intent)
        } catch (_: Throwable) {
            failAndRearm("Live speech listener could not start")
        }
    }

    override fun onReadyForSpeech(params: Bundle?) = Unit
    override fun onBeginningOfSpeech() = Unit
    override fun onRmsChanged(rmsdB: Float) = Unit
    override fun onBufferReceived(buffer: ByteArray?) = Unit

    override fun onEndOfSpeech() {
        recognitionStarted = false
    }

    override fun onPartialResults(partialResults: Bundle?) {
        if (finishingTurn) return

        val partial = firstResult(partialResults)
        if (partial.isBlank()) return

        val (clean, ended) = stripTerminalOver(partial)
        if (!ended) return

        // OVER is our radio-style end-of-turn marker. The moment it appears as the
        // terminal word in live recognition, finish the turn without waiting for an
        // external recognizer UI to close.
        finishingTurn = true
        try { recognizer?.stopListening() } catch (_: Throwable) {}

        val transcript = joinTranscript(accumulatedTranscript, clean)
        completeTurn(transcript)
    }

    override fun onResults(results: Bundle?) {
        recognitionStarted = false
        if (finishingTurn) return

        val heard = firstResult(results)
        if (heard.isBlank()) {
            scheduleRestart()
            return
        }

        val (clean, ended) = stripTerminalOver(heard)
        accumulatedTranscript = joinTranscript(accumulatedTranscript, clean)

        if (ended) {
            finishingTurn = true
            completeTurn(accumulatedTranscript)
        } else {
            // A normal pause is not the end of the user's turn. Keep what was heard,
            // restart the listener, and wait for the explicit word OVER.
            scheduleRestart()
        }
    }

    override fun onError(error: Int) {
        recognitionStarted = false
        if (finishingTurn) return

        // Errors such as NO_MATCH / SPEECH_TIMEOUT often simply mean a pause.
        // Preserve the accumulated words and reopen the live listener.
        scheduleRestart()
    }

    override fun onEvent(eventType: Int, params: Bundle?) = Unit

    private fun scheduleRestart() {
        if (finishingTurn || isFinishing || isDestroyed) return
        handler.removeCallbacksAndMessages(null)
        handler.postDelayed({
            if (!finishingTurn && !isFinishing && !isDestroyed && !recognitionStarted) {
                startListening()
            }
        }, RESTART_DELAY_MS)
    }

    private fun firstResult(bundle: Bundle?): String =
        bundle
            ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
            ?.firstOrNull()
            ?.trim()
            .orEmpty()

    private fun stripTerminalOver(text: String): Pair<String, Boolean> {
        val match = Regex("""(?i)(?:^|\s)over[.!?,;:]*\s*$""").find(text)
            ?: return text.trim() to false
        return text.substring(0, match.range.first).trim() to true
    }

    private fun joinTranscript(first: String, second: String): String =
        listOf(first.trim(), second.trim())
            .filter { it.isNotBlank() }
            .joinToString(" ")
            .trim()

    private fun completeTurn(transcript: String) {
        val cleanTranscript = transcript.trim()
        accumulatedTranscript = ""

        if (cleanTranscript.isBlank()) {
            failAndRearm("Nothing was spoken before OVER")
            return
        }

        if (VisionVoiceCommand.isVisionRequest(cleanTranscript)) {
            TextRadioStore.visionTranscriptReady(this, cleanTranscript)
            try {
                startActivity(
                    Intent(this, VisionCaptureActivity::class.java).apply {
                        putExtra(VisionCaptureActivity.EXTRA_SEND_TO_CHATGPT, true)
                        putExtra(VisionCaptureActivity.EXTRA_PROMPT, cleanTranscript)
                    }
                )
                finish()
                return
            } catch (_: Throwable) {
                failAndRearm("Vision capture could not open")
                return
            }
        }

        TextRadioStore.transcriptReady(this, cleanTranscript)

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

    private fun failAndRearm(message: String) {
        finishingTurn = true
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

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        try { recognizer?.cancel() } catch (_: Throwable) {}
        try { recognizer?.destroy() } catch (_: Throwable) {}
        recognizer = null
        super.onDestroy()
    }
}
