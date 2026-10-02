# Coordinator Function — Daisy-Chain Parallelism Gate

## Purpose
When the production map reveals an unavoidable sequential dependency, preserve the required daisy-chain order while checking whether useful work inside each link can safely fan out.

## Trigger
A Coordinator identifies a route segment where state B cannot begin until state A is complete.

## Coordinator Hat Check

1. **DAISY CHAIN DETECTED**
   - Confirm the dependency is real and not an accidental sequencing choice.

2. **UPSTREAM STATE**
   - What must already be DONE before this link can start?

3. **INNER PARALLELISM CHECK**
   - Can Bill survey multiple candidate paths/resources at once?
   - Can Ted build, adapt, test, or prepare independent subfunctions in parallel?
   - Can supporting evidence/provenance checks run concurrently?
   - Are there any hidden shared prerequisites that must be pulled earlier?

4. **FAN-OUT**
   - Release only branches whose inputs are independently ready.
   - Preserve job ID, purpose, provenance, interfaces, and stop rules.

5. **JOIN CONDITION**
   - Define what must return before the link can be considered complete.
   - Do not advance merely because one branch finishes.

6. **LINDA VERIFY**
   - Verify each branch as needed.
   - Verify compatibility at the join.
   - Confirm the complete link has reached DONE.

7. **RELEASE NEXT STATE**
   - Only after the join is VERIFIED does the outer daisy chain advance.

## Standing Rule
**DEPENDENCY FIRST → PARALLELIZE INSIDE WHERE SAFE → REJOIN → LINDA VERIFY → RELEASE NEXT STATE.**

## Route Shapes
- 1→1 = Daisy-chain dependency
- 1→many = Fan-out
- many→1 = Join
- many→many = Continued parallel production

## Bill / Ted / Linda Roles
- **Bill:** Survey all relevant available function paths; do not bias toward inward or outward sources.
- **Ted:** Reuse, adapt, compose, borrow, or borgarize the usable subfunctions.
- **Linda:** Verify each meaningful DONE and the final join state before release.
- **Coordinator:** Detect dependencies, expose safe parallelism, define joins, and preserve overall job alignment.

## Reuse
This is a generic Anderson House Coordinator function and may be applied at any scale:
- one tiny transform,
- a department,
- a product branch,
- a complete production line,
- or a whole factory job.
