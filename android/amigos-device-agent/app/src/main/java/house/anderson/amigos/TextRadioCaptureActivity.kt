package house.anderson.amigos

import android.app.Activity
import android.content.ComponentName
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognitionService
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import java.util.Locale

class TextRadioCaptureActivity : Activity(), RecognitionListener {
    companion object {
        private const val REQ_SPEECH = 4401
        private const val FUTO_PACKAGE = "org.futo.voiceinput"
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
        private const val END_WORD = "over"
        private const val RESTART_DELAY_MS = 250L
    }

    private val handler = Handler(Looper.getMainLooper())
    private var recognizer: SpeechRecognizer? = null
    private var accumulatedTranscript = ""
    private var finishingTurn = false
    private var recognitionStarted = false
    private var consecutiveErrors = 0
    private var usingExternalFallback = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        accumulatedTranscript = savedInstanceState
            ?.getString("accumulatedTranscript")
            .orEmpty()

        TextRadioStore.beginCapture(this)

        val component = findFutoRecognitionService()
        if (component == null) {
            launchExternalRecognizer()
            return
        }

        try {
            recognizer = SpeechRecognizer.createSpeechRecognizer(this, component).also {
                it.setRecognitionListener(this)
            }
            startListening()
        } catch (_: Throwable) {
            launchExternalRecognizer()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString("accumulatedTranscript", accumulatedTranscript)
        super.onSaveInstanceState(outState)
    }

    private fun findFutoRecognitionService(): ComponentName? {
        val query = Intent(RecognitionService.SERVICE_INTERFACE).setPackage(FUTO_PACKAGE)
        return try {
            val matches =
                if (Build.VERSION.SDK_INT >= 33) {
                    packageManager.queryIntentServices(
                        query,
                        PackageManager.ResolveInfoFlags.of(0L)
                    )
                } else {
                    @Suppress("DEPRECATION")
                    packageManager.queryIntentServices(query, 0)
                }
            val service = matches.firstOrNull()?.serviceInfo ?: return null
            ComponentName(service.packageName, service.name)
        } catch (_: Throwable) {
            null
        }
    }

    private fun startListening() {
        if (finishingTurn || usingExternalFallback || isFinishing || isDestroyed) return

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
            launchExternalRecognizer()
        }
    }

    private fun launchExternalRecognizer() {
        if (finishingTurn || usingExternalFallback) return
        usingExternalFallback = true
        recognitionStarted = false
        try { recognizer?.cancel() } catch (_: Throwable) {}
        try { recognizer?.destroy() } catch (_: Throwable) {}
        recognizer = null

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE,
                Locale.getDefault().toLanguageTag()
            )
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            setPackage(FUTO_PACKAGE)
        }

        try {
            startActivityForResult(intent, REQ_SPEECH)
            TextRadioStore.recognizerState(this, "external_fallback")
        } catch (_: Throwable) {
            failAndRearm("Speech recognizer could not start")
        }
    }

    override fun onReadyForSpeech(params: Bundle?) {
        consecutiveErrors = 0
        TextRadioStore.recognizerState(this, "ready")
    }

    override fun onBeginningOfSpeech() {
        TextRadioStore.recognizerState(this, "speech_started")
    }

    override fun onRmsChanged(rmsdB: Float) = Unit
    override fun onBufferReceived(buffer: ByteArray?) = Unit

    override fun onEndOfSpeech() {
        recognitionStarted = false
    }

    override fun onPartialResults(partialResults: Bundle?) {
        if (finishingTurn || usingExternalFallback) return

        val partial = firstResult(partialResults)
        if (partial.isBlank()) return
        TextRadioStore.recognizerState(this, "partial", partial = partial)

        val (clean, ended) = stripTerminalOver(partial)
        if (!ended) return

        finishingTurn = true
        try { recognizer?.stopListening() } catch (_: Throwable) {}

        val transcript = joinTranscript(accumulatedTranscript, clean)
        completeTurn(transcript)
    }

    override fun onResults(results: Bundle?) {
        recognitionStarted = false
        if (finishingTurn || usingExternalFallback) return

        val heard = firstResult(results)
        if (heard.isNotBlank()) {
            TextRadioStore.recognizerState(this, "result", partial = heard)
        }
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
            scheduleRestart()
        }
    }

    override fun onError(error: Int) {
        recognitionStarted = false
        if (finishingTurn || usingExternalFallback) return

        consecutiveErrors += 1
        TextRadioStore.recognizerState(this, "error", error = error)

        if (consecutiveErrors >= 3) {
            launchExternalRecognizer()
        } else {
            scheduleRestart()
        }
    }

    override fun onEvent(eventType: Int, params: Bundle?) = Unit

    private fun scheduleRestart() {
        if (finishingTurn || usingExternalFallback || isFinishing || isDestroyed) return
        handler.removeCallbacksAndMessages(null)
        handler.postDelayed({
            if (!finishingTurn && !usingExternalFallback &&
                !isFinishing && !isDestroyed && !recognitionStarted) {
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
        val match = Regex("""(?i)(?:^|\\s)over[.!?,;:]*\\s*$""").find(text)
            ?: return text.trim() to false
        return text.substring(0, match.range.first).trim() to true
    }

    private fun joinTranscript(first: String, second: String): String =
        listOf(first.trim(), second.trim())
            .filter { it.isNotBlank() }
            .joinToString(" ")
            .trim()

    @Deprecated("Legacy result callback retained for Android 11 compatibility")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != REQ_SPEECH) return

        if (resultCode != RESULT_OK) {
            failAndRearm("Speech capture cancelled")
            return
        }

        val heard = data
            ?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            ?.firstOrNull()
            ?.trim()
            .orEmpty()

        if (heard.isBlank()) {
            failAndRearm("Speech capture returned no text")
            return
        }

        val (clean, _) = stripTerminalOver(heard)
        finishingTurn = true
        completeTurn(clean)
    }

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
