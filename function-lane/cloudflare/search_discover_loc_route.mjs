import { searchDiscoverLoc } from "./search_discover_loc.mjs";
import { searchDiscoverLocSru } from "./search_discover_loc_sru.mjs";

// Official-first LOC routing.
// 1) loc.gov JSON search
// 2) official LOC SRU catalog on lx2.loc.gov when the JSON front door is blocked
export async function searchDiscoverLocRoute(query, limit=5) {
  const direct=await searchDiscoverLoc(query,limit);
  if(direct.ok) return direct;

  const mayFallback = direct.blocked || direct.error==="HTTP_403" || direct.error==="HTTP_429" || direct.error==="NON_JSON_RESPONSE";
  if(!mayFallback) return direct;

  const sru=await searchDiscoverLocSru(query,limit);
  if(sru.ok) {
    return {
      ...sru,
      function:"SEARCH_DISCOVER_LOC",
      route:"OFFICIAL_SRU_FALLBACK",
      direct_error:direct.error
    };
  }

  return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC",
    error:"ALL_OFFICIAL_LOC_ROUTES_FAILED",
    blocked:Boolean(direct.blocked || direct.error==="HTTP_403" || direct.error==="HTTP_429"),
    direct_error:direct.error,
    sru_error:sru.error,
    sru_sample:sru.sample ?? "",
    source_door:"LIBRARY_OF_CONGRESS_JSON_API",
    provenance:direct.provenance ?? "https://www.loc.gov/search/?fo=json",
    results:[]
  };
}
