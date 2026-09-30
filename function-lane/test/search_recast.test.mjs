import test from "node:test";
import assert from "node:assert/strict";
import { buildSearchRecasts } from "../cloudflare/search_recast.mjs";

test("recast simplifies Perth salmon question and adds geographic hypothesis",()=>{
  const state={
    subject:"salmon",
    locations:["Perth"],
    content:["fishing","may","salmon","perth","australia","bait","best"]
  };
  const out=buildSearchRecasts(state,["Perth australia salmon fishing may best bait"],5);
  assert.ok(out.some(x=>x.query.toLowerCase().includes("salmon perth australia bait")));
  assert.ok(out.some(x=>x.query.includes('"Australian salmon"')));
  assert.ok(out.length<=5);
});
