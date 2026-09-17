# Anderson House Hive Control

STATE: ACTIVE
ROLE: shared two-way mailbox between Tomo Coordinator and authorized workers.

## Protocol
- `hive/inbox/` = parcels from Tomo/Coordinator to workers.
- `hive/outbox/` = worker returns to Coordinator.
- `hive/state/` = durable verified state/checkpoints.
- Stable parcel IDs. Do not duplicate completed parcels.
- Workers claim the next useful parcel, execute it, and return result + evidence.
- Failed parcels are retried individually; after three failures mark QUARANTINE.
- Coordinator reconciles returns and updates verified state.
- Preserve proven production functions while R&D tests copies.

## Human-touch policy
Brian is not the communications bus. Routine decomposition, routing, retries, collection and reconciliation belong to Coordinator/workers wherever authorized tooling permits.
