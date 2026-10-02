# Anderson House Policy — External Receiver Purpose / Constraint Rule

## Core principle

An external platform, customer, publisher, service, machine, department, or downstream system does **not** need a new Anderson House character or special permanent role.

Instead, it is treated as an **external purpose / constraint source** that Bill, Ted, Linda, and the Coordinator handle through their normal jobs.

## Example: KDP

KDP's role is not to govern the literary work itself.

KDP is an external receiver with:
- a purpose,
- a required input state,
- technical constraints,
- policy constraints,
- acceptance conditions,
- and failure/rejection conditions.

The Coordinator holds both:
1. the Anderson House product purpose / DONE, and
2. the external receiver's required input state.

The bridge must make these meet.

## Bill — Survey the receiver

Bill asks:

**What does the external receiver actually need from us?**

Bill surveys:
- official requirements,
- current specifications,
- acceptance rules,
- rejection conditions,
- legal/licensing constraints,
- end-user/operator evidence,
- historical or alternate methods where useful,
- and any downstream consequences.

Bill translates rules into **functional requirements**.

Example:
- "page count must be within range" becomes a **page-count verification function**.
- "cover dimensions depend on final pagination" becomes a **cover-geometry calculation function**.
- "public-domain edition must be differentiated" becomes a **differentiation verification function**.

Bill does not merely copy rules; he returns the functions necessary to satisfy them.

## Ted — Build the adapter

Ted asks:

**What usable functions do we need to build, reuse, adapt, compose, borrow, or borgarize so our output reaches the receiver in its required state?**

Ted builds the **adapter layer** between the Anderson House internal product and the external receiver.

This adapter should remain modular and replaceable.

## Linda — Verify both sides

Linda asks:

1. **Does the product still satisfy our original purpose?**
2. **Does the resulting output satisfy the external receiver's required input state?**

Linda verifies:
- technical fit,
- legal/policy fit,
- provenance,
- source integrity,
- downstream compatibility,
- and actual acceptance readiness.

## Coordinator — Hold the relationship

The Coordinator keeps the external receiver visible in the route map without allowing it to take over the whole factory.

The Coordinator distinguishes:

**CORE PRODUCT BRIDGE**
from
**EXTERNAL RECEIVER ADAPTER / CONTAINER BRIDGE**

## Standing formula

**OUR DONE → ADAPTER FUNCTIONS → EXTERNAL RECEIVER'S REQUIRED INPUT STATE**

Or, when the external platform acts as a container:

**EXTERNAL CONTAINER BRIDGE**
contains
**CORE PRODUCT / LITERARY BRIDGE**

## Permanent Bill Hat-Check Question

**EXTERNAL RECEIVER: Who receives this output, and what exact state must it be in for them to accept, use, manufacture, publish, process, or continue it?**

## Reuse

This rule is not KDP-specific.

It applies to:
- publishers,
- print platforms,
- app stores,
- APIs,
- databases,
- downstream departments,
- manufacturing systems,
- customers,
- regulators,
- delivery services,
- file formats,
- machines,
- and any other receiver that imposes an input contract.

When the receiver changes, preserve the core production bridge where possible and replace or adapt only the external receiver layer.

## Architectural consequence

External requirements become **function-discovery inputs**, not hard-coded control over unrelated parts of the factory.

Bill surveys them.
Ted builds the functions that satisfy them.
Linda verifies them.
The Coordinator keeps the whole route aligned.

This allows Anderson House to remain portable, modular, and function-first.
