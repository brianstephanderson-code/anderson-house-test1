package house.anderson.amigos

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import java.util.Locale
import java.util.concurrent.atomic.AtomicBoolean

class BargeInReplayActivity : Activity(), TextToSpeech.OnInitListener {
    private lateinit var status: TextView
    private var tts: TextToSpeech? = null
    private var recognizer: SpeechRecognizer? = null
    private val interrupted = AtomicBoolean(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "BARGE-IN REPLAY v1\n\nREPLAY ONLY — does not alter Open Sesame production behavior."
            textSize = 20f
        })

        status = TextView(this).apply {
            text = "Ready. Tap Start Replay, then interrupt Tomo naturally."
            textSize = 18f
            setPadding(0, 30, 0, 30)
        }
        layout.addView(status)

        layout.addView(Button(this).apply {
            text = "Start Replay"
            setOnClickListener { startReplay() }
        })

        layout.addView(Button(this).apply {
            text = "Stop Replay"
            setOnClickListener { stopReplay("Stopped manually") }
        })

        setContentView(layout)
        tts = TextToSpeech(this, this)
    }

    override fun onInit(result: Int) {
        if (result == TextToSpeech.SUCCESS) {
            tts?.language = Locale.US
            status.text = "Ready. Tap Start Replay."
        } else {
            status.text = "TTS could not initialize."
        }
    }

    private fun startReplay() {
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            status.text = "Speech recognition is not available on this device."
            return
        }

        stopRecognizerOnly()
        interrupted.set(false)

        recognizer = SpeechRecognizer.createSpeechRecognizer(this).also { sr ->
            sr.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    status.text = "Listening while Tomo speaks. Interrupt naturally."
                }

                override fun onBeginningOfSpeech() {
                    if (interrupted.compareAndSet(false, true)) {
                        tts?.stop()
                        status.text = "BARGE-IN DETECTED — Tomo stopped. Keep talking."
                    }
                }

                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {}

                override fun onError(error: Int) {
                    status.text = "Recognizer ended with code " + error + ". Replay can be retried."
                    stopRecognizerOnly()
                }

                override fun onResults(results: Bundle?) {
                    val heard = results
                        ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        ?.firstOrNull()
                        .orEmpty()
                    val label = if (interrupted.get()) "GREEN candidate" else "No barge-in detected"
                    status.text = label + "\nCaptured: " + heard
                    stopRecognizerOnly()
                }

                override fun onPartialResults(partialResults: Bundle?) {
                    val heard = partialResults
                        ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        ?.firstOrNull()
                        .orEmpty()
                    if (heard.isNotBlank() && interrupted.compareAndSet(false, true)) {
                        tts?.stop()
                        status.text = "BARGE-IN DETECTED — Tomo stopped.\nPartial: " + heard
                    }
                }

                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
        }

        val listenIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
        }

        try {
            recognizer?.startListening(listenIntent)
        } catch (err: Throwable) {
            status.text = "Could not start recognition: " + err.javaClass.simpleName
            stopRecognizerOnly()
            return
        }

        tts?.speak(
            "The camera bridge is working through several small functions, and I will keep talking until you interrupt me naturally. The purpose of this sentence is to be long enough for you to cut in anywhere you like.",
            TextToSpeech.QUEUE_FLUSH,
            null,
            "barge_in_replay"
        )
    }

    private fun stopReplay(message: String) {
        try { tts?.stop() } catch (_: Throwable) {}
        stopRecognizerOnly()
        status.text = message
    }

    private fun stopRecognizerOnly() {
        try { recognizer?.cancel() } catch (_: Throwable) {}
        try { recognizer?.destroy() } catch (_: Throwable) {}
        recognizer = null
    }

    override fun onDestroy() {
        stopRecognizerOnly()
        try { tts?.stop() } catch (_: Throwable) {}
        try { tts?.shutdown() } catch (_: Throwable) {}
        tts = null
        super.onDestroy()
    }
}
