# Anderson House Warehouse

The warehouse is the quiet end of a completed loop.

## Two shelves

### functions/
Holds receipts for verified reusable functions.

The canonical function code stays at its normal source path. The warehouse stores a versioned receipt pointing to the canonical code and its proof, so we do not create drifting duplicate copies.

Function receipt fields:
- FUNCTION_ID
- CANONICAL_PATH
- VERSION_COMMIT
- STATUS=VERIFIED
- PROVIDERS / execution surface
- EVIDENCE
- WAREHOUSED_UTC

### communications/
Holds closure manifests for completed communication loops.

A communication is not closed merely because a worker says DONE.

It is closed only when the required return/ACK exists, matches the original MESSAGE_ID/correlation, and a closure receipt is written.

Core loop:

SEND -> IN -> PENDING -> WORK -> OUT -> RETURN -> VERIFY RETURN -> CLOSED -> WAREHOUSE

BLOCKED never enters the completed warehouse.

The source and return files remain immutable evidence in Git history. The closure marker makes them logically inactive so they are no longer dangling work.
