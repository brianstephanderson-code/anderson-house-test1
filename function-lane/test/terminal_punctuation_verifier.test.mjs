import test from "node:test";
import assert from "node:assert/strict";
import { punctuationResultFor } from "../core/terminal_punctuation.mjs";
import { verifyTerminalPunctuation } from "../core/terminal_punctuation_verifier.mjs";

test("verifier independently agrees with a correct claim", () => {
  assert.deepEqual(
    verifyTerminalPunctuation({ text: "Many hands work.", claimed: true }),
    { expected: true, claimed: true, passed: true },
  );
});

test("verifier catches a false claim", () => {
  assert.equal(
    verifyTerminalPunctuation({ text: "Many hands work", claimed: true }).passed,
    false,
  );
});

test("micro particle uses only its approved crosstalk verifier", () => {
  const result = punctuationResultFor("Many hands work.");
  assert.equal(result.terminalPunctuation, true);
  assert.deepEqual(result.crosstalkVerification, {
    by: "terminal_punctuation_verifier",
    returnTo: "text_profile",
    passed: true,
  });
});
