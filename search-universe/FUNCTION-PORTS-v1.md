# Anderson House Search Universe — FUNCTION PORTS v1

STATUS=DESIGN_READY
COST_GATE=$0_ONLY
PURPOSE=Connect the Three Amigos to interchangeable web-research functions without binding the hive to one browser, search engine, or provider.

## Senior rule

Compile the flow, not the functions.

The Three Amigos speak the existing Anderson House bus. External web capabilities sit behind small adapters and return standardized evidence.

## Function ports

### SEARCH_DISCOVER
STATE: query + search-pattern/cast + source-door constraints
DONE: candidate URLs/titles/snippets/source-door metadata

### FETCH_URL
STATE: URL
DONE: retrieved body + content type + retrieval metadata

### RENDER_URL
STATE: URL that FETCH_URL could not adequately read
DONE: rendered/readable content + retrieval metadata

### ARCHIVE_DISCOVER
STATE: URL/domain/phrase/date clues
DONE: historical captures/corpus candidates

### SPECIALIST_DISCOVER
STATE: query + universe (books/code/papers/government/etc.)
DONE: specialist candidates + source-door metadata

### EVIDENCE_EXTRACT
STATE: retrieved content + research target
DONE: evidence units with source identity and provenance

### SUFFICIENCY_CHECK
STATE: purpose + collected evidence + contradictions/holes
DONE: SUFFICIENT or RECAST with missing-function/search-door reason

## Bus mapping

Orders retain the live schema:
MESSAGE_ID=<unique>
CHANNEL=ORDERS
FROM=<dispatcher>
TO=<AWS|GOOGLE|CLOUDFLARE|ALL>
DEPT=GENERAL
TYPE=<SEARCH_DISCOVER|FETCH_URL|RENDER_URL|ARCHIVE_DISCOVER|SPECIALIST_DISCOVER|EVIDENCE_EXTRACT|SUFFICIENCY_CHECK>
CORRELATION_ID=<parent work/order when applicable>
PAYLOAD=<data only; never executable shell code>

Returns use CHANNEL=UPLINK and preserve MESSAGE_ID/CORRELATION_ID.

DONE is not CLOSED. Existing Anderson House closure rules still apply: correlated return -> verification -> CLOSED receipt -> warehouse manifest.

## Adapter rule

Each outside capability gets one narrow adapter:

BUS ORDER -> FUNCTION ROUTER -> ADAPTER -> OUTSIDE SERVICE/CORPUS -> STANDARD RETURN -> UPLINK

An adapter must declare:
- function(s) supplied;
- $0/free-tier boundary;
- authentication/account-owner gate if any;
- rate/quota boundary;
- machine-readable input/output;
- failure/decline states;
- provenance fields returned;
- terms/robots/policy constraints where applicable.

No adapter may silently fall through into paid usage. If a hard $0 boundary cannot be guaranteed, mark it NOT_ELIGIBLE until explicitly re-authorized.

## Recovery

DISCOVER A fails -> Aikido -> DISCOVER B.
FETCH fails because rendering is required -> RENDER_URL.
Evidence weak/contradictory -> SUFFICIENCY_CHECK -> RECAST using a materially different pattern/door.

## First-fish acceptance test

1. Create one real SEARCH_DISCOVER order.
2. Route it through one verified $0 machine-readable adapter.
3. Return at least five candidate URLs with source-door/provenance metadata when available.
4. Issue one correlated FETCH_URL order for a candidate.
5. Return evidence through UPLINK.
6. Linda/checker verifies identity, provenance and required evidence fields.
7. Closure Clerk writes CLOSED receipt and warehouse manifest.

PASS only when the complete communication loop closes. A search result alone is not PASS.

## Brian gate

Target: zero Brian action.

Escalate only if an account-owner action is genuinely required (for example enable a free service, accept terms, or create/copy a credential). The escalation must name only the smallest required Brian action.

## Candidate-function hunt

Keep casting for interchangeable $0 implementations of each port. Current candidate families to fit-test include:
- metasearch / machine-readable discover;
- direct specialist APIs and catalogs;
- ordinary HTTP fetch;
- browser rendering for difficult pages;
- web corpora/archives;
- local warehouse indexes.

Candidate names are not architecture. FUNCTION PORTS are architecture.
