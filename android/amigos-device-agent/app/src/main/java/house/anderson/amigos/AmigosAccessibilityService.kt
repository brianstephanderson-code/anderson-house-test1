package house.anderson.amigos

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class AmigosAccessibilityService : AccessibilityService() {
    companion object {
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
        private val GO_QUIET_PHRASES = listOf("go quiet", "tomo go quiet")
        @Volatile private var lastQuietAt = 0L
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        event ?: return
        val pkg = event.packageName?.toString() ?: return
        val text = event.text?.joinToString(" ")?.takeIf { it.isNotBlank() }

        val deviceEvent = DeviceEvent(
            source = "accessibility",
            packageName = pkg,
            text = text
        )
        EventStore.record(this, deviceEvent)
        LocalBridgeSender.send(deviceEvent)
        DeviceEventBus.publish(deviceEvent)

        if (pkg == CHATGPT_PACKAGE && containsGoQuiet(text)) {
            goQuiet()
        }
    }

    private fun containsGoQuiet(text: String?): Boolean {
        val normalized = text?.lowercase()?.replace(Regex("[^a-z0-9 ]"), " ")
            ?.replace(Regex("\\s+"), " ")?.trim() ?: return false
        return GO_QUIET_PHRASES.any { normalized.contains(it) }
    }

    private fun goQuiet() {
        val now = System.currentTimeMillis()
        if (now - lastQuietAt < 2500L) return
        lastQuietAt = now

        val event = DeviceEvent(source = "go_quiet", packageName = CHATGPT_PACKAGE)
        EventStore.record(this, event)
        LocalBridgeSender.send(event)
        DeviceEventBus.publish(event)

        // Leave the Three Amigos wake service armed. Moving Home ends the visible
        // ChatGPT voice surface on supported builds; WakeService detects release of
        // ChatGPT's communication mic and automatically reacquires Open Sesame.
        performGlobalAction(GLOBAL_ACTION_HOME)

        // Nudge WakeService without disarming it. Its handoff/reacquire loop owns
        // the microphone transition, so Open Sesame remains the wake path.
        try {
            startService(Intent(this, WakeService::class.java).setAction(WakeService.ACTION_START))
        } catch (_: Throwable) {
            // WakeService is already sticky in the normal path; no destructive fallback.
        }
    }

    override fun onInterrupt() = Unit

    fun findByText(text: String): List<AccessibilityNodeInfo> =
        rootInActiveWindow?.findAccessibilityNodeInfosByText(text).orEmpty()

    fun click(node: AccessibilityNodeInfo): Boolean =
        node.performAction(AccessibilityNodeInfo.ACTION_CLICK)

    fun setText(node: AccessibilityNodeInfo, value: String): Boolean {
        val args = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, value)
        }
        return node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
    }

    fun scrollForward(node: AccessibilityNodeInfo): Boolean =
        node.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)
}
