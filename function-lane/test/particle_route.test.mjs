import test from "node:test";
import assert from "node:assert/strict";
import { canCrosstalk, crosstalkEnvelope, routeFor, uplinkFor } from "../core/particle_route.mjs";

test("particle carries sideways and upward routes", () => {
  assert.deepEqual(routeFor("terminal_punctuation"), {
    returnsTo: "text_profile",
    backupTo: "function_lane_checkpoint",
    crosstalk: ["terminal_punctuation_verifier"],
  });
});

test("primary uplink goes to immediate parent", () => {
  assert.deepEqual(uplinkFor("terminal_punctuation"), {
    via: "primary",
    to: "text_profile",
  });
});

test("backup uplink activates only when primary is unavailable", () => {
  assert.deepEqual(
    uplinkFor("terminal_punctuation", { primaryAvailable: false }),
    { via: "backup", to: "function_lane_checkpoint" },
  );
});

test("approved verifier crosstalk is allowed", () => {
  assert.equal(canCrosstalk("terminal_punctuation", "terminal_punctuation_verifier"), true);
});

test("unrelated sideways crosstalk is denied", () => {
  assert.equal(canCrosstalk("terminal_punctuation", "metadata"), false);
});

test("approved envelope carries both return paths", () => {
  assert.deepEqual(
    crosstalkEnvelope("terminal_punctuation", "terminal_punctuation_verifier", { terminalPunctuation: true }),
    {
      from: "terminal_punctuation",
      to: "terminal_punctuation_verifier",
      payload: { terminalPunctuation: true },
      returnTo: "text_profile",
      backupTo: "function_lane_checkpoint",
    },
  );
});

test("denied envelope cannot be created", () => {
  assert.throws(
    () => crosstalkEnvelope("terminal_punctuation", "metadata", {}),
    /Crosstalk denied/,
  );
});
