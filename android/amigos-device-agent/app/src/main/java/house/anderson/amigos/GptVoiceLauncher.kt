package house.anderson.amigos

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.net.Uri

object GptVoiceLauncher {
    private const val PACKAGE = "com.openai.chatgpt"
    private val voiceComponent = ComponentName(
        PACKAGE,
        "com.openai.voice.assistant.AssistantActivity"
    )

    fun launch(context: Context): Boolean {
        val direct = Intent().apply {
            component = voiceComponent
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        try {
            context.startActivity(direct)
            return true
        } catch (_: Throwable) {}

        return try {
            val fallback = Intent(
                Intent.ACTION_VIEW,
                Uri.parse("https://chat.com/?mode=voice")
            ).apply {
                setPackage(PACKAGE)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            }
            context.startActivity(fallback)
            true
        } catch (_: Throwable) {
            false
        }
    }
}
