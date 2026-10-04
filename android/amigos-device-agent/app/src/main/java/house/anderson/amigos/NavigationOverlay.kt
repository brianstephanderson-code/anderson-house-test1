package house.anderson.amigos

import android.content.Context
import android.graphics.PixelFormat
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.view.Gravity
import android.view.WindowManager
import android.widget.TextView
import kotlin.math.roundToInt

object NavigationOverlay {
    private val main = Handler(Looper.getMainLooper())
    private var view: TextView? = null
    private var wm: WindowManager? = null
    @Volatile private var latestInstruction: String = ""

    fun updateInstruction(context: Context, instruction: String?) {
        latestInstruction = instruction?.trim().orEmpty()
        update(context)
    }

    fun update(context: Context) {
        val app = context.applicationContext
        if (!Settings.canDrawOverlays(app)) return
        main.post {
            try {
                val text = buildText(app)
                if (text.isBlank()) {
                    hide(app)
                    return@post
                }
                val existing = view
                if (existing != null) {
                    existing.text = text
                    return@post
                }

                val manager = app.getSystemService(WindowManager::class.java)
                val tv = TextView(app).apply {
                    setTextColor(0xffffffff.toInt())
                    setBackgroundColor(0xdd111111.toInt())
                    textSize = 16f
                    setPadding(24, 14, 24, 14)
                    this.text = text
                    maxLines = 3
                }
                val params = WindowManager.LayoutParams(
                    WindowManager.LayoutParams.MATCH_PARENT,
                    WindowManager.LayoutParams.WRAP_CONTENT,
                    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                        WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or
                        WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                    PixelFormat.TRANSLUCENT
                ).apply {
                    gravity = Gravity.TOP
                }
                manager.addView(tv, params)
                wm = manager
                view = tv
            } catch (_: Throwable) {
            }
        }
    }

    fun hide(context: Context) {
        main.post {
            val v = view ?: return@post
            try { (wm ?: context.getSystemService(WindowManager::class.java)).removeView(v) } catch (_: Throwable) {}
            view = null
            wm = null
            latestInstruction = ""
        }
    }

    private fun buildText(context: Context): String {
        val loc = LocationTracker.latest(context)
        val extras = mutableListOf<String>()
        if (loc != null) {
            if (loc.speedMps >= 0) extras += ((loc.speedMps * 2.2369363f).roundToInt().toString() + " mph")
            if (loc.bearingDeg >= 0) extras += heading(loc.bearingDeg)
        }
        val line1 = latestInstruction
        val line2 = extras.joinToString("  •  ")
        return when {
            line1.isNotBlank() && line2.isNotBlank() -> "$line1\n$line2"
            line1.isNotBlank() -> line1
            line2.isNotBlank() -> line2
            else -> ""
        }
    }

    private fun heading(deg: Float): String {
        val names = arrayOf("N","NE","E","SE","S","SW","W","NW")
        val i = ((deg + 22.5f) / 45f).toInt() % 8
        return "Heading " + names[i]
    }
}
