import test from "node:test";
import assert from "node:assert/strict";
import { basketFor, managementShouldWatch, promoteCrosstalk, orderEnvelope, uplinkEnvelope } from "../core/communication_baskets.mjs";

test("management watches orders and uplink, not routine crosstalk", () => {
  assert.equal(managementShouldWatch("ORDERS"), true);
  assert.equal(managementShouldWatch("UPLINK"), true);
  assert.equal(managementShouldWatch("CROSSTALK"), false);
});

test("basket directions are explicit", () => {
  assert.equal(basketFor("ORDERS").direction, "down");
  assert.equal(basketFor("CROSSTALK").direction, "sideways");
  assert.equal(basketFor("UPLINK").direction, "up");
});

test("resolved crosstalk stays local", () => {
  assert.equal(promoteCrosstalk({ resolved: true }), "CROSSTALK");
});

test("blocked or authority-requiring crosstalk promotes to uplink", () => {
  assert.equal(promoteCrosstalk({ resolved: false }), "UPLINK");
  assert.equal(promoteCrosstalk({ requiresAuthority: true }), "UPLINK");
  assert.equal(promoteCrosstalk({ policyConflict: true }), "UPLINK");
  assert.equal(promoteCrosstalk({ blocked: true }), "UPLINK");
});

test("order and uplink envelopes preserve direction", () => {
  assert.deepEqual(orderEnvelope({ id: "o-1", to: "google", payload: "process" }), {
    id: "o-1", channel: "ORDERS", from: "management", to: "google", payload: "process"
  });
  assert.equal(uplinkEnvelope({ id: "u-1", from: "google", status: "DONE" }).channel, "UPLINK");
});
