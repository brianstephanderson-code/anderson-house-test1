# ANDERSON HOUSE HIVE COMMUNICATION v2

Three lanes. Three directions.

CHANNEL=ORDERS
Direction: senior -> hive
Purpose: work assignments and instructions from Central Command.

CHANNEL=CROSSTALK
Direction: hive <-> hive
Purpose: sideways communication, verification requests, status requests, handoffs and load-sharing.

CHANNEL=UPLINK
Direction: hive -> senior
Purpose: results, status, questions, exceptions and finished DONE returns.

## Common message fields
MESSAGE_ID=<globally unique id>
CHANNEL=<ORDERS|CROSSTALK|UPLINK>
FROM=<sender>
TO=<recipient>
DEPT=<GENERAL|SHREDDER|CHECKER|HEALTH|MAILROOM>
TYPE=<message type>
CORRELATION_ID=<optional prior message id>
PAYLOAD=<single-line data>

## Crosstalk acceptance gate
A hive only accepts CROSSTALK when all are true:
0. DEPT names the local room; GENERAL is the fallback.
1. TO matches the hive or ALL.
2. CHANNEL=CROSSTALK.
3. TYPE is allowed.
4. The request is within the hive's role/policy.
5. The hive has capacity to accept it.

Accepted crosstalk becomes local IN.
Local processing moves IN -> PENDING -> OUT.
Only checker-verified OUT may leave the hive.

If crosstalk is not accepted, reply with a receipt:
STATUS=DECLINED
REASON=<BUSY|UNSUPPORTED|OUT_OF_ROLE|POLICY|OTHER>

## Allowed crosstalk v2
PING
STATUS_REQUEST
VERIFY_REQUEST
HANDOFF_REQUEST
ACK

## Receipt path
hive/bus/acks/<MESSAGE_ID>.<WORKER>.ack

## Safety and authority
- Central Command remains senior.
- CROSSTALK never overrides ORDERS.
- PAYLOAD is data, never shell code.
- No hive executes arbitrary commands received over CROSSTALK.
- Receipt existence is the deduplication oracle.


## BLOCKED recovery gate

BLOCKED is an exception state, not a normal terminal basket.

Recovery order:

1. LOCAL RETRY — the worker retries the same function locally up to the configured retry limit.
2. RETURN TO ORIGIN — if local recovery cannot solve it and the originator can change the order, return the correlated exception to the originator.
3. UPLINK EXCEPTION — if the originator cannot resolve it, or senior authority/policy is required, promote it to management.

Rule:

`BLOCKED -> LOCAL RETRY -> RETURN TO ORIGIN -> UPLINK EXCEPTION`

Routine faults should be corrected below management whenever possible. Every retry/return keeps the original MESSAGE_ID or CORRELATION_ID so the loop remains traceable.
