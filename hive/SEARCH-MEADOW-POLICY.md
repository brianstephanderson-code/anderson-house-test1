# Anderson House — Search Meadow Policy

## Parent rule

STATE A -> SEARCH MEADOW -> PROVEN DO -> STATE B / VERIFIED DONE

The search is a bounded room or meadow. Its boundaries come from the actual starting STATE, the required DONE, and House policy. Search expands only as far as needed to find and prove a useful DO.

## Dimensions

### BREADTH — Find doors
Ask materially different useful questions and expose plausible roads.

### DEPTH — Open doors
Follow promising roads downward. Shred the problem and, when useful, open STATE into smaller characteristics or functions.

### HEIGHT — Prove doors
Strengthen evidence. Check whether the road works in reality, satisfies policy, and actually reaches the required STATE. Use independent evidence/oracles and Bridge Search/two funnels where applicable.

### VOLUME — The search meadow
VOLUME is the useful search space created by breadth x depth x height.

The meadow may expand outward for alternatives and implode inward for detail. Do not explore volume merely for its own sake. Stop when sufficient evidence supports a lawful, tested DO to the required STATE.

## Adaptive rule

If no useful DO appears -> increase BREADTH.
If a promising road is blocked -> increase DEPTH.
If several roads exist but certainty is weak -> increase HEIGHT.
If the road reaches and proves the required STATE -> DO it and stop searching.

## STATE-opening rule

When a road appears to say NO, open the relevant STATE before accepting the NO.

A general label may hide a useful capability. Example: a device described generally as an Android phone may also contain relevant characteristics such as ARM64 compute, a Linux-like environment, Python, SSH, or outbound HTTPS.

Open STATE progressively, only as far as needed to discover the next DO.

## DON'T-to-DO rule

The House does not collect DON'Ts as endpoints.

Shred every DON'T until a DO falls out.

A blocked or prohibited road becomes a new search question:
"What lawful function or alternative road reaches the same required STATE?"

WALL != STOP.
WALL = NEW SEARCH QUESTION.

## OPEN THE NO — warning-to-requirement rule

A credible NO, DON'T, UNSUPPORTED, DANGEROUS, or NOT AVAILABLE is evidence, not an endpoint.

When a warning blocks a promising road:

1. Preserve the warning. Do not ignore or bypass it.
2. Shred it into the exact condition or joint that causes the problem.
3. Ask: "What must be true for this to become a lawful DO?"
4. Convert those conditions into requirements.
5. Search breadth, depth, and height for a road that satisfies those requirements.
6. Test and verify the modified road.

The warning may contain part of the engineering specification for the bridge.

Do not stop at a general label when a smaller characteristic is the real blocker. Continue opening only the relevant part of STATE or TRANSFORM until the blocking condition is understood.

If a lawful proven road exists -> DO it.
If another warning appears -> OPEN THE NO again.
If the required STATE cannot be reached within House policy after the useful search meadow has been exhausted -> return the verified boundary and evidence.

## Search-to-policy feedback rule

Bridge Search is also a debugging surface for Anderson House itself.

When a search exposes a repeatable failure in the House search method, and a tested correction produces a better road:

SEARCH FAILURE -> SHRED -> PROVEN CORRECTION -> POLICY CANDIDATE -> VERIFY -> HOUSE POLICY

The purpose is to make the next search stronger, not merely to solve the current parcel.

## DONE

Search is complete when the actual starting STATE has been transformed into the required STATE through a lawful, tested road and the result is VERIFIED.

The objective is not to build something impressive. The objective is to reach the required STATE with the smallest sufficient proven road.

## OPEN THE YES — answer-debugging rule

A promising YES is evidence, not automatically DONE.

When an answer, road, tool, or source says a required function can be done, ask:
"Show me. How? What must be true?"

Open the YES only as far as useful:
- expose the assumptions and required conditions underneath it;
- Bridge Search any uncertain or consequential joint;
- test the conditions that matter to the required DONE;
- fold the detail back up once sufficient proof exists.

