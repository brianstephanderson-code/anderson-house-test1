import test from "node:test";
import assert from "node:assert/strict";
import { rankCandidatesByRelevance, semanticSufficiency } from "../cloudflare/search_relevance.mjs";

const state={
  target:"salmon",
  origin:"Perth",
  time:["may"],
  environment:["beach"],
  action:"fishing",
  what:"best bait"
};

test("relevant Perth salmon result outranks readable but unrelated fish pages",()=>{
  const ranked=rankCandidatesByRelevance([
    {title:"Marlin fishing",url:"https://example.org/marlin",snippet:"offshore billfish bait"},
    {title:"Australian Salmon Fishing Perth Beach Guide",url:"https://example.org/salmon-perth",snippet:"Perth beach salmon bait and fishing guide"}
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

test("semantic sufficiency accepts target place environment and purpose match",()=>{
  const out=semanticSufficiency([
    {title:"Australian salmon Perth beach",url:"https://example.org/salmon",text:"Perth beach anglers target salmon with bait while fishing from shore.",integrity_verified:true}
  ],state);
  assert.equal(out.summary.sufficient,true);
});
