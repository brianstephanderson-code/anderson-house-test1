# ANDERSON HOUSE HIVE PEER BUS v1

Purpose: lightweight hive-to-hive crosstalk over the shared GitHub repository.

## Message path
hive/bus/messages/<MESSAGE_ID>.msg

## Receipt path
hive/bus/acks/<MESSAGE_ID>.<WORKER>.ack

## Message format
MESSAGE_ID=<globally unique id>
FROM=<CLASSICQUILL|S20|HOTSPOT|MOTO-LOCAL>
TO=<CLASSICQUILL|S20|HOTSPOT|MOTO-LOCAL|ALL>
TYPE=<PING|STATUS_REQUEST|VERIFY_REQUEST|ACK>
CORRELATION_ID=<optional prior message id>
PAYLOAD=<single-line payload>

## Rules
1. Central Command remains senior to all hives.
2. Peer hives may exchange requests, status, verification, and handoff information.
3. A peer message does not override Central Command policy or worker safety limits.
4. Every consumed message gets one receipt file.
5. Receipt existence is the deduplication oracle.
6. Unknown message types are acknowledged as UNSUPPORTED rather than executed.
7. PAYLOAD is data, never shell code.
8. No peer may execute arbitrary commands received over the bus.
