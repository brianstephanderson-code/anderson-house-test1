# Function-owned master work records

This directory holds the durable original record for each work instance.

The master stays with the work.

Communication is by copy:

```
MASTER WORK RECORD
      |
      +---- transport copy -> ORDERS / CROSSTALK
                              |
                              +-> worker
                              +-> return / ACK
                              |
                         verify closure
                              |
                    CLOSED + warehouse
```

A live basket file may be routed, retried, closed, and archived without becoming the source of truth.

Typical fields:
- WORK_ID
- RECORD_KIND
- STATUS
- ORIGIN
- TARGET
- MESSAGE_TYPE
- COMMUNICATION_COPY
- COMMUNICATION_SHA256
- COMM_STATE
- CLOSURE_MANIFEST

Rule: **master stays; copies travel.**
