package house.anderson.amigos

import android.content.Context

object TextRadioStore {
    private const val PREFS = "text_radio"
    private const val KEY_PHASE = "phase"
    private const val KEY_TRANSCRIPT = "transcript"
    private const val KEY_SENT_AT = "sent_at"
    private const val KEY_BASELINE_READ_ALOUD = "baseline_read_aloud"
    private const val KEY_GENERATION_SEEN = "generation_seen"
    private const val KEY_LAST_ERROR = "last_error"
    private const val KEY_CYCLE_COUNT = "cycle_count"
    private const val KEY_VISION_PENDING = "vision_pending"

    const val PHASE_IDLE = "idle"
    const val PHASE_CAPTURING = "capturing"
    const val PHASE_READY_TO_SEND = "ready_to_send"
    const val PHASE_WAITING_REPLY = "waiting_reply"
    const val PHASE_SPEAKING = "speaking"

    private fun prefs(context: Context) =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    @Synchronized
    fun beginCapture(context: Context) {
        prefs(context).edit()
            .putString(KEY_PHASE, PHASE_CAPTURING)
            .remove(KEY_TRANSCRIPT)
            .putBoolean(KEY_GENERATION_SEEN, false)
            .remove(KEY_LAST_ERROR)
            .apply()
    }

    @Synchronized
    fun transcriptReady(context: Context, transcript: String) {
        prefs(context).edit()
            .putString(KEY_TRANSCRIPT, transcript.trim())
            .putBoolean(KEY_VISION_PENDING, false)
            .putString(KEY_PHASE, PHASE_READY_TO_SEND)
            .apply()
    }

    @Synchronized
    fun visionTranscriptReady(context: Context, transcript: String) {
        prefs(context).edit()
            .putString(KEY_TRANSCRIPT, transcript.trim())
            .putBoolean(KEY_VISION_PENDING, true)
            .putString(KEY_PHASE, PHASE_READY_TO_SEND)
            .apply()
    }

    fun visionPending(context: Context): Boolean =
        prefs(context).getBoolean(KEY_VISION_PENDING, false)

    fun transcript(context: Context): String =
        prefs(context).getString(KEY_TRANSCRIPT, "") ?: ""

    fun phase(context: Context): String =
        prefs(context).getString(KEY_PHASE, PHASE_IDLE) ?: PHASE_IDLE

    @Synchronized
    fun markWaitingForReply(context: Context, baselineReadAloud: Int) {
        prefs(context).edit()
            .putString(KEY_PHASE, PHASE_WAITING_REPLY)
            .putLong(KEY_SENT_AT, System.currentTimeMillis())
            .putInt(KEY_BASELINE_READ_ALOUD, baselineReadAloud)
            .putBoolean(KEY_GENERATION_SEEN, false)
            .putBoolean(KEY_VISION_PENDING, false)
            .remove(KEY_TRANSCRIPT)
            .apply()
    }

    fun sentAt(context: Context): Long = prefs(context).getLong(KEY_SENT_AT, 0L)

    fun baselineReadAloud(context: Context): Int =
        prefs(context).getInt(KEY_BASELINE_READ_ALOUD, 0)

    @Synchronized
    fun markGenerationSeen(context: Context) {
        prefs(context).edit().putBoolean(KEY_GENERATION_SEEN, true).apply()
    }

    fun generationSeen(context: Context): Boolean =
        prefs(context).getBoolean(KEY_GENERATION_SEEN, false)

    @Synchronized
    fun markSpeaking(context: Context) {
        val p = prefs(context)
        p.edit()
            .putString(KEY_PHASE, PHASE_SPEAKING)
            .putLong(KEY_CYCLE_COUNT, p.getLong(KEY_CYCLE_COUNT, 0L) + 1L)
            .apply()
    }

    @Synchronized
    fun complete(context: Context) {
        prefs(context).edit()
            .putString(KEY_PHASE, PHASE_IDLE)
            .remove(KEY_TRANSCRIPT)
            .putBoolean(KEY_GENERATION_SEEN, false)
            .putBoolean(KEY_VISION_PENDING, false)
            .apply()
    }

    @Synchronized
    fun fail(context: Context, message: String) {
        prefs(context).edit()
            .putString(KEY_PHASE, PHASE_IDLE)
            .putString(KEY_LAST_ERROR, message.take(240))
            .remove(KEY_TRANSCRIPT)
            .putBoolean(KEY_VISION_PENDING, false)
            .apply()
    }

    fun snapshot(context: Context): String {
        val p = prefs(context)
        return "Text Radio phase: " + phase(context) + "\n" +
            "Completed spoken replies: " + p.getLong(KEY_CYCLE_COUNT, 0L) + "\n" +
            "Generation seen: " + p.getBoolean(KEY_GENERATION_SEEN, false) + "\n" +
            "Vision handoff pending: " + p.getBoolean(KEY_VISION_PENDING, false) + "\n" +
            "Last error: " + (p.getString(KEY_LAST_ERROR, "none") ?: "none")
    }
}
