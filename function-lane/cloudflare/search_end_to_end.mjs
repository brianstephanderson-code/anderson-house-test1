import { searchDiscover } from "./search_discover.mjs";
import { searchDiscoverLocRoute } from "./search_discover_loc_route.mjs";
import { searchWebPublic } from "./search_web_public.mjs";
import { compileSearchQueries } from "./search_query_compiler.mjs";
import { readTextLinks } from "./read_text_links.mjs";
import { normalizeResults, deduplicateResults } from "./search_socket.mjs";
import { rankCandidatesByRelevance, semanticSufficiency } from "./search_relevance.mjs";

export function verifyEvidenceParcel(candidate = {}, read = {}) {
  let publicHttp=false;
  try { publicHttp=/^https?:$/.test(new URL(candidate.url).protocol); } catch {}
  const text=typeof read.text==="string" ? read.text : "";
  const integrity_verified=Boolean(publicHttp && candidate.source_door && candidate.provenance && read.ok && read.provenance && text.length>=100);
  return {
    title:candidate.title??"",
    url:candidate.url??"",
    source_door:candidate.source_door??"UNKNOWN",
    discovery_provenance:candidate.provenance??null,
    reader_provenance:read.provenance??null,
    chars:Number(read.chars??text.length??0),
    text,
    links:Array.isArray(read.links)?read.links.slice(0,10):[],
    integrity_verified
  };
}

export function sufficiencyCheck(evidence = []) {
  const verified=(evidence||[]).filter(x=>x?.integrity_verified);
  return {
    sufficient:verified.length>0,
    sufficient_for:"END_TO_END_TRANSPORT_PROOF",
    verified_evidence_count:verified.length,
    reason:verified.length>0
      ? "At least one discovered public source was read and returned with an intact discovery-to-reader provenance chain."
      : "No discovered source completed the read plus provenance verification chain."
  };
}

export async function searchEndToEndV1(query,{limit=5,readLimit=3,maxChars=4000}={}) {
  const q=String(query??"").trim();
  if(!q) return {ok:false,function:"SEARCH_END_TO_END_V1",error:"EMPTY_QUERY"};
  const n=Math.max(1,Math.min(Number(limit)||5,10));
  const reads=Math.max(1,Math.min(Number(readLimit)||3,5));
  const chars=Math.max(1000,Math.min(Number(maxChars)||4000,12000));

  const compiled=compileSearchQueries(q,4);
  const casts=(compiled.queries||[]).map(x=>x.query).filter(Boolean);
  const primary=casts[0]||q;

  const [wiki,loc,webReturns]=await Promise.all([
    searchDiscover(primary,n).catch(e=>({ok:false,function:"SEARCH_DISCOVER",error:String(e),results:[]})),
    searchDiscoverLocRoute(primary,n).catch(e=>({ok:false,function:"SEARCH_DISCOVER_LOC",error:String(e),results:[]})),
    Promise.all(casts.map(async cast=>{
      try { return {cast,...await searchWebPublic(cast,n)}; }
      catch(e) { return {cast,ok:false,function:"SEARCH_WEB_PUBLIC",error:String(e),results:[]}; }
    }))
  ]);

  const webResults=deduplicateResults(webReturns.flatMap(x=>normalizeResults(x.results,"OPEN_WEB")));
  const web={
    ok:webResults.length>0,
    results:webResults,
    route:"QUERY_COMPILER_MULTI_CAST",
    casts:webReturns.map(x=>({query:x.cast,ok:!!x.ok,count:x.results?.length??0,route:x.route??null,error:x.error??null}))
  };

  const candidates=deduplicateResults([\n    ...normalizeResults(web.results,"OPEN_WEB"),\n    ...normalizeResults(wiki.results,"WIKIPEDIA_MEDIAWIKI_API"),\n    ...normalizeResults(loc.results,"LIBRARY_OF_CONGRESS_JSON_API")\n  ]);\n  const rankedCandidates=rankCandidatesByRelevance(candidates,compiled.state);\n  const shortlist=rankedCandidates.slice(0,reads);
  const readReturns=await Promise.all(shortlist.map(async candidate=>{
    try { return verifyEvidenceParcel(candidate,await readTextLinks(candidate.url,{maxChars:chars,maxLinks:20})); }
    catch(e) { return verifyEvidenceParcel(candidate,{ok:false,error:String(e)}); }
  }));
  const evidence=readReturns.filter(x=>x.integrity_verified);\n  const transportSufficiency=sufficiencyCheck(evidence);\n  const semantic=semanticSufficiency(evidence,compiled.state);\n  const sufficiency=semantic.summary;

  return {
    ok:sufficiency.sufficient,
    function:"SEARCH_END_TO_END_V1",
    query:q,
    query_compiler:{
      function:compiled.function,
      state:compiled.state,
      casts:compiled.queries
    },
    stages:{
      cast:true,
      compile:casts.length>0,
      collect:candidates.length>0,
      shortlist:shortlist.length>0,
      read:readReturns.some(x=>x.chars>=100),
      verify:evidence.length>0,\n      relevance:semantic.summary.verified_relevant_evidence_count>0,\n      sufficient:sufficiency.sufficient
    },
    doors:[
      {door:"OPEN_WEB",ok:!!web.ok,count:web.results?.length??0,error:web.error??null,route:web.route??null,casts:web.casts},
      {door:"WIKIPEDIA_MEDIAWIKI_API",ok:!!wiki.ok,count:wiki.results?.length??0,error:wiki.error??null,query:primary},
      {door:"LIBRARY_OF_CONGRESS",ok:!!loc.ok,blocked:!!loc.blocked,count:loc.results?.length??0,error:loc.error??null,route:loc.route??null,query:primary}
    ],
    candidate_count:candidates.length,\n    shortlist_count:shortlist.length,\n    shortlist:shortlist.map(x=>({title:x.title,url:x.url,source_door:x.source_door,relevance:x.relevance})),\n    evidence:semantic.judged,\n    transport_sufficiency:transportSufficiency,\n    sufficiency
  };
}
