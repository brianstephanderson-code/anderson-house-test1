# Anderson House — Function Production Grammar

## Parent rule

**We are looking for the function.**

Every production problem is expressed as:

**STATE → TRANSFORMATION → DONE**

Each part may contain smaller, nested STATE → TRANSFORMATION → DONE units. Repeat until transformations are small enough to understand, prove, test, replace, reorder, parallelize, and reuse.

## Production-line design

**PURPOSE → STATE → work BACKWARDS from DONE → identify FUNCTIONS → expose ??? → fill/prove bridges → run FORWARDS → AUDIT → DESIGN VERIFIED → execute → verify actual DONE**

### Backward pass
Start from the required DONE and determine what must be true immediately before it. Continue backward until the starting STATE is reached.

### Forward pass
Starting from the real STATE, walk through the proposed functions toward DONE. Check that every output satisfies the next function's required input and remains consistent with the evidenced purpose.

### Unknowns
Any unexplained joint is written explicitly as:

**STATE → ??? → DONE**

Do not hide the unknown inside a larger function. Use evidence, Bridge Search, the Warehouse, R&D, or a new small function to close it.

### Design Proof gate
Before execution, audit each joint:
- Is the input real and defined?
- Is the transformation identified and supported?
- Is the output defined and verifiable?
- Can the next function accept that output?
- Is the transformation consistent with the evidenced originator purpose and required end-user function?
- Are failure states and important contrary evidence accounted for?

Backward and forward models must agree sufficiently for the purpose. Only then mark **DESIGN VERIFIED**.

Design Verified means the proposed line has defined, supported, testable joints and no material unexplained hole. It does not replace proof from actually running the line.

## Modular-flow rule

**Keep the little functions separate; compile the flow, not the functions.**

Do not bind multiple transformations into a fixed composite function without a compelling reason. Prefer small independent functions with explicit inputs, outputs, gates, and handoffs so they can be reordered, parallelized, replaced, rerouted, tested, and improved independently.

## Communication-universe template

For books, music, visual works, speech, software, or another communication sub-universe, use:

**ORIGINATOR → PURPOSE → WORK → FUNCTIONS → END USER**

Identify what function each relevant component performs. Work backward from the required end-user result and forward from the evidenced originator purpose. The aim is not to invent an unsupported intention, but to preserve evidenced purpose and functional relationships through the transformation.

## Execution

After DESIGN VERIFIED:

**verified design → select proven Warehouse functions → build any missing small functions → Amigos execute/test → join → verify actual DONE → return reusable verified functions to Warehouse**

The subject, specialist functions, and depth may change. The parent grammar remains:

# STATE → TRANSFORMATION → DONE
