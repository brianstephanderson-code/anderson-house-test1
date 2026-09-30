# BORG EVERYTHING — Search Department Function Harvest

Parent rule: when a useful tool, site, workflow, or system is encountered, extract the reusable function/pattern. Do not copy proprietary code, private data, credentials, or protected material.

## Harvest loop
CAST -> FIND -> BORG -> TEST -> WAREHOUSE -> REUSE

## Borged functions

### CAST
- SEARCH_QUERY — send a query to one search door.
- FAN_OUT — send one purpose/query family to multiple independent doors.
- QUERY_VARIANTS — create materially different casts for the same purpose.
- SPECIALIST_ROUTE — route a cast to a specialist meadow appropriate to its function.
- OPEN_WEB_ROUTE — route a cast to broad public-web discovery.

### RETURN
- NORMALIZE_RESULT — convert heterogeneous search returns to a common parcel: title, URL, snippet, source door, provenance.
- RETURN_AS_READY — return each independent child as soon as it finishes.
- CORRELATE_CHILD — attach parent ticket + child ticket.
- PARENT_COMPLETE — announce expected/received completion without delaying child returns.
- DEDUPLICATE_URL — merge repeated URLs/results from different doors while preserving provenance.

### READ
- FETCH_PUBLIC — retrieve a public HTTP/HTTPS resource.
- STRIP_FURNITURE — remove scripts, styles, navigation, forms, images and other non-reading furniture.
- EXTRACT_READABLE_TEXT — return normalized readable text.
- PRESERVE_LINKS — retain useful outbound/link structure separately from display furniture.
- BOUND_PAYLOAD — cap returned material to a useful size.
- KEEP_PROVENANCE — keep original/final URL and source door attached to every parcel.

### EVIDENCE
- SHORTLIST — cheaply select promising leads before deeper fetch/read.
- EXTRACT_EVIDENCE — pull the specific passage/date/claim needed for the purpose.
- CLAIM_EVIDENCE_JOIN — marry evidence to the claim it is meant to support.
- VERIFY_FINALIST — apply strict verification only when a lead is promoted toward ANSWER/DONE.
- SUFFICIENCY_CHECK — ask whether collected evidence is sufficient for the parent purpose.
- RECAST_MISSING — identify the missing evidence/function and issue a new cast.

### RESILIENCE
- DOOR_FALLBACK — redirect a search/read when one door is unavailable or unsuitable.
- RATE_GAUGE — observe throttling/rate limits and reduce or reroute load.
- FAILURE_RETURN — return a failed child explicitly instead of silently losing it.
- SOURCE_DOOR_TRACE — record which door produced every useful finding.

## Patterns borged from encountered systems
- Text browsers (Lynx/w3m/Links): fetch -> ignore visual furniture -> readable text -> links.
- SearXNG: fan-out -> aggregate -> normalize -> deduplicate.
- Search-result pages/APIs: title -> URL -> snippet -> relevance lead.
- Library/catalog systems: metadata -> identifiers -> provenance -> specialist retrieval.
- Archives: historical version -> date navigation -> old-path/content retrieval.
- Anderson House streaming search: concurrent children -> return-as-ready -> parent completion.
- Linda: claim -> evidence check -> provenance check -> verified finalist.
- Fisherman's Net: purpose -> cast -> collect -> compress -> inspect -> sufficient? -> recast.

## Architecture rule
Functions belong above machines. Cloudflare, AWS, and Google are workers capable of hosting functions; no function is permanently married to one worker.

## Discovery rule
For every useful thing found, ask two questions:
1. What answer/evidence did it give us?
2. What reusable function or workflow is hiding inside how it works?

The second catch goes to the Warehouse.
