function flattenParts(v) {
  if (typeof v === "string") return v.trim();
  if (!Array.isArray(v)) return "";
  return v.map(x => typeof x === "string" ? x : String(x?.value ?? "")).join("").replace(/\s+/g," ").trim();
}

export function normalizeMwmblResults(rows = [], limit = 10) {
  const n=Math.max(1,Math.min(Number(limit)||10,20));
  return (Array.isArray(rows)?rows:[]).slice(0,n).map(x=>({
    title:flattenParts(x?.title),
    url:String(x?.url??"").trim(),
    snippet:flattenParts(x?.extract),
    source_door:"MWMBL_OPEN_WEB",
    provenance:"https://api.mwmbl.org/api/v1/search/"
  })).filter(x=>/^https?:\/\//.test(x.url));
}

export function normalizeMarginaliaResults(rows = [], limit = 10) {
  const n=Math.max(1,Math.min(Number(limit)||10,20));
  return (Array.isArray(rows)?rows:[]).slice(0,n).map(x=>({
    title:String(x?.title??"").trim(),
    url:String(x?.url??"").trim(),
    snippet:String(x?.description??"").replace(/\s+/g," ").trim(),
    source_door:"MARGINALIA_PUBLIC_API",
    provenance:"https://api2.marginalia-search.com/search"
  })).filter(x=>/^https?:\/\//.test(x.url));
}

async function searchMwmbl(query, limit) {
  const u=new URL("https://api.mwmbl.org/api/v1/search/");
  u.searchParams.set("s",query);
  const r=await fetch(u.toString(),{headers:{accept:"application/json","user-agent":"AndersonHouse-Search/1.0"}});
  if(!r.ok) return {ok:false,error:"HTTP_"+r.status,results:[]};
  const j=await r.json();
  const results=normalizeMwmblResults(j,limit);
  return {ok:true,provider:"MWMBL_OPEN_WEB",results};
}

async function searchMarginalia(query, limit) {
  const u=new URL("https://api2.marginalia-search.com/search");
  u.searchParams.set("query",query);
  u.searchParams.set("count",String(Math.max(1,Math.min(Number(limit)||10,20))));
  const r=await fetch(u.toString(),{headers:{accept:"application/json","API-Key":"public","user-agent":"AndersonHouse-Search/1.0"}});
  if(!r.ok) return {ok:false,error:"HTTP_"+r.status,results:[]};
  const j=await r.json();
  const results=normalizeMarginaliaResults(j?.results,limit);
  return {ok:true,provider:"MARGINALIA_PUBLIC_API",results,license:j?.license??null};
}

export async function searchWebPublic(query, limit=10) {
  const q=String(query??"").trim();
  if(!q) return {ok:false,function:"SEARCH_WEB_PUBLIC",error:"EMPTY_QUERY",results:[]};
  const n=Math.max(1,Math.min(Number(limit)||10,20));

  let mwmbl;
  try { mwmbl=await searchMwmbl(q,n); }
  catch(e) { mwmbl={ok:false,error:String(e),results:[]}; }

  if(mwmbl.ok && mwmbl.results.length) {
    return {
      ok:true,function:"SEARCH_WEB_PUBLIC",cost_gate:"$0",query:q,
      route:"MWMBL_OPEN_WEB",results:mwmbl.results,
      doors:[{door:"MWMBL_OPEN_WEB",ok:true,count:mwmbl.results.length}]
    };
  }

  let marginalia;
  try { marginalia=await searchMarginalia(q,n); }
  catch(e) { marginalia={ok:false,error:String(e),results:[]}; }

  return {
    ok:!!(marginalia.ok && marginalia.results.length),
    function:"SEARCH_WEB_PUBLIC",cost_gate:"$0",query:q,
    route:marginalia.ok?"MARGINALIA_PUBLIC_API":"NO_PUBLIC_WEB_DOOR",
    results:marginalia.results??[],
    doors:[
      {door:"MWMBL_OPEN_WEB",ok:!!mwmbl.ok,count:mwmbl.results?.length??0,error:mwmbl.error??null},
      {door:"MARGINALIA_PUBLIC_API",ok:!!marginalia.ok,count:marginalia.results?.length??0,error:marginalia.error??null}
    ]
  };
}
