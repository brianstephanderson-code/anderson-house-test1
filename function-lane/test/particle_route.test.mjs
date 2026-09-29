import test from "node:test";
import assert from "node:assert/strict";
import { canCrosstalk, crosstalkEnvelope, routeFor } from "../core/particle_route.mjs";

test("particle carries its permitted sideways route", () => {
  assert.deepEqual(routeFor("terminal_punctuation"), {
    returnsTo: "text_profile",
    crosstalk: ["terminal_punctuation_verifier"],
  });
});

test("approved verifier crosstalk is allowed", () => {
  assert.equal(canCrosstalk("terminal_punctuation", "terminal_punctuation_verifier"), true);
});

test("unrelated sideways crosstalk is denied", () => {
  assert.equal(canCrosstalk("terminal_punctuation", "metadata"), false);
});

test("approved envelope knows where the result returns", () => {
  assert.deepEqual(
    crosstalkEnvelope("terminal_punctuation", "terminal_punctuation_verifier", { terminalPunctuation: true }),
    {
      from: "terminal_punctuation",
      to: "terminal_punctuation_verifier",
      payload: { terminalPunctuation: true },
      returnTo: "text_profile",
    },
  );
});

test("denied envelope cannot be created", () => {
  assert.throws(
    () => crosstalkEnvelope("terminal_punctuation", "metadata", {}),
    /Crosstalk denied/,
  );
});
