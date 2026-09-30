# BORG EVERYTHING — Search Department Function Harvest

Parent rule: when a useful tool, site, workflow, or system is encountered, extract the reusable function/pattern. Do not copy proprietary code, private data, credentials, or protected material.

## Harvest loop
CAST -> FIND -> BORG -> TEST -> WAREHOUSE -> REUSE

## BOOKED / IMPLEMENTED — 2026-09-30

- READ_TEXT_LINKS is now a live reusable 3 Amigos function.
- It accepts a public HTTP/HTTPS URL, follows redirects, strips non-reading furniture, returns bounded readable text, extracts normalized unique HTTP/HTTPS links, and preserves final-URL provenance.
- It rejects localhost/private-network targets and unsupported content types.
- It remains separate from FETCH_TEXT so either small function can be replaced or improved independently.
- The function is wired into the common 3 Amigos worker interface as type READ_TEXT_LINKS.
- LIVE PROOF: GitHub Actions run 289 tested the deployed Cloudflare Worker and passed READ_TEXT_LINKS with 167 readable characters, 1 normalized HTTP/HTTPS link, and final-URL provenance.
- Plumbing bug found and fixed: GET requests were dropping url/max_chars/max_links before dispatch; fixed in commit 2b71c5f5b5f6902ad48bda1210031d0caf6546ff.
- Proven implementation commits:
  - 6fc73397429d4b24e12a079e42c515fa2fce9753 — Borg text browser readable text and links pattern.
  - c6b71ad4e5983ade1832f96e3b1b957f7b6cdf1f — Wire borged text browser function into Three Amigos.

### BOOKED REPAIR — Library of Congress door — 2026-09-30

- STATE: the normal LOC JSON search door at `www.loc.gov/search/?fo=json` returned HTTP 403 from the Cloudflare Worker.
- Proven cause boundary: the same query logic was valid; the blockage was the `www.loc.gov` security front door for that cloud-origin road.
- Failed alternate carriers were preserved as evidence, not promoted:
  - Reader carrier reached LOC's bot-verification page and later returned 429.
  - Search carrier returned 401 without an API key.
- Official fallback found: Library of Congress SRU catalog service on `http://lx2.loc.gov:210/LCDB`.
- Independent proof: the GitHub-runner `LOC SRU Probe` passed both LOC's documented sample query and the Anderson House Washington Irving / Sleepy Hollow query.
- LIVE 3 AMIGOS PROOF: deploy run 313 completed GREEN. The live LOC gate returned 5 LOC catalog records through `LIBRARY_OF_CONGRESS_SRU_CATALOG` with `route=OFFICIAL_SRU_FALLBACK`.
- The generic FETCH_TEXT probe was decoupled from LOC's challenge page and now uses a neutral HTML page; it passed in the same green run.
- In run 313 every live check passed: profile, SEARCH_DISCOVER, LOC, FETCH_TEXT, READ_TEXT_LINKS, SEARCH_END_TO_END_V1, and the 20-way return-as-ready benchmark.
- Repair pattern borged: SOURCE BLOCKED -> KEEP AUTHORITY -> CHANGE OFFICIAL DOOR -> VERIFY OUTSIDE WORKER -> WIRE FALLBACK -> LIVE PROOF.
- Key repair commits:
  - c4b75b11cf27b344618fa4ad29c3b81975c6c4c8 — add official LOC SRU catalog fallback.
  - d36d5dd436b2f070086db0d88d98a2bed9fcc7fa — route blocked LOC search to official SRU catalog.
  - f069a47d1516a420932b6eb43768897a31748ffe — use documented LOC SRU port 210 endpoint.
  - 8099dd3e69e729ccd9d1a5aeb02f0e156617e19a — probe official LOC SRU outside Cloudflare.
  - 9c394bad9490a1fbc49b44fccd4e80efde8699fc — fix LOC live gate URL validation.
  - 7d153d01781ed2afe92a3c5c88db85cbc991aa57 — decouple generic FETCH_TEXT probe from LOC challenge page.

## BOOKED / LIVE PROVEN — SEARCH_END_TO_END_V1 — 2026-09-30

- Purpose: prove the search machine can walk end to end without gluing its small functions together.
- Flow: CAST -> MULTI-DOOR DISCOVERY -> NORMALIZE/DEDUP -> SHORTLIST -> READ -> PROVENANCE VERIFY -> SUFFICIENCY.
- Live proof: The 3 Amigos Deploy run 309.
- Result: 5 candidates discovered; 3 shortlisted pages completed the read + provenance chain.
- First verified evidence parcel: Wikipedia Old Dutch Church of Sleepy Hollow, 4,151 readable characters.
- Door state during proof: Wikipedia GREEN; LOC unavailable to that concurrent child, without stopping the parent flow.
- Separate LOC probe in the same run returned 5 official Library of Congress SRU catalog records through OFFICIAL_SRU_FALLBACK after the direct JSON door returned HTTP 403.
- Meaning of verification here: transport/integrity + provenance chain only. It does not claim the page proves a research conclusion.
- Sufficiency label: END_TO_END_TRANSPORT_PROOF.
- Implementation commit: b781408e042df4f0a98e1028c63a54b016ba4c47.

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
- READ_TEXT_LINKS — composed live socket implementing the READ family while keeping the underlying small functions conceptually separate.

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
