# Function Land basket worker loop

The cloud functions are serverless and sleep between invocations, so GitHub Actions supplies the periodic wake-up.

Every five minutes, **Function Land Basket Poller** checks:

- `hive/bus/orders/*.msg`
- `hive/bus/crosstalk/*.msg`

## Worker behavior

For an ORDERS message addressed to AWS, GOOGLE, CLOUDFLARE, or ALL:

`ORDERS -> provider worker -> UPLINK`

The provider does the work. The poller writes the returned result into:

`hive/bus/uplink/<MESSAGE_ID>.<provider>.uplink`

That is management-visible.

For a CROSSTALK message:

`CROSSTALK -> provider worker -> ACK`

Routine worker-side returns go into:

`hive/bus/acks/<MESSAGE_ID>.<provider>.ack`

Management does not need to inspect them.

If CROSSTALK cannot be completed, the failure is promoted to UPLINK as an exception.

## Duplicate gate

An existing ACK or UPLINK file for the same message/provider is treated as already handled, so the periodic poller does not repeat the job.

## Authority

ORDERS remain senior to CROSSTALK. The poller only passes the message PAYLOAD to the existing text-processing function; it does not execute PAYLOAD as shell code.
