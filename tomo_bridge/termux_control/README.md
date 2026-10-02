# Termux Control Bridge

Purpose: allow Anderson House / Tomo jobs to reach the Moto Termux worker through GitHub without exposing a remote shell.

## Security model
- GitHub is the only command door.
- No inbound public port is opened.
- Worker polls once per minute.
- Accepted actions are only: heartbeat, repo_sync, run_vetted.
- run_vetted can execute only scripts physically present in tomo_bridge/termux_control/actions/.
- Job results are written to results/ and pushed back to main.

## Install on Moto
Run once:

```bash
cd ~/anderson-house-mailbox && git pull --ff-only origin main && bash tomo_bridge/termux_control/install.sh
```

Termux:Boot will start the bridge after phone reboot.

## Job example
```json
{
  "job_id": "termux-health-001",
  "action": "run_vetted",
  "script": "health.sh",
  "timeout": 120
}
```