A YES may therefore become a new local STATE A and start a smaller Bridge Search:

YES -> HOW? -> WHAT MUST BE TRUE? -> TEST -> VERIFIED YES

This process is recursive/fractal. Any important joint can be opened into a smaller STATE -> TRANSFORM -> DONE unit, and that unit can be opened again if needed.

Do not fractalize for its own sake. Use progressive disclosure:
- enough evidence to DO safely -> fold the meadow and act;
- uncertainty, friction, contradiction, or consequence -> open that joint and Bridge Search it;
- stop when the smallest sufficient proven road reaches the required STATE.

## Debug the answer upstream

Prefer:

SEARCH -> ANSWER -> DEBUG THE ANSWER -> BUILD

over discovering avoidable hidden assumptions only after implementation:

SEARCH -> ANSWER -> BUILD -> BUG -> TROUBLESHOOT

This does not promise to eliminate all bugs. It moves useful checking earlier, when changing a search question is cheaper than repairing a built system.

OPEN THE NO finds hidden roads.
OPEN THE YES finds hidden assumptions.
VERIFY decides whether the bridge is ready.

## OPEN THE PARENT — whole-production-line rule

The production line currently visible may be only a child inside a larger production line.

Before treating an important DONE as complete, ask:
"What larger system does this DONE become STATE for?"

Open upward only as far as consequence requires.

A child DONE is not sufficient if its resulting STATE damages, blocks, or contradicts a required parent DONE.

CHILD DONE -> RESULTING STATE -> PARENT SYSTEM -> PARENT DONE

Examples:
- extracting ore can be a mining DONE without being a land, water, community, or generational DONE;
- creating a recreational fishery can be a human-use DONE without being an ecological-restoration DONE;
- catching fish can be an angler DONE while damaging the future fishery.

Do not confuse a useful replacement state with restoration of the previous ecosystem. If restoration is impossible or not the actual objective, name the new target STATE honestly and verify it against the relevant parent requirements.

## Ecological introduction rule

Adding a species, process, resource, or function to solve a local problem creates a new transformation and must be opened.

Do not assume:
"Something useful now exists" = "the ecosystem is restored."

Ask:
- Did it belong in the relevant system?
- What does it consume, compete with, support, or displace?
- What new dependencies and downstream effects does it create?
- What happens after repeated generations or long time periods?
- Does the resulting STATE remain acceptable to the parent DONE?

The local product and the continuing health of its production line must both be considered where the parent DONE requires both.

## Long-lived local knowledge / Country knowledge rule

Long-lived local and Indigenous ecological knowledge can be a high-value evidence universe because repeated observation of the same Country may preserve relationships between visible indicators and larger hidden STATE.

Publicly shared knowledge may reveal compressed indicators such as changes in plants, animals, weather, water, season, or landscape that coincide with useful transitions elsewhere in the system.

Treat such knowledge with respect and attribution:
- identify the people/Country/source where known;
- use knowledge that custodians have chosen to make public;
- do not treat culturally restricted, sacred, or private knowledge as an Anderson House resource;
- do not strip observations from their local context and assume they are universal.

Bridge Search the observation rather than romanticizing or dismissing it:

LOCAL OBSERVATION -> WHAT DOES IT INDICATE? -> WHAT ELSE CHANGES? -> INDEPENDENT EVIDENCE -> VERIFIED USEFUL SIGN

An indicator may be a proxy rather than a cause. Search for the deeper STATE that makes the relationship reliable and identify conditions under which it may stop being reliable.

## Complexity-behind-the-answer rule

When a large evidence universe can be reduced to a reliable observable sign or small action rule, keep the complexity behind the answer.

HUGE STATE -> VERIFIED RELEVANT CHARACTERISTICS -> SIMPLE RELIABLE SIGN -> ACTION

The end user should receive the smallest sufficient instruction needed to reach DONE, while the evidence, assumptions, provenance, and deeper meadow remain available to reopen if reality produces a bug.
