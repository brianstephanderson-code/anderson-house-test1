package house.anderson.amigos

object MicHandoffEvents {
    const val RELEASE_FOR_REPLAY = "mic_release_request_replay"
    const val TEXT_RADIO_RELEASED = "mic_released_text_radio"
    const val TEXT_RADIO_RELEASE_BLOCKED = "mic_release_blocked_text_radio"
    const val WAKE_RELEASED = "mic_released_wake"
}

object TextRadioRuntime {
    @Volatile var captureActive: Boolean = false
}
