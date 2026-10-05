package house.anderson.amigos

import android.content.Context
import android.content.Intent

object TextRadioLauncher {
    fun launch(context: Context): Boolean {
        return try {
            context.startActivity(
                Intent(context, TextRadioCaptureActivity::class.java).apply {
                    addFlags(
                        Intent.FLAG_ACTIVITY_NEW_TASK or
                            Intent.FLAG_ACTIVITY_CLEAR_TOP or
                            Intent.FLAG_ACTIVITY_SINGLE_TOP
                    )
                }
            )
            true
        } catch (_: Throwable) {
            false
        }
    }
}
