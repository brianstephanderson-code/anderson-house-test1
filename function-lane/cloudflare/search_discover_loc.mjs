// Zero-cost Library of Congress SEARCH_DISCOVER door.
export async function searchDiscoverLoc(query, limit = 5) {
  const q=String(query??"").trim();
  if(!q) return {ok:false,function:"SEARCH_DISCOVER_LOC",error:"EMPTY_QUERY",results:[]};
  const n=Math.max(1,Math.min(Number(limit)||5,10));
  const u=new URL("https://www.loc.gov/search/");
  u.searchParams.set("q",q); u.searchParams.set("fo","json"); u.searchParams.set("c",String(n)); u.searchParams.set("at","results");
  const r=await fetch(u,{headers:{"accept":"application/json","user-agent":"AndersonHouse-SearchDiscover/1.0"}});
  if(!r.ok) return {ok:false,function:"SEARCH_DISCOVER_LOC",error:"HTTP_"+r.status,results:[]};
  const j=await r.json();
  const results=(j?.results??[]).slice(0,n).map(x=>({
    title:x.title??"",
    url:x.id??x.url??"",
    date:x.date??null,
    description:Array.isArray(x.description)?x.description[0]??"":x.description??"",
    source_door:"LIBRARY_OF_CONGRESS_JSON_API",
    provenance:"loc.gov/search/?fo=json"
  }));
  return {ok:true,function:"SEARCH_DISCOVER_LOC",cost_gate:"$0",query:q,results};
}
