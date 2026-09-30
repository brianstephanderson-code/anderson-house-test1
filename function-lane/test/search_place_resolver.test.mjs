import test from "node:test";
import assert from "node:assert/strict";
import { normalizePlaceResult, resolvePlaceOpenMeteo } from "../cloudflare/search_place_resolver.mjs";

test("normalizes a place result to provider-neutral coordinates",()=>{
  const out=normalizePlaceResult({
    name:"Perth",
    latitude:-31.95,
    longitude:115.86,
    country:"Australia",
    country_code:"AU",
    admin1:"Western Australia"
  },"TEST");
  assert.equal(out.name,"Perth");
  assert.equal(out.lat,-31.95);
  assert.equal(out.lon,115.86);
  assert.equal(out.provider,"TEST");
});

test("Open-Meteo adapter is replaceable and testable with injected fetch",async()=>{
  const fakeFetch=async()=>({
    ok:true,
    async json(){
      return {results:[{
        name:"Perth",
        latitude:-31.95224,
        longitude:115.8614,
        country:"Australia",
        country_code:"AU",
        admin1:"Western Australia",
        timezone:"Australia/Perth"
      }]};
    }
  });
  const out=await resolvePlaceOpenMeteo("Perth",{countryCode:"AU",fetchImpl:fakeFetch});
  assert.equal(out.ok,true);
  assert.equal(out.results[0].name,"Perth");
  assert.equal(out.results[0].country_code,"AU");
  assert.ok(Number.isFinite(out.results[0].lat));
  assert.ok(Number.isFinite(out.results[0].lon));
});
