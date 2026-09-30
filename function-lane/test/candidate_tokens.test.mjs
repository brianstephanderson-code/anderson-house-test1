import test from "node:test";
import assert from "node:assert/strict";
import { candidateTokenResultFor } from "../core/candidate_tokens.mjs";

test("nominates deterministic candidates without changing source", () => {
  const text = "Ichabod read Cotton Mather and rode toward Sleepy Hollow.";
  const before = text;
  const result = candidateTokenResultFor(text);
  assert.equal(text, before);
  assert.deepEqual(result.candidateTokens.namedReferences, ["Cotton Mather", "Sleepy Hollow"]);
  assert.ok(result.candidateTokens.wordCandidates.includes("ichabod"));
  assert.deepEqual(candidateTokenResultFor(text), result);
});

test("returns candidates only, not annotations or judgments", () => {
  const result = candidateTokenResultFor("Cotton Mather wrote extensively.");
  assert.deepEqual(Object.keys(result), ["candidateTokens"]);
  assert.equal("annotation" in result.candidateTokens, false);
  assert.equal("friction" in result.candidateTokens, false);
});
