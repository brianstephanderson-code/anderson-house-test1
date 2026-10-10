# Temperature Bee — isolated command lane (staging design)

Status: DESIGN ONLY. No Moto listener has been switched to this lane.

## Separation
- Command source: staging branch only, under `hive/linux-bee/commands/`.
- Results: a separate `temperature-bee-results` branch, never `main`.
- No force pushes, no production mailbox edits, no Android permissions changes.
- Each command has a unique ID; only `repo_status` permitted for first real probe.
- Commands are treated as untrusted input; reject all other actions and duplicate IDs.
- Record acknowledgement and outcome; retry delivery without re-executing acknowledged IDs.
- Read-only first: no code execution, installs, or sensor collection changes.

## Real-device acceptance gate
1. Install/activate a separately configured listener on Moto (not yet done).
2. Observe Moto acknowledging a unique staging-only `repo_status` command.
3. Observe result on isolated results branch with matching command ID.
4. Verify production mailbox and main unchanged by this test.
5. Only then consider a separately authorised temperature reading request.

## Current limitations
Existing Moto listener polls `origin/main` and pushes to `main` and `moto-results`.
Writing a staging command alone cannot reach that listener. A new, isolated
receiver configuration must be deployed and validated on-device before any
claim of remote Moto control. No automatic cloud transmission is active.
