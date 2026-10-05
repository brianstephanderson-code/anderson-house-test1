# Three Amigos Text Radio

Purpose: keep the normal ChatGPT text conversation as the permanent written ledger while adding a hands-free speech shell around it.

## Loop

1. Open Sesame local wake word fires.
2. Device Agent releases its microphone.
3. Android `ACTION_RECOGNIZE_SPEECH` opens FUTO Voice Input when installed.
4. FUTO returns a completed transcript to Device Agent.
5. Device Agent opens ChatGPT.
6. Accessibility automation finds the editable composer, inserts the transcript, and activates Send.
7. Device Agent watches the semantic ChatGPT accessibility tree for generation state.
8. When a new reply is complete, Device Agent activates the newest **Read aloud** action.
9. Audio is monitored until playback ends.
10. Open Sesame is re-armed.

The loop is:

`WAKE -> LISTEN -> TRANSCRIBE -> INSERT -> SEND -> WATCH -> SPEAK -> SLEEP`

## Design rules

- No fixed screen coordinates.
- FUTO is called through Android's standard recognition intent; HeliBoard is not required by the hands-free path.
- ChatGPT remains the text ledger. Text Radio does not use ChatGPT Live Voice.
- The wake-word microphone is released before FUTO starts.
- A 150-second recovery fence re-arms Open Sesame if a capture/UI handoff is lost.
- Private message text remains on the phone and is not published to GitHub.

## First device verification

After installing a build:

1. Accessibility service enabled.
2. Microphone permission granted.
3. Display-over-other-apps permission granted if required by the handset for background activity launch.
4. FUTO Voice Input installed and configured.
5. Open Sesame armed.
6. Say the wake phrase and dictate one short test question.
7. Confirm the dictated text appears in the ChatGPT text conversation.
8. Confirm the response is read aloud.
9. Confirm Open Sesame re-arms after playback.

Screen-off/locked behavior is a separate handset verification gate. The first build deliberately does not add a lock-screen bypass attribute.
