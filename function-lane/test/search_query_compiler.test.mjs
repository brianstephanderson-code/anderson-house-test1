import test from "node:test";
import assert from "node:assert/strict";
import { extractSearchState, compileSearchQueries } from "../cloudflare/search_query_compiler.mjs";

test("extracts useful search state from conversational fishing request",()=>{
  const q="I want to go fishing in May. I want to go fishing for salmon. I'm in Perth, Australia. I don't want to go 200 kilometers out of Perth to catch the salmon. I'd like to catch them within that distance. What bait is the best?";
  const s=extractSearchState(q);
  assert.equal(s.subject,"salmon");
  assert.ok(s.times.includes("may"));
  assert.ok(s.constraints.some(x=>x.startsWith("200 ")));
  assert.ok(s.content.includes("salmon"));
  assert.ok(s.content.includes("bait"));
});

test("compiler emits compact and operator-aware variants",()=>{
  const q="I want to go fishing in May. I want to go fishing for salmon. I'm in Perth, Australia. I don't want to go 200 kilometers out of Perth to catch the salmon. I'd like to catch them within that distance. What bait is the best?";
  const out=compileSearchQueries(q,5);
  assert.equal(out.ok,true);
  assert.ok(out.queries.length>=3);
  assert.ok(out.queries.some(x=>x.kind==="BOOLEAN_AND"&&x.query.includes("AND")));
  assert.ok(out.queries.some(x=>x.query.toLowerCase().includes("salmon")));
  assert.ok(out.queries.some(x=>x.query.toLowerCase().includes("bait")));
});
