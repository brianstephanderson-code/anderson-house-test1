import test from "node:test";
import assert from "node:assert/strict";
import { distanceKm, checkDistanceBoundary } from "../cloudflare/search_boundary.mjs";

test("distance boundary passes a nearby Perth-coast point",()=>{
  const perth={lat:-31.9523,lon:115.8613};
  const mandurah={lat:-32.5269,lon:115.7217};
  const d=distanceKm(perth,mandurah);
  assert.ok(d>50 && d<100);
  const out=checkDistanceBoundary(perth,mandurah,{operator:"<=",value:200,unit:"kilometers"});
  assert.equal(out.ok,true);
  assert.equal(out.pass,true);
});

test("distance boundary rejects a point beyond 200 km",()=>{
  const perth={lat:-31.9523,lon:115.8613};
  const albany={lat:-35.0275,lon:117.8839};
  const out=checkDistanceBoundary(perth,albany,{operator:"<=",value:200,unit:"kilometers"});
  assert.equal(out.ok,true);
  assert.equal(out.pass,false);
});

test("miles convert before comparison",()=>{
  const a={lat:0,lon:0};
  const b={lat:0,lon:1};
  const out=checkDistanceBoundary(a,b,{operator:"<=",value:70,unit:"miles"});
  assert.equal(out.pass,true);
});
