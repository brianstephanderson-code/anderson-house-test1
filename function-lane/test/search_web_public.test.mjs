import test from "node:test";
import assert from "node:assert/strict";
import { normalizeMwmblResults, normalizeMarginaliaResults } from "../cloudflare/search_web_public.mjs";

test("normalizes Mwmbl segmented title and extract",()=>{
  const out=normalizeMwmblResults([{url:"https://example.com/x",title:[{value:"Perth "},{value:"salmon"}],extract:[{value:"Best "},{value:"bait"}]}],5);
  assert.deepEqual(out[0],{
    title:"Perth salmon",url:"https://example.com/x",snippet:"Best bait",
    source_door:"MWMBL_OPEN_WEB",provenance:"https://api.mwmbl.org/api/v1/search/"
  });
});

test("normalizes Marginalia JSON",()=>{
  const out=normalizeMarginaliaResults([{url:"https://example.org/",title:"Title",description:"  useful   result "}],5);
  assert.equal(out[0].snippet,"useful result");
  assert.equal(out[0].source_door,"MARGINALIA_PUBLIC_API");
});
