# Anderson House — Synchronous Handoff Policy

Status: ACTIVE CANDIDATE POLICY
Added: 2026-09-23

## Purpose
Make handoffs observable and detect abnormal flow before responsibility silently transfers.

## Core
A handoff is its own STATE -> TRANSFORM -> DONE unit.

The smallest useful action should complete at the handoff before the next state assumes responsibility.

## Handoff contract
Where practical record:
- sender state;
- parcel identity/count;
- expected receiver;
- expected timing/window;
- acceptance signal;
- resulting state.

## PENDING rule
PENDING is not wasted time.
It is the trust zone between SEND and ACCEPT.

SEND -> PENDING / VERIFY -> ACCEPT -> OUT / NEXT STATE.

Responsibility transfers only after the required acceptance condition is met.

## Synchrony rule
Timing is part of the handoff state.
If one worker, parcel, count, or acknowledgement arrives materially outside the expected pattern, treat the timing mismatch as an anomaly signal and recheck the joint.

Examples:
- expected N parcels, observed N+1 or N-1;
- acknowledgement arrives before the send state exists;
- return appears too early for the claimed transformation;
- expected heartbeat/checkpoint is stale.

## Count rule
Counts are cheap oracles.
When a flow expects a known number of items, compare expected vs observed before accepting the next state.

377 monkeys out and 378 monkeys back = STOP AND CHECK.

## Failure rule
A handoff anomaly does not automatically mean the whole production line failed.
Freeze the affected joint, preserve verified work, inspect the mismatch, repair/reroute, then resume from the last trusted state.

## Shorthand
SEND -> PENDING -> VERIFY -> ACCEPT -> NEXT STATE.
TIMING OUT = CHECK THE JOINT.
COUNT OUT = CHECK THE JOINT.
