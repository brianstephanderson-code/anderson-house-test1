# Shelf: Verification

Purpose: functions that independently check the finding/output of another function.

Warehouse rule:
- A checker inspects the original material.
- A verifier checks another function's finding.
- Verification stays separate from the function being verified where practical.

- terminal_punctuation_verifier
  - Verifies: terminal_punctuation
  - Source: function-lane/core/terminal_punctuation_verifier.mjs
  - Proof: function-lane/test/terminal_punctuation_verifier.test.mjs
  - Status: TEST-PRESENT

This shelf is intended to grow across Anderson House: text, routing, communications, production, policy, and other functions can each have independent verification functions.
