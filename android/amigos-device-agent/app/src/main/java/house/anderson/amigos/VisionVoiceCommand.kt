package house.anderson.amigos

object VisionVoiceCommand {
    private val exact = setOf(
        "look at this",
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

        val withoutName = normalized
            .removePrefix("tomo ")
            .removePrefix("tommy ")
            .removePrefix("tomo, ")
            .trim()

        if (withoutName in exact) return true

        return withoutName.startsWith("look at this ") ||
            withoutName.startsWith("take a look at this ") ||
            withoutName.startsWith("what am i looking at ") ||
            withoutName.startsWith("what is this ")
    }
}
