function norm(v=""){ return String(v??"").toLowerCase().replace(/[^a-z0-9]+/g," ").replace(/\s+/g," ").trim(); }
function has(hay,needle){ const n=norm(needle); return !!n && norm(hay).includes(n); }
function uniq(xs=[]){ const out=[]; const seen=new Set(); for(const x of xs){ const k=norm(x); if(!k||seen.has(k)) continue; seen.add(k); out.push(x); } return out; }

export function relevanceSignals(candidate={}, state={}) {
  const title=String(candidate.title??"");
  const snippet=String(candidate.snippet??"");
  const url=String(candidate.url??"");
  const hay=`${title} ${snippet} ${url}`;
  const subject=String(state.subject??"").trim();
  const locations=Array.isArray(state.locations)?state.locations:[];
  const times=Array.isArray(state.times)?state.times:[];
  const content=Array.isArray(state.content)?state.content:[];
  const focus=uniq(content.filter(x=>["bait","best","fishing","catch","salmon"].includes(norm(x))));
  const subject_hit=subject ? has(hay,subject) : true;
  const location_hits=locations.filter(x=>has(hay,x));
  const time_hits=times.filter(x=>has(hay,x));
  const focus_hits=focus.filter(x=>has(hay,x));
  let score=0;
  if(subject && subject_hit) score+=8;
  score+=location_hits.length*4;
  score+=time_hits.length*1;
  score+=focus_hits.length*2;
  if(/\.gov\.|\.edu\.|gov\.au|org\.au/.test(url.toLowerCase())) score+=1;
  return {score,subject_hit,location_hits,time_hits,focus_hits};
}

export function rankCandidatesByRelevance(candidates=[], state={}) {
  return (Array.isArray(candidates)?candidates:[])
    .map((candidate,index)=>({candidate,index,signals:relevanceSignals(candidate,state)}))
    .sort((a,b)=>{
      const as=a.signals.subject_hit?1:0, bs=b.signals.subject_hit?1:0;
      if(bs!==as) return bs-as;
      const al=a.signals.location_hits.length?1:0, bl=b.signals.location_hits.length?1:0;
      if(bl!==al) return bl-al;
      return b.signals.score-a.signals.score || a.index-b.index;
    })
    .map(x=>({...x.candidate,relevance:x.signals}));
}

export function evidenceRelevance(evidence={}, state={}) {
  const hay=`${evidence.title??""} ${evidence.url??""} ${evidence.text??""}`;
  const subject=String(state.subject??"").trim();
  const locations=Array.isArray(state.locations)?state.locations:[];
  const content=Array.isArray(state.content)?state.content:[];
  const subject_hit=subject ? has(hay,subject) : true;
  const location_hits=locations.filter(x=>has(hay,x));
  const focusTerms=uniq(content.filter(x=>["bait","best","fishing","catch"].includes(norm(x))));
  const focus_hits=focusTerms.filter(x=>has(hay,x));
  const relevant=Boolean(subject_hit && (locations.length===0 || location_hits.length>0) && focus_hits.length>0);
  return {relevant,subject_hit,location_hits,focus_hits};
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
        ? "At least one readable verified source also matches the subject, location and search purpose."
        : "Readable evidence exists, but none yet matches the required subject, location and search purpose."
    }
  };
}
