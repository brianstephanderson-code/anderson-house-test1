package house.anderson.amigos

object VisionVoiceCommand {
    private val exact = setOf(
        "look at this",
        "tomo look at this",
        "tommy look at this",
        "take a look at this",
        "what am i looking at",
        "what is this",
        "see this"
    )

    fun isVisionRequest(raw: String): Boolean {
        val normalized = raw
            .lowercase()
            .replace(Regex("[^a-z0-9 ]+"), " ")
            .replace(Regex("\\s+"), " ")
            .trim()
        if (normalized in exact) return true
        return normalized.startsWith("look at this ") ||
            normalized.startsWith("tomo look at this ") ||
            normalized.startsWith("take a look at this ")
    }
}
