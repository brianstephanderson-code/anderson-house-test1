# Conversational Barge-In REPLAY v1

Status: REPLAY ONLY — NOT PRODUCTION

## Purpose
Prove one thing on the Moto G Power (2021):
while Tomo speech is playing, Brian can begin speaking and the device stops Tomo quickly enough to capture Brian's interruption as the next conversational turn.

## Architecture gate
One conversation controller owns microphone + speech output.
Do not run competing speech recognizers/listeners for this replay.

## Test phrase
Tomo speaks a deliberately long line:
> "The camera bridge is working through several small functions, and I will keep talking until you interrupt me naturally."

Brian interrupts at an unpredictable point with:
> "Hang on, what do you mean by the bridge?"

## Required observations
Record:
1. Did Brian's voice get detected while TTS was active?
2. Did TTS stop?
3. Approximate stop latency: immediate / under 0.5 s / 0.5–1 s / over 1 s.
4. Was Brian's interruption captured correctly?
5. Did Tomo retain context so "the bridge" resolved to the camera-to-Tomo bridge?
6. Did speaker audio falsely trigger the recognizer?

## PASS
GREEN only if all are true:
- interruption detected while TTS is active;
- TTS stops within about 1 second;
- interruption is substantially captured;
- no repeated self-trigger loop from Tomo's own speaker;
- context survives into the next turn.

## YELLOW
Any of:
- interruption works but is slow;
- first words are clipped;
- occasional speaker false trigger;
- context needs a retry.

## RED
Any of:
- microphone cannot hear Brian during TTS;
- TTS cannot be stopped from the listener event;
- recognizer mostly hears Tomo instead of Brian;
- two audio components fight for microphone ownership.

## Recast order if not GREEN
1. Enable/check platform AcousticEchoCanceler where available.
2. Use voice-activity detection as the interrupt trigger before full speech recognition.
3. Duck TTS volume immediately when human speech energy is detected.
4. Stop TTS, then hand the captured buffer to recognition.
5. If full duplex remains unreliable, use half-duplex fallback:
   Tomo speaks in short chunks with tiny listening gaps.
6. Keep push-to-talk only as last-resort fallback.

## Production rule
Do not merge a barge-in implementation to production until this replay is GREEN on the actual Moto.
