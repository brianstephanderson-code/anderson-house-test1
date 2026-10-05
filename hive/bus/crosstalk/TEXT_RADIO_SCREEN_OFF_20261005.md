# CROSSTALK — Text Radio / screen-off hands-free convergence

Date: 2026-10-05
From: Three Amigos cross-chat review
Target lane: `tomo/text-radio-v1`

## User goal

Keep two hands-free doors into the SAME Three Amigos function library:

1. **Open Sesame** -> normal ChatGPT voice path.
2. **Text Sesame** (distinct text wake phrase; avoid prefix collision with "Open Sesame") -> hands-free dictation/text path.

After either door, route into the same function/intent layer so GPS, navigation, search, Go Quiet, and future Three Amigos functions are not duplicated.

The text path must continue to be available when the user presses the power button and the screen is black.

## Cast / recast result

### What is already solid

- The Device Agent already has a microphone foreground service and local Sherpa-ONNX keyword spotter.
- Android 11 permits an already-started microphone foreground service to continue capturing while the app is not visible, provided the microphone foreground-service type and RECORD_AUDIO permission are present.
- The current app already declares microphone/location foreground-service types and the required microphone permission.
- The existing Text Radio branch already has:
  - wake-word capture
  - FUTO `ACTION_RECOGNIZE_SPEECH` handoff
  - transcript -> ChatGPT composer insertion
  - Send automation
  - reply completion watch
  - Read Aloud automation
  - re-arm/recovery fence
- The existing GPS/location code can remain one shared function behind the router.

### Important correction

Do **not** treat FUTO's current recognition-intent window as the final screen-off transcription engine.

FUTO Voice Input currently supports `android.speech.action.RECOGNIZE_SPEECH` and IME voice mode, but does not currently expose Android's `SpeechRecognizer` API. Its supported route opens UI. That is good for the first Text Radio proof, but it is not the strongest basis for a screen-black/locked permanent path.

### Screen-off path that closes the architecture

Use the existing local Sherpa-ONNX stack for the always-on wake layer, then hand the same microphone foreground service to a **local streaming ASR engine inside Device Agent** after the text wake phrase.

Flow:

`SCREEN OFF -> local KWS -> TEXT WAKE -> release KWS stream -> local ASR capture -> transcript -> shared command router -> Three Amigos function -> response path -> KWS re-arm`

This avoids relying on keyboard UI or a recognition popup while the screen is black.

Sherpa-ONNX publishes Android-capable streaming ASR models, including small English streaming Zipformer models, so this path is technically available without ChatGPT Voice minutes.

## Wake phrase decision

Use a phrase that does not begin with the complete voice wake phrase.

Preferred:
- **Open Sesame** = ChatGPT voice
- **Text Sesame** = Text Radio

Reason: `Open Sesame Text` contains `Open Sesame` as a complete prefix. A keyword spotter can fire the shorter keyword before the final word is resolved. A distinct phrase removes that ambiguity.

## Shared-function rule

Do not build separate GPS/search/navigation functions for Text Radio.

Both entry doors normalize to one command envelope:

`source = voice | text_radio`
`utterance = <recognized text>`
`intent = router(utterance)`
`function = shared Three Amigos function`

Examples:
- "Where am I?" -> shared location/GPS function
- "Navigate to ..." -> shared navigation function
- "Search for ..." -> shared search function
- "Go quiet" -> close active session and return to wake listening

## Implementation order

1. Preserve existing **Open Sesame -> GptVoiceLauncher** behavior.
2. Add distinct **Text Sesame** keyword to the local KWS engine.
3. Dispatch KWS result by keyword tag instead of a Boolean.
4. Keep the current FUTO path as the screen-on proof/fallback.
5. Add in-service local streaming ASR for the screen-off Text Sesame path.
6. Feed transcript into the same command router/function layer used by voice.
7. Verify on Moto G Power Android 11:
   - screen on
   - screen off after power button
   - repeated wake/re-arm cycles
   - GPS request
   - Go Quiet
   - recovery after failed transcription
8. Only then mark screen-off Text Radio closed.

## Status

Architecture: **YES — feasible and coherent.**
Current FUTO proof: **useful but not the final screen-off engine.**
Remaining physical gate: **device verification on Moto after local ASR integration.**
