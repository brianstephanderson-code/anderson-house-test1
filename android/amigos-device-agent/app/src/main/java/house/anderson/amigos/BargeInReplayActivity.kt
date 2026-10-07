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
    private var listenerReady = false
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        layout.addView(TextView(this).apply {
            text = "BARGE-IN REPLAY v4\n\nISOLATED REPLAY — this does NOT send anything to ChatGPT. It proves microphone handoff, local speech, interruption, capture, and safe return to Open Sesame."
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

        handler.removeCallbacksAndMessages(null)
        stopRecognizerOnly()
        interrupted.set(false)
        listenerReady = false

        // Ask any active Text Radio capture to surrender explicitly.
        DeviceEventBus.publish(
            DeviceEvent(
                source = MicHandoffEvents.RELEASE_FOR_REPLAY,
                packageName = packageName
            )
        )

        // Pause Open Sesame without changing the user's armed preference.
        pauseOpenSesame()

        status.text = "Requesting microphone release…\nWake active: " +
            WakeRuntime.captureActive + "\nText Radio active: " +
            TextRadioRuntime.captureActive

        waitForMicFree(System.currentTimeMillis())
    }

    private fun waitForMicFree(startedAt: Long) {
        if (isFinishing || isDestroyed) return

        val wakeBusy = WakeRuntime.captureActive
        val textBusy = TextRadioRuntime.captureActive

        if (!wakeBusy && !textBusy) {
            status.text = "Microphone FREE. Starting replay listener…"
            startReplayAfterMicHandoff()
            return
        }

        if (System.currentTimeMillis() - startedAt >= 4000L) {
            status.text =
                "MIC HANDOFF BLOCKED\nWake active: " + wakeBusy +
                "\nText Radio active: " + textBusy +
                "\nReplay did not steal the microphone."
            rearmOpenSesame()
            return
        }

        handler.postDelayed({
            waitForMicFree(startedAt)
        }, 100L)
    }

    private fun startReplayAfterMicHandoff() {
        recognizer = SpeechRecognizer.createSpeechRecognizer(this).also { sr ->
            sr.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    listenerReady = true
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

        handler.postDelayed({
            if (!listenerReady && recognizer != null && !isFinishing && !isDestroyed) {
                status.text =
                    "LISTENER NOT READY\nWake active: " + WakeRuntime.captureActive +
                    "\nText Radio active: " + TextRadioRuntime.captureActive +
                    "\nRecognizer never became ready."
                stopRecognizerOnly()
                rearmOpenSesame()
            }
        }, 4000L)
    }

    private fun speakReplayOnlyWhenListenerReady() {
        if (interrupted.get()) return
        val result = tts?.speak(
            "This is an isolated barge in replay. I am only a local test voice. Keep listening to me, then interrupt me naturally with any words you like. The moment your voice is detected, this test speech should stop.",
            TextToSpeech.QUEUE_FLUSH,
            null,
            "barge_in_replay_v4"
        )
        if (result == TextToSpeech.ERROR) {
            status.text = "Listener READY, but local TTS failed to start."
        }
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
        listenerReady = false
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
