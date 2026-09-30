function norm(v=""){ return String(v??"").toLowerCase().replace(/[^a-z0-9]+/g," ").replace(/\s+/g," ").trim(); }
function has(hay,needle){ const n=norm(needle); return !!n && norm(hay).includes(n); }
function uniq(xs=[]){ const out=[]; const seen=new Set(); for(const x of xs){ const k=norm(x); if(!k||seen.has(k)) continue; seen.add(k); out.push(x); } return out; }

function keywords(v=""){
  const stop=new Set(["a","an","the","is","are","what","which","best","good","better","most"]);
  return uniq(norm(v).split(" ").filter(x=>x.length>2&&!stop.has(x)));
}

function functionalFocus(state={}){
  return uniq([
    state.action,
    ...keywords(state.what),
    ...(Array.isArray(state.environment)?state.environment:[])
  ].filter(Boolean));
}

export function relevanceSignals(candidate={}, state={}) {
  const title=String(candidate.title??"");
  const snippet=String(candidate.snippet??"");
  const url=String(candidate.url??"");
  const hay=`${title} ${snippet} ${url}`;

  const target=String(state.target??"").trim();
  const origin=String(state.origin??"").trim();
  const times=Array.isArray(state.time)?state.time:[];
  const environment=Array.isArray(state.environment)?state.environment:[];
  const focus=functionalFocus(state);

  const target_hit=target ? has(hay,target) : true;
  const origin_hit=origin ? has(hay,origin) : true;
  const time_hits=times.filter(x=>has(hay,x));
  const environment_hits=environment.filter(x=>has(hay,x));
  const focus_hits=focus.filter(x=>has(hay,x));

  let score=0;
  if(target && target_hit) score+=10;
  if(origin && origin_hit) score+=6;
  score+=environment_hits.length*3;
  score+=time_hits.length;
  score+=focus_hits.length*2;
  if(/\.gov\.|\.edu\.|gov\.au|org\.au/.test(url.toLowerCase())) score+=1;

  return {score,target_hit,origin_hit,time_hits,environment_hits,focus_hits};
}

export function rankCandidatesByRelevance(candidates=[], state={}) {
  return (Array.isArray(candidates)?candidates:[])
    .map((candidate,index)=>({candidate,index,signals:relevanceSignals(candidate,state)}))
    .sort((a,b)=>{
      const at=a.signals.target_hit?1:0, bt=b.signals.target_hit?1:0;
      if(bt!==at) return bt-at;
      const ao=a.signals.origin_hit?1:0, bo=b.signals.origin_hit?1:0;
      if(bo!==ao) return bo-ao;
      return b.signals.score-a.signals.score || a.index-b.index;
    })
    .map(x=>({...x.candidate,relevance:x.signals}));
}

export function evidenceRelevance(evidence={}, state={}) {
  const hay=`${evidence.title??""} ${evidence.url??""} ${evidence.text??""}`;
  const target=String(state.target??"").trim();
  const origin=String(state.origin??"").trim();
  const environment=Array.isArray(state.environment)?state.environment:[];
  const unknownTerms=keywords(state.what);

  const target_hit=target ? has(hay,target) : true;
  const origin_hit=origin ? has(hay,origin) : true;
  const environment_hits=environment.filter(x=>has(hay,x));
  const unknown_hits=unknownTerms.filter(x=>has(hay,x));

  const place_ok=!origin || origin_hit;
  const environment_ok=environment.length===0 || environment_hits.length>0;
  const unknown_ok=unknownTerms.length===0 || unknown_hits.length>0;
  const relevant=Boolean(target_hit && place_ok && environment_ok && unknown_ok);

  return {relevant,target_hit,origin_hit,environment_hits,unknown_hits};
}

export function semanticSufficiency(evidence=[], state={}) {
  const judged=(Array.isArray(evidence)?evidence:[]).map(x=>({...x,semantic_relevance:evidenceRelevance(x,state)}));
  const relevant=judged.filter(x=>x.integrity_verified && x.semantic_relevance.relevant);
  return {
    judged,
    summary:{
      sufficient:relevant.length>0,
      sufficient_for:"SEMANTIC_PURPOSE_PROOF",
      verified_relevant_evidence_count:relevant.length,
      reason:relevant.length>0
        ? "At least one readable verified source matches the Blackboard target, place, environment and what."
        : "Readable evidence exists, but none yet matches the Blackboard target, place, environment and what."
    }
  };
}
