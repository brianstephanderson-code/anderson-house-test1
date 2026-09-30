import { searchDiscoverLoc } from "./search_discover_loc.mjs";
import { searchDiscoverLocViaReader } from "./search_discover_loc_bridge.mjs";
import { searchDiscoverLocViaSearchCarrier } from "./search_discover_loc_search_bridge.mjs";

// Compile the flow, not the functions:
// direct official JSON API first; alternate carriers only when that road is blocked.
export async function searchDiscoverLocRoute(query, limit=5) {
  const direct=await searchDiscoverLoc(query,limit);
  if(direct.ok) return direct;

  const mayBridge = direct.blocked || direct.error==="HTTP_403" || direct.error==="HTTP_429" || direct.error==="NON_JSON_RESPONSE";
  if(!mayBridge) return direct;

  const reader=await searchDiscoverLocViaReader(query,limit);
  if(reader.ok) {
    return {
      ...reader,
      function:"SEARCH_DISCOVER_LOC",
      route:"READER_CARRIER_FALLBACK",
      direct_error:direct.error
    };
  }

  const searched=await searchDiscoverLocViaSearchCarrier(query,limit);
  if(searched.ok) {
    return {
      ...searched,
      function:"SEARCH_DISCOVER_LOC",
      route:"SEARCH_CARRIER_FALLBACK",
      direct_error:direct.error,
      reader_error:reader.error
    };
  }

  return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC",
    error:"ALL_LOC_ROUTES_FAILED",
    direct_error:direct.error,
    reader_error:reader.error,
    reader_sample:reader.sample ?? "",
    search_error:searched.error,
    results:[]
  };
}
