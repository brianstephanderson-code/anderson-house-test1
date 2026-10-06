# Vision Band — Promotion Status

Date: 2026-10-06

## Verified
- Endpoint simulator exists.
- Bridge client exists.
- Automated replay exists.
- GitHub Actions Vision Band Replay completed GREEN multiple times.
- Allowlisted Vision bridge actions exist.
- Signed Three Amigos Device Agent build completed successfully.
- Physical Android phone camera capture completed successfully.
- Local Android Vision endpoint is live on 127.0.0.1:8787.
- Real phone replay verified:
  - POST /ping -> 200
  - initial state -> parked
  - capture while parked -> 409 parked_mode
  - POST /mode active -> 200
  - real camera capture -> 200
  - returned image/jpeg
  - image size -> 1920x1080
  - JPEG payload -> 225337 bytes
  - JPEG SHA-256 -> 394f7f385f513816616e33460caa9fb7bf9b3baf04f881624377c818ad0d0109
  - status recorded last_capture_ms
  - POST /mode parked -> 200
  - capture after park -> 409 parked_mode
  - overall -> VISION_PHONE_REAL_ENDPOINT_REPLAY_GREEN

## Gate
CI/SIMULATION: GREEN
SIGNED ANDROID BUILD: GREEN
PHYSICAL PHONE CAMERA: GREEN
REAL PHONE VISION ENDPOINT: GREEN
PARKED PRIVACY GATE: GREEN
ACTIVE CAPTURE: GREEN
JPEG RETURN PATH: GREEN
PHONE-AS-VISION-BAND SUBSTITUTE: GREEN

## Remaining
The phone substitute is now end-to-end proven.
Future XIAO/wearable hardware should implement the same endpoint contract and then run the same replay before promotion.

PRODUCTION STATUS FOR PHONE SUBSTITUTE: GREEN
WEARABLE HARDWARE: NOT YET BUILT / NOT YET PHYSICALLY REPLAYED


## Bridge Function Promotion
- Privacy-safe Termux v2 Vision actions added: vision_status, vision_mode, vision_capture.
- Simulator replay for these v2 actions completed successfully in GitHub Actions.
- Photo bytes remain local/private; public results contain metadata only.

TERMUX V2 VISION ACTIONS: GREEN
PHONE DEPLOYMENT OF UPDATED V2 LISTENER: PENDING
