// Official Library of Congress SRU catalog fallback.
// Separate hostname/protocol path from the www.loc.gov JSON search front door.

function xmlText(s="") {
  return String(s)
    .replace(/<[^>]+>/g," ")
    .replace(/&amp;/g,"&")
    .replace(/&lt;/g,"<")
    .replace(/&gt;/g,">")
    .replace(/&quot;/g,'"')
    .replace(/&#39;|&apos;/g,"'")
    .replace(/\s+/g," ")
    .trim();
}

function first(block, re) {
  const m=block.match(re);
  return m ? xmlText(m[1]) : "";
}

export async function searchDiscoverLocSru(query, limit=5) {
  const q=String(query??"").trim();
  if(!q) return {ok:false,function:"SEARCH_DISCOVER_LOC_SRU",error:"EMPTY_QUERY",results:[]};

  const n=Math.max(1,Math.min(Number(limit)||5,10));
  const u=new URL("http://lx2.loc.gov:210/LCDB");
  u.searchParams.set("version","1.1");
  u.searchParams.set("operation","searchRetrieve");
  u.searchParams.set("query",'"'+q.replace(/"/g," ")+'"');
  u.searchParams.set("startRecord","1");
  u.searchParams.set("maximumRecords",String(n));
  u.searchParams.set("recordSchema","mods");

  let r;
  try {
    r=await fetch(u.toString(),{
      redirect:"follow",
      headers:{
        "accept":"application/xml,text/xml;q=0.9,*/*;q=0.1",
        "user-agent":"AndersonHouse-LOC-SRU/1.0"
      }
    });
  } catch(e) {
    return {ok:false,function:"SEARCH_DISCOVER_LOC_SRU",error:"SRU_FETCH_FAILED",detail:String(e?.message??e),provenance:u.toString(),results:[]};
  }

  if(!r.ok) return {ok:false,function:"SEARCH_DISCOVER_LOC_SRU",error:"SRU_HTTP_"+r.status,provenance:u.toString(),results:[]};

  const xml=await r.text();
  const out=[];
  const seen=new Set();
  const recordRe=/<(?:\w+:)?recordData\b[^>]*>([\s\S]*?)<\/(?:\w+:)?recordData>/gi;
  let m;

  while((m=recordRe.exec(xml)) && out.length<n) {
    const block=m[1];
    const title=first(block,/<(?:\w+:)?title\b[^>]*>([\s\S]*?)<\/(?:\w+:)?title>/i);
    const lccn=first(block,/<(?:\w+:)?identifier\b[^>]*type=["']lccn["'][^>]*>([\s\S]*?)<\/(?:\w+:)?identifier>/i)
      .replace(/\s+/g,"");
    if(!title || !lccn) continue;

    const url="https://lccn.loc.gov/"+encodeURIComponent(lccn);
    if(seen.has(url)) continue;
    seen.add(url);

    const author=first(block,/<(?:\w+:)?namePart\b[^>]*>([\s\S]*?)<\/(?:\w+:)?namePart>/i);
    const date=first(block,/<(?:\w+:)?dateIssued\b[^>]*>([\s\S]*?)<\/(?:\w+:)?dateIssued>/i);

    out.push({
      title,
      url,
      date:date||null,
      description:author ? "Creator: "+author : "",
      source_door:"LIBRARY_OF_CONGRESS_SRU_CATALOG",
      provenance:u.toString(),
      authority_url:url,
      scope:"LIBRARY_CATALOG"
    });
  }

  if(!out.length) return {
    ok:false,
    function:"SEARCH_DISCOVER_LOC_SRU",
    error:"NO_CATALOG_RESULTS",
    provenance:u.toString(),
    sample:xml.slice(0,1800),
    results:[]
  };

  return {
    ok:true,
    function:"SEARCH_DISCOVER_LOC_SRU",
    cost_gate:"$0",
    query:q,
    authority:"LIBRARY_OF_CONGRESS",
    scope:"LIBRARY_CATALOG",
    results:out
  };
}
