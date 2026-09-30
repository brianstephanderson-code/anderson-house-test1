// Search-carrier fallback for LOC.
// Search carrier discovers loc.gov URLs; authority remains each returned loc.gov page.

function locOnly(raw="") {
  try {
    const u=new URL(raw);
    const h=u.hostname.toLowerCase();
    if(h!=="loc.gov" && h!=="www.loc.gov") return "";
    u.hash="";
    return u.toString();
  } catch { return ""; }
}

export async function searchDiscoverLocViaSearchCarrier(query, limit=5) {
  const q=String(query??"").trim();
  if(!q) return {ok:false,function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",error:"EMPTY_QUERY",results:[]};

  const n=Math.max(1,Math.min(Number(limit)||5,10));
  const carrier="https://s.jina.ai/"+encodeURIComponent("site:loc.gov "+q);

  let r;
  try {
    r=await fetch(carrier,{
      redirect:"follow",
      headers:{
        "accept":"application/json",
        "user-agent":"AndersonHouse-LOC-SearchBridge/1.0"
      }
    });
  } catch(e) {
    return {
      ok:false,
      function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",
      error:"SEARCH_CARRIER_FETCH_FAILED",
      detail:String(e?.message??e),
      provenance:carrier,
      results:[]
    };
  }

  if(!r.ok) return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",
    error:"SEARCH_CARRIER_HTTP_"+r.status,
    provenance:carrier,
    results:[]
  };

  let j;
  try { j=await r.json(); }
  catch {
    return {
      ok:false,
      function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",
      error:"SEARCH_CARRIER_NON_JSON",
      provenance:carrier,
      results:[]
    };
  }

  const items=Array.isArray(j)?j:(Array.isArray(j?.data)?j.data:[]);
  const out=[];
  const seen=new Set();

  for(const x of items) {
    if(out.length>=n) break;
    const url=locOnly(x?.url??"");
    if(!url || seen.has(url)) continue;
    seen.add(url);
    out.push({
      title:String(x?.title??"").trim(),
      url,
      date:x?.date??null,
      description:String(x?.description??x?.content??"").replace(/\s+/g," ").slice(0,500),
      source_door:"LIBRARY_OF_CONGRESS_VIA_SEARCH_CARRIER",
      provenance:carrier,
      authority_url:url
    });
  }

  if(!out.length) return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",
    error:"NO_LOC_RESULTS_FROM_SEARCH_CARRIER",
    provenance:carrier,
    results:[]
  };

  return {
    ok:true,
    function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",
    cost_gate:"$0_BASIC",
    query:q,
    carrier:"JINA_SEARCH",
    authority:"LIBRARY_OF_CONGRESS",
    results:out
  };
}
