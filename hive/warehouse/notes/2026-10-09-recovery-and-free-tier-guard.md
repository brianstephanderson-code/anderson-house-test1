# Recovery and Free-Tier Guard — Staging Notebook

Status: DESIGN / NOT PRODUCTION VALIDATED
Date: 2026-10-09

## User operating rule
All canonical production artifacts belong in GitHub/cloud, not on the user's phone. Do not require local phone downloads or Termux file management.

## Current production focus
Dispatcher → Basket Poller → Closure Clerk: safe recovery, job ownership, precheck, cooldown, and replay before deployment.

## Known issues to replay
- Dispatcher-owned order missing a result: poller intentionally skips it; clerk waits for a result.
- Poller BLOCKED uplink exists: later polls skip existing file; failure may remain unresolved.
- Shared concurrency group and scheduled triggers must be preserved until alternative is validated.
- GITHUB_TOKEN pushes do not ordinarily trigger subsequent push workflows.

## Next staged checks
1. Inventory existing recovery implementations and avoid duplication.
2. Implement a read-only recovery triage with run-status evidence and warehouse cross-check.
3. Replay against completed, in-progress, failed, cancelled, delayed, and ambiguous cases.
4. Confirm idempotency and quota guard approval before allowing any retry action.
5. Require review and evidence before promoting to main.

## Hive-the-Hive notebook (critical; parked while production continues)
Quota Guard, Policy Watchdog, Discovery Sensors, Continuity Manager, and independent Hive Heartbeat. Require verified free allowances, conservative reserves, stop before possible billing, and revalidation of replenishment. Design only, not active protections.

## Safety
No automatic retry, provider provisioning, paid usage, or production workflow change from this notebook.
