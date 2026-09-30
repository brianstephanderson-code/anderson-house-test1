import test from "node:test";
import assert from "node:assert/strict";
import { aiSourceGate } from "../cloudflare/search_ai_source_gate.mjs";

test("AI words are discarded and source evidence is returned", async()=>{
  const fakeReader=async(url)=>({
    ok:true,
    provenance:url,
    chars:500,
    text:"Perth beach salmon anglers commonly use bait and lures. This sentence came from the source page, not the AI.",
    links:[]
  });

  const out=await aiSourceGate({
    answer:"Use marshmallows. This AI answer is deliberately wrong.",
    sources:["https://example.com/source"]
  },{
    evidenceTerms:["bait","salmon"],
    reader:fakeReader
  });

  assert.equal(out.ok,true);
  assert.equal(out.ai_answer_discarded,true);
  assert.equal(out.ai_answer_present,true);
  assert.equal(out.policy,"AI_WORDS_ARE_LEADS_SOURCE_IS_EVIDENCE");
  assert.ok(!JSON.stringify(out).includes("marshmallows"));
  assert.match(out.evidence[0].evidence,/source page/i);
});
