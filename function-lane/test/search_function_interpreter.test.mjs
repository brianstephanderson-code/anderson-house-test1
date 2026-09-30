import test from "node:test";
import assert from "node:assert/strict";
import { interpretSearchInput } from "../cloudflare/search_function_interpreter.mjs";
import { createSearchBlackboard } from "../cloudflare/search_blackboard.mjs";

test("interprets the function of each part of the Perth fishing request",()=>{
  const q="I want to go fishing in May for salmon within 200 kilometers of Perth on the beach. What is the best bait?";
  const i=interpretSearchInput(q);
  assert.equal(i.ok,true);
  assert.equal(i.roles.action,"fishing");
  assert.equal(i.roles.target,"salmon");
  assert.deepEqual(i.roles.time,["may"]);
  assert.equal(i.roles.origin,"Perth");
  assert.equal(i.roles.boundary.value,200);
  assert.equal(i.roles.boundary.operator,"<=");
  assert.ok(i.roles.environment.includes("beach"));
  assert.equal(i.roles.what,"best bait");

  const b=createSearchBlackboard(i);
  assert.equal(b.state.target,"salmon");
  assert.equal(b.state.origin,"Perth");
  assert.equal(b.state.environment[0],"beach");
  assert.equal(b.sufficient,false);
});
