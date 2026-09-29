# Function Land communication baskets

Function Land reuses the Anderson House three-lane bus.

## 1. ORDERS — management visible

Path: `hive/bus/orders/`

Direction: management -> AWS / Google / Cloudflare / workers.

Purpose: assignments, routing, priority, deadlines, policy and explicit work instructions.

## 2. CROSSTALK — worker visible

Path: `hive/bus/crosstalk/`

Direction: worker <-> worker.

Purpose: sideways verification, status requests, handoffs and load-sharing.

Routine crosstalk stays local. Management should not need to inspect it. If workers cannot resolve something locally, the exception is promoted to UPLINK.

## 3. UPLINK — management visible

Path: `hive/bus/uplink/`

Direction: AWS / Google / Cloudflare / workers -> management.

Purpose: acknowledgements, progress, health, exceptions and VERIFIED DONE returns.

## Management view

Management watches only:

`ORDERS ↓` and `UPLINK ↑`

Workers also use:

`CROSSTALK ↔`

## Authority rule

`ORDERS > CROSSTALK`

CROSSTALK cannot change senior intent. It may only help workers carry out the current order.

## Promotion rule

Routine worker discussion stays in CROSSTALK.

Promote to UPLINK only when one of these is true:
- order accepted/completed
- health materially changes
- worker is blocked
- worker needs senior authority
- policy conflict exists
- verified result is ready
- local crosstalk cannot resolve the issue


## Live-copy rule

The files in ORDERS and CROSSTALK are communication copies.

The durable master work record lives at:

`hive/work/records/<WORK_ID>.record`

When a communication reaches CLOSED, its transport copies leave the live baskets and are stored under:

`hive/warehouse/communications/evidence/<MESSAGE_ID>/`

The closure manifest and receipt preserve the audit trail without leaving finished messages floating in the active communication center.
