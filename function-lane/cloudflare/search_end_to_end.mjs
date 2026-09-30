import { searchDiscover } from "./search_discover.mjs";
import { searchDiscoverLocRoute } from "./search_discover_loc_route.mjs";
import { searchWebPublic } from "./search_web_public.mjs";
import { compileSearchQueriesFromState } from "./search_query_compiler.mjs";
import { interpretSearchInput } from "./search_function_interpreter.mjs";
import { createSearchBlackboard } from "./search_blackboard.mjs";
import { readTextLinks } from "./read_text_links.mjs";
import { normalizeResults, deduplicateResults } from "./search_socket.mjs";
import { rankCandidatesByRelevance, semanticSufficiency } from "./search_relevance.mjs";
import { buildSearchRecasts } from "./search_recast.mjs";
import { resolvePlace } from "./search_place_resolver.mjs";
import { applyBoundaryEvidence } from "./search_boundary_evidence.mjs";

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

  const interpreted=interpretSearchInput(q);
  const blackboard=createSearchBlackboard(interpreted);

  let boundaryResolution={required:false,origin_resolved:false,candidates:[],selected:null};
  if(blackboard.state.boundary && blackboard.state.origin){
    boundaryResolution.required=true;
    const resolved=await resolvePlace(blackboard.state.origin,{count:3}).catch(e=>({ok:false,error:String(e),results:[]}));
    boundaryResolution={
      required:true,
      origin_resolved:!!resolved.ok,
      provider:resolved.provider??null,
      error:resolved.error??null,
      candidates:Array.isArray(resolved.results)?resolved.results:[],
      selected:resolved.ok && resolved.results?.length ? resolved.results[0] : null,
      attribution:resolved.attribution??null
    };
    if(boundaryResolution.selected){
      blackboard.state.origin_location=boundaryResolution.selected;
    }
  }

  const compiled=compileSearchQueriesFromState(blackboard.state,4);
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

  let candidates=deduplicateResults([
    ...normalizeResults(web.results,"OPEN_WEB"),
    ...normalizeResults(wiki.results,"WIKIPEDIA_MEDIAWIKI_API"),
    ...normalizeResults(loc.results,"LIBRARY_OF_CONGRESS_JSON_API")
  ]);
  const initialCandidateCount=candidates.length;

  async function judgeCandidateSet(rows) {
    const rankedCandidates=rankCandidatesByRelevance(rows,compiled.state);
    const shortlist=rankedCandidates.slice(0,reads);
    const readReturns=await Promise.all(shortlist.map(async candidate=>{
      try { return verifyEvidenceParcel(candidate,await readTextLinks(candidate.url,{maxChars:chars,maxLinks:20})); }
      catch(e) { return verifyEvidenceParcel(candidate,{ok:false,error:String(e)}); }
    }));
    const evidence=readReturns.filter(x=>x.integrity_verified);
    const transportSufficiency=sufficiencyCheck(evidence);
    const semantic=semanticSufficiency(evidence,compiled.state);
    return {rankedCandidates,shortlist,readReturns,evidence,transportSufficiency,semantic};
  }

  let phase=await judgeCandidateSet(candidates);
  let allWebReturns=[...webReturns];
  let recast={attempted:false,casts:[],new_candidate_count:0};

  if(!phase.semantic.summary.sufficient) {
    const recasts=buildSearchRecasts(compiled.state,casts,4);
    if(recasts.length) {
      const recastReturns=await Promise.all(recasts.map(async item=>{
        try { return {cast:item.query,kind:item.kind,...await searchWebPublic(item.query,n)}; }
        catch(e) { return {cast:item.query,kind:item.kind,ok:false,function:"SEARCH_WEB_PUBLIC",error:String(e),results:[]}; }
      }));
      allWebReturns=[...allWebReturns,...recastReturns];
      const recastResults=deduplicateResults(recastReturns.flatMap(x=>normalizeResults(x.results,"OPEN_WEB")));
      candidates=deduplicateResults([...candidates,...recastResults]);
      phase=await judgeCandidateSet(candidates);
      recast={
        attempted:true,
        casts:recastReturns.map(x=>({kind:x.kind,query:x.cast,ok:!!x.ok,count:x.results?.length??0,error:x.error??null,route:x.route??null})),
        new_candidate_count:Math.max(0,candidates.length-initialCandidateCount)
      };
    }
  }

  const {shortlist,readReturns,evidence,transportSufficiency,semantic}=phase;
  const boundaryEvidence=applyBoundaryEvidence(semantic.judged,compiled.state);
  const boundaryRequired=!!compiled.state.boundary;
  const qualifiedEvidence=boundaryEvidence.filter(x=>
    x.integrity_verified &&
    x.semantic_relevance?.relevant &&
    (!boundaryRequired || x.boundary_verification?.pass)
  );
  const sufficiency={
    sufficient:qualifiedEvidence.length>0,
    sufficient_for:boundaryRequired?"FUNCTIONAL_PURPOSE_PROOF_WITH_BOUNDARY":"SEMANTIC_PURPOSE_PROOF",
    verified_relevant_evidence_count:qualifiedEvidence.length,
    reason:qualifiedEvidence.length>0
      ? (boundaryRequired
        ? "At least one readable relevant source also has a verified geographic anchor inside the requested boundary."
        : "At least one readable verified source matches the Blackboard functional purpose.")
      : (boundaryRequired
        ? "Relevant evidence exists, but no source yet has a verified geographic anchor inside the requested boundary."
        : "No readable verified source yet matches the Blackboard functional purpose.")
  };
  const allWebResults=deduplicateResults(allWebReturns.flatMap(x=>normalizeResults(x.results,"OPEN_WEB")));

  return {
    ok:sufficiency.sufficient,
    function:"SEARCH_END_TO_END_V1",
    query:q,
    interpreter:{
      function:interpreted.function,
      roles:interpreted.roles
    },
    blackboard:{
      function:blackboard.function,
      state:blackboard.state,
      history:blackboard.history
    },
    boundary_resolution:boundaryResolution,
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
      verify:evidence.length>0,
      relevance:semantic.summary.verified_relevant_evidence_count>0,
      boundary:!boundaryRequired || qualifiedEvidence.length>0,
      sufficient:sufficiency.sufficient
    },
    doors:[
      {door:"OPEN_WEB",ok:allWebResults.length>0,count:allWebResults.length,error:null,route:recast.attempted?"QUERY_COMPILER_PLUS_RECAST":"QUERY_COMPILER_MULTI_CAST",casts:allWebReturns.map(x=>({kind:x.kind??null,query:x.cast,ok:!!x.ok,count:x.results?.length??0,route:x.route??null,error:x.error??null}))},
      {door:"WIKIPEDIA_MEDIAWIKI_API",ok:!!wiki.ok,count:wiki.results?.length??0,error:wiki.error??null,query:primary},
      {door:"LIBRARY_OF_CONGRESS",ok:!!loc.ok,blocked:!!loc.blocked,count:loc.results?.length??0,error:loc.error??null,route:loc.route??null,query:primary}
    ],
    initial_candidate_count:initialCandidateCount,
    candidate_count:candidates.length,
    recast,
    shortlist_count:shortlist.length,
    shortlist:shortlist.map(x=>({title:x.title,url:x.url,source_door:x.source_door,relevance:x.relevance})),
    evidence:boundaryEvidence,
    transport_sufficiency:transportSufficiency,
    semantic_sufficiency:semantic.summary,
    sufficiency
  };
}
