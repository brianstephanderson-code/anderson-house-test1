function flattenParts(v) {
  if (typeof v === "string") return v.trim();
  if (!Array.isArray(v)) return "";
  return v.map(x => typeof x === "string" ? x : String(x?.value ?? "")).join("").replace(/\s+/g," ").trim();
}

function htmlText(v="") {
  return String(v).replace(/<[^>]+>/g," ").replace(/&amp;/g,"&").replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/\s+/g," ").trim();
}

export function normalizeMwmblResults(rows = [], limit = 10) {
  const n=Math.max(1,Math.min(Number(limit)||10,20));
  return (Array.isArray(rows)?rows:[]).slice(0,n).map(x=>({
    title:flattenParts(x?.title), url:String(x?.url??"").trim(), snippet:flattenParts(x?.extract),
    source_door:"MWMBL_OPEN_WEB", provenance:"https://api.mwmbl.org/api/v1/search/"
  })).filter(x=>/^https?:\/\//.test(x.url));
}

export function normalizeMarginaliaResults(rows = [], limit = 10) {
  const n=Math.max(1,Math.min(Number(limit)||10,20));
  return (Array.isArray(rows)?rows:[]).slice(0,n).map(x=>({
    title:String(x?.title??"").trim(), url:String(x?.url??"").trim(),
    snippet:String(x?.description??"").replace(/\s+/g," ").trim(),
    source_door:"MARGINALIA_PUBLIC_API", provenance:"https://api2.marginalia-search.com/search"
  })).filter(x=>/^https?:\/\//.test(x.url));
}

export function normalizeDuckDuckGoHtml(html="", limit=10) {
  const out=[]; const seen=new Set(); const n=Math.max(1,Math.min(Number(limit)||10,20));
  const re=/<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  let m;
  while((m=re.exec(String(html))) && out.length<n) {
    let href=m[1].replace(/&amp;/g,"&");
    try {
      const u=new URL(href, "https://html.duckduckgo.com");
      const target=u.searchParams.get("uddg");
      if(target) href=decodeURIComponent(target);
    } catch {}
    if(!/^https?:\/\//.test(href) || seen.has(href)) continue;
    seen.add(href);
    out.push({title:htmlText(m[2]),url:href,snippet:"",source_door:"DUCKDUCKGO_HTML",provenance:"https://html.duckduckgo.com/html/"});
  }
  return out;
}

async function searchMwmbl(query, limit) {
  const u=new URL("https://api.mwmbl.org/api/v1/search/"); u.searchParams.set("s",query);
  const r=await fetch(u,{headers:{accept:"application/json","user-agent":"AndersonHouse-Search/1.0"}});
  if(!r.ok) return {ok:false,provider:"MWMBL_OPEN_WEB",error:"HTTP_"+r.status,results:[]};
  const results=normalizeMwmblResults(await r.json(),limit);
  return {ok:results.length>0,provider:"MWMBL_OPEN_WEB",results,error:results.length?"":"NO_RESULTS"};
}

async function searchMarginalia(query, limit) {
  const u=new URL("https://api2.marginalia-search.com/search"); u.searchParams.set("query",query); u.searchParams.set("count",String(limit));
  const r=await fetch(u,{headers:{accept:"application/json","API-Key":"public","user-agent":"AndersonHouse-Search/1.0"}});
  if(!r.ok) return {ok:false,provider:"MARGINALIA_PUBLIC_API",error:"HTTP_"+r.status,results:[]};
  const j=await r.json(); const results=normalizeMarginaliaResults(j?.results,limit);
  return {ok:results.length>0,provider:"MARGINALIA_PUBLIC_API",results,error:results.length?"":"NO_RESULTS"};
}

async function searchDuckDuckGo(query, limit) {
  const u=new URL("https://html.duckduckgo.com/html/"); u.searchParams.set("q",query);
  const r=await fetch(u,{headers:{"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36","accept":"text/html"}});
  if(!r.ok) return {ok:false,provider:"DUCKDUCKGO_HTML",error:"HTTP_"+r.status,results:[]};
  const results=normalizeDuckDuckGoHtml(await r.text(),limit);
  return {ok:results.length>0,provider:"DUCKDUCKGO_HTML",results,error:results.length?"":"NO_RESULTS"};
}

function canonicalUrl(raw) {
  let k=String(raw??"");
  try {
    const u=new URL(k);
    u.hash="";
    for(const p of ["utm_source","utm_medium","utm_campaign","utm_term","utm_content","fbclid","gclid"]) {
      u.searchParams.delete(p);
    }
    k=u.toString();
  } catch {}
  return k;
}

function roundRobinDedupe(groups,limit) {
  const out=[]; const seen=new Set();
  let i=0;
  while(out.length<limit) {
    let added=false;
    for(const g of groups) {
      const x=g?.[i];
      if(!x) continue;
      added=true;
      const k=canonicalUrl(x.url);
      if(!k || seen.has(k)) continue;
      seen.add(k);
      out.push(x);
      if(out.length>=limit) break;
    }
    if(!added) break;
    i++;
  }
  return out;
}

export async function searchWebPublic(query, limit=10) {
  const q=String(query??"").trim();
  if(!q) return {ok:false,function:"SEARCH_WEB_PUBLIC",error:"EMPTY_QUERY",results:[]};
  const n=Math.max(1,Math.min(Number(limit)||10,20));

  const calls=[
    ["DUCKDUCKGO_HTML",()=>searchDuckDuckGo(q,n)],
    ["MWMBL_OPEN_WEB",()=>searchMwmbl(q,n)],
    ["MARGINALIA_PUBLIC_API",()=>searchMarginalia(q,n)]
  ];
  const returns=await Promise.all(calls.map(async ([provider,fn])=>{
    const t=Date.now();
    try { const x=await fn(); return {...x,elapsed_ms:Date.now()-t}; }
    catch(e) { return {ok:false,provider,error:String(e),results:[],elapsed_ms:Date.now()-t}; }
  }));
  // Keep provider diversity: do not let the first provider fill the whole result set.
  // Interleave DDG, Mwmbl, and Marginalia results before deduplication.
  const results=roundRobinDedupe(returns.map(x=>x.results||[]),n);
  return {
    ok:results.length>0,function:"SEARCH_WEB_PUBLIC",cost_gate:"$0",query:q,
    route:"MULTI_DOOR_FAIL_SOFT",results,
    doors:returns.map(x=>({door:x.provider,ok:!!x.ok,count:x.results?.length??0,error:x.error||null,elapsed_ms:x.elapsed_ms})),
    health:{green:returns.filter(x=>x.ok).map(x=>x.provider),red:returns.filter(x=>!x.ok).map(x=>x.provider)}
  };
}
