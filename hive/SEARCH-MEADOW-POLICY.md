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
