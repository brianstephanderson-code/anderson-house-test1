import test from "node:test";
import assert from "node:assert/strict";
import { verifyEvidenceBoundary } from "../cloudflare/search_boundary_evidence.mjs";

const state={
  origin:"Perth",
  origin_location:{name:"Perth",lat:-31.95224,lon:115.8614,provider:"TEST"},
  boundary:{type:"distance",operator:"<=",value:200,unit:"kilometers"}
};

test("Perth-titled evidence passes a Perth 200 km boundary conservatively",()=>{
  const out=verifyEvidenceBoundary({title:"Australian Salmon Fishing Perth - Beach Guide"},state);
  assert.equal(out.required,true);
  assert.equal(out.verified,true);
  assert.equal(out.pass,true);
  assert.equal(out.distance.measured_km,0);
});

test("unanchored evidence does not get guessed into the boundary",()=>{
  const out=verifyEvidenceBoundary({title:"WA Salmon Run - South West Beaches"},state);
  assert.equal(out.required,true);
  assert.equal(out.verified,false);
  assert.equal(out.pass,false);
  assert.equal(out.reason,"EVIDENCE_PLACE_NOT_YET_ANCHORED");
});
