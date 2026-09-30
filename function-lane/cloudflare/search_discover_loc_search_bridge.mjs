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

function addResult(out,seen,n,title,rawUrl,provenance) {
  if(out.length>=n) return;
  const url=locOnly(rawUrl);
  if(!url || seen.has(url)) return;
  seen.add(url);
  out.push({
    title:String(title??"").replace(/\s+/g," ").trim(),
    url,
    date:null,
    description:"",
    source_door:"LIBRARY_OF_CONGRESS_VIA_SEARCH_CARRIER",
    provenance,
    authority_url:url
  });
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
        "accept":"text/plain",
        "user-agent":"AndersonHouse-LOC-SearchBridge/1.1"
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

  const text=await r.text();
  const out=[];
  const seen=new Set();

  // Shape 1: Jina text blocks with "Title:" and "URL Source:" lines.
  let pendingTitle="";
  for(const rawLine of text.split(/\r?\n/)) {
    const line=rawLine.trim();
    if(line.startsWith("Title:")) {
      pendingTitle=line.slice(6).trim();
      continue;
    }
    if(line.startsWith("URL Source:")) {
      addResult(out,seen,n,pendingTitle,line.slice(11).trim(),carrier);
      pendingTitle="";
      if(out.length>=n) break;
    }
  }

  // Shape 2: Markdown links.
  if(out.length<n) {
    const re=/\[([^\]]{2,300})\]\((https?:\/\/(?:www\.)?loc\.gov\/[^)\s]+)\)/gi;
    let m;
    while((m=re.exec(text)) && out.length<n) addResult(out,seen,n,m[1],m[2],carrier);
  }

  if(!out.length) return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",
    error:"NO_LOC_RESULTS_FROM_SEARCH_CARRIER",
    provenance:carrier,
    sample:text.slice(0,2500),
    results:[]
  };

  return {
    ok:true,
    function:"SEARCH_DISCOVER_LOC_SEARCH_BRIDGE",
    cost_gate:"$0_BASIC",
    query:q,
    carrier:"JINA_SEARCH_TEXT",
    authority:"LIBRARY_OF_CONGRESS",
    results:out
  };
}
