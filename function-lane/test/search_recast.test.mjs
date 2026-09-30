import test from "node:test";
import assert from "node:assert/strict";
import { buildSearchRecasts } from "../cloudflare/search_recast.mjs";

test("recast works from functional Blackboard state",()=>{
  const state={
    target:"salmon",
    origin:"Perth",
    time:["may"],
    environment:["beach"],
    action:"fishing",
    what:"best bait"
  };
  const out=buildSearchRecasts(state,["salmon Perth beach may best bait"],5);
  assert.ok(out.some(x=>x.query.toLowerCase().includes("salmon")));
  assert.ok(out.some(x=>x.query.toLowerCase().includes("perth")));
  assert.ok(out.some(x=>x.query.toLowerCase().includes("beach")));
  assert.ok(out.some(x=>x.query.includes('"Australian salmon"')));
  assert.ok(out.length<=5);
});
