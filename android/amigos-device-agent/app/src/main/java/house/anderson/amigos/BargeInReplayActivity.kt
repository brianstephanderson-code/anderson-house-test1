package house.anderson.amigos

import android.app.Activity
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
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
    private var borrowedMic = false
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "BARGE-IN REPLAY v3\n\nISOLATED REPLAY — this does NOT send anything to ChatGPT. It only proves: listen while local test speech plays, stop on your voice, capture the interruption, then return the microphone to Open Sesame."
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

        // Open Sesame normally owns the microphone. The replay must explicitly
        // borrow it or Android can leave SpeechRecognizer with no usable input.
        pauseOpenSesame()
        status.text = "Borrowing microphone from Open Sesame…"

        handler.postDelayed({
            if (!isFinishing && !isDestroyed) {
                startReplayAfterMicHandoff()
            }
        }, 600L)
    }

    private fun startReplayAfterMicHandoff() {
        recognizer = SpeechRecognizer.createSpeechRecognizer(this).also { sr ->
            sr.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    status.text = "Listener READY. Starting local test speech now — interrupt naturally."
                    speakReplayOnlyWhenListenerReady()
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
                    rearmOpenSesame()
                }

                override fun onResults(results: Bundle?) {
                    val heard = results
                        ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        ?.firstOrNull()
                        .orEmpty()
                    val label = if (interrupted.get()) "GREEN candidate" else "No barge-in detected"
                    status.text = label + "\nCaptured: " + heard + "\nOpen Sesame re-armed."
                    stopRecognizerOnly()
                    rearmOpenSesame()
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
            rearmOpenSesame()
            return
        }

    }

    private fun speakReplayOnlyWhenListenerReady() {
        if (interrupted.get()) return
        tts?.speak(
            "This is an isolated barge in replay. I am only a local test voice. Keep listening to me, then interrupt me naturally with any words you like. The moment your voice is detected, this test speech should stop.",
            TextToSpeech.QUEUE_FLUSH,
            null,
            "barge_in_replay_v3"
        )
    }

    private fun pauseOpenSesame() {
        if (!WakeService.isArmed(this)) {
            borrowedMic = false
            return
        }
        borrowedMic = true
        try {
            startService(Intent(this, WakeService::class.java).setAction(WakeService.ACTION_PAUSE))
        } catch (_: Throwable) {}
    }

    private fun rearmOpenSesame() {
        if (!borrowedMic) return
        borrowedMic = false
        val intent = Intent(this, WakeService::class.java).setAction(WakeService.ACTION_REARM)
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(intent)
            } else {
                startService(intent)
            }
        } catch (_: Throwable) {}
    }

    private fun stopReplay(message: String) {
        handler.removeCallbacksAndMessages(null)
        try { tts?.stop() } catch (_: Throwable) {}
        stopRecognizerOnly()
        rearmOpenSesame()
        status.text = message + "\nOpen Sesame re-armed."
    }

    private fun stopRecognizerOnly() {
        try { recognizer?.cancel() } catch (_: Throwable) {}
        try { recognizer?.destroy() } catch (_: Throwable) {}
        recognizer = null
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        stopRecognizerOnly()
        rearmOpenSesame()
        try { tts?.stop() } catch (_: Throwable) {}
        try { tts?.shutdown() } catch (_: Throwable) {}
        tts = null
        super.onDestroy()
    }
}
