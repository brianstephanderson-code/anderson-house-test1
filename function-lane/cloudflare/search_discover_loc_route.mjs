import { searchDiscoverLoc } from "./search_discover_loc.mjs";
import { searchDiscoverLocViaReader } from "./search_discover_loc_bridge.mjs";

// Compile the flow, not the functions:
// direct official JSON API first; carrier bridge only when that road is blocked.
export async function searchDiscoverLocRoute(query, limit=5) {
  const direct=await searchDiscoverLoc(query,limit);
  if(direct.ok) return direct;

  const mayBridge = direct.blocked || direct.error==="HTTP_403" || direct.error==="HTTP_429" || direct.error==="NON_JSON_RESPONSE";
  if(!mayBridge) return direct;

  const bridged=await searchDiscoverLocViaReader(query,limit);
  if(bridged.ok) {
    return {
      ...bridged,
      function:"SEARCH_DISCOVER_LOC",
      route:"CARRIER_FALLBACK",
      direct_error:direct.error
    };
  }

  return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC",
    error:"ALL_LOC_ROUTES_FAILED",
    direct_error:direct.error,
    bridge_error:bridged.error,
    results:[]
  };
}
