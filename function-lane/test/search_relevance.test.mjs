import test from "node:test";
import assert from "node:assert/strict";
import { rankCandidatesByRelevance, semanticSufficiency } from "../cloudflare/search_relevance.mjs";

const state={
  subject:"salmon",
  locations:["Perth"],
  times:["may"],
  content:["fishing","may","salmon","perth","australia","bait","best"]
};

test("relevant Perth salmon result outranks readable but unrelated fish pages",()=>{
  const ranked=rankCandidatesByRelevance([
    {title:"Marlin fishing",url:"https://example.org/marlin",snippet:"offshore billfish"},
    {title:"Australian Salmon Fishing: How to Catch Salmon in WA | Perth",url:"https://example.org/salmon",snippet:"Perth salmon bait and fishing guide"}
  ],state);
  assert.match(ranked[0].title,/Australian Salmon/i);
  assert.ok(ranked[0].relevance.score>ranked[1].relevance.score);
});

test("semantic sufficiency rejects unrelated readable evidence",()=>{
  const out=semanticSufficiency([
    {title:"Marlin fishing",url:"https://example.org/marlin",text:"Marlin fishing with live bait offshore.",integrity_verified:true}
  ],state);
  assert.equal(out.summary.sufficient,false);
});

test("semantic sufficiency accepts subject location and purpose match",()=>{
  const out=semanticSufficiency([
    {title:"Australian salmon Perth",url:"https://example.org/salmon",text:"Perth anglers target Australian salmon with bait during the autumn run.",integrity_verified:true}
  ],state);
  assert.equal(out.summary.sufficient,true);
});
