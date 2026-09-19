# Anderson House — Full Policy Bridge Search

Status: ACTIVE CANDIDATE FUNCTION
Added: 2026-09-19

## Purpose
A Full Policy Bridge Search applies the current Anderson House policy set as reasoning logic to find and verify a road from known STATE to required DONE.

## Start
Before a Full Policy Bridge Search:
1. Pull the current policy/function files from the Anderson House repository.
2. Treat those policies as the search engine's operating logic.
3. State the known STATE and required DONE.
4. Check Alexandria/repository for an already verified road before rediscovering it.

## Question -> DONE Gate
Treat the user's question/request as the first source of DONE.

1. Extract the requested end state from the user's own words before searching.
2. Preserve explicit constraints in the question as part of DONE (for example: what, when, where, who, method, cost, legality, availability, or other stated conditions).
3. Do not silently replace the user's DONE with an easier or different DONE.
4. Work backwards from DONE by asking: **What must be true for this DONE to exist?**
5. Turn those required truths into preconditions/checks. Search and verify them before choosing or optimizing a road.
6. Ask prospectively: **What required supply, condition, access, service, permission, capacity, or dependency could disappear or fail before DONE?**
7. If a required precondition fails, DONE is not currently reachable by that road. Apply Aikido / NO -> substitute while preserving the original DONE as closely as possible.
8. Only then investigate, compare, optimize, and verify the transformation.

Shorthand:
**QUESTION -> EXTRACT DONE -> WHAT MUST BE TRUE? -> VERIFY PRECONDITIONS -> FIND/TEST ROAD -> DONE**

## Core
STATE -> TRANSFORM -> DONE.

## Search
- Shred at natural joints when useful.
- Search Many Roads rather than assuming the first road is best.
- Borg proven mechanisms instead of reinventing them.
- Use two funnels whenever real-world users/operators are applicable:
  A. authoritative/official/research evidence;
  B. end-user/operator/practitioner experience.
- Reconcile the funnels at the Bridge.
- Preserve provenance and distinguish evidence, inference, anecdote and unknowns.
- Do not duplicate already harvested/search-tested mechanisms unless retesting is necessary.

## Recursive logic
For each material YES, NO, assumption, contradiction, near miss or unexplained result ask HOW COME?
Let useful answers generate the next material questions.
Continue while new branches could materially change the road or DONE.
Stop at verified, rejected, bounded UNKNOWN, or diminishing useful returns.

## Validation
- WHY YES: identify what caused success and whether it repeats.
- WHY NO + Aikido: identify the failure mechanism, preserve what worked, redirect/repair and retest.
- Kill the Riddick: attack apparent DONEs and assumptions.
- Question the policy itself when failures survive transformation changes.
- Check whether STATE is still true.
- Test joints/handoffs: verified module + verified module does not automatically make a verified combined system.
- Treat near misses as evidence.
- Prefer prevention/mistake-proofing over repeatedly repairing the same known failure.

## Contract / proof package
Where useful, define:
- Preconditions: what must be true before TRANSFORM.
- Postconditions: what must be true at DONE.
- Invariants: what must remain true throughout.
A promoted DONE should carry WHY + EVIDENCE + ASSUMPTIONS + LIMITS + VERIFICATION.

## Reality check
Where humans are involved distinguish:
- work-as-imagined;
- work-as-done;
- work-as-experienced.
The official description is not automatically the real STATE.


## Mandatory Two-Funnel Gate
When real-world end-user/operator/practitioner evidence is applicable, the search MUST NOT advance to DONE or RETURN until all three checks are completed:

1. OFFICIAL FUNNEL — authoritative/official/research evidence checked.
2. END-USER FUNNEL — end-user/operator/practitioner experience checked.
3. BRIDGE — agreements, conflicts, friction, failures, workarounds, and unknowns reconciled.

If useful end-user evidence cannot be found, record **END-USER EVIDENCE = UNKNOWN**. UNKNOWN is acceptable; silently skipping the funnel is not.

### Return gate
Immediately before RETURN ask:

**Were all required gates completed?**

Minimum check when the two-funnel rule applies:
- Official funnel: PASS / UNKNOWN
- End-user funnel: PASS / UNKNOWN
- Bridge reconciliation: PASS / UNKNOWN

Any missing/unexamined required gate = **NOT DONE**. Return to search rather than presenting the road as verified.

### NO -> substitute
When a proposed road returns NO, use Aikido to preserve the user's DONE and search for the nearest lawful/practical substitute. Any substitute must pass the same required gates before RETURN.

## Security / legality
GREEN ONLY.
No phishing, credential theft, deception, secret collection, unauthorized access, or security bypass.
Search logic never overrides authorization, safety, law, or policy.

## DO, Don't Defer Gate
The Coordinator owns routine continuation of the search.

- If the next step is available, authorized, safe, and does not require a consequential user choice: **DO IT NOW.**
- Do not end a response with "next step", "next move", "I can check", or a request for routine approval when the Coordinator can perform that step.
- Missing evidence -> search for it.
- Search road fails -> try another lawful road.
- Data conflict -> reconcile it.
- Required gate fails -> repair/reroute/retest.
- Continue until DONE, bounded UNKNOWN, a genuine tool/access limit, or a step that truly requires the user.
- Only return an unfinished result when further progress genuinely requires Brian. State the blocking fact simply.

Shorthand:
**CAN DO -> DO. DON'T DEFER.**

## Return
Return:
- the best-supported road(s);
- new nectar/logic discovered;
- unresolved UNKNOWNs;
- attacks survived/failed;
- provenance;
- reusable policy candidates.

Promote new logic only after appropriate verification.

## Simple invocation
"Run a Full Policy Bridge Search on [STATE/problem] -> [DONE]."

The Coordinator should then pull the current GitHub policy set first and use it as the reasoning constitution for that search.
