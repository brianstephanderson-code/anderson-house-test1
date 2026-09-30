import test from "node:test";
import assert from "node:assert/strict";
import {cloudflareAiCasts} from "../cloudflare/cloudflare_ai_casts.mjs";

test("Cloudflare AI cast planner keeps AI out of evidence",async()=>{
  const fake={run:async()=>({response:JSON.stringify({
    interpreted_need:"find practical salmon bait near Perth in May",
    casts:["salmon Perth beach May best bait","Australian salmon Perth surf bait","site:reddit.com Perth salmon bait beach"],
    missing:["current operator reports"]
  })})};
  const out=await cloudflareAiCasts("What bait?",fake);
  assert.equal(out.ok,true);
  assert.equal(out.ai_answer_is_evidence,false);
  assert.equal(out.casts.length,3);
  assert.equal(JSON.stringify(out).includes("source"),false);
});
