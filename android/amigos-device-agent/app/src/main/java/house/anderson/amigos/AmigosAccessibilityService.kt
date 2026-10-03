package house.anderson.amigos

import android.accessibilityservice.AccessibilityService
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class AmigosAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        event ?: return
        val pkg = event.packageName?.toString() ?: return
        DeviceEventBus.publish(
            DeviceEvent(
                source = "accessibility",
                packageName = pkg,
                text = event.text?.joinToString(" ")?.takeIf { it.isNotBlank() }
            )
        )
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
