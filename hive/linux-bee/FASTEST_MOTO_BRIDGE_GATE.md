# Fastest Moto bridge — inspected 2026-10-10

## Evidence
- Existing phone listener reportedly polls `origin/main` and writes to `main` / `moto-results` (see STAGING_COMMAND_LANE.md). Its actual installed source/configuration has NOT been inspected from this connector.
- Staging receiver exists but is NOT activated on Moto. It records results locally only.
- GitHub Actions tests process a saved Moto reading; they do NOT prove live remote control.
- Staging and main have diverged; do not merge or move either branch for this experiment.

## Shortest safe acceptance path
1. Obtain a **read-only** snapshot of the *actual running* Moto listener configuration, preferably via an already-existing authorized status/telemetry channel. Do not guess filenames or trigger shell commands remotely.
2. Determine whether it supports an isolated second command source and an isolated acknowledgement destination without changing production.
3. If yes, add a single allowlisted `repo_status` probe with a unique ID to staging. If not, use the already-written staging receiver with a one-time explicit Moto activation.
4. Require Moto-generated acknowledgement with matching ID, timestamp, device origin and observed status; save it to a separate results branch. A cloud-created result is not acceptable evidence.
5. Verify no writes to production mailbox/main and no repeat execution on retry.
6. Only then expand to battery-temperature readings; camera/microphone/location require separate Android authorization and end-to-end tests.

## Minimum user interaction
No new APK. No OAuth secrets or commands pasted into chat. Only a one-time phone action if the existing listener cannot already reach the isolated channel. Never call the bridge live until a real device acknowledgement is observed.
