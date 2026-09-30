import test from "node:test";
import assert from "node:assert/strict";
import { verifyEvidenceParcel, sufficiencyCheck } from "../cloudflare/search_end_to_end.mjs";

test("end-to-end verifier requires readable text plus both provenance joints",()=>{
  const candidate={title:"Example",url:"https://example.com/",source_door:"TEST_DOOR",provenance:"TEST_SEARCH"};
  const good=verifyEvidenceParcel(candidate,{ok:true,provenance:"https://example.com/",chars:150,text:"x".repeat(150),links:[]});
  assert.equal(good.integrity_verified,true);
  assert.equal(sufficiencyCheck([good]).sufficient,true);
  const bad=verifyEvidenceParcel({...candidate,provenance:null},{ok:true,provenance:"https://example.com/",chars:150,text:"x".repeat(150)});
  assert.equal(bad.integrity_verified,false);
  assert.equal(sufficiencyCheck([bad]).sufficient,false);
});
