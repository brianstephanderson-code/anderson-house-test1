// Carrier fallback for LOC when direct cloud egress is challenged.
// Authority remains loc.gov; Jina Reader is only the carrier/rendering bridge.

function cleanTitle(s="") {
  return String(s).replace(/\s+/g," ").replace(/[*_]/g,"").trim();
}

function normalizeLocUrl(raw="") {
  try {
    const u=new URL(raw);
    if (u.hostname!=="www.loc.gov" && u.hostname!=="loc.gov") return "";
    u.hash="";
    return u.toString();
  } catch { return ""; }
}

export async function searchDiscoverLocViaReader(query, limit=5) {
  const q=String(query??"").trim();
  if(!q) return {ok:false,function:"SEARCH_DISCOVER_LOC_BRIDGE",error:"EMPTY_QUERY",results:[]};

  const n=Math.max(1,Math.min(Number(limit)||5,10));
  const target=new URL("https://www.loc.gov/search/");
  target.searchParams.set("q",q);

  const carrier="https://r.jina.ai/"+target.toString();
  const r=await fetch(carrier,{
    redirect:"follow",
    headers:{
      "accept":"text/plain",
      "user-agent":"AndersonHouse-LOC-Bridge/1.0"
    }
  });

  if(!r.ok) return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC_BRIDGE",
    error:"CARRIER_HTTP_"+r.status,
    source_door:"LIBRARY_OF_CONGRESS_VIA_READER",
    provenance:carrier,
    authority_url:target.toString(),
    sample:text.slice(0,2500),
    results:[]
  };

  const text=await r.text();
  const out=[];
  const seen=new Set();

  // Jina Reader returns Markdown. Harvest LOC result links, not carrier links.
  const re=/\[([^\]]{2,300})\]\((https?:\/\/(?:www\.)?loc\.gov\/(?:item|resource)\/[^)\s]+)\)/gi;
  let m;
  while((m=re.exec(text)) && out.length<n) {
    const url=normalizeLocUrl(m[2]);
    if(!url || seen.has(url)) continue;
    seen.add(url);
    out.push({
      title:cleanTitle(m[1]),
      url,
      date:null,
      description:"",
      source_door:"LIBRARY_OF_CONGRESS_VIA_READER",
      provenance:carrier,
      authority_url:target.toString()
    });
  }

  if(!out.length) return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC_BRIDGE",
    error:"NO_LOC_RESULTS_PARSED",
    source_door:"LIBRARY_OF_CONGRESS_VIA_READER",
    provenance:carrier,
    authority_url:target.toString(),
    results:[]
  };

  return {
    ok:true,
    function:"SEARCH_DISCOVER_LOC_BRIDGE",
    cost_gate:"$0_BASIC",
    query:q,
    carrier:"JINA_READER",
    authority:"LIBRARY_OF_CONGRESS",
    results:out
  };
}
