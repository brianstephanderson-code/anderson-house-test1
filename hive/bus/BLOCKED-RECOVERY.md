# BLOCKED self-correction

A worker entering BLOCKED does not immediately become a management interruption.

```
work
  ↓
BLOCKED
  ↓
local retry (up to 3 attempts)
  ├─ recovered → continue → OUT
  └─ still blocked
       ↓
return/correlate to originator where possible
       ↓
unresolved / authority needed
       ↓
UPLINK EXCEPTION → management
```

The Function Land basket poller now performs three local attempts before creating a BLOCKED uplink exception.

Every exception preserves the original message correlation so a coordinator can loop it back, reroute it, or escalate it without losing the parent order.

## Management meaning

IN / PENDING / OUT describe normal flow.

BLOCKED describes work that left the normal flow and entered recovery.

Management should normally see only BLOCKED items whose local recovery path has been exhausted.
