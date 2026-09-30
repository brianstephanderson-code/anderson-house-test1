import { searchDiscover } from "./search_discover.mjs";
import { searchDiscoverLocRoute } from "./search_discover_loc_route.mjs";
import { searchWebPublic } from "./search_web_public.mjs";
import { readTextLinks } from "./read_text_links.mjs";
import { normalizeResults, deduplicateResults } from "./search_socket.mjs";

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

  const [wiki,loc,web]=await Promise.all([
    searchDiscover(q,n).catch(e=>({ok:false,function:"SEARCH_DISCOVER",error:String(e),results:[]})),
    searchDiscoverLocRoute(q,n).catch(e=>({ok:false,function:"SEARCH_DISCOVER_LOC",error:String(e),results:[]})),
    searchWebPublic(q,n).catch(e=>({ok:false,function:"SEARCH_WEB_PUBLIC",error:String(e),results:[]}))
  ]);

  const candidates=deduplicateResults([
    ...normalizeResults(web.results,"OPEN_WEB"),
    ...normalizeResults(wiki.results,"WIKIPEDIA_MEDIAWIKI_API"),
    ...normalizeResults(loc.results,"LIBRARY_OF_CONGRESS_JSON_API")
  ]);
  const shortlist=candidates.slice(0,reads);
  const readReturns=await Promise.all(shortlist.map(async candidate=>{
    try { return verifyEvidenceParcel(candidate,await readTextLinks(candidate.url,{maxChars:chars,maxLinks:20})); }
    catch(e) { return verifyEvidenceParcel(candidate,{ok:false,error:String(e)}); }
  }));
  const evidence=readReturns.filter(x=>x.integrity_verified);
  const sufficiency=sufficiencyCheck(evidence);

  return {
    ok:sufficiency.sufficient,
    function:"SEARCH_END_TO_END_V1",
    query:q,
    stages:{
      cast:true,
      collect:candidates.length>0,
      shortlist:shortlist.length>0,
      read:readReturns.some(x=>x.chars>=100),
      verify:evidence.length>0,
      sufficient:sufficiency.sufficient
    },
    doors:[
      {door:"OPEN_WEB",ok:!!web.ok,count:web.results?.length??0,error:web.error??null,route:web.route??null},
      {door:"WIKIPEDIA_MEDIAWIKI_API",ok:!!wiki.ok,count:wiki.results?.length??0,error:wiki.error??null},
      {door:"LIBRARY_OF_CONGRESS",ok:!!loc.ok,blocked:!!loc.blocked,count:loc.results?.length??0,error:loc.error??null,route:loc.route??null}
    ],
    candidate_count:candidates.length,
    shortlist_count:shortlist.length,
    evidence,
    sufficiency
  };
}
