package house.anderson.amigos

import android.content.Context
import android.content.Intent
import android.media.AudioManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.accessibility.AccessibilityNodeInfo
import java.util.concurrent.atomic.AtomicBoolean

class TextRadioAutomation(
    private val service: AmigosAccessibilityService
) {
    companion object {
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
        private val SEND_LABELS = listOf("send", "send message")
        private val READ_ALOUD_LABELS = listOf("read aloud", "read out loud")
        private val STOP_LABELS = listOf("stop", "stop generating")
    }

    private val handler = Handler(Looper.getMainLooper())
    private var sendScheduled = false
    private var inspectScheduled = false
    private val playbackMonitorRunning = AtomicBoolean(false)

    fun onAccessibilityEvent(packageName: String) {
        if (packageName != CHATGPT_PACKAGE) return
        when (TextRadioStore.phase(service)) {
            TextRadioStore.PHASE_READY_TO_SEND -> scheduleSend()
            TextRadioStore.PHASE_WAITING_REPLY -> scheduleInspect()
        }
    }

    private fun scheduleSend() {
        if (sendScheduled) return
        sendScheduled = true
        val delay = if (TextRadioStore.visionPending(service)) 2200L else 350L
        handler.postDelayed({
            sendScheduled = false
            attemptSend()
        }, delay)
    }

    private fun attemptSend() {
        if (TextRadioStore.phase(service) != TextRadioStore.PHASE_READY_TO_SEND) return
        val root = service.rootInActiveWindow ?: return
        val transcript = TextRadioStore.transcript(service)
        if (transcript.isBlank()) return

        val composer = findComposer(root) ?: run {
            scheduleSend()
            return
        }

        val baseline = findMatchingNodes(root, READ_ALOUD_LABELS).size

        composer.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
        val args = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, transcript)
        }
        val set = composer.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        if (!set) {
            TextRadioStore.fail(service, "Could not place dictated text into ChatGPT")
            rearmWake()
            return
        }

        handler.postDelayed({
            val latestRoot = service.rootInActiveWindow
            val sendNode = latestRoot?.let { findBestClickable(it, SEND_LABELS) }
            val sent = sendNode?.let { clickNodeOrParent(it) } ?: false
            if (sent) {
                TextRadioStore.markWaitingForReply(service, baseline)
                scheduleInspect()
            } else {
                scheduleSend()
            }
        }, 300L)
    }

    private fun scheduleInspect() {
        if (inspectScheduled) return
        inspectScheduled = true
        handler.postDelayed({
            inspectScheduled = false
            inspectReply()
        }, 450L)
    }

    private fun inspectReply() {
        if (TextRadioStore.phase(service) != TextRadioStore.PHASE_WAITING_REPLY) return
        val root = service.rootInActiveWindow ?: run {
            scheduleInspect()
            return
        }

        val stopVisible = findMatchingNodes(root, STOP_LABELS).isNotEmpty()
        if (stopVisible) {
            TextRadioStore.markGenerationSeen(service)
            scheduleInspect()
            return
        }

        val readAloud = findMatchingNodes(root, READ_ALOUD_LABELS)
        val baseline = TextRadioStore.baselineReadAloud(service)
        val generationSeen = TextRadioStore.generationSeen(service)
        val age = System.currentTimeMillis() - TextRadioStore.sentAt(service)

        val replyReady =
            readAloud.isNotEmpty() &&
                (generationSeen || readAloud.size > baseline) &&
                age >= 700L

        if (!replyReady) {
            if (age > 120000L) {
                TextRadioStore.fail(service, "Timed out waiting for ChatGPT reply")
                rearmWake()
            } else {
                scheduleInspect()
            }
            return
        }

        val target = readAloud.last()
        if (clickNodeOrParent(target)) {
            TextRadioStore.markSpeaking(service)
            monitorPlaybackAndRearm()
        } else {
            TextRadioStore.fail(service, "Reply arrived but Read aloud could not be started")
            rearmWake()
        }
    }

    private fun monitorPlaybackAndRearm() {
        if (!playbackMonitorRunning.compareAndSet(false, true)) return
        Thread({
            try {
                val audio = service.getSystemService(Context.AUDIO_SERVICE) as AudioManager
                val startedAt = System.currentTimeMillis()
                var heardPlayback = false
                var quietSince = 0L

                while (System.currentTimeMillis() - startedAt < 180000L) {
                    val active = audio.isMusicActive
                    val now = System.currentTimeMillis()
                    if (active) {
                        heardPlayback = true
                        quietSince = 0L
                    } else if (heardPlayback) {
                        if (quietSince == 0L) quietSince = now
                        if (now - quietSince >= 1400L) break
                    } else if (now - startedAt >= 10000L) {
                        break
                    }
                    try {
                        Thread.sleep(250L)
                    } catch (_: InterruptedException) {
                        break
                    }
                }
            } finally {
                playbackMonitorRunning.set(false)
                TextRadioStore.complete(service)
                rearmWake()
            }
        }, "text-radio-playback").start()
    }

    private fun rearmWake() {
        try {
            service.startService(
                Intent(service, WakeService::class.java)
                    .setAction(WakeService.ACTION_REARM)
            )
        } catch (_: Throwable) {}
    }

    private fun findComposer(root: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        val all = mutableListOf<AccessibilityNodeInfo>()
        collect(root, all)
        return all.lastOrNull { node ->
            node.isVisibleToUser &&
                node.isEnabled &&
                (node.isEditable ||
                    node.className?.toString()?.contains("EditText", ignoreCase = true) == true)
        }
    }

    private fun findMatchingNodes(
        root: AccessibilityNodeInfo,
        labels: List<String>
    ): List<AccessibilityNodeInfo> {
        val all = mutableListOf<AccessibilityNodeInfo>()
        collect(root, all)
        return all.filter { node ->
            if (!node.isVisibleToUser) return@filter false
            val haystack = listOf(
                node.text?.toString(),
                node.contentDescription?.toString()
            ).filterNotNull().joinToString(" ").lowercase()
            labels.any { label ->
                haystack == label || haystack.contains(label)
            }
        }
    }

    private fun findBestClickable(
        root: AccessibilityNodeInfo,
        labels: List<String>
    ): AccessibilityNodeInfo? =
        findMatchingNodes(root, labels).lastOrNull()

    private fun clickNodeOrParent(node: AccessibilityNodeInfo): Boolean {
        var current: AccessibilityNodeInfo? = node
        var hops = 0
        while (current != null && hops < 5) {
            if (current.isClickable && current.isEnabled &&
                current.performAction(AccessibilityNodeInfo.ACTION_CLICK)) {
                return true
            }
            current = current.parent
            hops += 1
        }
        return false
    }

    private fun collect(
        node: AccessibilityNodeInfo,
        out: MutableList<AccessibilityNodeInfo>
    ) {
        out.add(node)
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { collect(it, out) }
        }
    }
}
