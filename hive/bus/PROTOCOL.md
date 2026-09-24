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
TYPE=<message type>
CORRELATION_ID=<optional prior message id>
PAYLOAD=<single-line data>

## Crosstalk acceptance gate
A hive only accepts CROSSTALK when all are true:
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
