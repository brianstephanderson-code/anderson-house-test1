import test from "node:test";
import assert from "node:assert/strict";
import { compileSearchQueries, compileSearchQueriesFromState } from "../cloudflare/search_query_compiler.mjs";
import { interpretSearchInput } from "../cloudflare/search_function_interpreter.mjs";
import { createSearchBlackboard } from "../cloudflare/search_blackboard.mjs";

const q="I want to go fishing in May for salmon within 200 kilometers of Perth on the beach. What is the best bait?";

test("compiler consumes functional Blackboard state",()=>{
  const interpreted=interpretSearchInput(q);
  const blackboard=createSearchBlackboard(interpreted);
  const out=compileSearchQueriesFromState(blackboard.state,6);
  assert.equal(out.ok,true);
  assert.equal(out.state.target,"salmon");
  assert.equal(out.state.origin,"Perth");
  assert.deepEqual(out.state.time,["may"]);
  assert.ok(out.state.environment.includes("beach"));
  assert.equal(out.state.unknown,"best bait");
  assert.ok(out.queries.some(x=>x.kind==="FUNCTIONAL_BOOLEAN"&&x.query.includes("AND")));
  assert.ok(out.queries.some(x=>x.query.toLowerCase().includes("salmon")));
  assert.ok(out.queries.some(x=>x.query.toLowerCase().includes("beach")));
  assert.ok(out.queries.some(x=>x.query.toLowerCase().includes("bait")));
});

test("text wrapper still routes through interpreter and Blackboard",()=>{
  const out=compileSearchQueries(q,5);
  assert.equal(out.ok,true);
  assert.equal(out.state.target,"salmon");
  assert.equal(out.state.origin,"Perth");
  assert.ok(out.queries.length>=3);
});
