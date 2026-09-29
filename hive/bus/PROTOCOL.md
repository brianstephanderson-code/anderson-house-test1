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


## CLOSED / warehouse gate

DONE is a worker state. CLOSED is the communication-loop terminal state.

A message loop closes only after:
1. the required recipient(s) return DONE/ACK;
2. the return keeps the original MESSAGE_ID/CORRELATION_ID;
3. the expected return count/identity matches the original target;
4. a warehouse manifest is written;
5. a `hive/bus/closed/<MESSAGE_ID>.closed` receipt retires the loop from active basket accounting.

Shorthand:

`SEND -> IN -> PENDING -> WORK -> OUT -> RETURN -> VERIFY RETURN -> CLOSED -> WAREHOUSE`

For `TO=ALL` in Function Land, closure requires successful correlated returns from AWS, Google and Cloudflare.

BLOCKED is not CLOSED. A blocked loop remains active until recovery succeeds or management explicitly resolves/supersedes it.

The original messages and returns remain as immutable evidence. The CLOSED receipt is the deduplication/retirement oracle, so communication copies do not float forever as dangling loops.


## MASTER / COPY rule

The work/function owns the master record.

Path:

`hive/work/records/<WORK_ID>.record`

A message placed in ORDERS or CROSSTALK is a transport copy of that work state, not the master itself.

Rule:

`MASTER STAYS WITH WORK -> COMM COPY TRAVELS -> RETURN CORRELATES -> COPY CLOSES -> COPY ARCHIVES`

The communication copy may move through baskets and be retired. The master record never depends on the continued existence of a live basket file.

When the loop closes, the Closure Clerk:
1. verifies the expected correlated return(s);
2. writes the CLOSED receipt;
3. writes the warehouse manifest;
4. moves the sent copy and returned copies out of the live baskets into warehouse evidence;
5. updates the master work record with the closure manifest.

This makes a live basket a view of unfinished communication, not a permanent pile of historical messages.

Management may explicitly resolve or supersede an abnormal loop. That disposition is recorded before the communication is warehoused.
