# Dictation Crosstalk — Open Sesame Text

Status: approved design handoff for the Three Amigos Device Agent.

## User goal

Provide two hands-free doors into the same Three Amigos function library:

- **Open Sesame** -> ChatGPT Voice door.
- **Open Sesame Text** -> hands-free dictation/text door.

Both doors must route to the same underlying Three Amigos functions (GPS, navigation, search, Go Quiet, and future functions).

The text door must remain available after the user presses the power button and the display is black.

## Locked architecture

SCREEN OFF
-> WakeService foreground microphone listener remains armed
-> keyword spotter detects either wake phrase
-> route by wake phrase:
   - OPEN_SESAME -> GptVoiceLauncher
   - OPEN_SESAME_TEXT -> text/dictation capture
-> normalize transcript into one shared command router
-> invoke the same Three Amigos functions
-> return response through the chosen interaction mode
-> Go Quiet closes the active session and re-arms the wake listener

Do not duplicate GPS, navigation, search, or other function implementations. Compile the flow; keep functions separate.

## Android feasibility findings

Target phone is Android 11.

Android 11 permits an already-started foreground service to continue microphone capture with the screen off when the service is declared as type `microphone` and RECORD_AUDIO is granted. The existing WakeService and manifest already contain the foreground microphone service plumbing.

Important launch rule: the microphone foreground service should be armed while the Device Agent is user-visible, then it can remain running when the screen turns off.

## FUTO finding

The installed FUTO Voice Input path supports `android.speech.action.RECOGNIZE_SPEECH`, which opens a floating recognition Activity. Its published API does not currently expose the standard SpeechRecognizer API in the released app.

Therefore the current FUTO Activity path is useful for visible-screen Text Radio, but it is not the final dependency for guaranteed black-screen hands-free dictation.

For true screen-off Text Radio, use a service-owned/on-device speech recognizer after the wake phrase, or another recognizer that can run inside the already-armed microphone foreground service. Do not require a keyboard or visible floating Activity.

## Implementation gates

1. Dual wake-word detection: distinguish OPEN_SESAME from OPEN_SESAME_TEXT.
2. Preserve Open Sesame -> voice behavior.
3. Open Sesame Text -> service-owned text capture.
4. Shared CommandRouter accepts transcripts from voice/text and calls the same function library.
5. GPS command examples: "where am I?", "where are we?", navigation requests.
6. Go Quiet ends the active session and re-arms both wake doors.
7. Screen-off test: arm once while visible, press power, confirm Open Sesame Text is still detected without lighting the screen.
8. Recovery test: recognizer failure/cancel/time-out must re-arm the listener.
9. Battery/notification test: foreground listener remains obvious to Android and survives ordinary app switching.

## Current caution

Do not claim the current APK already completes black-screen dictation. It already has most of the wake/GPS/accessibility plumbing, but the FUTO capture Activity is still a visible-UI handoff. The remaining production step is service-owned text capture plus dual wake routing.

## Crosstalk rule

This file is the shared handoff between chats. The dictation workbench should treat it as the canonical requirement and continue from here rather than rebuilding the concept from conversation memory.
