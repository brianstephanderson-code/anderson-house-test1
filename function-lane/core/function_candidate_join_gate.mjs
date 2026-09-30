// FUNCTION CANDIDATE JOIN GATE
// Collect function candidates returned by many O-survey bees without confusing popularity with fit.
// Preserve provenance, collapse exact repeats, and send disagreements onward for testing.

export function functionCandidateJoinGate({returns=[]}={}) {
  const candidates=new Map();
  const invalid=[];

  for (const r of returns) {
    for (const c of (r.candidates??[])) {
      if (!c.functionId || !c.provenance) { invalid.push(c); continue; }
      if (!candidates.has(c.functionId)) candidates.set(c.functionId,{functionId:c.functionId,claims:[],surveyDoors:new Set()});
      const entry=candidates.get(c.functionId);
      entry.claims.push(c);
      if (r.surveyDoor) entry.surveyDoors.add(r.surveyDoor);
    }
  }

  const joined=[...candidates.values()].map(x=>({
    functionId:x.functionId,
    claims:x.claims,
    surveyDoors:[...x.surveyDoors],
    mentionCount:x.claims.length
  }));

  return {
    functionCandidateJoin:{
      candidates:joined,invalid,
      state:joined.length?'fit-test-ready':'recast-o-fanout',
      rule:'JOIN THE CANDIDATES; NEVER MISTAKE MOST-MENTIONED FOR BEST-FITTING'
    }
  };
}
